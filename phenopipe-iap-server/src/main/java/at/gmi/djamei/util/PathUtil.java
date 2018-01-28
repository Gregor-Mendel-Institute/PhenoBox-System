package at.gmi.djamei.util;

import java.nio.file.Path;
import java.nio.file.Paths;

import at.gmi.djamei.config.Config;



public class PathUtil {
	//TODO Error handling for malformed paths
	public static Path getLocalPathFromSmbUrl(String url){
		//TODO sanitize and remove e.g: /../ entries
		String pathParts[] =url.split("/");
		StringBuilder sb = new StringBuilder();
		sb.append(pathParts[0]);
		sb.append("//");
		sb.append(pathParts[2]);
		sb.append('/');
		sb.append(pathParts[3]);
		Path mountPoint = Paths.get(Config.INSTANCE.getLocalPathFromSmbUrl(sb.toString()));
		if (mountPoint!=null){
			if(pathParts.length>4){
				for(int i=4; i<pathParts.length; i++){
					mountPoint = mountPoint.resolve(pathParts[i]);	
				}
			}
			return mountPoint;
		}
		return null;
	}
	public static String getSmbUrlFromLocalPath(Path path){
		return Config.INSTANCE.getSmbUrlFromLocalPath(path.toString());
	}
	public static String toFilename(String s){
		return s.replaceAll("[^A-Za-z0-9 ]", "").replaceAll("[ ]", "_");
	}
}
