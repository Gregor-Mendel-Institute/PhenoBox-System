package at.gmi.djamei.r;

import java.io.IOException;
import java.io.PipedReader;

/**
 * Runnable used to read the output of executed RScripts and emit status messages and progress
 * updates via a GrpcRStatusProvider based on some formatting rules
 * It will set a new status message if the R scripts outputs a message with the following format:
 * '[S]:<status_message>'
 * It will set a new progress value if the R scripts outputs a message with the following format:
 * '[P]:<progress_value>' where progress value has to be a number
 * 
 * @author Sebastian Seitner
 *
 */
public class OutputHandler implements Runnable {
	private final GrpcRStatusProvider sp;
	private final PipedReader reader;
	
	public OutputHandler(PipedReader reader, GrpcRStatusProvider sp){
		this.sp=sp;
		this.reader=reader;
	}
	@Override
	public void run() {
		while(!Thread.currentThread().isInterrupted()){
			try {
				int c;
				int cnt=0;
				boolean isMessage=false;
				boolean isProgress=false;
				StringBuilder sb= new StringBuilder();
				while((c = reader.read())!=-1){
					cnt++;
					if(cnt<=5){continue;}//R output starts with [1] "
					sb.append((char)c);
					if(cnt==9){
						switch(sb.toString()){
							case "[S]:": isMessage=true; sb.setLength(0); break;
							case "[P]:": isProgress=true; sb.setLength(0); break;
						}
					}
					
					if(((char)c)=='\n'){
						if(isMessage){
							sp.setCurrentStatusText(sb.toString().substring(0, sb.length()-2)); //Remove trailing "
						}else if(isProgress){
							sp.setCurrentProgress(Integer.valueOf(sb.toString().substring(0, sb.length()-2)));//Remove trailing "
						}
						isMessage=false;
						isProgress=false;
						cnt=0;
						sb.setLength(0);
					}
				}
			} catch (IOException e) {
				//Pipe is broken. Most likely it was closed so we shut ourself down
				Thread.currentThread().interrupt();
				
			}
		}
	}

}
