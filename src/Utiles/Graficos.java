package Utiles;



/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



import javax.swing.JPanel;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
/**
 *
 * @author 666
 */
public class Graficos {
JFreeChart graficaD;
JFreeChart graficaA; 
XYSeriesCollection datos=new XYSeriesCollection();
String titulo;
String etiquetax;
String etiquetay;
public Graficos(String t,String x,String y){
 titulo=t;
 etiquetax=x;
 etiquetay=y;
 graficaD=ChartFactory.createScatterPlot(titulo, x, y, datos);
 graficaA=ChartFactory.createXYAreaChart(t, x, y, datos, PlotOrientation.VERTICAL, true, true, true);
}
public Graficos(){
     this(null, "x", "y");
 }
public void crearGrafica(String id,double[] x,double[] y){
datos.removeAllSeries();
addGrafica(id,x,y);
}
public void addGrafica(String id,double[] x,double[] y){
XYSeries s=new XYSeries(id);
int n=x.length;
for(int i=0;i<n;i++){
s.add(x[i],y[i]);
}
datos.addSeries(s);   
}
public void limpiar(){
    datos.removeAllSeries();
}
public JPanel getGraficaA(){
return new ChartPanel(graficaA);   
}
public JPanel getGraficaD(){
return new ChartPanel(graficaD);   
}

}
