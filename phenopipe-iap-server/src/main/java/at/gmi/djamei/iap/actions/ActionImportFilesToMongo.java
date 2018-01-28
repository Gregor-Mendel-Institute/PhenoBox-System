package at.gmi.djamei.iap.actions;

import java.io.File;
import java.util.ArrayList;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.LinkedHashSet;

import org.ErrorMsg;
import org.MergeCompareRequirements;
import org.SystemAnalysis;
import org.graffiti.plugin.algorithm.ThreadSafeOptions;
import org.graffiti.plugin.io.resources.FileSystemHandler;

import de.ipk.ag_ba.commands.AbstractNavigationAction;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.gui.MainPanelComponent;
import de.ipk.ag_ba.gui.navigation_model.NavigationButton;
import de.ipk.ag_ba.gui.picture_gui.BackgroundThreadDispatcher;
import de.ipk.ag_ba.mongo.MongoDB;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.Experiment;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeader;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.SubstanceInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.layout_control.dbe.RunnableWithMappingData;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.layout_control.dbe.TableData;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.Condition3D;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.Sample3D;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.Substance3D;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.images.ImageData;

/**
 * @author Sebastian Seitner
 * IAP Action used to import image data from a specified folder containing a fileimport.xlsx metadata file into IAP
 * Based on the class 'de.ipk.ag_ba.commands.mongodb.SaveExperimentInCloud' by klukas
 */
public class ActionImportFilesToMongo extends AbstractNavigationAction implements AutomatableAction {
	
	private File directory;
	private ExperimentInterface savedExperiment;
	
	private final ArrayList<String> messages = new ArrayList<String>();
	
	private MongoDB m;
	private String experimentName;
	private String coordinatorName;
	private String userName;
	/**
	 * The passed directory must not contain other files than images (jpeg,jpg,png,tif,tiff) and the necessary fileimport.xlsx file
	 * 
	 * @param directory
	 * @param m
	 */
	public ActionImportFilesToMongo(File directory, String experimentName, String coordinatorName, String userName,MongoDB m) {
		super("Import files to Mongo");
		this.directory = directory;
		this.m = m;
		this.experimentName = experimentName;
		this.coordinatorName=coordinatorName;
		this.userName=userName;
	}
	
	@Override
	public MainPanelComponent getResultMainPanel() {
		return null;
	}
	
