package at.gmi.djamei.mongo;

import java.net.UnknownHostException;


import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bson.Document;

import com.mongodb.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

public enum PhenopipeMongoDb {
	INSTANCE;
    static final Logger logger = LogManager.getLogger();
	private MongoClient mongoClient;
	private MongoDatabase db;
	private String collIapPostprocessingStack="iap_postprocessing_stacks";//TODO Rename to postprocessing_stack
	
	public void init(String host, int port, String dbName) throws UnknownHostException{
		init(host, port, dbName, null);
	}
	public void init(String host, int port, String dbName, String collIapPostprocessingStack) throws UnknownHostException{
		if(mongoClient == null){
			mongoClient = new MongoClient(host, port);
			db = mongoClient.getDatabase(dbName);
			if(collIapPostprocessingStack != null){
				this.collIapPostprocessingStack=collIapPostprocessingStack;
			}
			
		}
		logger.info("Successfully connected to MongoDB instance on {}:{}. Database: {}",host, port,dbName);
	}
	
	public MongoDatabase getDB(){
		return db;
	}
	public MongoCollection<Document> getIapPostprocessingStackCollection(){
		return db.getCollection(collIapPostprocessingStack);
	}
	
	public String getIapPostprocessingStackCollectionName() {
		return collIapPostprocessingStack;
	}
}
	