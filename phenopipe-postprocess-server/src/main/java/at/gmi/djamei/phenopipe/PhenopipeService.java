package at.gmi.djamei.phenopipe;

import java.util.UUID;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import at.gmi.djamei.phenopipe.util.ProgressResponder;
import io.grpc.stub.StreamObserver;
import io.reactivex.Observable;

public class PhenopipeService extends PhenopipeGrpc.PhenopipeImplBase{
	static final Logger logger = LogManager.getLogger();
	/**
	 * Gets the Status Observable of the given task and pushes its output into the ResponseObserver and completes when the status observable completes.
	 * If there is no Status Observable for the given jobId then the responseObserver completes immediately.
	 */
	@Override
	public void watchJob(WatchJobRequest request,
	        StreamObserver<ProgressResponse> responseObserver){
		logger.info("Request to watch job with id {}", request.getJobId());
		System.out.println("Request to watch job");
		UUID jobId =UUID.fromString(request.getJobId());
		Observable<ProgressResponse> status$ = JobMapper.INSTANCE.get(jobId);
		if(status$ != null){
			ProgressResponder responder = new ProgressResponder(status$, responseObserver);
			responder.activate();
		}else{
			responseObserver.onCompleted();
		}
	}
}
