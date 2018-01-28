package at.gmi.djamei.config;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map.Entry;
import java.util.Properties;

public enum Config {
	INSTANCE;
	private Properties props = new Properties();
	private HashMap<String,String> smb2local = new HashMap<>();
	//TODO think about this approach for user editable config 
	//https://stackoverflow.com/questions/35709227/javafxeditable-configuration-files-after-packaging
	public void load(){
		Properties folderMap = new Properties();
		InputStream input = Config.class.getClassLoader().getResourceAsStream("postprocessing.properties");
		InputStream shared_folder_map = Config.class.getClassLoader().getResourceAsStream("shared_folder_map.properties");
		try {
			props.load(input);
			folderMap.load(shared_folder_map);
			for (final String name: folderMap.stringPropertyNames()){
		        smb2local.put(name, folderMap.getProperty(name));
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}finally{
			if(input!=null){
				try{
					input.close();
				}catch(IOException e){
					e.printStackTrace();
				}
			}
		}
	}
	public String getRProperty(String key){
		return props.getProperty("r."+key);
	}
	public String getMongoProperty(String key){
		return props.getProperty("mongo."+key);
	}
	public String getLocalPathFromSmbUrl(String url){
		return smb2local.get(url);
	}
	public String getSmbUrlFromLocalPath(String path){
		for (Entry<String, String> entry : smb2local.entrySet()) {
	        if (path.startsWith(entry.getValue())) {
	        	int l = entry.getValue().length();
	        	if(l<path.length()){
	        		String remainder = path.substring(l).replaceAll(File.pathSeparator, "/");
	        		return entry.getKey()+'/'+remainder;
	        	}else{
	        		return entry.getKey();
	        	}
	        }
	    }
		return null;
	}

}
