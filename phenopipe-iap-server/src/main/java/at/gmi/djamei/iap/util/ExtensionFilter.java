package at.gmi.djamei.iap.util;

import java.io.File;
import java.io.FileFilter;

/**
 * 
 * @author  Sebastian Seitner
 *
 */
public class ExtensionFilter implements FileFilter {
	private String[] extensions;
	
	public ExtensionFilter(String[] extensions) {
		this.extensions = extensions;
	}
	
	@Override
	public boolean accept(File pathname) {
		for (String extension : extensions) {
			if (pathname.getName().endsWith("." + extension)) {
				return true;
			}
		}
		return false;
	}
	
}
