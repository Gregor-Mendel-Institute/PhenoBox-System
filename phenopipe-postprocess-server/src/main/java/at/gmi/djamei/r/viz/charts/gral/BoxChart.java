package at.gmi.djamei.r.viz.charts.gral;

import de.erichseifert.gral.data.DataSource;
import de.erichseifert.gral.data.DataTable;
import de.erichseifert.gral.graphics.Insets2D;
import de.erichseifert.gral.plots.Plot;
import de.erichseifert.gral.plots.XYPlot;
import de.erichseifert.gral.plots.colors.ColorMapper;
import de.erichseifert.gral.plots.colors.IndexedColors;
import de.erichseifert.gral.plots.colors.RainbowColors;
import de.erichseifert.gral.util.DataUtils;
import org.renjin.sexp.DoubleArrayVector;
import org.renjin.sexp.IntArrayVector;
import org.renjin.sexp.StringArrayVector;
import org.renjin.sexp.Symbol;

import java.awt.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class BoxChart extends GralXYPlot {
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
        this.data = data;
    }

    private Double getFromList(List<Double> list, int index) {
        if (index < list.size()) {
            return list.get(index);
        }
        return null;
    }

    private DataTable consolidateData() {//TODO allow matrix form?
        int groupCount = groups.getAttribute(Symbol.get("levels")).length();
        DataTable dataTable = new DataTable(groupCount, Double.class);
        HashMap<Integer, List<Double>> group2values = new HashMap<>();
        List<Double> values;
        for (int i = 0; i < data.length(); i++) {
            values = group2values.get(groups.getElementAsInt(i) - 1);
            if (values == null) {
                values = new ArrayList<>();
                group2values.put(groups.getElementAsInt(i) - 1, values);
            }
            values.add(data.getElementAsDouble(i));
        }
        int maxLen = 0;
        for (List<Double> l : group2values.values()) {
            if (l.size() > maxLen) {
                maxLen = l.size();
            }
        }
        List<Double> row;
        for (int i = 0; i < maxLen; i++) {
            row = new ArrayList<>(groupCount);
            for (List<Double> l : group2values.values()) {
                row.add(getFromList(l, i));
            }
            dataTable.add(row);
        }
        return dataTable;
    }

    private String[] getGroupNames() {
        return ((StringArrayVector) groups.getAttribute(Symbol.get("levels"))).toArray();
    }

    @Override
    public Plot createPlot() {
        DataTable dataTable = consolidateData();

        DataSource boxData = AnnotatedBoxPlot.createBoxData(dataTable);

        AnnotatedBoxPlot plot = new AnnotatedBoxPlot(boxData);
        double insetsTop = 20.0,
                insetsLeft = 60.0,
                insetsBottom = 60.0,
                insetsRight = 40.0;
        plot.setInsets(new Insets2D.Double(
                insetsTop, insetsLeft, insetsBottom, insetsRight));
        plot.getTitle().setText(getTitle());
        String[] tickNames = getGroupNames();
        Double[] ticks = new Double[tickNames.length];
        for (int i = 0; i < ticks.length; i++) {
            ticks[i] = i + 1.0;
        }
        plot.getAxisRenderer(AnnotatedBoxPlot.AXIS_X).setCustomTicks(DataUtils.map(
                ticks,
                tickNames
                )
        );
        plot.getAxisRenderer(AnnotatedBoxPlot.AXIS_X).getLabel().setText(xLabel);
        plot.getAxisRenderer(AnnotatedBoxPlot.AXIS_Y).getLabel().setText(yLabel);

        Color[] colors = getColorInstances();
        ColorMapper colorMapper;
        if (colors.length == 0) {
            colorMapper = new RainbowColors();
        } else {
            colorMapper = new IndexedColors(colors[0], Arrays.copyOfRange(colors, 1, colors.length));
        }
        ((AnnotatedBoxPlot.BoxWhiskerRenderer) plot.getPointRenderers(boxData).get(0)).setBoxBackground(colorMapper);
        addMarkerLines(plot);
        plot.autoscaleAxis(AnnotatedBoxPlot.AXIS_Y);
        plot.getNavigator().setZoom(0.9);
        this.plot = plot;
        return plot;
    }
}
