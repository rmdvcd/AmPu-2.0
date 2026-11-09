package Utiles;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import javax.swing.JTable;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;


/**
 *
 * @author 666
 */
public class ExportarE {
Workbook wb;  

    public ExportarE() {
    }
public String exportar(File archivo,JTable tabla,String tipo){
String mensaje="No se pudo guardar el documento";
int numFila=tabla.getRowCount();
int numColumnas=tabla.getColumnCount();
wb=new XSSFWorkbook();
Sheet hoja=wb.createSheet(tipo);
    try {
        for(int i=-1;i<numFila;i++){
            hoja.createRow(i+1);
            for(int j=0;j<numColumnas;j++){
            hoja.getRow(i+1).createCell(j);
            if(i==-1)
            hoja.getRow(i+1).getCell(j).setCellValue(tabla.getColumnName(j));
            else
            hoja.getRow(i+1).getCell(j).setCellValue(String.valueOf(tabla.getValueAt(i, j)));  
            }
            wb.write(new FileOutputStream(archivo+".xlsx"));
        }
        mensaje="Guardado con éxito";
    } catch (IOException e) {
    }
return mensaje;
}
}
