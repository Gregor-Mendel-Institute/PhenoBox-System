package at.gmi.djamei.iap.actions;

import java.util.ArrayList;

import org.IniIoProvider;
import org.StringManipulationTools;
import org.SystemAnalysis;
import org.SystemOptions;
import org.graffiti.plugin.algorithm.ThreadSafeOptions;

import de.ipk.ag_ba.commands.AbstractNavigationAction;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.commands.experiment.process.ActionPerformAnalysisLocally;
import de.ipk.ag_ba.commands.vfs.ActionDataExportToVfs;
import de.ipk.ag_ba.commands.vfs.VirtualFileSystemVFS2;
import de.ipk.ag_ba.gui.images.IAPexperimentTypes;
import de.ipk.ag_ba.gui.navigation_model.NavigationButton;
import de.ipk.ag_ba.gui.util.ExperimentReference;
import de.ipk.ag_ba.gui.util.ExperimentReferenceInterface;
import de.ipk.ag_ba.mongo.MongoDB;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentInterface;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.layout_control.dbe.RunnableWithMappingData;

/**
 * 
 * @author Sebastian Seitner
 */
public class AnalysisActionWrapper extends AbstractNavigationAction implements AutomatableAction {
	
	private IniIoProvider iniIO;
	private ExperimentReferenceInterface expRef;
	private MongoDB m;
	SystemOptions so;
	private boolean local;
	private boolean resultAvailable = false;
	private long startTime;
	private ThreadSafeOptions result = new ThreadSafeOptions();
	ExperimentReference resultExpRef;
	private RunnableWithMappingData resultReceiver = new RunnableWithMappingData() {
		ExperimentInterface experimentResult;
		
		@Override
		public void run() {
			experimentResult.getHeader().setImportUserGroup(IAPexperimentTypes.AnalysisResults + "");
			String nn = so.getString("DESCRIPTION", "pipeline_name", "analysis", true);
			if (nn != null) {
				if (!nn.contains(expRef.getExperimentName() + ""))
					nn = nn + " of " + expRef.getExperimentName();
				nn = StringManipulationTools.stringReplace(nn, ":", "_");
				experimentResult.getHeader().setExperimentname(nn);
				
				experimentResult.getHeader().setRemark(
						(experimentResult.getHeader().getRemark() != null && !experimentResult.getHeader().getRemark().isEmpty() ? experimentResult.getHeader()
								.getRemark() + " // " : "")
								+
								"analysis started: " + SystemAnalysis.getCurrentTime(startTime) +
								" // processing time: " +
								SystemAnalysis.getWaitTime(System.currentTimeMillis() - startTime) +
								" // finished: " + SystemAnalysis.getCurrentTime());
				// System.out.println("Stat: " + ((Experiment) statisticsResult).getExperimentStatistics());
				experimentResult.getHeader().setOriginDbId(expRef.getHeader().getDatabaseId());
				experimentResult.setHeader(experimentResult.getHeader());
				
				VirtualFileSystemVFS2 vfs = VirtualFileSystemVFS2.getKnownFromDatabaseId(expRef.getHeader().getDatabaseId());
				try {
					if (!experimentResult.getHeader().getDatabaseId().startsWith("mongo_") && vfs != null) {
						ActionDataExportToVfs ac = new ActionDataExportToVfs(m,
								new ExperimentReference(experimentResult), vfs, false, null);
						ac.setSkipClone(true);
						ac.setSource(null, null);
						if (status != null) {
							ac.setStatusProvider(status);
						}
						ac.performActionCalculateResults(null);
						
					} else {
						if (m != null) {
							m.saveExperiment(experimentResult, getStatusProvider());
							result.setParam(0, new ExperimentReference(experimentResult));
							resultAvailable = true;
						}
					}
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		}
		
		@Override
		public void setExperimenData(ExperimentInterface experiment) {
			this.experimentResult = experiment;
		}
		
	};
	
	public AnalysisActionWrapper(IniIoProvider iniIO, ExperimentReferenceInterface expRef, boolean local, MongoDB m) {
		super(null);
		this.iniIO = iniIO;
		this.expRef = expRef;
		this.m = m;
		this.local = local;
		so = SystemOptions.getInstance(null, iniIO);
	}
	
	@Override
	public void performActionCalculateResults(NavigationButton src) throws Exception {
		if (local) {
			ActionPerformAnalysisLocally analysisAction = new ActionPerformAnalysisLocally(iniIO, expRef, m);
			analysisAction.setResultReceiver(resultReceiver);
			analysisAction.setStatusProvider(this.getStatusProvider());
			startTime = System.currentTimeMillis();
			analysisAction.performActionCalculateResults(null);
		} else {
			// TODO Use Grid analysis Action
		}
		
	}
	
	public ExperimentReference getResultExpRef() {
		// Wait for the id to be stored by the resultReceiver
		while (!resultAvailable);
		return (ExperimentReference) result.getParam(0, null);
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewActionSet() {
		// TODO Auto-generated method stub
		return null;
	}
	
}
