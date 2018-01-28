package at.gmi.djamei.r.viz.charts.gral;

import de.erichseifert.gral.data.DataSeries;
import de.erichseifert.gral.data.DataTable;
import de.erichseifert.gral.graphics.Insets2D;
import de.erichseifert.gral.graphics.Location;
import de.erichseifert.gral.graphics.Orientation;
import de.erichseifert.gral.plots.Plot;
import de.erichseifert.gral.plots.XYPlot;
import de.erichseifert.gral.plots.points.DefaultPointRenderer2D;
import de.erichseifert.gral.plots.points.PointRenderer;
import org.renjin.primitives.matrix.Matrix;
import org.renjin.sexp.*;

import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.util.ArrayList;
import java.util.List;

public class ScatterChart extends GralXYPlot {
    SEXP data;//TODO change to vector /DoubleVector
    IntArrayVector groups;//factor
    StringArrayVector labels;//vector

    Boolean showLabels = false;


    //TODO check if dimensions match when set
    public Boolean getShowLabels() {
        return showLabels;
    }

    public void setShowLabels(Boolean showLabels) {
        this.showLabels = showLabels;
    }

    public StringArrayVector getLabels() {
        return labels;
    }

    public void setLabels(StringArrayVector labels) {
        this.labels = labels;
    }


    public IntArrayVector getGroups() {
        return groups;
    }

    public void setGroups(IntArrayVector groups) {
        if (groups.getAttributes().getClassVector().indexOf(new StringArrayVector("factor"), 0, 0) == -1) {
            throw new IllegalArgumentException("'groups' must be a factor");
        }
        this.groups = groups;
    }


    public SEXP getData() {
        return data;
    }

    public void setData(SEXP data) {
        if (data.getAttributes().getDim() instanceof Null || data.getAttributes().getDim().getElementAsInt(1) != 2) {
            throw new IllegalArgumentException("'data' has to be a matrix with 2 columns (x,y)");
        }
        this.data = data;

    }


    @Override
    public Plot createPlot() {
        Matrix m = new Matrix((Vector) data);

        DataTable[] dataTables = new DataTable[groups.getAttribute(Symbol.get("levels")).length()];
        DataTable dataTable;
        for (int i = 0; i < m.getNumRows(); i++) {
            List<Comparable<?>> row = new ArrayList<>(3);
            for (int j = 0; j < 2; j++) {
                row.add(m.getElementAsDouble(i, j));
            }
            if (labels != null) {
                row.add(labels.getElementAsString(i));
            } else {
                row.add("");
            }
            dataTable = dataTables[groups.getElementAsInt(i) - 1];
            if (dataTable == null) {
                dataTable = new DataTable(Double.class, Double.class, String.class);
                dataTables[groups.getElementAsInt(i) - 1] = dataTable;
            }
            dataTable.add(row);
        }

        XYPlot plot = new XYPlot();
        addMarkerLines(plot);

        for (int i = 0; i < dataTables.length; i++) {
            dataTable = dataTables[i];
            DataSeries s = new DataSeries(legend.getElementAsString(i), dataTable, 0, 1, 2);
            plot.add(s);
            PointRenderer pointRenderer = new DefaultPointRenderer2D();
            pointRenderer.setShape(new Ellipse2D.Double(-3.0, -3.0, 6.0, 6.0));
            String color = colors.getElementAsString(i);
            Color c = Color.decode(color.substring(0, 7));//Drop Alpha value
            pointRenderer.setColor(c);
            pointRenderer.setValueColumn(2);
            pointRenderer.setValueVisible(showLabels);
            pointRenderer.setValueDistance(0.1);
            pointRenderer.setValueLocation(Location.NORTH);
            plot.setPointRenderers(s, pointRenderer);

        }

        plot.getTitle().setText(this.title);

        plot.getAxisRenderer(XYPlot.AXIS_X).getLabel().setText(this.xLabel);
        plot.getAxisRenderer(XYPlot.AXIS_Y).getLabel().setText(this.yLabel);
        plot.getAxisRenderer(XYPlot.AXIS_X).setTickSpacing(1.0);
        plot.getAxisRenderer(XYPlot.AXIS_Y).setTickSpacing(1.0);
        plot.getAxisRenderer(XYPlot.AXIS_X).setIntersection(-Double.MAX_VALUE);
        plot.getAxisRenderer(XYPlot.AXIS_Y).setIntersection(-Double.MAX_VALUE);
        plot.setLegendVisible(true);
        plot.getLegend().setOrientation(Orientation.VERTICAL);

        plot.setLegendLocation(Location.EAST);
        // Style the plot
        double insetsTop = 20.0,
                insetsLeft = 60.0,
                insetsBottom = 90.0,
                insetsRight = plot.getLegendDistance() * plot.getLegend().getFont().getSize() + plot.getLegend().getWidth();
        plot.setInsets(new Insets2D.Double(
                insetsTop, insetsLeft, insetsBottom, insetsRight));
        plot.getNavigator().setZoom(0.9);
        this.plot = plot;
        return plot;

    }
}
