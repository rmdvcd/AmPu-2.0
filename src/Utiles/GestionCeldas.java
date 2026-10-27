/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package Utiles;

import java.awt.Component;
import java.awt.Font;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.table.DefaultTableCellRenderer;

/**
 *
 * @author 666
 */
public class GestionCeldas extends DefaultTableCellRenderer{
private String tipo=null;
private final Font normal;
public GestionCeldas(){
        this.normal = new Font("Verdana",Font.PLAIN,12);
}
public GestionCeldas(String tipo){
        this.normal = new Font("Verdana",Font.PLAIN,12);
this.tipo=tipo;   
}
@Override
public Component getTableCellRendererComponent(JTable table,Object value,boolean selected,boolean focused,int row,int column){
if(tipo.equals("numerico")){
this.setHorizontalAlignment(JLabel.CENTER);
this.setText((String) value);
this.setFont(normal);
}
return this;
}

}
