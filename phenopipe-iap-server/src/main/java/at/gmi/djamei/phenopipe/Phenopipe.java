package at.gmi.djamei.phenopipe;


import java.io.IOException;
import java.net.UnknownHostException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import at.gmi.djamei.config.Config;
import at.gmi.djamei.iap.IAPAutomation;
import at.gmi.djamei.mongo.PhenopipeIapMongoDb;

/**
 * Main Class of the Phenopipe server.
 * @author Sebastian Seitner
 *
 */
public class Phenopipe {
	static final Logger logger = LogManager.getLogger();
	public static void main(String[] args) {
		logger.info("Starting up Phenopipe IAP Server");
		Config.INSTANCE.load();
		
		final IAPAutomation iap = new IAPAutomation();
		final PhenopipeServer server = new PhenopipeServer(iap);

			//TODO use config file
		try {
			PhenopipeIapMongoDb.INSTANCE.init("localhost", 27017,Config.INSTANCE.getMongoProperty("database_name"));
		} catch (UnknownHostException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		try {
			server.start();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			server.blockUntilShutdown();
			
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
