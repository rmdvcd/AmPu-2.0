/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package Utiles;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.TableCellRenderer;

/**
 *
 * @author 666
 
 */
public class GestionEncabezadoTabla implements TableCellRenderer{
 private final Font bold;
 String[] binomialTabla={"x","n","p","P(X=x)","P(X≤x)","P(X≥x)","Media","Varianza"};
    String[] binomialNTabla={"x","r","p","P(X=x)","Media","Varianza"};
    String[] multinomialTabla={"x","p"};
    String[] geometricaTabla={"x","p","P(X=x)","Media","Varianza"};
    String[] hipergeometricaTabla={"x","N","n","k","P(X=x)","P(X≤x)","P(X≥x)","Media","Varianza"};
    String[] poissonTabla={"x","λ","P(X=x)","P(X≤x)","P(X≥x)"};
    String[] uniformeTabla={"x","A","B","Valor p","Media","T","f(x)"};
    String[] finitoTabla={"N","α","p","d","Submuestra n"};
    String[] finitoTabla2={ "Selección"};
    String[] infinitoTabla={"α","p","d","Submuestra n"};
    String[] estratificadoTabla={"Nh","nh"};

    public GestionEncabezadoTabla() {
        this.bold = new Font("Verdana",Font.BOLD,12);
    }
    public String[] getD1(){
        return this.binomialTabla;
    }
    public String[] getD2(){
        return this.binomialNTabla;
    }
    public String[] getD3(){
    return this.multinomialTabla;    
    }
    public String[] getD4(){
    return this.geometricaTabla;    
    }
    public String[] getD5(){
    return this.hipergeometricaTabla;    
    }
    public String[] getD6(){
    return this.poissonTabla;    
    }
    public String[] getC1(){
    return this.uniformeTabla;    
    }
    public String[] getMF1(){
    return this.finitoTabla;    
    }
    public String[] getMF2(){
    return this.finitoTabla2;   
    }
    public String[] getMI(){
    return this.infinitoTabla;    
    }
    public String[] getME1(){
    return this.estratificadoTabla;    
    }
@Override
public Component getTableCellRendererComponent(JTable table,Object value,boolean isSelected,boolean hasFocus,int row,int column){
JComponent jc=null;
if(value instanceof String){
    jc=new JLabel((String) value);
    ((JLabel) jc).setHorizontalAlignment(SwingConstants.CENTER);
    jc.setOpaque(true);
    jc.setBorder(javax.swing.BorderFactory.createMatteBorder(0, 0, 1, 1, Color.black));
    jc.setFont(bold);
    jc.setBackground(new Color(51,102,255));
    jc.setForeground(Color.white);
}
    return jc;
}
}
