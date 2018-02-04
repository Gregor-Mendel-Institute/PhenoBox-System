package at.gmi.djamei;

import java.io.IOException;
import java.net.UnknownHostException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import at.gmi.djamei.config.Config;
import at.gmi.djamei.mongo.PhenopipeMongoDb;
import at.gmi.djamei.phenopipe.PhenopipeRService;
import at.gmi.djamei.phenopipe.PhenopipeService;
import at.gmi.djamei.util.PathUtil;
import io.grpc.Server;
import io.grpc.ServerBuilder;

public class PostprocessingServer {
    static final Logger logger = LogManager.getLogger();
    
	private Server server;
	public void start() throws IOException {
		/* The port on which the server should run */
		int port = 50052;
		server = ServerBuilder
				.forPort(port)
				.addService(new PhenopipeService())
				.addService(new PhenopipeRService())
				.build()
				.start();
		logger.info("Server started, listening on " + port);
		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				// Use stderr here since the logger may have been reset by its
				// JVM shutdown hook.
				System.err.println("*** shutting down gRPC server since JVM is shutting down");
				PostprocessingServer.this.stop();
				System.err.println("*** server shut down");
			}
		});
	}

	public void stop() {
		if (server != null) {
			server.shutdown();
		}
	}

	/**
	 * Await termination on the main thread since the grpc library uses daemon
	 * threads.
	 */
	public void blockUntilShutdown() throws InterruptedException {
		if (server != null) {
			server.awaitTermination();
		}
	}
	public static void main(String[] args) {
		Config.INSTANCE.load();
		try {
			//TODO use config file
			PhenopipeMongoDb.INSTANCE.init("localhost", 27017,Config.INSTANCE.getMongoProperty("database_name"));
		} catch (UnknownHostException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		PostprocessingServer server = new PostprocessingServer();
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
