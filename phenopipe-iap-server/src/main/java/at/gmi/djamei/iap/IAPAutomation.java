package at.gmi.djamei.iap;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.ReleaseInfo;
import org.SystemAnalysis;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.graffiti.plugin.algorithm.ThreadSafeOptions;
import org.graffiti.plugin.io.resources.ResourceIOManager;
import org.ini4j.Ini;
import org.ini4j.InvalidFileFormatException;

import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;

import at.gmi.djamei.iap.actions.ActionDelete;
import at.gmi.djamei.iap.actions.ActionExportAnalysedImages;
import at.gmi.djamei.iap.actions.ActionExportResults;
import at.gmi.djamei.iap.actions.ActionImportFilesToMongo;
import at.gmi.djamei.iap.actions.ActionSetAnalysisPipeline;
import at.gmi.djamei.iap.actions.AnalysisActionWrapper;
import at.gmi.djamei.iap.actions.GrpcStatusProvider;
import at.gmi.djamei.iap.exceptions.PipelineAlreadyExistsException;
import at.gmi.djamei.mongo.PhenopipeIapMongoDb;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.gui.IAPfeature;
import de.ipk.ag_ba.gui.util.ExperimentReference;
import de.ipk.ag_ba.gui.webstart.IAPmain;
import de.ipk.ag_ba.gui.webstart.IAPrunMode;
import de.ipk.ag_ba.mongo.MongoDB;
import de.ipk.ag_ba.server.gwt.UrlCacheManager;
import de.ipk.ag_ba.server.task_management.BackupSupport;
import de.ipk.ag_ba.server.task_management.CloudComputingService;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeader;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeaderInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentInterface;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.DataMappingTypeManager3D;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.LoadedDataHandler;

/**
 * 
 * @author Sebastian Seitner
 * Class used to start up the IAP service and run jobs with an Executor service
 */
public class IAPAutomation {
	//TODO make singleton?
	static final Logger logger = LogManager.getLogger();
	

	private MongoDB m;
	
	private final UrlCacheManager urlCacheManager;
	private static Boolean first = true;
	private final ExecutorService taskExec = Executors.newSingleThreadExecutor();
	
	public IAPAutomation() {
		logger.info("Initialize IAP");
		IAPmain.setRunMode(IAPrunMode.AUTOMATION);
		synchronized (first) {
			SystemAnalysis.simulateHeadless = true;
			
			this.urlCacheManager = new UrlCacheManager();
			
			if (first) {
				registerIOhandlers();
				
				ReleaseInfo.setRunningAsApplet(null);
				{
					setM(MongoDB.getDefaultCloud());
					if (getM() != null) {
						CloudComputingService cc = CloudComputingService.getInstance(getM());
						cc.setEnableCalculations(false);
						cc.switchStatus(getM());
					}
					if (IAPmain.isSettingEnabled(IAPfeature.TOMCAT_AUTOMATIC_HSM_BACKUP)) {
						BackupSupport sb = BackupSupport.getInstance();
						sb.scheduleBackup();
					}
				}
			}
			first = false;
		}
	}
	
	/**
	 * Add a new task which will execute an IAP action in the background
	 * @param actionTask a Runnable which invokes an IAP action
	 */
	public void submitActionTask(Runnable actionTask){
		if(!taskExec.isShutdown()){
			taskExec.execute(actionTask);
		}
	}
	
	/**
	 * Shutdown the ExecutorService and the IAP instance
	 */
	public void stop(){
		logger.info("Stop IAP Executor and IAP itself");
		taskExec.shutdown();
		try {
			taskExec.awaitTermination(1, TimeUnit.MINUTES);
		} catch (InterruptedException ignored) {
			SystemAnalysis.exit(1);
		}
	}
	
	private void registerIOhandlers() {
		ResourceIOManager.registerIOHandler(LoadedDataHandler.getInstance());
		for (MongoDB m : MongoDB.getMongos())
			ResourceIOManager.registerIOHandler(m.getHandler());
		
		DataMappingTypeManager3D.replaceVantedMappingTypeManager();
	}
	//Check if concurrent action executions are possible, if not use a task queue
	/**
	 * Performs some setup before executing the given IAP Automatable Action
	 * @param action The IAP action to perform
	 * @param sp The status provider which should be used by the action
	 * @throws Exception
	 */
	public void executeCommand(AutomatableAction action, GrpcStatusProvider sp) throws Exception {
			logger.info("Execute action: {}", action.getDefaultTitle());
			action.setSource(action, null);// GuiSetting is set to null so we can only use actions which don't use it
			action.setStatusProvider(sp);
			
			action.performActionCalculateResults(null);// Check if all needed actions are able to cope with null as src
			
	}

