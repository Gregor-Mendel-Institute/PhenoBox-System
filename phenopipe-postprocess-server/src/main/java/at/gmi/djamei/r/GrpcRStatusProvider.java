package at.gmi.djamei.r;

import io.reactivex.Observable;
import io.reactivex.subjects.PublishSubject;

public class GrpcRStatusProvider {
	private int progress=0;
	private String status="";
	private PublishSubject<String> statu$ = PublishSubject.create(); 
	private PublishSubject<Integer> progress$ = PublishSubject.create(); 
	
	public Observable<Integer> getProgressObservable(){
		return progress$;
	}
	public Observable<String> getStatusObservable(){
		return statu$;
	}
	
	public void setCurrentStatusText(String value) {
		if (!status.equals(value)) {
			System.out.println("RStatusProvider M1: " + value);
			status = value;
			statu$.onNext(value);
		}
	}

	public void setCurrentProgress(int value) {
		if (value != progress) {
			progress = value;
			progress$.onNext(progress);
			System.out.println("RStatusProvider Progress: " + value);
		}
	}

}
