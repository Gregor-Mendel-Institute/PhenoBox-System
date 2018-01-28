package at.gmi.djamei.iap.actions;

import java.util.ArrayList;

import org.SystemOptions;
import org.apache.commons.lang3.StringEscapeUtils;

import at.gmi.djamei.iap.IAPPipeline;
import de.ipk.ag_ba.commands.AbstractNavigationAction;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.commands.experiment.process.ExperimentAnalysisSettingsIOprovder;
import de.ipk.ag_ba.gui.MainPanelComponent;
import de.ipk.ag_ba.gui.navigation_model.NavigationButton;
import de.ipk.ag_ba.gui.util.ExperimentReferenceInterface;

/**
 * 
 * @author Sebastian Seitner
 *
 * Based on the class 'de.ipk.ag_ba.commands.experiment.process.ActionAssignAnalysisTemplate' by klukas 
 */
public class ActionSetAnalysisPipeline extends AbstractNavigationAction implements AutomatableAction {
	
	private IAPPipeline pipeline;
	private ExperimentReferenceInterface exp;
	
	public ActionSetAnalysisPipeline(ExperimentReferenceInterface exp,
			IAPPipeline pipeline) {
		super("Set Analysis Pipeline for given Experiment");
		this.exp = exp;
		this.pipeline=pipeline;
	}
	
	@Override
	public void performActionCalculateResults(NavigationButton src) throws Exception {
		String ini = pipeline.getSource();
		ini = (ini == null) ? null : StringEscapeUtils.escapeXml(ini);
		exp.getHeader().setSettings(ini);
		if (exp.getM() != null) {
			try {
				exp.getM().saveExperimentHeader(exp.getHeader());
				
				if (exp.getIniIoProvider() != null && exp.getIniIoProvider().getInstance() != null)
					exp.getIniIoProvider().getInstance().reload();
				else
					exp.setIniIoProvider(new ExperimentAnalysisSettingsIOprovder(exp.getHeader(), exp.getM()));
			} catch (Exception e) {
				e.printStackTrace();
				// TODO settings could not be changed
			}
		} else {
			// TODO no mongoDB found, should not be possible
			if (exp.getHeader().getExperimentHeaderHelper() != null) {
				exp.getHeader().getExperimentHeaderHelper().saveUpdatedProperties(status);
			}
		}
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewActionSet() {
		return null;
	}
	
	@Override
	public MainPanelComponent getResultMainPanel() {
		return null;
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewNavigationSet(ArrayList<NavigationButton> currentSet) {
		return currentSet;
	}
	
	@Override
	public String getDefaultTitle() {
		return "Set Analysis Pipeline for given Experiment";
	}
	
	@Override
	public String getDefaultImage() {
		if (pipeline != null)
			return "img/ext/gpl2/Gnome-Insert-Object-64.png";
		else
			return "img/ext/gpl2/Gnome-Emblem-Unreadable-64.png";
	}
	
}
