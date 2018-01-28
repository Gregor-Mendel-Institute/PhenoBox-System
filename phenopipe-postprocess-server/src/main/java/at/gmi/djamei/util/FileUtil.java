package at.gmi.djamei.util;

import java.io.File;
import java.io.IOException;

public class FileUtil {
	private FileUtil(){}
	/**
	 * Delete a file or a directory and its descendants.
	 * @param file The directory/file to delete.
	 * @throws IOException Exception when deleting a file or directory was unsuccessful
	 */
	public static void delete(File file) throws IOException {
 
		for (File childFile : file.listFiles()) {
 
			if (childFile.isDirectory()) {
				delete(childFile);
			} else {
				if (!childFile.delete()) {
					throw new IOException();
				}
			}
		}
		if (!file.delete()) {
			throw new IOException();
		}
	}
}
