package at.gmi.djamei.r;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public enum PostprocessExecutor {
	INSTANCE;
	private final ExecutorService taskExec = Executors.newSingleThreadExecutor();
	
	public void submitTask(Runnable task){
		if(!taskExec.isShutdown()){
			taskExec.execute(task);
		}
	}
	
	public void stop(){
		taskExec.shutdown();
		try {
			taskExec.awaitTermination(1, TimeUnit.MINUTES);
		} catch (InterruptedException ignored) {
			//System.exit(1);
		}
	}
}
