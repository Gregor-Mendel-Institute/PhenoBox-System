package at.gmi.djamei.phenopipe;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.google.protobuf.Message.Builder;

//TODO Move to shared library
public enum ResponseCache {
	INSTANCE;
	static final Logger logger = LogManager.getLogger();
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
		logger.info("Add response for job with id {}",jobID.toString());
		responseBuilders.put(jobID, builder);
	}
	public void putError(UUID jobID, Exception e){
		logger.info("Add error for job with id {}",jobID.toString());
		errors.put(jobID, e);
	}
	
	public Builder get(UUID jobID){
		return responseBuilders.getIfPresent(jobID);
	}
	public Exception getError(UUID jobID){
		return errors.getIfPresent(jobID);
	}
}
