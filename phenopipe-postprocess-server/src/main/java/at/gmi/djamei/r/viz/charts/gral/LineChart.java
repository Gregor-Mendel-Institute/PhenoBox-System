package at.gmi.djamei.r.viz.charts.gral;

import de.erichseifert.gral.data.DataSeries;
import de.erichseifert.gral.data.DataTable;
import de.erichseifert.gral.graphics.Insets2D;
import de.erichseifert.gral.graphics.Location;
import de.erichseifert.gral.graphics.Orientation;
import de.erichseifert.gral.plots.Plot;
import de.erichseifert.gral.plots.XYPlot;
import de.erichseifert.gral.plots.colors.ColorMapper;
import de.erichseifert.gral.plots.lines.DefaultLineRenderer2D;
import de.erichseifert.gral.plots.lines.LineRenderer;
import de.erichseifert.gral.plots.points.DefaultPointRenderer2D;
import de.erichseifert.gral.plots.points.PointRenderer;
import org.renjin.primitives.matrix.Matrix;
import org.renjin.sexp.*;

import java.awt.geom.Ellipse2D;
import java.util.ArrayList;
import java.util.List;

public class LineChart extends GralXYPlot {
    DoubleArrayVector data;
    IntArrayVector groups;

    public IntArrayVector getGroups() {
        return groups;
    }

    public void setGroups(IntArrayVector groups) {
        if (groups.getAttributes().getClassVector().indexOf(new StringArrayVector("factor"), 0, 0) == -1) {
            throw new IllegalArgumentException("'groups' must be a factor");
        }
        this.groups = groups;
    }

    public DoubleArrayVector getData() {

        return data;
    }

    public void setData(DoubleArrayVector data) {
        if (data.getAttributes().getDim() instanceof Null || data.getAttributes().getDim().getElementAsInt(1) != 2) {
            throw new IllegalArgumentException("'data' has to be a matrix with 2 columns (x,y)");
        }
        this.data = data;
    }

    private DataTable[] consolidateData(Matrix m) {

        DataTable[] dataTables = new DataTable[groups.getAttribute(Symbol.get("levels")).length()];
        //DataTable data = new DataTable(m.getNumCols(), Double.class);
        DataTable data;
        for (int i = 0; i < m.getNumRows(); i++) {
            List<Double> row = new ArrayList<>(m.getNumCols());
            for (int j = 0; j < m.getNumCols(); j++) {
                row.add(m.getElementAsDouble(i, j));
            }
            data = dataTables[groups.getElementAsInt(i) - 1];
            if (data == null) {
                data = new DataTable(m.getNumCols(), Double.class);
                dataTables[groups.getElementAsInt(i) - 1] = data;
            }
            data.add(row);
        }
        return dataTables;
    }

    @Override
    public Plot createPlot() {
        Matrix m = new Matrix((Vector) data);
        DataTable[] dataTables = consolidateData(m);
        XYPlot plot = new XYPlot();
        DataTable dataTable;
        ColorMapper colorMapper = getColorMapper();
        for (int i = 0; i < dataTables.length; i++) {
            dataTable = dataTables[i];
            for (int j = 0; j < m.getNumCols() - 1; j++) {
                DataSeries s = new DataSeries(legend.getElementAsString(i), dataTable, 0, j + 1);
                plot.add(s);
                PointRenderer pointRenderer = new DefaultPointRenderer2D();
                pointRenderer.setShape(new Ellipse2D.Double(-3.0, -3.0, 6.0, 6.0));
                pointRenderer.setColor(colorMapper.get(i));
                plot.setPointRenderers(s, pointRenderer);

                LineRenderer lineRenderer = new DefaultLineRenderer2D();
                lineRenderer.setColor(colorMapper.get(i));
                plot.setLineRenderers(s, lineRenderer);

            }
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
        this.plot = plot;
        plot.getNavigator().setZoom(0.9);
        return plot;

    }
}
