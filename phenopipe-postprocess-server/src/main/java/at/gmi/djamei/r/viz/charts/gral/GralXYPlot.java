package at.gmi.djamei.r.viz.charts.gral;

import de.erichseifert.gral.data.DataTable;
import de.erichseifert.gral.graphics.Location;
import de.erichseifert.gral.io.plots.DrawableWriter;
import de.erichseifert.gral.io.plots.DrawableWriterFactory;
import de.erichseifert.gral.plots.Plot;
import de.erichseifert.gral.plots.XYPlot;
import de.erichseifert.gral.plots.colors.ColorMapper;
import de.erichseifert.gral.plots.colors.IndexedColors;
import de.erichseifert.gral.plots.colors.RainbowColors;
import de.erichseifert.gral.plots.lines.DefaultLineRenderer2D;
import de.erichseifert.gral.plots.lines.LineRenderer;
import de.erichseifert.gral.plots.points.DefaultPointRenderer2D;
import de.erichseifert.gral.plots.points.PointRenderer;
import org.renjin.primitives.Indexes;
import org.renjin.primitives.matrix.Matrix;
import org.renjin.sexp.Null;
import org.renjin.sexp.StringArrayVector;
import org.renjin.sexp.StringVector;
import org.renjin.sexp.Vector;

import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;

public abstract class GralXYPlot {
    protected Plot plot;
    String title;
    StringArrayVector legend;
    StringArrayVector colors;

    String xLabel;
    String yLabel;

    Vector markerLines;

    public Vector getMarkerLines() {
        return markerLines;
    }

    public void setMarkerLines(Vector markerLines) {
        if (markerLines.getAttributes().getDim() instanceof Null || markerLines.getAttributes().getDim().getElementAsInt(1) != 6) {
            throw new IllegalArgumentException("'markerLines' has to be a matrix with 6 columns (x1,y1,x2,y2, label, color)");
        }
        this.markerLines = markerLines;
    }


    public StringArrayVector getColors() {
        return colors;
    }

    public void setColors(StringArrayVector colors) {
        this.colors = colors;
    }

    public String getxLabel() {
        return xLabel;
    }

    public void setxLabel(String xLabel) {
        this.xLabel = xLabel;
    }

    public String getyLabel() {
        return yLabel;
    }

    public void setyLabel(String yLabel) {
        this.yLabel = yLabel;
    }

    public StringVector getLegend() {
        return legend;
    }

    public void setLegend(StringArrayVector legend) {
        this.legend = legend;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void writePlotAsSvg(String filepath) throws IOException {
        if (plot == null) {
            plot = createPlot();
        }
        if (!filepath.endsWith(".svg")) {
            filepath += ".svg";
        }
        DrawableWriter svgWriter = DrawableWriterFactory.getInstance().get("image/svg+xml");
        File svgFile = new File(filepath);
        if (!svgFile.exists()) {
            svgFile.createNewFile();
        }
        svgWriter.write(plot, new FileOutputStream(svgFile), 800, 600);
    }

    public abstract Plot createPlot();

    protected Color decodeColor(String color){
        return Color.decode(color.substring(0,7));
    }
    protected Color[] getColorInstances() {
        Color[] colors = new Color[this.colors.length()];
        for (int i = 0; i < this.colors.length(); i++) {
            colors[i] = decodeColor(this.colors.getElementAsString(i));
        }
        return colors;
    }

    protected ColorMapper getColorMapper() {
        Color[] colors = getColorInstances();
        if (colors.length == 0) {
            return new RainbowColors();
        } else {
            return new IndexedColors(colors[0], Arrays.copyOfRange(colors, 1, colors.length));
        }
    }
    protected void addMarkerLines(XYPlot plot) {
        if (markerLines != null) {
            Matrix lines = new Matrix(markerLines);
            DataTable lineTable;
            for (int i = 0; i < lines.getNumRows(); i++) {
                lineTable = new DataTable(Double.class, Double.class, String.class);
                //TODO move column numbers to static variables?
                double x1,y1,x2,y2;
                x1 = lines.getElementAsDouble(i, 0);
                y1=lines.getElementAsDouble(i, 1);
                x2=lines.getElementAsDouble(i, 2);
                y2=lines.getElementAsDouble(i, 3);
                String label = lines.getVector().getElementAsString(Indexes.matrixIndexToVectorIndex(i, 4, lines.getNumRows(), lines.getNumCols()));
                double labelX= (x1+x2)/2;
                double labelY= (y1+y2)/2;
                lineTable.add(x1,y1,"");
                lineTable.add(labelX, labelY, label);
                lineTable.add(x2,y2,"");

                plot.add(lineTable);
                LineRenderer lineRenderer = new DefaultLineRenderer2D();
                String colorString = lines.getVector().getElementAsString(Indexes.matrixIndexToVectorIndex(i, 5, lines.getNumRows(), lines.getNumCols()));
                lineRenderer.setColor(decodeColor(colorString));

                plot.setLineRenderers(lineTable, lineRenderer);

                PointRenderer pointRenderer = new DefaultPointRenderer2D();
                pointRenderer.setShape(new Ellipse2D.Double(0,0,0,0));
                pointRenderer.setValueVisible(true);
                pointRenderer.setValueColor(decodeColor(colorString));
                pointRenderer.setColor(plot.getBackground());
                pointRenderer.setValueColumn(2);
                pointRenderer.setValueLocation(Location.NORTH);
                pointRenderer.setValueDistance(0.1);
                plot.setPointRenderers(lineTable, pointRenderer);
                plot.getLegend().remove(lineTable);

            }
        }
    }
}
