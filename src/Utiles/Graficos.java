package Utiles;



/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JPanel;
import javax.swing.Timer;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYAreaRenderer;
import org.jfree.chart.renderer.xy.XYBarRenderer;
import org.jfree.chart.ui.RectangleInsets;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
/**
 * Gráficos de la aplicación.
 * - Distribuciones discretas: gráfico de barras (más legible para P(X=x)).
 * - Distribuciones continuas: gráfico de área (densidad f(x) y área acumulada).
 * Incluye animación de carga progresiva de los puntos y estilo mejorado.
 * @author 666
 */
public class Graficos {
private JFreeChart graficaD;
private JFreeChart graficaA;
private final XYSeriesCollection datos=new XYSeriesCollection();
private ChartPanel panelD;
private ChartPanel panelA;
private String titulo;
private String etiquetax;
private String etiquetay;
// Animación de carga progresiva
private Timer animacion;
private final List<double[]> pendientesX=new ArrayList<double[]>();
private final List<double[]> pendientesY=new ArrayList<double[]>();
private final List<String> pendientesId=new ArrayList<String>();
private XYSeries serieActual;
private int indicePunto;
public Graficos(String t,String x,String y){
 titulo=t;
 etiquetax=x;
 etiquetay=y;
 // Discreta: barras verticales, ideal para datos discretos
 graficaD=ChartFactory.createXYBarChart(titulo, x, y, datos, PlotOrientation.VERTICAL, true, true, false);
 estilizarBarras(graficaD);
 // Continua: área bajo la curva
 graficaA=ChartFactory.createXYAreaChart(t, x, y, datos, PlotOrientation.VERTICAL, true, true, true);
 estilizarArea(graficaA);
}
public Graficos(){
     this(null, "x", "y");
 }
public void crearGrafica(String id,double[] x,double[] y){
    detenerAnimacion();
    datos.removeAllSeries();
    pendientesX.clear();
    pendientesY.clear();
    pendientesId.clear();
    encolar(id,x,y);
}
public void addGrafica(String id,double[] x,double[] y){
    encolar(id,x,y);
}
private void encolar(String id,double[] x,double[] y){
    if(x==null||y==null||x.length==0||y.length==0)
        return;
    pendientesX.add(x);
    pendientesY.add(y);
    pendientesId.add(id);
    if(animacion==null||!animacion.isRunning())
        iniciarAnimacion();
}
private void iniciarAnimacion(){
    serieActual=null;
    indicePunto=0;
    animacion=new Timer(15,new ActionListener(){
        @Override
        public void actionPerformed(ActionEvent e){
            if(serieActual==null){
                if(pendientesX.isEmpty()){
                    detenerAnimacion();
                    return;
                }
                serieActual=new XYSeries(pendientesId.remove(0));
                datos.addSeries(serieActual);
                indicePunto=0;
            }
            double[] x=pendientesX.get(0);
            double[] y=pendientesY.get(0);
            // avanza varios puntos por tick para una animación fluida (~1s)
            int paso=Math.max(1,x.length/60);
            int fin=Math.min(x.length,indicePunto+paso);
            for(int i=indicePunto;i<fin;i++){
                serieActual.add(x[i],y[i]);
            }
            indicePunto=fin;
            if(indicePunto>=x.length){
                pendientesX.remove(0);
                pendientesY.remove(0);
                serieActual=null;
            }
        }
    });
    animacion.start();
}
private void detenerAnimacion(){
    if(animacion!=null)
        animacion.stop();
    pendientesX.clear();
    pendientesY.clear();
    pendientesId.clear();
    serieActual=null;
}
public void limpiar(){
    detenerAnimacion();
    datos.removeAllSeries();
}
public JPanel getGraficaA(){
    if(panelA==null){
        panelA=new ChartPanel(graficaA);
        panelA.setPreferredSize(new Dimension(394,260));
        panelA.setMouseWheelEnabled(true);
    }
    return panelA;
}
public JPanel getGraficaD(){
    if(panelD==null){
        panelD=new ChartPanel(graficaD);
        panelD.setPreferredSize(new Dimension(394,260));
        panelD.setMouseWheelEnabled(true);
    }
    return panelD;
}
private void estilizar(JFreeChart c){
    c.setAntiAlias(true);
    c.setBackgroundPaint(Color.WHITE);
    c.setPadding(new RectangleInsets(10,10,10,10));
    if(c.getTitle()!=null){
        c.getTitle().setFont(new Font("SansSerif",Font.BOLD,15));
        c.getTitle().setPaint(new Color(40,40,40));
    }
    if(c.getLegend()!=null){
        c.getLegend().setBackgroundPaint(new Color(248,248,248));
        c.getLegend().setItemFont(new Font("SansSerif",Font.PLAIN,11));
    }
    XYPlot p=c.getXYPlot();
    p.setBackgroundPaint(new Color(250,250,252));
    p.setDomainGridlinePaint(new Color(215,215,225));
    p.setRangeGridlinePaint(new Color(215,215,225));
    p.setDomainGridlinesVisible(true);
    p.setRangeGridlinesVisible(true);
    p.setAxisOffset(new RectangleInsets(5,5,5,5));
    p.setOutlinePaint(new Color(170,170,170));
    estilizarEje((NumberAxis)p.getDomainAxis());
    estilizarEje((NumberAxis)p.getRangeAxis());
}
private void estilizarEje(NumberAxis eje){
    eje.setLabelFont(new Font("SansSerif",Font.BOLD,12));
    eje.setTickLabelFont(new Font("SansSerif",Font.PLAIN,11));
    eje.setLabelPaint(new Color(60,60,60));
    eje.setTickLabelPaint(new Color(60,60,60));
    eje.setAxisLinePaint(new Color(120,120,120));
    eje.setTickMarkPaint(new Color(120,120,120));
}
private void estilizarBarras(JFreeChart c){
    estilizar(c);
    XYPlot p=c.getXYPlot();
    XYBarRenderer r=(XYBarRenderer)p.getRenderer();
    r.setDrawBarOutline(false);
    r.setShadowVisible(false);
    r.setSeriesPaint(0,new Color(51,102,255));
    r.setSeriesPaint(1,new Color(255,140,0));
    r.setSeriesPaint(2,new Color(0,170,120));
    r.setSeriesPaint(3,new Color(200,60,60));
}
private void estilizarArea(JFreeChart c){
    estilizar(c);
    XYPlot p=c.getXYPlot();
    XYAreaRenderer r=(XYAreaRenderer)p.getRenderer();
    r.setSeriesPaint(0,new Color(51,102,255));
    r.setSeriesPaint(1,new Color(255,80,80));
    r.setSeriesPaint(2,new Color(0,170,120));
    r.setForegroundAlpha(0.45f);
}

}
