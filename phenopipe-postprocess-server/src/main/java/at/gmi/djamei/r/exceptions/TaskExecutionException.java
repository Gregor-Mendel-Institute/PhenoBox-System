package at.gmi.djamei.r.exceptions;

import at.gmi.djamei.r.AbstractRTask;

public class TaskExecutionException extends Exception{

	private static final long serialVersionUID = 666727088643427773L;
	private static final String DEFAULT_MESSAGE = "Error while executing R script.";
	private AbstractRTask failedTask;
	
	public TaskExecutionException(AbstractRTask failedTask) {
        this(failedTask, DEFAULT_MESSAGE);
    }
	public TaskExecutionException(AbstractRTask failedTask,String message) {
        this(failedTask,message,null);     
    }
	public TaskExecutionException(AbstractRTask failedTask,Throwable cause) {
        this(failedTask, DEFAULT_MESSAGE, cause);
    }
	public TaskExecutionException(AbstractRTask failedTask, String message,Throwable cause) {
        super(message, cause);
        this.failedTask=failedTask;
    }
	public AbstractRTask getFailedTask(){
		return failedTask;
	}
}
