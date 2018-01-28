package at.gmi.djamei.phenopipe;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.DirectoryNotEmptyException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.ini4j.Ini;
import org.ini4j.InvalidFileFormatException;

import com.google.protobuf.Message.Builder;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;

import at.gmi.djamei.iap.IAPAutomation;
import at.gmi.djamei.iap.IAPPipeline;
import at.gmi.djamei.iap.actions.GrpcStatusProvider;
import at.gmi.djamei.iap.exceptions.PipelineAlreadyExistsException;
import at.gmi.djamei.mongo.PhenopipeIapMongoDb;
import at.gmi.djamei.phenopipe.util.FileUtil;
import at.gmi.djamei.phenopipe.util.Util;
import at.gmi.djamei.phenopipe.util.Util.CheckDirectoryState;
import at.gmi.djamei.util.PathUtil;
import de.ipk.ag_ba.gui.util.ExperimentReference;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeader;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeaderInterface;
import io.grpc.Metadata;
import io.grpc.Status;
import io.grpc.StatusException;
import io.grpc.Metadata.Key;
import io.grpc.stub.StreamObserver;
import io.reactivex.Observable;

/**
 * The GRPC Service class for all endpoints related to IAP actions 
 * @author Sebastian Seitner
 *
 */
public class PhenopipeIapService extends PhenopipeIapGrpc.PhenopipeIapImplBase {
	static final Logger logger = LogManager.getLogger();
	private final IAPAutomation iap;

	public PhenopipeIapService(IAPAutomation iap) {
		this.iap = iap;
	}

	/**
	 * Utility method to constructs a valid Grpc Status exception with the given parameters
	 * @param code The status code of the Exception
	 * @param message The message to be sent
	 * @param cause The Throwable which caused the exception
	 * @param details Additional Key,Value pairs to further describe the problem which occured (Sent as metadata)
	 * @return A fully constructed GRPC StatusExcetion
	 */
	private StatusException constructGrpcException(Status.Code code, String message, Throwable cause,
			Map<String, String> details) {
		// TODO Move to shared library
		Status status = Status.fromCode(code);
		if (message != null) {
			status = status.withDescription(message);
		}
		if (cause != null) {
			status = status.withCause(cause);
		}
		Metadata meta = new Metadata();
		if (details != null) {
			for (String k : details.keySet()) {
				meta.put(Key.of(k, Metadata.ASCII_STRING_MARSHALLER), details.get(k));
			}
		}
		return new StatusException(status, meta);
	}
	/**
	 * Utility method to create an Observable of ProgressResponses from the output of a GrpcStatusProvider
	 * @param sp The GrpcStatusProvider from which the Responses should be constructed
	 * @return An Observable of ProgressRepsonses which emits when either the Progress or the message of the underlying Status Provider emits
	 */
	private Observable<ProgressResponse> statusObservable(GrpcStatusProvider sp) {
		return Observable.combineLatest(sp.getMessage1Observable().startWith("Started to watch progress"),
				sp.getProgressObservable().startWith(0), (String m, Integer p) -> {
					return ProgressResponse.newBuilder().setMessage(m).setProgress(p);
				})
				// .sample(1, TimeUnit.SECONDS)
				// TODO Only build on return?
				.map(b -> b.build());
	}

	

	/* GRPC Service Methods */
	@Override
	public void importExperiment(ImportRequest request, StreamObserver<JobResponse> responseObserver) {
		
		ExperimentHeader h = iap.getExpHeaderByName(request.getUserName(), request.getExperimentName());
		if (h == null) {
			
			GrpcStatusProvider sp = new GrpcStatusProvider();
			UUID jobID = UUID.randomUUID();
			logger.info("Import experiment'{}' by user '{}'. JobID: '{}'",request.getExperimentName(), request.getUserName(), jobID.toString());
			Observable<ProgressResponse> statusObs = statusObservable(sp);
			JobMapper.INSTANCE.put(jobID, statusObs, "Signal: [Completed]");
			Path path = PathUtil.getLocalPathFromSmbUrl(request.getPath());
			iap.submitActionTask(new Runnable() {
				public void run() {
					// TODO possible race condition if iap tasks are executed
					// concurrently by the pool in IAPAutomation
					try {
						ExperimentReference expRef = iap.importExperiment(path.toString(), request.getExperimentName(),
								request.getCoordinatorName(), request.getUserName(), sp, iap.getM());
						Builder responseBuilder = ImportResponse.newBuilder()
								.setExperimentId(expRef.getHeader().getDatabaseId().toString());
						ResponseCache.INSTANCE.put(jobID, responseBuilder);
					} catch (Exception e) {
						logger.error("Import of experiment failed. (Experiment Name: "+request.getExperimentName()+", User: "+request.getUserName()+", Source: "+request.getPath()+")",e);
						ResponseCache.INSTANCE.putError(jobID, e);

					} finally {
						sp.setCurrentStatusText1("Signal: [Completed]");
					}
				}
			});
			responseObserver.onNext(JobResponse.newBuilder().setJobId(jobID.toString()).build());
			responseObserver.onCompleted();
		} else {
			String message = "The experiment with name '" + request.getExperimentName() + "' by user '"
					+ request.getUserName() + "' already exists";
			logger.info(message);
			Map<String, String> detail = new HashMap<String, String>();
			detail.put("experiment_id", h.getDatabaseId());
			responseObserver.onError(constructGrpcException(Status.Code.ALREADY_EXISTS, message, null, detail));
		}
	}

