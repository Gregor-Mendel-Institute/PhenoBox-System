package at.gmi.djamei.phenopipe.util;

import at.gmi.djamei.phenopipe.ProgressResponse;
import io.grpc.stub.StreamObserver;
import io.reactivex.Observable;

public class ProgressResponder {
	private StreamObserver<ProgressResponse> responseObserver;
	private Observable<ProgressResponse> status;
	public ProgressResponder(Observable<ProgressResponse> status, StreamObserver<ProgressResponse> responseObserver){
		this.status=status;
		this.responseObserver=responseObserver;
	}
	
	
	private void handleProgressResponse(ProgressResponse resp){
		responseObserver.onNext(resp);
		/*if(completeOn!=null && resp.getMessage().equals(completeOn)){
			responseObserver.onCompleted();
			
			statusDisposable.dispose();
		}*/
		
	}
	/**
	 * Start the Responder and subscribe to the status observable
	 */
	public void activate(){
		status.subscribe(responseObserver::onNext, responseObserver::onError, responseObserver::onCompleted);			
	}
}
