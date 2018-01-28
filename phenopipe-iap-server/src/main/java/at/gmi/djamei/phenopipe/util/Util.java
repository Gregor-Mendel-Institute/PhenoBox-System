package at.gmi.djamei.phenopipe.util;

import java.io.File;
import java.nio.file.Path;

public class Util {
	public enum CheckDirectoryState{
		NO_PATH("No Path"),
		NO_DIRECTORY("No Directory"),
		NOT_EXISTING("Not Existing"),
		NOT_EMPTY("Not Empty"),
		OK("Ok");
		
		private final String repr;
		
		CheckDirectoryState(String repr){
			this.repr=repr;
		}
		@Override
		public String toString(){
			return repr;
		}
	}
	/**
	 * Checks the state of the given directory path. It checks whether it exists, it is a directory(and not a file) or is not empty.
	 * @param dest
	 * @return
	 */
	public static CheckDirectoryState checkDirectory(String dest){
		if (dest == null || dest.trim().isEmpty())
			return CheckDirectoryState.NO_PATH;
		else {
			File f = new File(dest);
			if(!f.exists()){
				return CheckDirectoryState.NOT_EXISTING;
			}
			if (!f.isDirectory()) {
				return CheckDirectoryState.NO_DIRECTORY;
			}
			if (f.list().length > 0) {	
				return CheckDirectoryState.NOT_EMPTY;
			}
		}
		return CheckDirectoryState.OK;
	}

}
