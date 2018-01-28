package at.gmi.djamei.iap.actions;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashSet;
import java.util.Set;

import org.StringManipulationTools;
import org.graffiti.plugin.io.resources.IOurl;
import org.graffiti.plugin.io.resources.ResourceIOHandler;
import org.graffiti.plugin.io.resources.ResourceIOManager;

import de.ipk.ag_ba.commands.AbstractNavigationAction;
import de.ipk.ag_ba.commands.AutomatableAction;
import de.ipk.ag_ba.commands.DeletionCommand;
import de.ipk.ag_ba.gui.MainPanelComponent;
import de.ipk.ag_ba.gui.navigation_model.NavigationButton;
import de.ipk.ag_ba.mongo.MongoDB;
import de.ipk_gatersleben.ag_nw.graffiti.plugins.gui.editing_tools.script_helper.ExperimentHeaderInterface;

/**
 * @author Sebastian Seitner
 * IAP action used to permanently delete an experiment identified by an Experiment Header
 * Based on the class 'de.ipk.ag_ba.commands.ActionTrash' by klukas
 */
public class ActionDelete extends AbstractNavigationAction implements AutomatableAction {
	
	private final MongoDB m;
	private String experimentName;
	private Set<ExperimentHeaderInterface> headers;
	private String message = "";
	private DeletionCommand cmd;
	
	public ActionDelete(ExperimentHeaderInterface header, MongoDB m) {
		super("Perform 'Delete'-operation");
		this.m = m;
		this.setHeader(header);
		this.cmd = DeletionCommand.DELETE;
	}
	
	@Override
	public String getDefaultTitle() {
		String desc = "";
		if (headers.size() == 1)
			desc = "";// headers.iterator().next().getExperimentName();
		else
			desc = headers.size() + " experiments";
		if (!desc.isEmpty())
			return "<html><center>" + cmd.toString() + "<br>(" + desc + ")</center>";
		else
			return cmd.toString();
	}
	
	@Override
	public String getDefaultImage() {
		return cmd.getImg();
	}
	
	@Override
	public void performActionCalculateResults(NavigationButton src) throws Exception {
		Collection<ExperimentHeaderInterface> list = getHeader();
		if (list != null && list.size() > 0) {
			int idx = 0;
			for (ExperimentHeaderInterface hhh : list) {
				status.setCurrentStatusText1("Processing");
				idx++;
				status.setCurrentStatusText2(idx + "/" + list.size());
				processExperiment(hhh);
				status.setCurrentStatusValueFine(100d * idx / list.size());
			}
			status.setCurrentStatusText1("Finished");
			status.setCurrentStatusText2("");
			message = "Finished processing of " + list.size() + " experiments!";
		}
	}
	
	private void processExperiment(ExperimentHeaderInterface hhh) throws Exception {
		experimentName = hhh.getExperimentName();
		message += "<li>Process Experiment " + experimentName + ": ";
		if (cmd == DeletionCommand.DELETE || cmd == DeletionCommand.EMPTY_TRASH_DELETE_ALL_TRASHED_IN_LIST) {
			if (m != null && getHeader() != null) {
				m.deleteExperiment(hhh.getDatabaseId());
				message += "<html><b>" + "Experiment " + experimentName + " has been deleted.";
			} else {
				ResourceIOHandler h = ResourceIOManager.getInstance().getHandlerFromPrefix(new IOurl(hhh.getDatabaseId()).getPrefix());
				if (h != null)
					h.deleteResource(new IOurl(hhh.getDatabaseId()));
			}
		}
		if (cmd == DeletionCommand.TRASH || cmd == DeletionCommand.TRASH_GROUP_OF_EXPERIMENTS) {
			try {
				if (m != null)
					m.setExperimentType(hhh, "Trash" + ";" + hhh.getExperimentType());
				else {
					hhh.setExperimentType("Trash" + ";" + hhh.getExperimentType());
					hhh.getExperimentHeaderHelper().saveUpdatedProperties(null);
				}
				message += "has been marked as trashed!";
			} catch (Exception e) {
				message += "Error: " + e.getMessage();
			}
		}
		if (cmd == DeletionCommand.UNTRASH || cmd == DeletionCommand.UNTRASH_ALL) {
			try {
				String type = hhh.getExperimentType();
				while (type.contains("Trash;"))
					type = StringManipulationTools.stringReplace(type, "Trash;", "");
				while (type.contains("Trash"))
					type = StringManipulationTools.stringReplace(type, "Trash", "");
				if (m != null)
					m.setExperimentType(hhh, type);
				else {
					hhh.setExperimentType(type);
					hhh.getExperimentHeaderHelper().saveUpdatedProperties(null);
				}
				message += "Experiment " + experimentName + " has been put out of trash!";
			} catch (Exception e) {
				message += "Error: " + e.getMessage();
			}
		}
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewNavigationSet(ArrayList<NavigationButton> currentSet) {
		ArrayList<NavigationButton> res = new ArrayList<NavigationButton>(currentSet);
		if (res.size() > 1)
			res.remove(res.size() - 1);
		res.add(null);
		return res;
	}
	
	@Override
	public ArrayList<NavigationButton> getResultNewActionSet() {
		return null;
	}
	
	@Override
	public MainPanelComponent getResultMainPanel() {
		return new MainPanelComponent(message);
	}
	
	private void setHeader(ExperimentHeaderInterface header) {
		LinkedHashSet<ExperimentHeaderInterface> h = new LinkedHashSet<ExperimentHeaderInterface>();
		h.add(header);
		h.addAll(header.getHistory().values());
		this.setHeaders(h);
	}
	
	private Collection<ExperimentHeaderInterface> getHeader() {
		return getHeaders();
	}
	
	private Set<ExperimentHeaderInterface> getHeaders() {
		return headers;
	}
	
	private void setHeaders(Set<ExperimentHeaderInterface> headers) {
		this.headers = headers;
		LinkedHashSet<ExperimentHeaderInterface> toBeAdded = new LinkedHashSet<ExperimentHeaderInterface>();
		for (ExperimentHeaderInterface h : this.headers)
			toBeAdded.addAll(h.getHistory().values());
		for (ExperimentHeaderInterface h : toBeAdded)
			this.headers.add(h);
	}
	
}
