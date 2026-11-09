package Utiles;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



import javax.swing.table.DefaultTableModel;
/**
 *
 * @author 666
 */
public class ModeloTabla extends DefaultTableModel{
String[] titulos;
String[][] datos;
boolean edit;
/**
* @param datos
 * @param titulos
*/
public ModeloTabla(String[][] datos,String[] titulos){
super();
this.datos=datos;
this.titulos=titulos;
setDataVector(datos,titulos);
edit=false;
}
public ModeloTabla(){
    
}
public void tabla(){
edit=true;
}
@Override
public boolean isCellEditable(int column,int row){
 return edit;   
}

}