	public MongoDB getM() {
		return m;
	}

	public void setM(MongoDB m) {
		this.m = m;
	}
	public ExperimentHeaderInterface getExperimentHeader(String id){
		return getM().getExperimentHeader(new iap.bson.types.ObjectId(id));
		/*try {
			//
			URLClassLoader cl = new URLClassLoader(new URL[] { new URL("file:lib/iap_2_0.jar")});
			Class iapBsonObjectIdClass = cl.loadClass("iap.bson.types.ObjectId");
			
			return getM().getExperimentHeader((iap.bson.types.ObjectId)iapBsonObjectIdClass.getDeclaredConstructor(String.class).newInstance(id));
		} catch (InstantiationException | IllegalAccessException | IllegalArgumentException | InvocationTargetException
				| NoSuchMethodException | SecurityException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ClassNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return null;*/
	}
	/**
	 * Creates the appropriate IAP ActionImportFilesToMongo action and executes it.
	 * @param path The source path of the images to be imported
	 * @param expName The name of the experiment
	 * @param userName The username of the user who is importing the experiment
	 * @param coordinatorName The name of the coordinator of the experiment
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @param m The mongoDB instance into which the experiment should be imported
	 * @return The ExperimentReference to the newly created Experiment
	 * @throws Exception
	 */
	public ExperimentReference importExperiment(String path, String expName, String userName, String coordinatorName,
			GrpcStatusProvider sp, MongoDB m) throws Exception {
		AutomatableAction importAction = new ActionImportFilesToMongo(new File(path), expName, userName,
				coordinatorName, m);

		this.executeCommand(importAction, sp);
		ExperimentInterface experiment = ((ActionImportFilesToMongo) importAction).getResultExperiment();
		ExperimentReference expRef = new ExperimentReference(experiment.getHeader(), m);
		return expRef;
	}

	/**
	 * Creates the appropriate IAP ActionSetAnalysisPipeline Action and executes it
	 * @param expRef The ExperimentReference identifying the experiment for which the pipeline should be set
	 * @param pipeline The instance of the IAPPipeline which should be set
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @throws Exception
	 */
	public void setAnalysisPipeline(ExperimentReference expRef, IAPPipeline pipeline, GrpcStatusProvider sp)
			throws Exception {
		AutomatableAction setAnalysisPipelineAction = new ActionSetAnalysisPipeline(expRef, pipeline);
		this.executeCommand(setAnalysisPipelineAction, sp);
	}

	/**
	 * Creates the appropriate IAP AnalysisActionWrapper Action and executes it
	 * @param expRef The ExperimentReference identifying the experiment which should be analyzed
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @param m The mongoDB instance in which the experiment is stored
	 * @return The ExperimentReference of the analyzed Experiment
	 * @throws Exception
	 */
	public ExperimentReference analyzeExperiment(ExperimentReference expRef, GrpcStatusProvider sp, MongoDB m)
			throws Exception {
		//TODO pass in a boolean to specify local or grid analysis
		AutomatableAction analysisAction = new AnalysisActionWrapper(expRef.getIniIoProvider(), expRef, true, m);
		this.executeCommand(analysisAction, sp);
		return ((AnalysisActionWrapper) analysisAction).getResultExpRef();
	}

	/**
	 * Creates the appropriate IAP ActionExportResults Action and executes it
	 * @param expRef The ExperimentReference identifying the experiment for which the analysis results should be exported
	 * @param path The destination path to which the results should be exported
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @throws Exception
	 */
	public void exportExperiment(ExperimentReference expRef, String path, GrpcStatusProvider sp) throws Exception {
		ThreadSafeOptions angles = new ThreadSafeOptions();
		angles.setBval(0, true);
		ThreadSafeOptions storeReplicates = new ThreadSafeOptions();
		storeReplicates.setBval(0, true);
		ThreadSafeOptions exportImages = new ThreadSafeOptions();
		exportImages.setBval(0, false);
		ActionExportResults exportAction = new ActionExportResults(path, expRef, null, angles, storeReplicates,
				exportImages, new ThreadSafeOptions(), false, null, null, null, null, null, true);
		exportAction.setUseIndividualReportNames(false);
		this.executeCommand(exportAction, sp);
	}

	/**
	 * Creates the appropriate IAP ActionDelete Action and executes it
	 * @param header The header of the experiment which should be deleted
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @param m The mongoDB instance in which the experiment is stored
	 * @throws Exception
	 */
	public void deleteExperiment(ExperimentHeaderInterface header, GrpcStatusProvider sp, MongoDB m) throws Exception {
		AutomatableAction action = new ActionDelete(header, m);
		this.executeCommand(action, sp);

	}

