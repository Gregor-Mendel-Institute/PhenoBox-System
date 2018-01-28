package at.gmi.djamei.iap.actions;

import org.BackgroundTaskStatusProviderSupportingExternalCall;

import io.reactivex.Observable;
import io.reactivex.subjects.PublishSubject;

/**
 * 
 * @author Sebastian Seitner
 * Class to let tasks report their status to different observers.
 */
public class GrpcStatusProvider implements BackgroundTaskStatusProviderSupportingExternalCall {
	private int currentProgress = 0;
	private String prefix;
	private String message1;
	private String message2;
	private String message3;
	
	private boolean wantsToStop = false;
	private PublishSubject<String> message1$ = PublishSubject.create(); 
	private PublishSubject<String> message2$ = PublishSubject.create(); 
	private PublishSubject<Integer> progress$ = PublishSubject.create(); 
	/*
	/*
	private StreamObserver<ProgressResponse> statusObserver;
	public GrpcStatusProvider(StreamObserver<ProgressResponse> statusObserver){
		this.statusObserver=statusObserver;
	}*/
	@Override
	public int getCurrentStatusValue() {
		return currentProgress;
	}
	
	@Override
	public void setCurrentStatusValue(int value) {
		if (value != currentProgress) {
			currentProgress = value;
			progress$.onNext(currentProgress);
			System.out.println("GRPCStatusProvider Progress: " + value);
		}
	}
	public Observable<Integer> getProgressObservable(){
		return progress$;
	}
	public Observable<String> getMessage1Observable(){
		return message1$;
	}
	public Observable<String> getMessage2Observable(){
		return message2$;
	}
	
	@Override
	public double getCurrentStatusValueFine() {
		return currentProgress;
	}
	
	@Override
	public String getCurrentStatusMessage1() {
		return prefix != null ? prefix + message1 : message1;
	}
	
	@Override
	public String getCurrentStatusMessage2() {
		return message2;
	}
	
	@Override
	public String getCurrentStatusMessage3() {
		return message3;
	}
	
	@Override
	public void pleaseStop() {
		wantsToStop = true;
	}
	
	@Override
	public boolean wantsToStop() {
		return wantsToStop;
	}
	
	@Override
	public boolean pluginWaitsForUser() {
		return false;
	}
	
	@Override
	public void pleaseContinueRun() {
	}
	
	@Override
	public void setCurrentStatusValueFine(double value) {
		setCurrentStatusValue((int) value);
	}
	
	@Override
	public void setCurrentStatusText1(String status) {
		if (!status.equals(message1)) {
			System.out.println("GRPCStatusProvider M1: " + status);
			message1 = status;
			message1$.onNext(message1);
		}
		
	}
	
	@Override
	public void setCurrentStatusText2(String status) {
		if (!status.equals(message2)) {
			System.out.println("GRPCStatusProvider M2: " + status);
			message2 = status;
			message2$.onNext(message2);
		}
		
	}
	
	@Override
	public void setCurrentStatusValueFineAdd(double smallProgressStep) {
		if (currentProgress < 0)
			currentProgress = 0;
		setCurrentStatusValue((int) (currentProgress + smallProgressStep));
	}
	
	@Override
	public void setPrefix1(String prefix1) {
		prefix = prefix1;
		
	}
	
}
