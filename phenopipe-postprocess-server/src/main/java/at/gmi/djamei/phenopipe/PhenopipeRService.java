package at.gmi.djamei.phenopipe;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.UUID;

import javax.script.ScriptException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bson.Document;
import org.bson.types.Binary;
import org.bson.types.ObjectId;

import com.google.protobuf.ByteString;
import com.google.protobuf.Message.Builder;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;

import at.gmi.djamei.config.Config;
import at.gmi.djamei.mongo.PhenopipeMongoDb;
import at.gmi.djamei.r.GrpcRStatusProvider;
import at.gmi.djamei.r.PostprocessExecutor;
import at.gmi.djamei.r.RTaskStack;
import at.gmi.djamei.r.exceptions.TaskExecutionException;
import at.gmi.djamei.r.exceptions.UnableToInitializeException;
import at.gmi.djamei.r.exceptions.UnableToRunException;
import at.gmi.djamei.util.FileUtil;
import at.gmi.djamei.util.PathUtil;
import io.grpc.Metadata.Key;
import io.grpc.Metadata;
import io.grpc.Status;
import io.grpc.StatusException;
import io.grpc.stub.StreamObserver;
import io.reactivex.Observable;

public class PhenopipeRService extends PhenopipeRGrpc.PhenopipeRImplBase{
	static final Logger logger = LogManager.getLogger();
	//TODO Move to shared library
	private StatusException constructGrpcException(Status.Code code, String message, Throwable cause, Map<String,String> details){
		Status status = Status.fromCode(code);
		if(message !=null){
			status = status.withDescription(message);
		}
		if(cause!=null){
			status=status.withCause(cause);
		}
		Metadata meta = new Metadata();
		if(details !=null){
			for(String k : details.keySet()){
				meta.put(Key.of(k, Metadata.ASCII_STRING_MARSHALLER), details.get(k));
			}
		}
		return new StatusException(status, meta);
	}
	private Observable<ProgressResponse> statusObservable(GrpcRStatusProvider sp){
		return Observable
				.combineLatest(sp.getStatusObservable().startWith("Started to watch progress"),sp.getProgressObservable().startWith(0), (String m, Integer p)->{

					return ProgressResponse
					.newBuilder()
					.setMessage(m)
					.setProgress(p);
				})
				//.sample(1, TimeUnit.SECONDS)
				.map(b -> b.build());//TODO build right before sending back?
	}
	
