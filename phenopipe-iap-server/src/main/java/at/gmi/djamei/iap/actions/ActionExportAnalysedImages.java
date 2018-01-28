package at.gmi.djamei.iap.actions;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.GregorianCalendar;
import java.util.WeakHashMap;

import org.StringManipulationTools;
import org.SystemAnalysis;
import org.graffiti.plugin.algorithm.ThreadSafeOptions;
import org.graffiti.plugin.io.resources.MyByteArrayInputStream;
import org.graffiti.plugin.io.resources.ResourceIOManager;

import de.ipk.ag_ba.commands.AbstractNavigationAction;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.gui.MainPanelComponent;
import de.ipk.ag_ba.gui.images.IAPimages;
import de.ipk.ag_ba.gui.navigation_model.NavigationButton;
import de.ipk.ag_ba.gui.picture_gui.BackgroundThreadDispatcher;
import de.ipk.ag_ba.gui.picture_gui.LocalComputeJob;
import de.ipk.ag_ba.gui.util.ExperimentReferenceInterface;
import de.ipk.ag_ba.image.structures.CameraType;
import de.ipk.ag_ba.image.structures.Image;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ConditionInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.NumericMeasurementInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.SampleInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.SubstanceInterface;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.BinaryMeasurement;
import de.ipk_gatersleben.ag_pbi.mmd.experimentdata.images.ImageData;

/**
 * @author Sebastian Seitner
 * IAP Action used to export segmented/analysed images for an experiment identified by an ExperimentReferenceInterface
 * to a specified destination path
 * Based on the class 'de.ipk.ag_ba.commands.experiment.view_or_export.ActionDataExportZIP' by klukas
 */
public class ActionExportAnalysedImages extends AbstractNavigationAction implements AutomatableAction {
	
	private ExperimentReferenceInterface er;
	private String fn;
	private String mb;
	private int files;
	private final ThreadSafeOptions tso = new ThreadSafeOptions();
	private String errorMessage;
	private ThreadSafeOptions jpg;
	private ThreadSafeOptions tsoQuality;
	private String destination_path;
	
	public ActionExportAnalysedImages(String tooltip) {
		super(tooltip);
	}
	
