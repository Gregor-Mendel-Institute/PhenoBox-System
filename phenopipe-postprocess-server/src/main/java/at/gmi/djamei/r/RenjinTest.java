package at.gmi.djamei.r;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.HashMap;

public class RenjinTest {
	
	public static void main(String[] args) {
		
		HashMap<String,String> env = new HashMap<>();
		env.put("data_file_name", "report.csv");
		GrpcRStatusProvider sp = new GrpcRStatusProvider();
		RTaskStack stack= new RTaskStack("TestStack", "/media/sf_linux_iap_share/pictures/Arabidopsis_Analysis/test_out",sp,env);
		try {
			stack.addTask(new FileReader("src/main/r/test1.r"), "test1");
			stack.addTask(new FileReader("src/main/r/test2.r"), "test2");
			//stack.addTask(new FileReader("src/main/r/IAP_output_processing_v2.r"), "reformatReport");
			try {
				stack.execute();
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}

}