	private ObjectId saveStackInDB(PostprocessingStack stack){
		List<PostprocessingScript> scripts = stack.getScriptsList();
		List<Document> scriptDocs = new ArrayList<Document>();
		for(PostprocessingScript script : scripts){
	
			Binary scriptContent = new Binary(script.getFile().toByteArray());
			
			Document scriptDoc = new Document("name", script.getName())
					.append("description", script.getDescription())
					.append("index", script.getIndex())
					.append("file", scriptContent);
			scriptDocs.add(scriptDoc);
		}
		MongoCollection<Document> stackCollection = PhenopipeMongoDb.INSTANCE.getIapPostprocessingStackCollection();
		Document stackDoc = new Document("name", stack.getName())
				.append("description", stack.getDescription())
				.append("author", stack.getAuthor())
				.append("scripts", scriptDocs);
		stackCollection.insertOne(stackDoc);
		return stackDoc.getObjectId("_id");
	}
	/**
	 * Read in and filter an IAP analysis report file. 
	 * 
	 * all entries corresponding to Plant IDs in the excluded Plants list are not appended to the resulting List.
	 * @param pathToReport The path to the report file to read
	 * @param excludedPlants A List of Plant IDs (those used in the IAP report file/the fileimport.xlsx metadata file) which should be filtered out
	 * @return A List of all lines from the report file which haven't been filtered out
	 * @throws IOException
	 */
	//TODO rename to filterReportFile?
	private List<String> readReportFile(Path pathToReport,List<String> excludedPlants) throws IOException{	
		HashSet<String> excluded = new HashSet<String>(excludedPlants);
		List<String> lines = new ArrayList<String>();
        try (BufferedReader reader = new BufferedReader(new FileReader(pathToReport.toString()))) {
        	String header = reader.readLine();
        	String[] columns = header.split(";");
        	lines.add(header);
        	int id_col=Arrays.asList(columns).indexOf("Plant ID");
        	String line = "";
            while ((line = reader.readLine()) != null) {
                String[] entry = line.split(";");
                if(!excluded.contains(entry[id_col])) {
                	lines.add(line);
                } 
            }
        }  
        return lines;
        
	}
	/**
	 * Writes all lines given to a file specified by the destination path
	 * 
	 * @param destination The path to the destination file the lines should be written to
	 * @param lines A list of strings representing the lines to be written
	 * @throws IOException 
	 */
	private void writeReportFile(Path destination, List<String> lines) throws IOException{
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(destination.toString()))){
        	for(String line : lines){
        		writer.write(line);
        		writer.newLine();
        	}
        } catch(IOException e){
        	if(Files.exists(destination)){
        		Files.delete(destination);
        	}
        	throw(e);
        }
	}
	@Override
	public void postprocessAnalysis(PostprocessRequest request,
    StreamObserver<JobResponse> responseObserver){
		
		final ObjectId stackId = new ObjectId(request.getPostprocessStackId());
		Document stack = PhenopipeMongoDb.INSTANCE.getIapPostprocessingStackCollection()
				.find(Filters.eq("_id", stackId)).first();
		if(stack!=null){		
			System.out.println(request.getPathToReport());
			Path reportPath = PathUtil.getLocalPathFromSmbUrl(request.getPathToReport());
			if(reportPath!=null){
				final Path targetPath =reportPath
						.resolve("../postprocess_result_"+stack.getObjectId("_id")+"_"+request.getSnapshotHash()).normalize();	
				if(!Files.exists(targetPath)){
					try {
						Files.createDirectory(targetPath);
						String reportFileName="report.csv";
						GrpcRStatusProvider sp = new GrpcRStatusProvider();
						UUID jobID = UUID.randomUUID();
						Observable<ProgressResponse> statusObs = statusObservable(sp);
						JobMapper.INSTANCE.put(jobID, statusObs ,"Signal: [Completed]");//TODO move completion marker to config or at least static variable
						logger.info("Analyse report at {} with stack {}. JobID: {}", request.getPathToReport(), stack.getString("name"), jobID.toString());
						RTaskStack rStack = new RTaskStack(stack.getString("name"),targetPath.toString(), sp);
						rStack.setDataFileName(reportFileName);
						rStack.setControlTreatmentName(request.getMeta().getControlTreatmentName());
						rStack.setExperimentName(request.getMeta().getExperimentName());
						for(Document script : (List<Document>)stack.get("scripts")){
							Binary scriptBinary = (Binary)script.get("file");
							Reader scriptReader = new InputStreamReader(new ByteArrayInputStream(scriptBinary.getData()));
							rStack.addTask(scriptReader,script.getString("name"));
						}
						responseObserver.onNext(JobResponse
								.newBuilder()
								.setJobId(jobID.toString())
								.build());
						
						PostprocessExecutor.INSTANCE.submitTask(new Runnable(){
							@Override
							public void run() {
								try{
									List<String> lines = readReportFile(reportPath.resolve(reportFileName), request.getExcludedPlantIdentifiersList());
									writeReportFile(targetPath.resolve(reportFileName), lines);
									rStack.execute();
									Builder responseBuilder = PostprocessResponse
											.newBuilder()
											.setPathToResults(PathUtil.getSmbUrlFromLocalPath(targetPath.toString()))
											.setPostprocessStackId(stackId.toHexString());
									ResponseCache.INSTANCE.put(jobID, responseBuilder);
								}catch(UnableToInitializeException | TaskExecutionException e){
									try {
										//TODO detailed output for TaskExecutionException
										logger.error("Error in postprocessing. Cleaning up.", e);
										FileUtil.delete(new File(targetPath.toString()));
									} catch (IOException e1) {
										logger.error("Unable to cleanup after postprocessing error",e1);
										// TODO notify --> most likely manual cleanup necessary
									}
									ResponseCache.INSTANCE.putError(jobID, e);
								}
								catch (IOException e){//read or writeReportFile failed
									try {
										logger.error("Error while filtering report. Cleaning up.", e);
										FileUtil.delete(new File(targetPath.toString()));
									} catch (IOException e1) {
										logger.error("Unable to cleanup after error",e1);
										// TODO notify --> most likely manual cleanup necessary
									}
									ResponseCache.INSTANCE.putError(jobID, e);
								} finally{
									sp.setCurrentStatusText("Signal: [Completed]");
								}	
							}
						});			
						responseObserver.onCompleted();
					} catch (IOException e) {
						String message = "Unable to create output directory";
						logger.error(message, e);
						responseObserver.onError(constructGrpcException(Status.Code.FAILED_PRECONDITION, message, e, null));
					}
				}else{
					String message = "The output directory already exists. This postprocessing was already applied. JobID";
					logger.info(message);
					responseObserver.onError(constructGrpcException(Status.Code.ALREADY_EXISTS,message,null,null));
				}
			}else{
				String message = "The given report path could not be resolved";
				logger.error(message);
				responseObserver.onError(constructGrpcException(Status.Code.INVALID_ARGUMENT,message,null,null));
			}
		}else{
			String message = "The postprocessing stack with ID "+request.getPostprocessStackId() +" does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String,String>();
			detail.put("postprocess_stack_id", request.getPostprocessStackId());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND,message,null,detail));
		}
	}
	@Override
	public void fetchPostprocessingResult(FetchJobResultRequest request,
    StreamObserver<PostprocessResponse> responseObserver){
		logger.info("Fetch results for jobID {}", request.getJobId());
		Builder responseBuilder = ResponseCache.INSTANCE.get(UUID.fromString(request.getJobId()));
		if(responseBuilder != null){
			responseObserver.onNext((PostprocessResponse) responseBuilder.build());
			responseObserver.onCompleted();
		}else{
			Exception e = ResponseCache.INSTANCE.getError(UUID.fromString(request.getJobId()));
			if(e != null){
				String message;
				Status.Code code;
				Map<String, String> detail = new HashMap<String, String>();
				if(e instanceof UnableToRunException){
					message = e.getMessage();
					code=Status.Code.RESOURCE_EXHAUSTED;
					
					String stackName=((UnableToRunException) e).getFailedTask().getName();
					String taskName=((UnableToRunException) e.getCause()).getFailedTask().getName();
					
					detail.put("stack_name", stackName);
					detail.put("task_name", taskName);
					
				}else if (e instanceof TaskExecutionException){
					message="There was an error while executing a R script";
					code=Status.Code.FAILED_PRECONDITION;
					
					String stackName=((TaskExecutionException) e).getFailedTask().getName();
					String taskName=((TaskExecutionException) e.getCause()).getFailedTask().getName();
					
					detail.put("stack_name", stackName);
					detail.put("task_name", taskName);
				}else{
					 message = "An error occured during postprocessing";
					 code=Status.Code.UNKNOWN;
				}
				logger.info("Return error information for jobID {} to client", request.getJobId());
				responseObserver.onError(constructGrpcException(code,message,e,detail));
				
			}else{
				logger.info("No Results for jobID {}",request.getJobId());
				responseObserver.onCompleted();
			}
		}
	}
	@Override
	public void uploadPostprocessingStack(UploadPostprocessingStackRequest request,
    StreamObserver<UploadPostprocessingStackResponse> responseObserver){
		PostprocessingStack stack = request.getStack();
		String name = stack.getName();
		MongoCollection<Document> stackCollection = PhenopipeMongoDb.INSTANCE.getIapPostprocessingStackCollection();
		FindIterable<Document> iter = stackCollection.find(Filters.eq("name",name));//TODO add author to filter to enable multiple authors to have equaly named stacks
		if(iter.first()==null){
			logger.info("Add postprocessing stack with name {} by ",name, stack.getAuthor());
			ObjectId stackId = saveStackInDB(stack);
			responseObserver.onNext(UploadPostprocessingStackResponse.newBuilder()
										.setSuccess(true)
										.setStackId(stackId.toHexString())
										.build());
			responseObserver.onCompleted();
		}else{
			String message = "The Postprocessing Stack with name '"+ name +"' already exists. Please choose a different name";
			logger.info(message);
			Map<String, String> detail = new HashMap<String,String>();
			detail.put("name", name);
			detail.put("id", iter.first().getObjectId("_id").toHexString());
			responseObserver.onError(constructGrpcException(Status.Code.ALREADY_EXISTS,message,null,detail));
		}
	}
	@SuppressWarnings("unchecked")
	@Override
	public void getPostprocessingStacks(GetPostprocessingStacksRequest request,
    StreamObserver<GetPostprocessingStacksResponse> responseObserver){
		MongoCollection<Document> stacksColl = PhenopipeMongoDb.INSTANCE.getIapPostprocessingStackCollection();
		GetPostprocessingStacksResponse.Builder respBuilder = GetPostprocessingStacksResponse.newBuilder();
		MongoCursor<Document> iter = stacksColl.find(Filters.eq("author", request.getAuthor())).projection(Projections.exclude("scripts.file")).iterator();
		while(iter.hasNext()){
			Document stackDoc = iter.next();
			
			PostprocessingStack.Builder stackBuilder = PostprocessingStack
					.newBuilder()
					.setName(stackDoc.getString("name"))
					.setDescription(stackDoc.getString("description"))
					.setAuthor(stackDoc.getString("author"))
					.setId(stackDoc.getObjectId("_id").toHexString());
			for(Document scriptDoc : (List<Document>)stackDoc.get("scripts")){
				stackBuilder.addScripts(PostprocessingScript
						.newBuilder()
						.setId(stackDoc.getObjectId("_id").toHexString()+"_"+scriptDoc.getInteger("index"))
						.setName(scriptDoc.getString("name"))
						.setIndex(scriptDoc.getInteger("index"))
						.setDescription(scriptDoc.getString("description"))
						);
			}
			respBuilder.addStacks(stackBuilder);
		}
		
		responseObserver.onNext(respBuilder.build());
		responseObserver.onCompleted();
	}
	@Override
	public void getPostprocessingStack(GetPostprocessingStackRequest request,
    StreamObserver<GetPostprocessingStackResponse> responseObserver){
		final ObjectId stackId = new ObjectId(request.getStackId());	
		Document stackDoc = PhenopipeMongoDb.INSTANCE.getIapPostprocessingStackCollection()
				.find(Filters.and(Filters.eq("_id", stackId), Filters.eq("author", request.getAuthor()))).projection(Projections.exclude("scripts.file")).first();
		if(stackDoc!=null){
			PostprocessingStack.Builder stackBuilder = PostprocessingStack.newBuilder()
					.setName(stackDoc.getString("name"))
					.setDescription(stackDoc.getString("description"))
					.setAuthor(stackDoc.getString("author"))
					.setId(stackDoc.getObjectId("_id").toHexString());
			for(Document scriptDoc : (List<Document>)stackDoc.get("scripts")){
				stackBuilder.addScripts(PostprocessingScript
						.newBuilder()
						.setId(stackDoc.getObjectId("_id").toHexString()+"_"+scriptDoc.getInteger("index"))
						.setName(scriptDoc.getString("name"))
						.setIndex(scriptDoc.getInteger("index"))
						.setDescription(scriptDoc.getString("description"))
						);
			}
			responseObserver.onNext(GetPostprocessingStackResponse.newBuilder().setStack(stackBuilder.build()).build());
			responseObserver.onCompleted();
		}else{
			String message = "The Postprocessing Stack with id '"+ request.getStackId() +"' does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String,String>();
			detail.put("postprocess_stack_id", request.getStackId());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND,message,null,detail));
		}
	}
}