	public ActionExportAnalysedImages(ExperimentReferenceInterface experimentReference, String destination_path, ThreadSafeOptions jpg, ThreadSafeOptions tsoQuality) {
		this("Export image files");
		this.er = experimentReference;
		this.jpg = jpg;
		this.tsoQuality = tsoQuality;
		this.destination_path = destination_path;
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewActionSet() {
		return null;
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewNavigationSet(ArrayList<NavigationButton> currentSet) {
		ArrayList<NavigationButton> res = new ArrayList<NavigationButton>(currentSet);
		// res.add(src);
		return res;
	}
	
	@Override
	public String getDefaultTitle() {
		return "<html><center>"
				+ "Create ZIP file<br>"
				+ "<small><font color='gray'>(" + (jpg.getBval(0, false) ? "JPG " : "") + "Image Export)</font></small>";
	}
	
	@Override
	public String getDefaultImage() {
		return IAPimages.saveAsArchive();
	}
	
	private static WeakHashMap<String, ActionExportAnalysedImages> validLinks2action = new WeakHashMap<String, ActionExportAnalysedImages>();
	
	public static void setOutputStreamForAction(String uiid, OutputStream os) throws Exception {
		ActionExportAnalysedImages da = validLinks2action.get(uiid);
		if (da == null)
			throw new Exception("" +
					"Action ID is unknown, please click data export command " +
					"button again to initiate a new download.");
		da.tso.setParam(0, os);
		da.tso.setParam(2, false);
	}
	
	public static String getFileNameForAction(String uiid) throws Exception {
		ActionExportAnalysedImages da = validLinks2action.get(uiid);
		if (da == null)
			throw new Exception("" +
					"Action ID is unknown, please click data export command " +
					"button again to initiate a new download.");
		return (String) da.tso.getParam(1, null);
	}
	
	public static Long getExperimentSizeForAction(String uiid) throws Exception {
		ActionExportAnalysedImages da = validLinks2action.get(uiid);
		if (da == null)
			throw new Exception("" +
					"Action ID is unknown, please click data export command " +
					"button again to initiate a new download.");
		return (Long) da.tso.getParam(3, null);
	}
	
	public static void waitForFinishedDownloadAction(String uiid) throws Exception {
		ActionExportAnalysedImages da = validLinks2action.get(uiid);
		if (da == null)
			throw new Exception("" +
					"Action ID is unknown, please click data export command " +
					"button again to initiate a new download.");
		Boolean finished;
		long seconds = 0;
		do {
			finished = (Boolean) da.tso.getParam(2, false);
			Thread.sleep(1000);
			seconds++;
			if (seconds > 60 * 60 * 24 * 7)
				break;
		} while (!finished);
	}
	
	@Override
	public void performActionCalculateResults(NavigationButton src) throws Exception {
		this.errorMessage = null;
		try {
			ExperimentReferenceInterface experimentReference = er;
			status.setCurrentStatusText1("Load Experiment");
			ExperimentInterface experiment = experimentReference.getData();
			
			// filename:
			// SNAPSHOTNAME=Image Config_[GRAD]Grad
			// plantID SNAPSHOTNAME DATUM ZEIT.png
			
			GregorianCalendar gc = new GregorianCalendar();
			
			final ThreadSafeOptions written = new ThreadSafeOptions();
			final ThreadSafeOptions read = new ThreadSafeOptions();
			
			this.files = 0;
			for (SubstanceInterface su : experiment)
				for (ConditionInterface co : su)
					for (SampleInterface sa : co) {
						for (NumericMeasurementInterface nm : sa) {
							if (nm instanceof BinaryMeasurement) {
								BinaryMeasurement bm = (BinaryMeasurement) nm;
								if (bm.getURL() == null)
									continue;
								files++;
							}
						}
					}
			ThreadSafeOptions idx = new ThreadSafeOptions();
			
			long startTime = System.currentTimeMillis();
			ArrayList<LocalComputeJob> wait = new ArrayList<>();
			experiment.visitNumericMeasurements(
					null,
					(nm) -> {
						if (nm instanceof BinaryMeasurement) {
							BinaryMeasurement bm = (BinaryMeasurement) nm;
							if (bm.getURL() == null)
								return;
							
							if (status.wantsToStop())
								return;
							
							status.setCurrentStatusValueFine(100d * (idx.addInt(1)) / files);
							
							final String zefnSRC;
							final ImageData id = (ImageData) bm;
							try {
								if (bm instanceof ImageData) {
									zefnSRC = getImageFileNameForExport(gc, id);
								} else {
									return; // We are only interested in image data
								}
								
								wait.add(BackgroundThreadDispatcher.addTask(() -> {
									MyByteArrayInputStream inSRC;
									try {
										inSRC = ResourceIOManager.getInputStreamMemoryCached(bm.getURL());
									} catch (Exception e1) {
										errorMessage = e1.getMessage();
										inSRC = null;
									}
									if (inSRC == null)
										return;
									final SubstanceInterface suf = nm.getParentSample().getParentCondition().getParentSubstance();
									MyByteArrayInputStream in = inSRC;
									String zefn = zefnSRC;
									boolean closed = false;
									try {
										if (in.getCount() > 0) {
											read.addLong(in.getCount());
											if (jpg.getBval(0, false)) {
												String ext = bm.getURL().getFileNameExtension().toLowerCase();
												if (!ext.endsWith("jpg") && !ext.endsWith("jpeg")) {
													Image img = new Image(in);
													int ss = tsoQuality.getInt();
													CameraType ct = CameraType.fromString(suf.getName());
													if (ss > 0 && ss < 100 && ct != CameraType.NIR && ct != CameraType.IR)
														img = img.resize(img.getWidth() * ss / 100, img.getHeight() * ss / 100);
													
													zefn = StringManipulationTools.removeFileExtension(zefn) + ".jpg";
													img.saveToFile(this.destination_path + File.separator + zefn, tsoQuality.getDouble());
												}
											} else {
												Image img = new Image(in);
												int ss = tsoQuality.getInt();
												CameraType ct = CameraType.fromString(suf.getName());
												if (ss > 0 && ss < 100 && ct != CameraType.NIR && ct != CameraType.IR)
													img = img.resize(img.getWidth() * ss / 100, img.getHeight() * ss / 100);
												
												img.saveToFile(this.destination_path + File.separator + zefn);
											}
											written.addLong(in.getCount());
											
										}
									} catch (IOException e) {
										System.err.println(SystemAnalysis.getCurrentTime() + ">ERROR: " + e.getMessage());
									} finally {
										if (!closed)
											try {
												in.close();
											} catch (IOException e) {
												System.err.println(SystemAnalysis.getCurrentTime() + ">ERROR: " + e.getMessage());
											}
									}
								}, "write image to disk"));
								
							} catch (Exception e) {
								System.out.println("ERROR: " + e.getMessage());
							}
							String pre = "Write Files...";
							status.setCurrentStatusText1(pre);
							long currTime = System.currentTimeMillis();
							if (read.getLong() > 0)
								status.setCurrentStatusText1("saved " + idx.getInt() + "/" + files + " files");
							status.setCurrentStatusText2("inp: " + SystemAnalysis.getDataTransferSpeedString(read.getLong(), startTime, currTime) + ", " +
									"out:<br>" + SystemAnalysis.getDataTransferSpeedString(written.getLong(), startTime, currTime) + " ("
									+ (int) (100d * written.getLong() / read.getLong()) + "% of inp)");
						}
					});
			BackgroundThreadDispatcher.waitFor(wait);
			status.setCurrentStatusValueFine(100d);
			
			this.mb = (written.getLong() / 1024 / 1024) + "";
			tso.setParam(2, true);
		} catch (Exception e) {
			
			tso.setParam(2, true);
			
			if (fn != null && fn.trim().length() > 0 && new File(fn).exists())
				new File(fn).delete();
			this.errorMessage = e.getClass().getName() + ": " + e.getMessage();
		}
	}
	
	public static String getImageFileNameForExport(GregorianCalendar gc, ImageData id) {
		
		StringBuilder sb = new StringBuilder();
		sb.append(id.getReplicateID());
		sb.append('_');
		sb.append(id.getQualityAnnotation());
		sb.append('_');
		sb.append(id.getPosition().intValue());
		sb.append(".png");
		return sb.toString();
	}
	
	@Override
	public MainPanelComponent getResultMainPanel() {
		String stop = "";
		if (status.wantsToStop())
			stop = "Cammand has been interrupted by the user. Created ZIP file may be incomplete! ";
		if (errorMessage == null)
			errorMessage = "";
		else {
			errorMessage = " " + errorMessage + "";
		}
		if (fn == null)
			return new MainPanelComponent(stop + "No output file has been generated." + errorMessage);
		else {
			if (errorMessage.trim().length() > 0)
				return new MainPanelComponent(stop + "Output incomplete. Last Error: " + errorMessage);
			else
				return new MainPanelComponent(stop + "The file " + fn + " has been created (size " + mb + " MB, " + files + " files)." + errorMessage);
		}
	}
	
	long startTime;
	File ff;
	
}