	@Override
	public void performActionCalculateResults(NavigationButton src) throws Exception {
		messages.clear();
		
		this.savedExperiment = null;
		
		final ThreadSafeOptions tso = new ThreadSafeOptions();
		
		try {
			prepareDataSetFromFileList(new RunnableWithMappingData() {
				@Override
				public void run() {
				}
				
				@Override
				public void setExperimenData(ExperimentInterface experiment) {
					tso.setParam(0, experiment);
				}
			});
		} catch (Exception e) {
			e.printStackTrace();
			ErrorMsg.addErrorMessage(e);
		}
		
		Experiment experiment = (Experiment) tso.getParam(0, null);
		if (experiment != null) {
			savedExperiment = m.saveExperiment(experiment, status);
		}
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewNavigationSet(ArrayList<NavigationButton> currentSet) {
		return currentSet;
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewActionSet() {
		ArrayList<NavigationButton> res2 = new ArrayList<NavigationButton>();
		return res2;
	}
	
	private void prepareDataSetFromFileList(RunnableWithMappingData resultProcessor) throws Exception {
		TableData tableData;
		File annotationFile = new File(directory, "fileimport.xlsx"); 
		if (annotationFile.exists()) {
			tableData = TableData.getTableData(annotationFile, true);
		} else {
			return; // There is no fileimport.xlsx file
		}
		
		Experiment e = new Experiment();
		ExperimentHeader eh = new ExperimentHeader();
		eh.setExperimentname(experimentName);
		eh.setExperimentType("File Import");
		eh.setCoordinator(coordinatorName); 
		eh.setImportDate(new Date());
		eh.setImportUserName(userName);
		
		eh.setOriginDbId(directory.getCanonicalPath());
		
		long sizekb = 0;
		int fileCount = 0;
		GregorianCalendar first = null;
		GregorianCalendar last = null;
		for (int row = 2; row <= tableData.getMaximumRow(); row++) {
			int metaColumn = 1;
			String importFile = tableData.getUnicodeStringCellData(metaColumn++, row);
			String plantId = tableData.getUnicodeStringCellData(metaColumn++, row);
			Integer replicate = ((Double) tableData.getCellData(metaColumn++, row, -1)).intValue();
			Integer time = ((Double) tableData.getCellData(metaColumn++, row, -1)).intValue();
			String timeUnit = tableData.getUnicodeStringCellData(metaColumn++, row);
			Date imagingTime = tableData.getCellDataDateObject(metaColumn++, row, null);
			String measurementTool = tableData.getUnicodeStringCellData(metaColumn++, row);
			String camera = tableData.getUnicodeStringCellData(metaColumn++, row);
			Double rotation = (Double) tableData.getCellData(metaColumn++, row, 0.0);
			String species = tableData.getUnicodeStringCellData(metaColumn++, row);
			String genotype = tableData.getUnicodeStringCellData(metaColumn++, row);
			String varity = tableData.getUnicodeStringCellData(metaColumn++, row);
			String growthConditions = tableData.getUnicodeStringCellData(metaColumn++, row);
			String treatment = tableData.getUnicodeStringCellData(metaColumn++, row);
			
			if (importFile == null || importFile.isEmpty()) {
				messages.add("No file name specified in column A, row " + (row + 1) + ".");
				continue;
			}
			
			File f = new File(directory, importFile);
			if (!f.exists()) {
				messages.add("The file '" + importFile + "' specified in column A, row " + (row + 1) + " could not be found.");
				continue;
			}
			long creationTime = f.lastModified();
			GregorianCalendar gc = new GregorianCalendar();
			gc.setTimeInMillis(creationTime);
			if (first == null)
				first = gc;
			if (last == null)
				last = gc;
			if (gc.after(last))
				last = gc;
			if (gc.before(first))
				first = gc;
			sizekb += f.length();
			fileCount++;
			
			Substance3D sub = new Substance3D();
			sub.setName(camera);
			e.add(sub);
			
			Condition3D con = new Condition3D(sub);
			con.setExperimentInfo(eh);
			con.setSpecies(species);
			con.setGenotype(genotype);
			con.setVariety(varity);
			con.setGrowthconditions(growthConditions);
			con.setTreatment(treatment);
			// con.setSequence("");
			sub.add(con);
			
			Sample3D sample = new Sample3D(con);
			con.add(sample);
			sample.setSampleFineTimeOrRowId(imagingTime.getTime());
			sample.setTime(time);
			sample.setTimeUnit(timeUnit);
			sample.setMeasurementtool(measurementTool);
			
			ImageData img = new ImageData(sample);
			img.setURL(FileSystemHandler.getURL(f));
			img.setQualityAnnotation(plantId);
			img.setPosition(rotation);
			img.setReplicateID(replicate);
			
			sample.add(img);
		}
		eh.setNumberOfFiles(fileCount);
		eh.setStartDate(first.getTime());
		eh.setStorageTime(last.getTime());
		eh.setSizekb(sizekb / 1024);
		e.setHeader(eh);
		
		Experiment res = new Experiment();
		res.setHeader(e.getHeader().clone());
		MergeCompareRequirements mcr = new MergeCompareRequirements();
		for (SubstanceInterface s : new ArrayList<SubstanceInterface>(e)) {
			Substance3D.addAndMergeA(res, s, true, BackgroundThreadDispatcher.getRunnableExecutor(), mcr);
		}
		e.clear();
		res.sortSubstances();
		res.sortConditions();
		
		resultProcessor.setExperimenData(res);
		resultProcessor.run();
	}
	
	private LinkedHashSet<String> hs(String string) {
		LinkedHashSet<String> res = new LinkedHashSet<String>();
		res.add(string);
		return res;
	}
	
	@Override
	public String getDefaultTitle() {
		return "Add files and create experiment in MongoDB";
		
	}
	
	@Override
	public String getDefaultImage() {
		return "img/ext/gpl2/Gnome-Emblem-Photos-64.png";
	}
	
	public ExperimentInterface getResultExperiment() {
		return savedExperiment;
	}
}