	@Override
	public void analyzeExperiment(AnalyzeRequest request, StreamObserver<JobResponse> responseObserver) {
		//ExperimentHeaderInterface header = iap.getM().getExperimentHeader(new ObjectId(request.getExperimentId()));
		ExperimentHeaderInterface header = iap.getExperimentHeader(request.getExperimentId());
		if (header != null) {
			IAPPipeline pipeline = iap.getPipeline(request.getPipelineId());
			if (pipeline != null) {
				UUID jobID = UUID.randomUUID();
				logger.info("Analyze experiment '{}' with pipeline '{}'. JobID: '{}'", header.getExperimentName(), pipeline.getName(), jobID.toString());
				// TODO check if experiment already analyzed with the selected
				// pipeline
				final ExperimentReference expRef = new ExperimentReference(header, iap.getM());
				GrpcStatusProvider sp = new GrpcStatusProvider();
				
				Observable<ProgressResponse> statusObs = statusObservable(sp);
				JobMapper.INSTANCE.put(jobID, statusObs, "Signal: [Completed]");
				iap.submitActionTask(new Runnable() {
					public void run() {
						try {
							iap.setAnalysisPipeline(expRef, pipeline, sp);
							ExperimentReference resRef = iap.analyzeExperiment(expRef, sp, iap.getM());
							Builder responseBuilder = AnalyzeResponse.newBuilder()
									.setResultId(resRef.getHeader().getDatabaseId().toString());
							ResponseCache.INSTANCE.put(jobID, responseBuilder);
						} catch (Exception e) {
							logger.error("Analysis of experiment failed. (Experiment ID: "+request.getExperimentId()+", Experiment Name: "+header.getExperimentName()+", Pipeline ID: "+pipeline.getId().toHexString()+")",e);
							ResponseCache.INSTANCE.putError(jobID, e);

						} finally {
							sp.setCurrentStatusText1("Signal: [Completed]");
						}
					}
				});
				responseObserver.onNext(JobResponse.newBuilder().setJobId(jobID.toString()).build());
				responseObserver.onCompleted();
			} else {
				String message = "The pipeline with id " + request.getPipelineId() + " does not exist";
				logger.info(message);
				Map<String, String> detail = new HashMap<String, String>();
				detail.put("pipeline_id", request.getPipelineId());
				responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND, message, null, detail));
			}
		} else {
			String message = "The experiment with ID " + request.getExperimentId() + " does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String, String>();
			detail.put("experiment_id", request.getExperimentId());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND, message, null, detail));
		}
	}

	@Override
	public void exportExperiment(ExportRequest request, StreamObserver<JobResponse> responseObserver) {
		//ExperimentHeaderInterface header = iap.getM().getExperimentHeader(new ObjectId(request.getExperimentId()));
		ExperimentHeaderInterface header = iap.getExperimentHeader(request.getExperimentId());
		if (header != null) {
			UUID jobID = UUID.randomUUID();
			logger.info("Export experiment '{}'. JobID: '{}'",header.getExperimentName(), jobID.toString());
			Ini ini;
			try {
				ini = new Ini(new StringReader(header.getSettings()));

			} catch (InvalidFileFormatException e) {
				String message = "Unable to read experiment settings, because they are malformed";
				logger.error("Unable to parse settings (ini) of experiment with ID '"+request.getExperimentId()+"'.",e);
				responseObserver.onError(constructGrpcException(Status.Code.INVALID_ARGUMENT, message, e, null));
				return;
			} catch (IOException e) {
				String message = "Unable to read experiment settings, due to IO error";
				logger.error("Unable to read experiment settings, due to IO error. Experiment ID '"+request.getExperimentId()+"'.",e);
				responseObserver.onError(constructGrpcException(Status.Code.INTERNAL, message, e, null));
				return;
			}
			String pipelineName = ini.get("DESCRIPTION", "pipeline_name", String.class);
			String exportFolderName = PathUtil.toFilename(pipelineName);
			// TODO move directory names to config
			String reportFolderName = "iap_report";
			String imageFolderName = "segmented_images";
			System.out.println("destination: " + request.getDestinationPath());
			Path exportFolder = PathUtil.getLocalPathFromSmbUrl(request.getDestinationPath()).resolve(exportFolderName);
			Path reportDestination = exportFolder.resolve(reportFolderName);
			Path imageDestination = exportFolder.resolve(imageFolderName);
			System.out.println("Local Destination: " + exportFolder.toString());
			CheckDirectoryState dirState = Util.checkDirectory(exportFolder.toString());
			if (dirState != CheckDirectoryState.OK && dirState != CheckDirectoryState.NOT_EXISTING) {
				String info = dirState.toString();
				Throwable cause = null;
				if (dirState == CheckDirectoryState.NO_DIRECTORY) {
					cause = new FileAlreadyExistsException(PathUtil.getSmbUrlFromLocalPath(exportFolder));
				} else if (dirState == CheckDirectoryState.NOT_EMPTY) {
					cause = new DirectoryNotEmptyException(PathUtil.getSmbUrlFromLocalPath(exportFolder));
				}

				String message = "The destination folder is not valid. (" + info + ")";
				logger.error("The destination folder is not valid. ({}) Path: {}", info,request.getDestinationPath());
				Map<String, String> detail = new HashMap<String, String>();
				detail.put("destination_path", request.getDestinationPath());
				responseObserver
						.onError(constructGrpcException(Status.Code.FAILED_PRECONDITION, message, cause, detail));
				return;
			}
			try {
				Files.createDirectories(exportFolder);
				Files.createDirectories(reportDestination);
				Files.createDirectories(imageDestination);
			} catch (FileAlreadyExistsException e) {
				String message = "Unable to create destination folder";
				logger.error(message, e);
				responseObserver.onError(constructGrpcException(Status.Code.FAILED_PRECONDITION, message, e, null));
				return;
			} catch (IOException e) {
				String message = "Unable to create destination folder";
				logger.error(message, e);
				responseObserver.onError(constructGrpcException(Status.Code.FAILED_PRECONDITION, message, e, null));
				return;
			}

			final ExperimentReference expRef = new ExperimentReference(header, iap.getM());
			GrpcStatusProvider sp = new GrpcStatusProvider();
			
			Observable<ProgressResponse> statusObs = statusObservable(sp);
			JobMapper.INSTANCE.put(jobID, statusObs, "Signal: [Completed]");
			iap.submitActionTask(new Runnable() {
				public void run() {
					try {
						iap.exportExperiment(expRef, reportDestination.toString(), sp);
						iap.exportSegmentedImages(expRef, imageDestination.toString(), sp);
						Builder responseBuilder = ExportResponse.newBuilder()
								.setPath(PathUtil.getSmbUrlFromLocalPath(reportDestination) + '/')
								.setImagePath(PathUtil.getSmbUrlFromLocalPath(imageDestination) + '/');
						ResponseCache.INSTANCE.put(jobID, responseBuilder);
					} catch (Exception e) {
						logger.error("IAP Export failed (Path: "+exportFolder.toString()+", ExperimentId: "+request.getExperimentId()+", Experiment Name: "+header.getExperimentName()+")", e);
						try {
							FileUtil.delete(new File(exportFolder.toString()));
						} catch (IOException e1) {
							logger.error("Unable to clean up after error. (Path: {})", exportFolder.toString());
						}
						ResponseCache.INSTANCE.putError(jobID, e);

					} finally {
						sp.setCurrentStatusText1("Signal: [Completed]");
					}
				}
			});
			responseObserver.onNext(JobResponse.newBuilder().setJobId(jobID.toString()).build());
			responseObserver.onCompleted();
		} else {
			String message = "The experiment with ID " + request.getExperimentId() + " does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String, String>();
			detail.put("experiment_id", request.getExperimentId());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND, message, null, detail));
		}
	}

	@Override
	public void deleteExperiment(DeleteRequest request, StreamObserver<JobResponse> responseObserver) {
		//ExperimentHeaderInterface header = iap.getM().getExperimentHeader(new ObjectId(request.getExperimentId()));
		ExperimentHeaderInterface header = iap.getExperimentHeader(request.getExperimentId());
		if (header != null) {
			GrpcStatusProvider sp = new GrpcStatusProvider();
			UUID jobID = UUID.randomUUID();
			Observable<ProgressResponse> statusObs = statusObservable(sp);
			JobMapper.INSTANCE.put(jobID, statusObs, "Signal: [Completed]");
			logger.info("Delete Experiment with ID '{}'. JobID: '{}'",request.getExperimentId(), jobID.toString());
			iap.submitActionTask(new Runnable() {
				public void run() {
					try {
						iap.deleteExperiment(header, sp, iap.getM());
						Builder responseBuilder = DeleteResponse.newBuilder().setSuccess(true);
						ResponseCache.INSTANCE.put(jobID, responseBuilder);
					} catch (Exception e) {
						logger.error("Deletion of experiment failed. (Experiment ID: "+request.getExperimentId()+", Experiment Name: "+header.getExperimentName()+")",e);	
						ResponseCache.INSTANCE.putError(jobID, e);
					} finally {
						sp.setCurrentStatusText1("Signal: [Completed]");
					}
				}
			});
			responseObserver.onNext(JobResponse.newBuilder().setJobId(jobID.toString()).build());
			responseObserver.onCompleted();
		} else {
			String message = "The experiment with ID " + request.getExperimentId() + " does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String, String>();
			detail.put("experiment_id", request.getExperimentId());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND, message, null, detail));
		}

	}

	/**
	 * Checks if there is a result in the ResultCache for the given id and
	 * returns the according response and completes. If no result is available
	 * it checks if an Exception occured and sets the according error on the responseObserver.
	 * If no result or error is present the responseObserver completes without emitting any value.
	 * 
	 * @param request
	 * @param responseObserver
	 */
	@Override
	public void fetchImportResult(FetchJobResultRequest request, StreamObserver<ImportResponse> responseObserver) {
		logger.info("Fetch import results for jobID {}", request.getJobId());
		Builder responseBuilder = ResponseCache.INSTANCE.get(UUID.fromString(request.getJobId()));
		if (responseBuilder != null) {
			System.out.println("Return Result");
			responseObserver.onNext((ImportResponse) responseBuilder.build());
			responseObserver.onCompleted();
		} else {
			Exception e = ResponseCache.INSTANCE.getError(UUID.fromString(request.getJobId()));
			if (e != null) {
				logger.info("Return error information for jobID {} to client", request.getJobId());
				String message = "An error occured during import";
				responseObserver.onError(constructGrpcException(Status.Code.UNKNOWN, message, e, null));
			} else {
				responseObserver.onCompleted();
			}
		}

	}

	/**
	 * Checks if there is a result in the ResultCache for the given id and
	 * returns the according response and completes. If no result is available
	 * it checks if an Exception occured and sets the according error on the responseObserver.
	 * If no result or error is present the responseObserver completes without emitting any value.
	 * 
	 * @param request
	 * @param responseObserver
	 */
	@Override
	public void fetchAnalyzeResult(FetchJobResultRequest request, StreamObserver<AnalyzeResponse> responseObserver) {
		logger.info("Fetch analysis results for jobID {}", request.getJobId());
		Builder responseBuilder = ResponseCache.INSTANCE.get(UUID.fromString(request.getJobId()));
		if (responseBuilder != null) {
			responseObserver.onNext((AnalyzeResponse) responseBuilder.build());
			responseObserver.onCompleted();
		} else {
			Exception e = ResponseCache.INSTANCE.getError(UUID.fromString(request.getJobId()));
			if (e != null) {
				logger.info("Return error information for jobID {} to client", request.getJobId());
				String message = "An error occured during analysis";
				responseObserver.onError(constructGrpcException(Status.Code.UNKNOWN, message, e, null));
			} else {
				responseObserver.onCompleted();
			}
		}

	}

	/**
	 * Checks if there is a result in the ResultCache for the given id and
	 * returns the according response and completes. If no result is available
	 * it checks if an Exception occured and sets the according error on the responseObserver.
	 * If no result or error is present the responseObserver completes without emitting any value.
	 * 
	 * @param request
	 * @param responseObserver
	 */
	@Override
	public void fetchExportResult(FetchJobResultRequest request, StreamObserver<ExportResponse> responseObserver) {
		logger.info("Fetch export results for jobID {}", request.getJobId());
		Builder responseBuilder = ResponseCache.INSTANCE.get(UUID.fromString(request.getJobId()));
		if (responseBuilder != null) {
			responseObserver.onNext((ExportResponse) responseBuilder.build());
			responseObserver.onCompleted();
		} else {
			Exception e = ResponseCache.INSTANCE.getError(UUID.fromString(request.getJobId()));
			if (e != null) {
				logger.info("Return error information for jobID {} to client", request.getJobId());
				String message = "An error occured during export";
				responseObserver.onError(constructGrpcException(Status.Code.UNKNOWN, message, e, null));
			} else {
				responseObserver.onCompleted();
			}
		}
	}

	/**
	 * Checks if there is a result in the ResultCache for the given id and
	 * returns the according response and completes. If no result is available
	 * it checks if an Exception occured and sets the according error on the responseObserver.
	 * If no result or error is present the responseObserver completes without emitting any value.
	 * 
	 * @param request
	 * @param responseObserver
	 */
	@Override
	public void fetchDeleteResult(FetchJobResultRequest request, StreamObserver<DeleteResponse> responseObserver) {
		logger.info("Fetch delete results for jobID {}", request.getJobId());
		Builder responseBuilder = ResponseCache.INSTANCE.get(UUID.fromString(request.getJobId()));
		if (responseBuilder != null) {
			responseObserver.onNext((DeleteResponse) responseBuilder.build());
			responseObserver.onCompleted();
		} else {
			Exception e = ResponseCache.INSTANCE.getError(UUID.fromString(request.getJobId()));
			if (e != null) {
				logger.info("Return error information for jobID {} to client", request.getJobId());
				String message = "An error occured during delete";
				responseObserver.onError(constructGrpcException(Status.Code.UNKNOWN, message, e, null));
			} else {
				responseObserver.onCompleted();
			}
		}
	}
	
	@Override
	public void uploadPipeline(UploadPipelineRequest request, StreamObserver<UploadPipelineResponse> responseObserver) {
		String content = request.getFile().toStringUtf8();
		try{
			IAPPipeline pipeline = iap.addPipeline(content, request.getAuthor());
			responseObserver.onNext(UploadPipelineResponse.newBuilder().setSuccess(true).build());
			responseObserver.onCompleted();
		}catch (InvalidFileFormatException e) {
				String message = "Unable to read pipeline file due to malformed file content";
				logger.error(message, e);
				responseObserver.onError(constructGrpcException(Status.Code.INVALID_ARGUMENT, message, e, null));
			} catch (IOException e) {
				String message = "Unable to read pipeline file due to an IO error. (" + e.getMessage() + ")";
				logger.error("Unable to read pipeline file due to an IO error.", e);
				responseObserver.onError(constructGrpcException(Status.Code.INTERNAL, message, e, null));
			} catch(PipelineAlreadyExistsException e){
				String message = "The pipeline with name '" + e.getPipelineName()
				+ "' already exists. Please choose a different name (alter name in DESCRIPTION block of the file)";
				Map<String, String> detail = new HashMap<String, String>();
				detail.put("name", e.getPipelineName());
				responseObserver.onError(constructGrpcException(Status.Code.ALREADY_EXISTS, message, null, detail));
			}
		/*Ini ini;
		try {
			ini = new Ini(new StringReader(content));
			String name = ini.get("DESCRIPTION", "pipeline_name", String.class);
			logger.info("Upload Pipeline with name {}", name);
			if (!iap.pipelineExists(name)) {
				File pipelineFile = new File(
						ReleaseInfo.getAppFolder() + File.separator + PathUtil.toFilename(name) + ".pipeline.ini");
				ini.store(pipelineFile);
				String filename = PathUtil.toFilename(name) + ".pipeline.ini";
				System.out.println(ReleaseInfo.getAppFolder() + File.separator + filename);
				responseObserver.onNext(UploadPipelineResponse.newBuilder().setSuccess(true).build());
				responseObserver.onCompleted();
			} else {
				String message = "The pipeline with name '" + name
						+ "' already exists. Please choose a different name (alter name in DESCRIPTION block of the file)";
				Map<String, String> detail = new HashMap<String, String>();
				detail.put("name", name);
				responseObserver.onError(constructGrpcException(Status.Code.ALREADY_EXISTS, message, null, detail));
			}
		} catch (InvalidFileFormatException e) {
			String message = "Unable to read pipeline file due to malformed file content";
			logger.error(message, e);
			responseObserver.onError(constructGrpcException(Status.Code.INVALID_ARGUMENT, message, e, null));
		} catch (IOException e) {
			String message = "Unable to read pipeline file due to an IO error. (" + e.getMessage() + ")";
			logger.error("Unable to read pipeline file due to an IO error.", e);
			responseObserver.onError(constructGrpcException(Status.Code.INTERNAL, message, e, null));
		}*/
	}

	@Override
	public void deletePipeline(DeletePipelineRequest request, StreamObserver<DeletePipelineResponse> responseObserver) {
		String message = "Safe deletion of pipeline files is not supported yet!";
		responseObserver.onError(Status.fromCode(Status.Code.UNIMPLEMENTED).withDescription(message).asException());
		return;

		/*
		 * //TODO check if pipeline is currently in use and delete it only if no
		 * analysis is using it File pipelineFile = new
		 * File(ReleaseInfo.getAppFolder()+File.separator+PathUtil.toFilename(
		 * request.getName())+".pipeline.ini"); if(pipelineFile.delete()){
		 * responseObserver.onNext(DeletePipelineResponse.newBuilder().
		 * setSuccess(true).build()); responseObserver.onCompleted(); }else{
		 * //Metadata trailer = new Metadata(); String message =
		 * "The pipeline with name '"+ request.getName()
		 * +"' could not be deleted.";
		 * responseObserver.onError(Status.fromCode(Status.Code.
		 * FAILED_PRECONDITION).withDescription(message).asException()); return;
		 * }
		 */
	}
	@Override
	public void getPipeline(GetPipelineRequest request, StreamObserver<GetPipelineResponse> responseObserver) {
		logger.info("Get pipeline with id '{}' by '{}'", request.getId(), request.getAuthor());
		MongoCollection<Document> pipelineColl = PhenopipeIapMongoDb.INSTANCE.getIapPipelineCollection();
		GetPipelineResponse.Builder respBuilder = GetPipelineResponse.newBuilder();
		Document pipelineDoc = pipelineColl.find(Filters.and(Filters.eq("_id",new ObjectId(request.getId())),Filters.eq("author", request.getAuthor()))).projection(Projections.exclude("source")).first();
		if(pipelineDoc !=null){
			respBuilder.setPipeline(Pipeline.newBuilder()
					.setName(pipelineDoc.getString("name"))
					.setDescription(pipelineDoc.getString("description"))
					.setId(pipelineDoc.getObjectId("_id").toHexString()));
			
			responseObserver.onNext(respBuilder.build());
			responseObserver.onCompleted();
		}else{
			String message = "The Pipeline with id '"+ request.getId() +"' by author '"+request.getAuthor()+"' does not exist";
			logger.info(message);
			Map<String, String> detail = new HashMap<String,String>();
			detail.put("pipeline_id", request.getId());
			detail.put("author", request.getAuthor());
			responseObserver.onError(constructGrpcException(Status.Code.NOT_FOUND,message,null,detail));
		}
	}
	@Override
	public void getPipelines(GetPipelinesRequest request, StreamObserver<GetPipelinesResponse> responseObserver) {
		logger.info("Get all pipelines by '{}'", request.getAuthor());
		MongoCollection<Document> pipelineColl = PhenopipeIapMongoDb.INSTANCE.getIapPipelineCollection();
		GetPipelinesResponse.Builder respBuilder = GetPipelinesResponse.newBuilder();
		MongoCursor<Document> iter = pipelineColl.find(Filters.eq("author", request.getAuthor())).projection(Projections.exclude("source")).iterator();
		while(iter.hasNext()){
			Document pipelineDoc = iter.next();
			respBuilder.addPipelines(Pipeline.newBuilder()
					.setName(pipelineDoc.getString("name"))
					.setDescription(pipelineDoc.getString("description"))
					.setId(pipelineDoc.getObjectId("_id").toHexString()));
		}
		responseObserver.onNext(respBuilder.build());
		responseObserver.onCompleted();
		/*ArrayList<PipelineDesc> pipelines = iap.getPipelines();
		at.gmi.djamei.phenopipe.GetPipelinesResponse.Builder responseBuilder = GetPipelinesResponse.newBuilder();
		for (PipelineDesc pd : pipelines) {
			responseBuilder.addPipelines(Pipeline.newBuilder().setName(pd.getName()).setDescription(pd.getTooltip()));
		}
		responseObserver.onNext(responseBuilder.build());
		responseObserver.onCompleted();*/
	}
}
