package at.gmi.djamei.phenopipe;


import java.io.IOException;
import java.net.UnknownHostException;
import java.util.Base64;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.DESKeySpec;

import org.SystemOptions;
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
		if(args.length==0){
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
		}else if (args.length==2 && args[0].equals("-encrypt-pw")){
			SystemOptions so = SystemOptions.getInstance("secret", null);
			String defaultValue = java.util.UUID.randomUUID().toString();
			String passphrase = so.getString("Symmetric Encryption", "key", defaultValue);
			DESKeySpec keySpec;
			try {
				keySpec = new DESKeySpec(passphrase.getBytes("UTF8"));
				SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("DES");
				SecretKey key = keyFactory.generateSecret(keySpec);
				Cipher encCipher = Cipher.getInstance("DES"); // cipher is not thread safe
				encCipher.init(Cipher.ENCRYPT_MODE, key);
				String res = Base64.getEncoder().encodeToString(encCipher.doFinal(args[1].getBytes("UTF-8")));
				System.out.println("encrypted:"+res);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

}
