package at.gmi.djamei.r.exceptions;

import at.gmi.djamei.r.AbstractRTask;

public class UnableToRunException extends Exception {

	private static final long serialVersionUID = 2073601674588214502L;
	private static final String DEFAULT_MESSAGE = "Unable to run R script.";
	private AbstractRTask failedTask;
	
	public UnableToRunException(AbstractRTask failedTask) {
        this(failedTask, DEFAULT_MESSAGE);
    }
	public UnableToRunException(AbstractRTask failedTask,String message) {
        this(failedTask,message,null);     
    }
	public UnableToRunException(AbstractRTask failedTask,Throwable cause) {
        this(failedTask, DEFAULT_MESSAGE, cause);
    }
	public UnableToRunException(AbstractRTask failedTask, String message,Throwable cause) {
        super(message, cause);
        this.failedTask=failedTask;
    }
	public AbstractRTask getFailedTask(){
		return failedTask;
	}
}
