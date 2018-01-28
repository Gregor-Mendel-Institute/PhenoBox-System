package at.gmi.djamei.r;

import java.io.IOException;
import java.io.PipedReader;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import javax.script.ScriptException;

import org.apache.commons.vfs2.FileSystemException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.renjin.sexp.ExternalPtr;
import org.renjin.sexp.ListVector;
import org.renjin.sexp.Null;
import org.renjin.sexp.SEXP;

import at.gmi.djamei.r.exceptions.TaskExecutionException;
import at.gmi.djamei.r.exceptions.UnableToInitializeException;
import at.gmi.djamei.r.exceptions.UnableToRunException;
import at.gmi.djamei.r.viz.charts.gral.GralXYPlot;

public class RTaskStack extends AbstractRTask{

	static final Logger logger = LogManager.getLogger();
	private static final String CONTROL_TREATMENT_NAME_KEY="control_treatment_name";
	private static final String DATA_FILE_NAME_KEY="data_file_name";
	private static final String EXPERIMENT_NAME_KEY="experiment_name";
	private final LinkedList<AbstractRTask> taskList = new LinkedList<>();
	private Thread outputHandler;
	
	public RTaskStack(String name, String workingDirectory, GrpcRStatusProvider sp) {
		super(name, workingDirectory, sp);
	}
	public RTaskStack(String name, String workingDirectory, GrpcRStatusProvider sp,  HashMap<String,String> environment){
		super(name, workingDirectory, sp, environment);
	}

	public boolean addTask(Reader scriptReader, String name){
		return taskList.add(new RTask(scriptReader, name, this.workingDirectory, statusProvider, environment));
	}
	
	@Override
	protected void init() throws UnableToInitializeException{
		super.init();
		logger.info("Initialize R Task Stack '{}'",this.name);
		
		try {
			logger.info("Prepare execution environment for R Task Stack '{}'",this.name);
			engine.eval("setwd(\"file://"+workingDirectory+"\")");
			engine.eval(CHARTS_KEY + "<-c()");
            engine.eval("phenopipe_add_chart <- function(chart){" + CHARTS_KEY + "<<-c(" + CHARTS_KEY + ",chart)}");
			engine.eval("phenopipe_set_status <- function(msg){if(is.character(msg) & length(msg)==1){print(paste(\"[S]\", msg, sep=\":\"))}}");
			engine.eval("phenopipe_set_progress <- function(progress){if(is.numeric(progress)){print(paste(\"[P]\", progress, sep=\":\"))}}");
		} catch (ScriptException e) {
			logger.error( "Unable prepare engine for execution", e);
			throw new UnableToInitializeException(this, "Unable prepare engine for execution of R Task Stack '"+this.name+"'.", e);
		}
		
		super.setEnvironment(environment);
		if(statusProvider!=null){
			PipedReader outputReader= super.redirectOutput();
			this.outputHandler= new Thread(new OutputHandler(outputReader,this.statusProvider));
			this.outputHandler.start();
			statusProvider.setCurrentStatusText("RStack '"+name+"' submitted");
		}
	}
	@Override
	protected void complete() {
		super.complete();
		logger.info("Completed R Task Stack '{}'",this.name);
		try {
			this.engine.getContext().getWriter().close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		this.outputHandler.interrupt();
		
		if(statusProvider!=null){
			statusProvider.setCurrentStatusText("RStack '"+name+"' completed");
		}
	}
	private void processCharts() throws IOException {
        SEXP charts = (SEXP) engine.get("phenopipe_charts");
        if (!(charts instanceof Null) && charts instanceof ListVector) {
        	if(statusProvider!=null){
				statusProvider.setCurrentStatusText("Write charts to disk");
			}
            Iterator<SEXP> chartIt = ((ListVector) charts).iterator();
            Path chartsDir = Paths.get(workingDirectory).resolve("charts");
            if (chartIt.hasNext() && !Files.exists(chartsDir)) {
                Files.createDirectory(chartsDir);
            }
            while (chartIt.hasNext()) {
                GralXYPlot chart = (GralXYPlot) ((ExternalPtr) chartIt.next()).getInstance();
                //TODO better sanitize filename
                chart.writePlotAsSvg(chartsDir.resolve(chart.getTitle()).toString().replace('.', '_'));
            }
        }

    }
	/**
	 * Sets the control treatment name in the metadata list. Must be called before this task is initialized.
	 *  
	 * @param name The name of the treatment which indicates the control group
	 */
	public void setControlTreatmentName(String name){
		addMetadata(CONTROL_TREATMENT_NAME_KEY, name);
	}
	/**
	 * Sets the data file name (iap report) in the metadata list. Must be called before this task is initialized.
	 *  
	 * @param name The name of the treatment which indicates the control group
	 */
	public void setDataFileName(String name){
		addMetadata(DATA_FILE_NAME_KEY, name);
	}
	public void setExperimentName(String name){
        addMetadata(EXPERIMENT_NAME_KEY, name);
    }
	public void execute() throws TaskExecutionException, UnableToInitializeException, IOException {	
		init();
		logger.info("Execute R Task Stack '{}'",this.name);
		Iterator<AbstractRTask> it = taskList.iterator();
		try{
			SEXP prevResult =null;
			while(it.hasNext()){
				AbstractRTask task = it.next();
				setInput(prevResult);
				task.execute(engine);
				prevResult=task.getResult();
				
				processCharts();
                engine.eval(CHARTS_KEY+"<-c()");
			}
			result=prevResult;
		}  catch (ScriptException e) {
            throw new TaskExecutionException(this, "Error while executing task stack'" + this.name + "'", e);
        }
		complete();		
	}
}
