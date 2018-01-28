package at.gmi.djamei.r.viz.charts.gral;

import de.erichseifert.gral.data.DataTable;
import de.erichseifert.gral.graphics.Insets2D;
import de.erichseifert.gral.graphics.Location;
import de.erichseifert.gral.graphics.Orientation;
import de.erichseifert.gral.plots.BarPlot;
import de.erichseifert.gral.plots.Plot;
import de.erichseifert.gral.plots.XYPlot;
import de.erichseifert.gral.plots.axes.AxisRenderer;
import de.erichseifert.gral.plots.colors.ColorMapper;
import org.renjin.primitives.matrix.Matrix;
import org.renjin.sexp.DoubleArrayVector;
import org.renjin.sexp.Null;
import org.renjin.sexp.StringArrayVector;
import org.renjin.sexp.Symbol;

import java.awt.*;
import java.util.HashMap;

public class BarChart extends GralXYPlot {
    private float barWidth = 1.0f;
    private DoubleArrayVector data;
    private StringArrayVector groups;

    public DoubleArrayVector getData() {
        return data;
    }

    /**
     * @param data Matrix where columns denote groupings and rows are the different entities of a grouping
     *             Groupings are displayed next to each other with a gap between groupings
     */
    public void setData(DoubleArrayVector data) {
        this.data = data;
    }

    public StringArrayVector getGroups() {
        return groups;
    }

    /**
     * Sets the names of the groups contained in data
     *
     * @param groups a character vector which contains the group names in the same order as they are entered in the data matrix
     */
    public void setGroups(StringArrayVector groups) {
        this.groups = groups;
    }

    public float getBarWidth() {
        return barWidth;
    }

    public void setBarWidth(float barWidth) {
        this.barWidth = barWidth;
    }

    private DataTable[] consolidateData() {
        DataTable[] dataTables;
        if (!(data.getAttribute(Symbol.get("dim")) instanceof Null)) {
            Matrix m = new Matrix(data);
            dataTables = new DataTable[m.getNumRows()];
            DataTable dataTable;
            for (int row = 0; row < m.getNumRows(); row++) {
                dataTable = new DataTable(Integer.class, Double.class, String.class);
                dataTables[row] = dataTable;
                for (int col = 0; col < m.getNumCols(); col++) {
                    int pos = row + (m.getNumRows() * col) + col + 2;//+2 used to move 0 Tick out of view
                    dataTable.add(pos, m.getElementAsDouble(row, col), legend.getElementAsString(row));
                }
            }
        } else {
            String[] groupNames = getGroupNames();
            dataTables = new DataTable[groupNames.length];
            DataTable dataTable;
            for (int i = 0; i < data.length(); i++) {
                dataTable = dataTables[i];
                if (dataTable == null) {
                    dataTable = new DataTable(Integer.class, Double.class, String.class);
                    dataTables[i] = dataTable;
                }
                dataTable.add(i, data.getElementAsDouble(i), legend.getElementAsString(i));
            }
        }
        return dataTables;
    }

    private String[] getGroupNames() {
        return groups.toArray();
    }

    private void customTicks(DataTable[] dataTables, AxisRenderer axisRenderer, boolean grouped) {
        HashMap<Double, String> tick2Label = new HashMap<>();
        String[] groupNames = getGroupNames();
        if (grouped) {
            int rows = dataTables[0].getRowCount();
            Double sum;
            for (int i = 0; i < rows; i++) {
                sum = 0.0;
                for (DataTable dataTable : dataTables) {
                    sum += ((Integer) dataTable.getRow(i).get(0)).doubleValue();
                }
                sum /= dataTables.length;
                tick2Label.put(sum, groupNames[i]);
            }
        } else {
            for (int i = 0; i < dataTables.length; i++) {
                tick2Label.put((double)i, groupNames[i]);
            }

        }
        axisRenderer.setCustomTicks(tick2Label);
    }

    @Override
    public Plot createPlot() {
        boolean grouped = !(data.getAttribute(Symbol.get("dim")) instanceof Null);
        DataTable[] dataTables = consolidateData();

        BarPlot plot = new BarPlot(dataTables);
        customTicks(dataTables, plot.getAxisRenderer(BarPlot.AXIS_X),grouped);
        double insetsTop = 20.0,
                insetsLeft = 60.0,
                insetsBottom = 60.0,
                insetsRight = 40.0;
        plot.setInsets(new Insets2D.Double(
                insetsTop, insetsLeft, insetsBottom, insetsRight));

        plot.getTitle().setText(getTitle());
        plot.setBarWidth(barWidth);

        plot.getAxisRenderer(BarPlot.AXIS_X).setTicksVisible(true);
        plot.getAxisRenderer(BarPlot.AXIS_X).setTickLength(0.0);
        plot.getAxisRenderer(BarPlot.AXIS_X).setTickSpacing(Integer.MAX_VALUE);//"Disable" Original ticks and only display custom ticks
        plot.getAxisRenderer(BarPlot.AXIS_X).setMinorTicksVisible(false);
        plot.getAxisRenderer(XYPlot.AXIS_X).setIntersection(-Double.MAX_VALUE);
        plot.getAxisRenderer(XYPlot.AXIS_Y).setIntersection(-Double.MAX_VALUE);

        ColorMapper colorMapper = getColorMapper();
        for (int i = 0; i < dataTables.length; i++) {
            BarPlot.BarRenderer pointRenderer = (BarPlot.BarRenderer) plot.getPointRenderers(dataTables[i]).get(0);
            pointRenderer.setColor(
                    colorMapper.get(i)
            );
            pointRenderer.setValueVisible(true);
            pointRenderer.setValueColumn(2);
            pointRenderer.setValueLocation(Location.CENTER);
            pointRenderer.setValueFont(Font.decode(null).deriveFont(Font.BOLD));
        }

        plot.setLegendVisible(false);
        plot.getLegend().setOrientation(Orientation.VERTICAL);
        plot.setLegendLocation(Location.EAST);

        return plot;
    }


}