	/**
	 * Creates the appropriate IAP ActionExportAnalysedImages Action and executes it
	 * @param expRef The ExperimentReference identifying the experiment for which the analysed/segmented images should be exported
	 * @param path The destination path to which the images should be exported to
	 * @param sp The GrpcStatusProvider which should be used to emit status updates from the Action
	 * @throws Exception
	 */
	public void exportSegmentedImages(ExperimentReference expRef, String path, GrpcStatusProvider sp)
			throws Exception {
		ThreadSafeOptions jpg = new ThreadSafeOptions();
		jpg.setBval(0, false);
		ThreadSafeOptions tsoQuality = new ThreadSafeOptions();
		tsoQuality.setDouble(1);
		AutomatableAction exportImagesAction = new ActionExportAnalysedImages(expRef, path, jpg, tsoQuality);
		this.executeCommand(exportImagesAction, sp);
	}
	
	/**
	 * Looks up the experiment in MongoDB by the username and the experiment name
	 * @param userName The name of the user to whom the experiment belongs
	 * @param expName The name of the experiment
	 * @return The ExperimentHeader instance of the experiment or null if no experiment is found
	 */
	public ExperimentHeader getExpHeaderByName(String userName, String expName) {
		return (ExperimentHeader) this.getM().getExperimentHeaderByName(userName, expName);
	}

	public IAPPipeline addPipeline(String pipeline, String author) throws PipelineAlreadyExistsException, InvalidFileFormatException, IOException{
		Ini ini = new Ini(new StringReader(pipeline));
		String name = ini.get("DESCRIPTION", "pipeline_name", String.class);
		logger.info("Add Pipeline with name {}", name);
		MongoCollection<Document> pipelineCollection = PhenopipeIapMongoDb.INSTANCE.getIapPipelineCollection();
		Document pipelineDoc = pipelineCollection.find(Filters.eq("name", name)).first();
		if(pipelineDoc==null){
			String description = ini.get("DESCRIPTION", "pipeline_description", String.class);
			String tunedForVersion = ini.get("DESCRIPTION", "tuned_for_IAP_version", String.class);
			pipelineDoc = new Document("name", name)
					.append("description", description)
					.append("author", author)
					.append("tuned_for_version", tunedForVersion)
					.append("source", pipeline);
			pipelineCollection.insertOne(pipelineDoc);
			return new IAPPipeline(pipelineDoc.getObjectId("_id"), name, description, author, tunedForVersion, pipeline);
		}else{
			throw new PipelineAlreadyExistsException(name, author,pipelineDoc.getObjectId("_id"));
		} 
		
	}
	public IAPPipeline getPipeline(String id){
		MongoCollection<Document> pipelineColl = PhenopipeIapMongoDb.INSTANCE.getIapPipelineCollection();
		Document pipelineDoc = pipelineColl.find(Filters.eq("_id", new ObjectId(id))).first();
		if(pipelineDoc==null){
			return null;
		}
		IAPPipeline pipeline = new IAPPipeline(pipelineDoc.getObjectId("_id"), 
				pipelineDoc.getString("name"), 
				pipelineDoc.getString("description"), 
				pipelineDoc.getString("author"), 
				pipelineDoc.getString("tuned_for_version"),
				pipelineDoc.getString("source"));
		return pipeline;
	}

	/**
	 * Fetches all available Pipelines for a specified author
	 * @return an List of all available pipelines
	 */
	public List<IAPPipeline> getPipelines(String author, boolean excludeSource) {
		MongoCollection<Document> pipelineColl = PhenopipeIapMongoDb.INSTANCE.getIapPipelineCollection();
		FindIterable<Document> findIter = pipelineColl.find(Filters.eq("author",author));
		if(excludeSource){
			findIter=findIter.projection(Projections.exclude("scripts.file"));
		}
		MongoCursor<Document> iter = findIter.iterator();
		
		List<IAPPipeline> res = new ArrayList<IAPPipeline>();
		while(iter.hasNext()){
			Document d = iter.next();
			String source;
			if(excludeSource){
				source=null;
			}else{
				source = d.getString("source");
			}
			res.add(
					new IAPPipeline(
							d.getObjectId("_id"), 
							d.getString("name"), 
							d.getString("description"), 
							d.getString("author"),
							d.getString("tuned_for_version"), 
							source
							)
					);
		}
		return res;
	}
}
