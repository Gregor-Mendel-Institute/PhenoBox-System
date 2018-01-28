package at.gmi.djamei.phenopipe;

import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import at.gmi.djamei.iap.IAPAutomation;
import io.grpc.Server;
import io.grpc.ServerBuilder;

/**
 * Class to setup the GRPC server and register the corresponding services
 * @author Sebastian Seitner
 *
 */
public class PhenopipeServer {
	static final Logger logger = LogManager.getLogger();

	private Server server;
	private IAPAutomation iap;
	PhenopipeServer(IAPAutomation iap){
		this.iap=iap;
	}
	void start() throws IOException {
		/* The port on which the server should run */
		int port = 50051;
		server = ServerBuilder
				.forPort(port)
				.addService(new PhenopipeService())
				.addService(new PhenopipeIapService(iap))
				.build()
				.start();
		logger.info("Server started, listening on " + port);
		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				// Use stderr here since the logger may have been reset by its
				// JVM shutdown hook.
				System.err.println("*** shutting down gRPC server since JVM is shutting down");
				PhenopipeServer.this.stop();
				System.err.println("*** server shut down");
			}
		});
	}

	void stop() {
		if (server != null) {
			server.shutdown();
		}
	}

	/**
	 * Await termination on the main thread since the grpc library uses daemon
	 * threads.
	 */
	void blockUntilShutdown() throws InterruptedException {
		if (server != null) {
			server.awaitTermination();
		}
	}
}
