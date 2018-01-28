package at.gmi.djamei.phenopipe;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.google.protobuf.Message.Builder;

/**
 * A Singleton to hold a ProgressRepsonses for different jobs for a limited amount of time
 * @author syt
 *
 */
public enum ResponseCache {
	//TODO Move to shared library
	INSTANCE;
	private final Cache<UUID, Builder> responseBuilders;
	private final Cache<UUID, Exception> errors;
	ResponseCache(){
		responseBuilders= CacheBuilder.newBuilder()
				.maximumSize(1000)
				.expireAfterWrite(1, TimeUnit.DAYS)
				.build();
		errors = CacheBuilder.newBuilder()
				.maximumSize(1000)
				.expireAfterWrite(1, TimeUnit.DAYS)
				.build();
	}
	
	public void put(UUID jobID, Builder builder){
		responseBuilders.put(jobID, builder);
	}
	public void putError(UUID jobID, Exception e){
		errors.put(jobID, e);
	}
	
	public Builder get(UUID jobID){
		return responseBuilders.getIfPresent(jobID);
	}
	public Exception getError(UUID jobID){
		return errors.getIfPresent(jobID);
	}
}
