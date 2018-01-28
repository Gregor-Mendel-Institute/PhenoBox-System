package at.gmi.djamei.r;

import java.io.Reader;
import java.util.HashMap;
import javax.script.ScriptException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.renjin.sexp.SEXP;

import at.gmi.djamei.r.exceptions.TaskExecutionException;
import at.gmi.djamei.r.exceptions.UnableToInitializeException;

public class RTask extends AbstractRTask {
	static final Logger logger = LogManager.getLogger();
	private final Reader scriptReader;
	
	public RTask(Reader scriptReader,String name, String workingDirectory, GrpcRStatusProvider sp, HashMap<String,String> environment){
		super(name,workingDirectory, sp, environment);
		this.scriptReader=scriptReader;
	}
	
	@Override
	protected void init() throws UnableToInitializeException {
		super.init();
		if (statusProvider != null) {
			statusProvider.setCurrentStatusText("RTask '" + name + "' submitted");
		}
	}

	@Override
	protected void complete() {
		super.complete();
		if (statusProvider != null) {
			statusProvider.setCurrentStatusText("RTask '" + name + "' completed");
			//statusProvider.setCurrentProgress(100);
		}
	}

	@Override
	public void execute() throws TaskExecutionException, UnableToInitializeException {
		init();
		try {
            result = (SEXP) engine.eval(scriptReader);
        } catch (ScriptException e) {
            throw new TaskExecutionException(this, "Error while executing task '" + this.name + "'", e);
        }
		complete();

	}
}
