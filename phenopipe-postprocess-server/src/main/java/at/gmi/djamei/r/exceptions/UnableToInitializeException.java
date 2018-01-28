package at.gmi.djamei.r.exceptions;

import at.gmi.djamei.r.AbstractRTask;

public class UnableToInitializeException extends Exception {

	private static final long serialVersionUID = -7259405492877973729L;
	private static final String DEFAULT_MESSAGE = "Unable to initialize R script for execution.";
	private AbstractRTask failedTask;
	
	public UnableToInitializeException(AbstractRTask failedTask) {
        this(failedTask, DEFAULT_MESSAGE);
    }
	public UnableToInitializeException(AbstractRTask failedTask,String message) {
        this(failedTask,message,null);     
    }
	public UnableToInitializeException(AbstractRTask failedTask,Throwable cause) {
        this(failedTask, DEFAULT_MESSAGE, cause);
    }
	public UnableToInitializeException(AbstractRTask failedTask, String message,Throwable cause) {
        super(message, cause);
        this.failedTask=failedTask;
    }
	public AbstractRTask getFailedTask(){
		return failedTask;
	}
}
