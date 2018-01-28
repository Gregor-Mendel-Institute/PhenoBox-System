package at.gmi.djamei.mongo;

import java.net.UnknownHostException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bson.Document;

import com.mongodb.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

public enum PhenopipeIapMongoDb {
	INSTANCE;
	static final Logger logger = LogManager.getLogger();
	private String collIapPipeline="iap_pipeline";
	private MongoClient mongoClient;
	private MongoDatabase db;
	public void init(String host, int port, String dbName) throws UnknownHostException{
		this.init(host, port, dbName, collIapPipeline);
	}
	private void init(String host, int port, String dbName, String collIapPipeline) throws UnknownHostException{
		if(mongoClient==null){
			mongoClient = new MongoClient(host, port);
			db=mongoClient.getDatabase(dbName);
			this.collIapPipeline=collIapPipeline;
		}
		logger.info("Successfully connected to MongoDB instance on {}:{}. Database: {}",host, port,dbName);
	}
	public MongoDatabase getDB(){
		return db;
	}
	public MongoCollection<Document> getIapPipelineCollection(){
		return db.getCollection(collIapPipeline);
	}
	
	public String getIapPipelineCollectionName() {
		return collIapPipeline;
	}
}
