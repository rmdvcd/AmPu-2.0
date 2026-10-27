package visual;



/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



import Clases.Funciones;
import Utiles.ExportarE;
import Utiles.GestionCeldas;
import Utiles.GestionEncabezadoTabla;
import Utiles.Graficos;
import Utiles.ModeloTabla;
import Utiles.Parsear;
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.ImageIcon;
import javax.swing.JEditorPane;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import javax.swing.*;
import java.awt.event.*;
import visual.creditos;
/**
 *
 * @author 666
 */
public class Interfaz extends javax.swing.JFrame{
    /**
     * Creates new form Interfaz
     */
    Funciones f=new Funciones();
    JFrame jf=new JFrame();
    JEditorPane panel=new JEditorPane();
    Parsear parse=new Parsear();
    JFrame cred=new creditos();
    GestionEncabezadoTabla GET=new GestionEncabezadoTabla();
    public Interfaz() {
        initComponents();
        ImageIcon imagen1 = new ImageIcon(getClass().getResource("/ImgVisual/icono_ampu.png"));
        this.setIconImage(imagen1.getImage());
    }
    public double redondeo(double x){
        return Math.rint(x*10000)/10000;
    }
    public void lineasTabla(JTable tabla){
        tabla.setShowHorizontalLines(true);
        tabla.setShowVerticalLines(true);
    }
    public JTableHeader encabezado(JTable tabla){
    JTableHeader jh=tabla.getTableHeader();
    jh.setDefaultRenderer(new GestionEncabezadoTabla()); 
    return jh;
    }
    public void componentesTabla(JTable table){
        for(int i=0;i<table.getModel().getColumnCount();i++){
           System.out.println(i);
           table.getColumnModel().getColumn(i).setCellRenderer(new GestionCeldas("numerico"));
        }
    }
    public void limpiarTabla(JTable tabla){
                DefaultTableModel temp=(DefaultTableModel) tabla.getModel();
        int aux=tabla.getModel().getRowCount();
        int c=aux;
        if(aux>0){
            for(int i=0;i<aux;i++){
                temp.removeRow(c-1);
                c--;
            }
            tabla.setModel(temp);
        }else{
            JOptionPane.showMessageDialog(null, "No hay filas q eliminar", null, JOptionPane.ERROR_MESSAGE);
        }
    }
    public void limpiarTabla2(JTable tabla){
         DefaultTableModel temp=(DefaultTableModel) tabla.getModel();
        for(int i=0;i<tabla.getRowCount();i++){
            for(int j=0;j<tabla.getColumnCount();j++){
                temp.setValueAt(null, i, j);
            }
        }
        componentesTabla(tabla);
    }
    public void lessFila(JTable tabla){
         int aux=tabla.getModel().getRowCount();
        DefaultTableModel temp=(DefaultTableModel) tabla.getModel();
        if(aux>0){
            temp.removeRow(aux-1);
            tabla.setModel(temp);
            componentesTabla(tabla);
        }else{
            JOptionPane.showMessageDialog(null, "No hay filas q eliminar", null, JOptionPane.ERROR_MESSAGE);
        }       
    }
    public void teoria(URL url){
    try {
           if(panel.getPage()!=url) {
            ImageIcon imagen2 = new ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_32.png"));
            jf.setIconImage(imagen2.getImage());
            jf.remove(panel);
            panel.setPage(url);
            jf.add(panel);
            jf.setSize(this.getWidth()/2, this.getHeight()/2);
            jf.setTitle("Elementos teóricos");
            jf.setResizable(false);
            jf.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            jf.setLocationRelativeTo(this);
            jf.setVisible(true);
           }else{
               jf.repaint();
           }
        } catch (IOException ex) {
            Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
        }    
    }
    public void iniciarParseador(){
    parse.defBinomialVp();
    parse.defBinomialVpMayor();
    parse.defBinomialVpMenor();
    parse.defBinomialNVp();
    parse.defMultinomialVp();
    parse.defGeometricaVp();
    parse.defHipergeometricaVp();
    parse.defHipergeometricaVpMayor();
    parse.defHipergeometricaVpMenor();
    parse.defPoissonVp();
    parse.defPoissonVpMayor();
    parse.defPoissonVpMenor();
    parse.defUniformeF();
    parse.defNormalF();
    parse.defJiF();
    parse.defExpF();
    parse.defTstudentF();
    parse.defFisherF();
    }
    public void exportar(JTable tabla,String tipo){
    ExportarE ge=new ExportarE();
JFileChooser selA=new JFileChooser();
File archivo;
selA.setFileFilter(new FileNameExtensionFilter("Excel (*.xls)","xls"));
selA.setFileFilter(new FileNameExtensionFilter("Excel (*.xlsx)","xlsx"));
if(tabla.getModel().getRowCount()==0)
    JOptionPane.showMessageDialog(null, "La tabla esta vacia");
else{
    if(selA.showSaveDialog(this)==JFileChooser.APPROVE_OPTION){ 
        if(selA.getSelectedFile()!=null){
         archivo=selA.getSelectedFile();
         JOptionPane.showMessageDialog(null, ge.exportar(archivo, tabla, tipo));
        }
      }
     }
    }
    public void graficar(Graficos grafica,double[] xx,double[] yy, String P){
    grafica.crearGrafica(P, xx, yy);
    }
    public void addgrafica(Graficos grafica,double[] xx,double[] yy, String P){
    grafica.addGrafica(P, xx, yy);
    }
    public double[] arreglo(double x){
    double[] xx=new double[(int) x*10];
    double temp=0;
    for(int  i=0;i<xx.length;i++){
    xx[i]=temp;
    temp+=0.1;
    }
    return xx;
    }
  public void validarN(java.awt.event.KeyEvent evt){
      char car = evt.getKeyChar();
        if((car<'0' || car>'9') && (car<',' || car>'.')) 
            evt.consume();
  }
  public void validarC(JTable tabla){
      JTextField textBox=new JTextField();
      tabla.setRowHeight(25);
      textBox.addKeyListener(new KeyAdapter(){
@Override
public void keyTyped(KeyEvent e)
{
if(!Character.isDigit(e.getKeyChar()) && e.getKeyChar() !=KeyEvent.VK_BACK_SPACE&&e.getKeyChar()!=','&&e.getKeyChar()!='.')
    e.consume();
}
});
      int cont=tabla.getColumnCount();
      for(int i=0;i<cont;i++){
          tabla.getColumnModel().getColumn(i).setCellEditor(new DefaultCellEditor (textBox));
      }
      
  }
    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        Func = new javax.swing.JTabbedPane();
        D_Dis = new javax.swing.JTabbedPane();
        Panel_Bino = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        DDBTabla = new javax.swing.JTable();
        DDBmodo = new javax.swing.JComboBox();
        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();
        DDBentX = new javax.swing.JTextField();
        DDBentN = new javax.swing.JTextField();
        DDBentP = new javax.swing.JTextField();
        DDBsalVp = new javax.swing.JLabel();
        DDBsalM = new javax.swing.JLabel();
        DDBsalV = new javax.swing.JLabel();
        DDBcalc = new javax.swing.JButton();
        DDBLcampos = new javax.swing.JButton();
        DDBLtabla = new javax.swing.JButton();
        DDBlessfila = new javax.swing.JButton();
        DDBTbimonialN = new javax.swing.JButton();
        DDBCexcel = new javax.swing.JButton();
        DDB_Grafico = graficaDDB.getGraficaD();
        Panel_Bino_Neg = new javax.swing.JPanel();
        jLabel5 = new javax.swing.JLabel();
        DDBNentX = new javax.swing.JTextField();
        DDBNLcampos = new javax.swing.JButton();
        DDBNentR = new javax.swing.JTextField();
        jLabel6 = new javax.swing.JLabel();
        DDBNentP = new javax.swing.JTextField();
        jLabel70 = new javax.swing.JLabel();
        DDBNcalc = new javax.swing.JButton();
        DDBNsalVp = new javax.swing.JLabel();
        DDBNsalM = new javax.swing.JLabel();
        DDBNsalV = new javax.swing.JLabel();
        jScrollPane12 = new javax.swing.JScrollPane();
        DDBNTabla = new javax.swing.JTable();
        DDBNCexcel = new javax.swing.JButton();
        DDBNLtabla = new javax.swing.JButton();
        DDBNlessfila = new javax.swing.JButton();
        DDBNTbimonialN = new javax.swing.JButton();
        jLabel71 = new javax.swing.JLabel();
        DDBN_Grafico = graficaDDBN.getGraficaD();
        Panel_Multino = new javax.swing.JPanel();
        jScrollPane2 = new javax.swing.JScrollPane();
        DDMTabla = new javax.swing.JTable();
        jLabel7 = new javax.swing.JLabel();
        DDMVpsal = new javax.swing.JLabel();
        DDMLtabla = new javax.swing.JButton();
        DDMAddTabla = new javax.swing.JButton();
        DDMLessTabla = new javax.swing.JButton();
        DDMCalc = new javax.swing.JButton();
        DDMTeoria = new javax.swing.JButton();
        DDM_Grafico = graficaDDM.getGraficaD();
        Panel_Geo = new javax.swing.JPanel();
        jLabel8 = new javax.swing.JLabel();
        jLabel10 = new javax.swing.JLabel();
        DDGCalc = new javax.swing.JButton();
        DDGsalVp = new javax.swing.JLabel();
        DDGsalM = new javax.swing.JLabel();
        DDGsalV = new javax.swing.JLabel();
        DDGentX = new javax.swing.JTextField();
        DDGentP = new javax.swing.JTextField();
        DDGLcampos = new javax.swing.JButton();
        DDGTgeo = new javax.swing.JButton();
        jLabel14 = new javax.swing.JLabel();
        jScrollPane11 = new javax.swing.JScrollPane();
        DDGTabla = new javax.swing.JTable();
        DDGLessfila = new javax.swing.JButton();
        DDGLtabla = new javax.swing.JButton();
        DDGCexcel = new javax.swing.JButton();
        DDG_Grafico = graficaDDG.getGraficaD();
        Panel_Hipergeo = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        DDHTabla = new javax.swing.JTable();
        DDHmodo = new javax.swing.JComboBox();
        jLabel11 = new javax.swing.JLabel();
        jLabel12 = new javax.swing.JLabel();
        jLabel13 = new javax.swing.JLabel();
        DDHentX = new javax.swing.JTextField();
        DDHentN = new javax.swing.JTextField();
        DDHentn = new javax.swing.JTextField();
        DDHsalVp = new javax.swing.JLabel();
        DDHsalM = new javax.swing.JLabel();
        DDHsalV = new javax.swing.JLabel();
        DDHcalc = new javax.swing.JButton();
        DDHLcampos = new javax.swing.JButton();
        DDHLtabla = new javax.swing.JButton();
        DDHlessfila = new javax.swing.JButton();
        DDHThiper = new javax.swing.JButton();
        jLabel17 = new javax.swing.JLabel();
        DDHentK = new javax.swing.JTextField();
        DDH_Grafico = graficaDDH.getGraficaD();
        DDHCexcel = new javax.swing.JButton();
        Panel_Poisson = new javax.swing.JPanel();
        jLabel15 = new javax.swing.JLabel();
        jLabel16 = new javax.swing.JLabel();
        DDPCalc = new javax.swing.JButton();
        DDPsalVp = new javax.swing.JLabel();
        DDPentX = new javax.swing.JTextField();
        DDPentLanda = new javax.swing.JTextField();
        DDPLcampos = new javax.swing.JButton();
        DDPTpoisson = new javax.swing.JButton();
        DDPmodo = new javax.swing.JComboBox();
        jScrollPane4 = new javax.swing.JScrollPane();
        DDPTabla = new javax.swing.JTable();
        DDPLtabla = new javax.swing.JButton();
        DDPlessfila = new javax.swing.JButton();
        DDPLtabla1 = new javax.swing.JButton();
        DDP_Grafico = graficaDDP.getGraficaD();
        D_Con = new javax.swing.JTabbedPane();
        Panel_UCont = new javax.swing.JPanel();
        jScrollPane5 = new javax.swing.JScrollPane();
        DCUTabla = new javax.swing.JTable();
        jLabel18 = new javax.swing.JLabel();
        jLabel19 = new javax.swing.JLabel();
        jLabel20 = new javax.swing.JLabel();
        DCUentX = new javax.swing.JTextField();
        DCUentA = new javax.swing.JTextField();
        DCUentB = new javax.swing.JTextField();
        DCUsalVp = new javax.swing.JLabel();
        DCUsalM = new javax.swing.JLabel();
        DCUsalDesv = new javax.swing.JLabel();
        DCUcalc = new javax.swing.JButton();
        DCULcampos = new javax.swing.JButton();
        DCULtabla = new javax.swing.JButton();
        DCUlessfila = new javax.swing.JButton();
        DCUTuniformec = new javax.swing.JButton();
        DCUsalF = new javax.swing.JLabel();
        DCU_Cexcel = new javax.swing.JButton();
        DCU_Grafico = graficaDCU.getGraficaA();
        DCU_AIvp = new javax.swing.JComboBox();
        Panel_NEst = new javax.swing.JPanel();
        jLabel26 = new javax.swing.JLabel();
        DCNentZ = new javax.swing.JTextField();
        DCNcalcp = new javax.swing.JButton();
        DCNsalVp = new javax.swing.JLabel();
        DCNLcamposz = new javax.swing.JButton();
        DCNTnormal = new javax.swing.JButton();
        jLabel29 = new javax.swing.JLabel();
        DCNentP = new javax.swing.JTextField();
        DCNLcamposp = new javax.swing.JButton();
        DCNcalcx = new javax.swing.JButton();
        DCNsalVz = new javax.swing.JLabel();
        jSeparator2 = new javax.swing.JSeparator();
        DCN_Grafico = graficaDCN.getGraficaA();
        DCN_guia = new javax.swing.JLabel();
        jSeparator1 = new javax.swing.JSeparator();
        DCN_AIvp = new javax.swing.JComboBox();
        DCN_AIvz = new javax.swing.JComboBox();
        Panel_ChiCuad = new javax.swing.JPanel();
        DCCLcampos1 = new javax.swing.JButton();
        jLabel27 = new javax.swing.JLabel();
        DCCLcamposp2 = new javax.swing.JButton();
        DCCcalcx = new javax.swing.JButton();
        DCCcalcp = new javax.swing.JButton();
        DCCentV2 = new javax.swing.JTextField();
        DCCTchicuadrado = new javax.swing.JButton();
        DCCentV1 = new javax.swing.JTextField();
        jLabel30 = new javax.swing.JLabel();
        jLabel31 = new javax.swing.JLabel();
        DCCentX = new javax.swing.JTextField();
        jLabel32 = new javax.swing.JLabel();
        DCCentP = new javax.swing.JTextField();
        DCCsalVp = new javax.swing.JLabel();
        DCCsalX = new javax.swing.JLabel();
        jSeparator4 = new javax.swing.JSeparator();
        DCC_AIvp = new javax.swing.JComboBox();
        DCC_AIvx = new javax.swing.JComboBox();
        jSeparator3 = new javax.swing.JSeparator();
        DCC_Grafico = graficaDCC.getGraficaA();
        Panel_Expo = new javax.swing.JPanel();
        DCEentX = new javax.swing.JTextField();
        DCEentLanda1 = new javax.swing.JTextField();
        jLabel34 = new javax.swing.JLabel();
        DCEcalcp = new javax.swing.JButton();
        DCEsalVp = new javax.swing.JLabel();
        jLabel35 = new javax.swing.JLabel();
        DCELcampos1 = new javax.swing.JButton();
        DCETexponencial = new javax.swing.JButton();
        DCEsalX = new javax.swing.JLabel();
        jLabel36 = new javax.swing.JLabel();
        DCEentLanda2 = new javax.swing.JTextField();
        DCEcalcx = new javax.swing.JButton();
        DCELcampos2 = new javax.swing.JButton();
        DCEentP = new javax.swing.JTextField();
        jLabel37 = new javax.swing.JLabel();
        jSeparator6 = new javax.swing.JSeparator();
        DCE_AIvp = new javax.swing.JComboBox();
        jSeparator5 = new javax.swing.JSeparator();
        DCE_AIvx = new javax.swing.JComboBox();
        DCE_Grafico = graficaDCE.getGraficaA();
        Panel_FFisher = new javax.swing.JPanel();
        jLabel39 = new javax.swing.JLabel();
        DCFLcampos1 = new javax.swing.JButton();
        DCFentV1 = new javax.swing.JTextField();
        DCFsalVp = new javax.swing.JLabel();
        DCFentV2 = new javax.swing.JTextField();
        jLabel40 = new javax.swing.JLabel();
        DCFentX = new javax.swing.JTextField();
        jLabel42 = new javax.swing.JLabel();
        jLabel44 = new javax.swing.JLabel();
        DCFsalVx = new javax.swing.JLabel();
        DCFentV3 = new javax.swing.JTextField();
        DCFLcampos2 = new javax.swing.JButton();
        DCFentV4 = new javax.swing.JTextField();
        jLabel43 = new javax.swing.JLabel();
        DCFentP = new javax.swing.JTextField();
        DCFTfisher = new javax.swing.JButton();
        DCFcalcx = new javax.swing.JButton();
        DCFcalcp = new javax.swing.JButton();
        jSeparator7 = new javax.swing.JSeparator();
        jLabel69 = new javax.swing.JLabel();
        DCF_AIvp = new javax.swing.JComboBox();
        DCF_AIvx = new javax.swing.JComboBox();
        jSeparator8 = new javax.swing.JSeparator();
        DCF_Grafico = graficaDCF.getGraficaA();
        Panel_TStudent = new javax.swing.JPanel();
        jSeparator15 = new javax.swing.JSeparator();
        jLabel45 = new javax.swing.JLabel();
        jLabel46 = new javax.swing.JLabel();
        DCTsalVp = new javax.swing.JLabel();
        DCTentX = new javax.swing.JTextField();
        DCTentV1 = new javax.swing.JTextField();
        DCTcalcp = new javax.swing.JButton();
        jLabel47 = new javax.swing.JLabel();
        jLabel48 = new javax.swing.JLabel();
        DCTentP = new javax.swing.JTextField();
        DCTentV2 = new javax.swing.JTextField();
        DCTcalcx = new javax.swing.JButton();
        DCTsalX = new javax.swing.JLabel();
        DCTLcampos1 = new javax.swing.JButton();
        DCTLcampos2 = new javax.swing.JButton();
        DCTTstudent = new javax.swing.JButton();
        DCT_AIvp = new javax.swing.JComboBox();
        DCT_AIvx = new javax.swing.JComboBox();
        jSeparator9 = new javax.swing.JSeparator();
        DCT_Grafico = graficaDCT.getGraficaA();
        Muest = new javax.swing.JTabbedPane();
        Panel_ASFinito = new javax.swing.JPanel();
        jSeparator10 = new javax.swing.JSeparator();
        jScrollPane6 = new javax.swing.JScrollPane();
        MASFTabla1 = new javax.swing.JTable();
        jLabel21 = new javax.swing.JLabel();
        MASFentN = new javax.swing.JTextField();
        jLabel22 = new javax.swing.JLabel();
        MASFentA = new javax.swing.JTextField();
        jLabel23 = new javax.swing.JLabel();
        MASFentP = new javax.swing.JTextField();
        jLabel50 = new javax.swing.JLabel();
        MASFentD = new javax.swing.JTextField();
        MASFcalc = new javax.swing.JButton();
        MASFsaln = new javax.swing.JLabel();
        jLabel52 = new javax.swing.JLabel();
        MASFTfinito = new javax.swing.JButton();
        MASFLcampos1 = new javax.swing.JButton();
        MASFentN1 = new javax.swing.JTextField();
        jLabel53 = new javax.swing.JLabel();
        MASFentn = new javax.swing.JTextField();
        jLabel54 = new javax.swing.JLabel();
        MASFLcampos2 = new javax.swing.JButton();
        jLabel55 = new javax.swing.JLabel();
        jScrollPane7 = new javax.swing.JScrollPane();
        MASFTabla2 = new javax.swing.JTable();
        MASFselec = new javax.swing.JButton();
        MASFLtabla = new javax.swing.JButton();
        MASFlessfila = new javax.swing.JButton();
        MASFCexcel = new javax.swing.JButton();
        MASFCexcel2 = new javax.swing.JButton();
        Panel_ASInfinito = new javax.swing.JPanel();
        jScrollPane8 = new javax.swing.JScrollPane();
        MASITabla = new javax.swing.JTable();
        MASIentA = new javax.swing.JTextField();
        MASIsaln = new javax.swing.JLabel();
        MASIentD = new javax.swing.JTextField();
        MASIentP = new javax.swing.JTextField();
        jLabel57 = new javax.swing.JLabel();
        jLabel58 = new javax.swing.JLabel();
        jLabel59 = new javax.swing.JLabel();
        MASILcampos = new javax.swing.JButton();
        MASITinfinnito = new javax.swing.JButton();
        MASILTabla = new javax.swing.JButton();
        MASILessfila = new javax.swing.JButton();
        MASIcalc = new javax.swing.JButton();
        MASICexcel = new javax.swing.JButton();
        Panel_Estrat = new javax.swing.JPanel();
        jScrollPane9 = new javax.swing.JScrollPane();
        MASETabla = new javax.swing.JTable();
        MASELTabla = new javax.swing.JButton();
        MASEAddE = new javax.swing.JButton();
        MASELessE = new javax.swing.JButton();
        MASETestratificado = new javax.swing.JButton();
        MASEentn = new javax.swing.JTextField();
        jLabel61 = new javax.swing.JLabel();
        MASEcalc = new javax.swing.JButton();
        jMenuBar1 = new javax.swing.JMenuBar();
        M_archivo = new javax.swing.JMenu();
        M_cerrar = new javax.swing.JMenuItem();
        M_herramientas = new javax.swing.JMenu();
        M_calculadora = new javax.swing.JMenuItem();
        M_TPantalla = new javax.swing.JMenuItem();
        M_soporte = new javax.swing.JMenu();
        jMenuItem1 = new javax.swing.JMenuItem();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setTitle("AmPu 2.0");
        setIconImage(getIconImage());
        setResizable(false);
        addWindowListener(new java.awt.event.WindowAdapter() {
            public void windowOpened(java.awt.event.WindowEvent evt) {
                formWindowOpened(evt);
            }
        });

        Func.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N

        D_Dis.setTabPlacement(javax.swing.JTabbedPane.LEFT);
        D_Dis.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N

        DDBTabla.setAutoCreateRowSorter(true);
        DDBTabla.setModel(new ModeloTabla(null,this.GET.getD1()));
        DDBTabla.setColumnSelectionAllowed(true);
        DDBTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDBTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDBTabla.setTableHeader(this.encabezado(this.DDBTabla)
        );
        jScrollPane1.setViewportView(DDBTabla);
        DDBTabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        DDBmodo.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBmodo.setMaximumRowCount(4);
        DDBmodo.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X=x)", "P(X≤x)", "P(X≥x)" }));
        DDBmodo.setToolTipText("Modo de p");
        DDBmodo.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        jLabel1.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel1.setText("x :");

        jLabel2.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel2.setText("n :");

        jLabel3.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel3.setText("p :");

        DDBentX.setToolTipText("Introducir valores enteros positivos,x<=n");
        DDBentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBentXKeyTyped(evt);
            }
        });

        DDBentN.setToolTipText("Introducir valores enteros positivos");
        DDBentN.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBentNKeyTyped(evt);
            }
        });

        DDBentP.setToolTipText("Introducir valores entre 0 y 1");
        DDBentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBentPKeyTyped(evt);
            }
        });

        DDBsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBsalVp.setText("Valor p :");

        DDBsalM.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBsalM.setText("Media :");

        DDBsalV.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBsalV.setText("Varianza :");

        DDBcalc.setText("Calcular");
        DDBcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBcalcActionPerformed(evt);
            }
        });

        DDBLcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDBLcampos.setToolTipText("Limpiar campos");
        DDBLcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBLcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBLcamposActionPerformed(evt);
            }
        });

        DDBLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDBLtabla.setToolTipText("Limpiar tabla");
        DDBLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBLtablaActionPerformed(evt);
            }
        });

        DDBlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDBlessfila.setToolTipText("Eliminar fila");
        DDBlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBlessfilaActionPerformed(evt);
            }
        });

        DDBTbimonialN.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDBTbimonialN.setToolTipText("Teoria");
        DDBTbimonialN.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBTbimonialN.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBTbimonialNActionPerformed(evt);
            }
        });

        DDBCexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DDBCexcel.setToolTipText("Guardar");
        DDBCexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBCexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBCexcelActionPerformed(evt);
            }
        });

        DDB_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDB_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDB_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DDB_GraficoLayout = new javax.swing.GroupLayout(DDB_Grafico);
        DDB_Grafico.setLayout(DDB_GraficoLayout);
        DDB_GraficoLayout.setHorizontalGroup(
            DDB_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DDB_GraficoLayout.setVerticalGroup(
            DDB_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 390, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_BinoLayout = new javax.swing.GroupLayout(Panel_Bino);
        Panel_Bino.setLayout(Panel_BinoLayout);
        Panel_BinoLayout.setHorizontalGroup(
            Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_BinoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDBmodo, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_BinoLayout.createSequentialGroup()
                        .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel1)
                            .addComponent(jLabel2)
                            .addComponent(jLabel3))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDBcalc)
                            .addGroup(Panel_BinoLayout.createSequentialGroup()
                                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                                    .addComponent(DDBentX, javax.swing.GroupLayout.DEFAULT_SIZE, 60, Short.MAX_VALUE)
                                    .addComponent(DDBentN)
                                    .addComponent(DDBentP))
                                .addGap(19, 19, 19)
                                .addComponent(DDBLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))
                    .addComponent(DDBsalM)
                    .addComponent(DDBsalVp)
                    .addComponent(DDBsalV))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 143, Short.MAX_VALUE)
                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDB_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 640, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDBTbimonialN, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDBLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(DDBlessfila, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addComponent(DDBCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        Panel_BinoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDBLcampos, DDBLtabla, DDBTbimonialN, DDBlessfila});

        Panel_BinoLayout.setVerticalGroup(
            Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_BinoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_BinoLayout.createSequentialGroup()
                        .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDBTbimonialN, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_BinoLayout.createSequentialGroup()
                                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addGroup(Panel_BinoLayout.createSequentialGroup()
                                        .addComponent(DDBmodo, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addGap(18, 18, 18)
                                        .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                            .addComponent(jLabel1)
                                            .addComponent(DDBentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                                    .addComponent(DDBLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(12, 12, 12)
                                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel2)
                                    .addComponent(DDBentN, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel3)
                                    .addComponent(DDBentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DDBcalc)
                                .addGap(14, 14, 14)
                                .addComponent(DDBsalVp)
                                .addGap(11, 11, 11)
                                .addComponent(DDBsalM)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DDBsalV)))
                        .addGap(0, 123, Short.MAX_VALUE))
                    .addComponent(DDB_Grafico, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 394, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_BinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 139, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_BinoLayout.createSequentialGroup()
                        .addComponent(DDBCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDBLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDBlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        Panel_BinoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDBLcampos, DDBLtabla, DDBTbimonialN, DDBlessfila});

        D_Dis.addTab("Binomial", Panel_Bino);

        jLabel5.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel5.setText("x :");

        DDBNentX.setToolTipText("Introducir valores enteros positivos");
        DDBNentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBNentXKeyTyped(evt);
            }
        });

        DDBNLcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDBNLcampos.setToolTipText("Limpiar campos");
        DDBNLcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNLcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNLcamposActionPerformed(evt);
            }
        });

        DDBNentR.setToolTipText("Introducir valores enteros positivos");
        DDBNentR.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBNentRKeyTyped(evt);
            }
        });

        jLabel6.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel6.setText("r :");

        DDBNentP.setToolTipText("Introducir valores entre 0 y 1");
        DDBNentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDBNentPKeyTyped(evt);
            }
        });

        jLabel70.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel70.setText("p :");

        DDBNcalc.setText("Calcular");
        DDBNcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNcalcActionPerformed(evt);
            }
        });

        DDBNsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBNsalVp.setText("Valor p :");

        DDBNsalM.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBNsalM.setText("Media :");

        DDBNsalV.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDBNsalV.setText("Varianza :");

        DDBNTabla.setAutoCreateRowSorter(true);
        DDBNTabla.setModel(new ModeloTabla(null,this.GET.getD2()));
        DDBNTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDBNTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDBNTabla.setTableHeader(this.encabezado(this.DDBNTabla)
        );
        jScrollPane12.setViewportView(DDBNTabla);
        DDBNTabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        DDBNCexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DDBNCexcel.setToolTipText("Guardar");
        DDBNCexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNCexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNCexcelActionPerformed(evt);
            }
        });

        DDBNLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDBNLtabla.setToolTipText("Limpiar tabla");
        DDBNLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNLtablaActionPerformed(evt);
            }
        });

        DDBNlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDBNlessfila.setToolTipText("Eliminar fila");
        DDBNlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNlessfilaActionPerformed(evt);
            }
        });

        DDBNTbimonialN.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDBNTbimonialN.setToolTipText("Teoria");
        DDBNTbimonialN.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDBNTbimonialN.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDBNTbimonialNActionPerformed(evt);
            }
        });

        jLabel71.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel71.setText("P(X=x)");
        jLabel71.setToolTipText("Modo de p");

        DDBN_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDBN_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDBN_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DDBN_GraficoLayout = new javax.swing.GroupLayout(DDBN_Grafico);
        DDBN_Grafico.setLayout(DDBN_GraficoLayout);
        DDBN_GraficoLayout.setHorizontalGroup(
            DDBN_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DDBN_GraficoLayout.setVerticalGroup(
            DDBN_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_Bino_NegLayout = new javax.swing.GroupLayout(Panel_Bino_Neg);
        Panel_Bino_Neg.setLayout(Panel_Bino_NegLayout);
        Panel_Bino_NegLayout.setHorizontalGroup(
            Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                        .addGap(19, 19, 19)
                        .addComponent(DDBNcalc))
                    .addComponent(DDBNsalM)
                    .addComponent(DDBNsalVp)
                    .addComponent(DDBNsalV)
                    .addComponent(jLabel71)
                    .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel5)
                            .addComponent(jLabel6)
                            .addComponent(jLabel70))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(DDBNentX)
                            .addComponent(DDBNentR)
                            .addComponent(DDBNentP, javax.swing.GroupLayout.PREFERRED_SIZE, 60, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(19, 19, 19)
                        .addComponent(DDBNLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(143, 143, 143)
                .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane12, javax.swing.GroupLayout.PREFERRED_SIZE, 640, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(DDBN_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDBNLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(DDBNlessfila, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addComponent(DDBNCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DDBNTbimonialN, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        Panel_Bino_NegLayout.setVerticalGroup(
            Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                        .addContainerGap()
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel71)
                            .addComponent(DDBNTbimonialN, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(16, 16, 16)
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                .addComponent(jLabel5)
                                .addComponent(DDBNentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addComponent(DDBNLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(12, 12, 12)
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel6)
                            .addComponent(DDBNentR, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel70)
                            .addComponent(DDBNentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DDBNcalc)
                        .addGap(14, 14, 14)
                        .addComponent(DDBNsalVp)
                        .addGap(11, 11, 11)
                        .addComponent(DDBNsalM)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DDBNsalV)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_Bino_NegLayout.createSequentialGroup()
                        .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DDBN_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)))
                .addGroup(Panel_Bino_NegLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane12, javax.swing.GroupLayout.PREFERRED_SIZE, 142, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_Bino_NegLayout.createSequentialGroup()
                        .addComponent(DDBNCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDBNLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDBNlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        D_Dis.addTab("Binomial Negativa", Panel_Bino_Neg);

        DDMTabla.setModel(new ModeloTabla(null,this.GET.getD3()));
        DDMTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDMTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDMTabla.setTableHeader(this.encabezado(this.DDMTabla)
        );
        DDMTabla.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDMTablaKeyTyped(evt);
            }
        });
        jScrollPane2.setViewportView(DDMTabla);

        jLabel7.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel7.setText("P(X=x)");
        jLabel7.setToolTipText("Modo de p");

        DDMVpsal.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDMVpsal.setText("Valor p :");

        DDMLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDMLtabla.setToolTipText("Limpiar tabla");
        DDMLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDMLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDMLtablaActionPerformed(evt);
            }
        });

        DDMAddTabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/add.png"))); // NOI18N
        DDMAddTabla.setToolTipText("Agregar fila");
        DDMAddTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDMAddTabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDMAddTablaActionPerformed(evt);
            }
        });

        DDMLessTabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDMLessTabla.setToolTipText("Eliminar fila");
        DDMLessTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDMLessTabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDMLessTablaActionPerformed(evt);
            }
        });

        DDMCalc.setText("Calcular");
        DDMCalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDMCalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDMCalcActionPerformed(evt);
            }
        });

        DDMTeoria.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDMTeoria.setToolTipText("Teoria");
        DDMTeoria.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDMTeoria.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDMTeoriaActionPerformed(evt);
            }
        });

        DDM_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDM_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDM_Grafico.setPreferredSize(new java.awt.Dimension(62, 395));

        javax.swing.GroupLayout DDM_GraficoLayout = new javax.swing.GroupLayout(DDM_Grafico);
        DDM_Grafico.setLayout(DDM_GraficoLayout);
        DDM_GraficoLayout.setHorizontalGroup(
            DDM_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 619, Short.MAX_VALUE)
        );
        DDM_GraficoLayout.setVerticalGroup(
            DDM_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_MultinoLayout = new javax.swing.GroupLayout(Panel_Multino);
        Panel_Multino.setLayout(Panel_MultinoLayout);
        Panel_MultinoLayout.setHorizontalGroup(
            Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_MultinoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addComponent(jLabel7)
                        .addGap(36, 36, 36)
                        .addComponent(DDMCalc)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 772, Short.MAX_VALUE)
                        .addComponent(DDMTeoria, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addGap(6, 6, 6)
                        .addGroup(Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDMVpsal, javax.swing.GroupLayout.PREFERRED_SIZE, 216, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_MultinoLayout.createSequentialGroup()
                                .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 216, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DDMLessTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DDMAddTabla, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DDMLtabla, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(21, 21, 21)
                                .addComponent(DDM_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, 623, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );

        Panel_MultinoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDMAddTabla, DDMLessTabla, DDMLtabla});

        Panel_MultinoLayout.setVerticalGroup(
            Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_MultinoLayout.createSequentialGroup()
                .addGroup(Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addGap(15, 15, 15)
                        .addComponent(DDMTeoria, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addGap(18, 18, 18)
                        .addComponent(DDMCalc, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jLabel7)))
                .addGap(8, 8, 8)
                .addGroup(Panel_MultinoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_MultinoLayout.createSequentialGroup()
                        .addComponent(DDMLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDMAddTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDMLessTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DDM_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 435, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(DDMVpsal, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(23, Short.MAX_VALUE))
        );

        Panel_MultinoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDMAddTabla, DDMLessTabla, DDMLtabla});

        D_Dis.addTab("Multinomial", Panel_Multino);

        jLabel8.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel8.setText("x :");

        jLabel10.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel10.setText("p :");

        DDGCalc.setText("Calcular");
        DDGCalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGCalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGCalcActionPerformed(evt);
            }
        });

        DDGsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDGsalVp.setText("Valor p :");

        DDGsalM.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDGsalM.setText("Media :");

        DDGsalV.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDGsalV.setText("Varianza :");

        DDGentX.setToolTipText("Valores enteros positivos");
        DDGentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDGentXKeyTyped(evt);
            }
        });

        DDGentP.setToolTipText("Valores entre 0 y 1");
        DDGentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDGentPKeyTyped(evt);
            }
        });

        DDGLcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDGLcampos.setToolTipText("Limpiar campos");
        DDGLcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGLcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGLcamposActionPerformed(evt);
            }
        });

        DDGTgeo.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDGTgeo.setToolTipText("Teoria");
        DDGTgeo.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGTgeo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGTgeoActionPerformed(evt);
            }
        });

        jLabel14.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel14.setText("P(X=x)");
        jLabel14.setToolTipText("Modo de p");

        DDGTabla.setModel(new ModeloTabla(null,this.GET.getD4()));
        DDGTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDGTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDGTabla.setTableHeader(this.encabezado(this.DDGTabla)
        );
        jScrollPane11.setViewportView(DDGTabla);

        DDGLessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDGLessfila.setToolTipText("Eliminar fila");
        DDGLessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGLessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGLessfilaActionPerformed(evt);
            }
        });

        DDGLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDGLtabla.setToolTipText("Limpiar tabla");
        DDGLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGLtablaActionPerformed(evt);
            }
        });

        DDGCexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DDGCexcel.setToolTipText("Guardar");
        DDGCexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDGCexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDGCexcelActionPerformed(evt);
            }
        });

        DDG_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDG_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDG_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DDG_GraficoLayout = new javax.swing.GroupLayout(DDG_Grafico);
        DDG_Grafico.setLayout(DDG_GraficoLayout);
        DDG_GraficoLayout.setHorizontalGroup(
            DDG_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DDG_GraficoLayout.setVerticalGroup(
            DDG_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_GeoLayout = new javax.swing.GroupLayout(Panel_Geo);
        Panel_Geo.setLayout(Panel_GeoLayout);
        Panel_GeoLayout.setHorizontalGroup(
            Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_GeoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                    .addComponent(jLabel14, javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, Panel_GeoLayout.createSequentialGroup()
                        .addGap(19, 19, 19)
                        .addComponent(DDGCalc))
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, Panel_GeoLayout.createSequentialGroup()
                        .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addGroup(Panel_GeoLayout.createSequentialGroup()
                                .addComponent(jLabel8)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DDGentX, javax.swing.GroupLayout.PREFERRED_SIZE, 55, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_GeoLayout.createSequentialGroup()
                                .addComponent(jLabel10)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addComponent(DDGentP, javax.swing.GroupLayout.PREFERRED_SIZE, 55, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DDGLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DDGsalM, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(DDGsalVp, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(DDGsalV, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 161, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 113, Short.MAX_VALUE)
                .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(DDG_Grafico, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jScrollPane11))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDGTgeo, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addComponent(DDGLessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DDGLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DDGCexcel, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        Panel_GeoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDGLcampos, DDGTgeo});

        Panel_GeoLayout.setVerticalGroup(
            Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_GeoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_GeoLayout.createSequentialGroup()
                        .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel14)
                            .addComponent(DDGTgeo, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(27, 27, 27)
                        .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDGLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                .addComponent(jLabel8)
                                .addComponent(DDGentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addGap(18, 18, 18)
                        .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel10)
                            .addComponent(DDGentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDGCalc)
                        .addGap(30, 30, 30)
                        .addComponent(DDGsalVp)
                        .addGap(18, 18, 18)
                        .addComponent(DDGsalM)
                        .addGap(18, 18, 18)
                        .addComponent(DDGsalV))
                    .addComponent(DDG_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(Panel_GeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_GeoLayout.createSequentialGroup()
                        .addComponent(DDGCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDGLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDGLessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jScrollPane11, javax.swing.GroupLayout.PREFERRED_SIZE, 139, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        Panel_GeoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDGLcampos, DDGTgeo});

        D_Dis.addTab("Geométrica", Panel_Geo);

        DDHTabla.setAutoCreateRowSorter(true);
        DDHTabla.setModel(new ModeloTabla(null,this.GET.getD5()));
        DDHTabla.setColumnSelectionAllowed(true);
        DDHTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDHTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDHTabla.setTableHeader(this.encabezado(this.DDHTabla)
        );
        jScrollPane3.setViewportView(DDHTabla);
        DDHTabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        DDHmodo.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDHmodo.setMaximumRowCount(4);
        DDHmodo.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X=x)", "P(X≤x)", "P(X≥x)" }));
        DDHmodo.setToolTipText("Modo de p");
        DDHmodo.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        jLabel11.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel11.setText("x :");

        jLabel12.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel12.setText("N :");

        jLabel13.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel13.setText("n :");

        DDHentX.setToolTipText("Introducir valores enteros positivos");
        DDHentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDHentXKeyTyped(evt);
            }
        });

        DDHentN.setToolTipText("Valores enteros positivos,N>x,N>n,N>k,N>=n+k");
        DDHentN.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDHentNKeyTyped(evt);
            }
        });

        DDHentn.setToolTipText("Valores enteros positivos,n>=x");
        DDHentn.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDHentnKeyTyped(evt);
            }
        });

        DDHsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDHsalVp.setText("Valor p :");

        DDHsalM.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDHsalM.setText("Media :");

        DDHsalV.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDHsalV.setText("Varianza :");

        DDHcalc.setText("Calcular");
        DDHcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHcalcActionPerformed(evt);
            }
        });

        DDHLcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDHLcampos.setToolTipText("Limpiar campos");
        DDHLcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHLcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHLcamposActionPerformed(evt);
            }
        });

        DDHLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDHLtabla.setToolTipText("Limpiar tabla");
        DDHLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHLtablaActionPerformed(evt);
            }
        });

        DDHlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDHlessfila.setToolTipText("Eliminar fila");
        DDHlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHlessfilaActionPerformed(evt);
            }
        });

        DDHThiper.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDHThiper.setToolTipText("Teoria");
        DDHThiper.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHThiper.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHThiperActionPerformed(evt);
            }
        });

        jLabel17.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel17.setText("k :");

        DDHentK.setToolTipText("Valores enteros positivos,k>=x");
        DDHentK.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDHentKKeyTyped(evt);
            }
        });

        DDH_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDH_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDH_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DDH_GraficoLayout = new javax.swing.GroupLayout(DDH_Grafico);
        DDH_Grafico.setLayout(DDH_GraficoLayout);
        DDH_GraficoLayout.setHorizontalGroup(
            DDH_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DDH_GraficoLayout.setVerticalGroup(
            DDH_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        DDHCexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DDHCexcel.setToolTipText("Guardar");
        DDHCexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDHCexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDHCexcelActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout Panel_HipergeoLayout = new javax.swing.GroupLayout(Panel_Hipergeo);
        Panel_Hipergeo.setLayout(Panel_HipergeoLayout);
        Panel_HipergeoLayout.setHorizontalGroup(
            Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDHsalVp)
                    .addComponent(DDHsalM)
                    .addComponent(DDHsalV)
                    .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                        .addComponent(jLabel17)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDHentK))
                    .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel11)
                            .addComponent(jLabel12)
                            .addComponent(jLabel13))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(DDHentX, javax.swing.GroupLayout.DEFAULT_SIZE, 60, Short.MAX_VALUE)
                            .addComponent(DDHentN)
                            .addComponent(DDHentn))
                        .addGap(18, 18, 18)
                        .addComponent(DDHLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DDHcalc)
                    .addComponent(DDHmodo, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(143, 143, 143)
                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane3)
                    .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                        .addGap(0, 0, Short.MAX_VALUE)
                        .addComponent(DDH_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addComponent(DDHlessfila, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DDHThiper, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DDHCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(DDHLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        Panel_HipergeoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDHLcampos, DDHLtabla, DDHThiper, DDHlessfila});

        Panel_HipergeoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDHentK, DDHentN, DDHentX, DDHentn});

        Panel_HipergeoLayout.setVerticalGroup(
            Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDH_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                                .addComponent(DDHmodo, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(18, 18, 18)
                                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel11)
                                    .addComponent(DDHentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                            .addComponent(DDHLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(12, 12, 12)
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel12)
                            .addComponent(DDHentN, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel13)
                            .addComponent(DDHentn, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel17)
                            .addComponent(DDHentK, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDHcalc)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DDHsalVp)
                        .addGap(12, 12, 12)
                        .addComponent(DDHsalM)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DDHsalV))
                    .addComponent(DDHThiper, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_HipergeoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE)
                    .addGroup(Panel_HipergeoLayout.createSequentialGroup()
                        .addComponent(DDHCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDHLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDHlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );

        Panel_HipergeoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDHLcampos, DDHLtabla, DDHThiper, DDHlessfila});

        Panel_HipergeoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDHentK, DDHentN, DDHentX, DDHentn});

        D_Dis.addTab("Hipergeométrica", Panel_Hipergeo);

        jLabel15.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel15.setText("x :");

        jLabel16.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel16.setText("λ :");

        DDPCalc.setText("Calcular");
        DDPCalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPCalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPCalcActionPerformed(evt);
            }
        });

        DDPsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDPsalVp.setText("Valor p :");

        DDPentX.setToolTipText("Valores enteros positivos");
        DDPentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDPentXKeyTyped(evt);
            }
        });

        DDPentLanda.setToolTipText("Valores positivos");
        DDPentLanda.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DDPentLandaKeyTyped(evt);
            }
        });

        DDPLcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDPLcampos.setToolTipText("Limpiar campos");
        DDPLcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPLcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPLcamposActionPerformed(evt);
            }
        });

        DDPTpoisson.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DDPTpoisson.setToolTipText("Teoria");
        DDPTpoisson.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPTpoisson.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPTpoissonActionPerformed(evt);
            }
        });

        DDPmodo.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DDPmodo.setMaximumRowCount(4);
        DDPmodo.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X=x)", "P(X≤x)", "P(X≥x)" }));
        DDPmodo.setToolTipText("Modo de p");
        DDPmodo.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DDPTabla.setModel(new ModeloTabla(null,this.GET.getD6()));
        DDPTabla.setColumnSelectionAllowed(true);
        DDPTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DDPTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DDPTabla.setTableHeader(this.encabezado(this.DDPTabla));
        jScrollPane4.setViewportView(DDPTabla);
        DDPTabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        DDPLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DDPLtabla.setToolTipText("Limpiar tabla");
        DDPLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPLtablaActionPerformed(evt);
            }
        });

        DDPlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DDPlessfila.setToolTipText("Eliminar fila");
        DDPlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPlessfilaActionPerformed(evt);
            }
        });

        DDPLtabla1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DDPLtabla1.setToolTipText("Guardar");
        DDPLtabla1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DDPLtabla1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DDPLtabla1ActionPerformed(evt);
            }
        });

        DDP_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DDP_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DDP_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DDP_GraficoLayout = new javax.swing.GroupLayout(DDP_Grafico);
        DDP_Grafico.setLayout(DDP_GraficoLayout);
        DDP_GraficoLayout.setHorizontalGroup(
            DDP_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DDP_GraficoLayout.setVerticalGroup(
            DDP_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_PoissonLayout = new javax.swing.GroupLayout(Panel_Poisson);
        Panel_Poisson.setLayout(Panel_PoissonLayout);
        Panel_PoissonLayout.setHorizontalGroup(
            Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_PoissonLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_PoissonLayout.createSequentialGroup()
                        .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel16, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(jLabel15, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DDPCalc)
                            .addComponent(DDPentLanda, javax.swing.GroupLayout.PREFERRED_SIZE, 55, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_PoissonLayout.createSequentialGroup()
                                .addComponent(DDPentX, javax.swing.GroupLayout.PREFERRED_SIZE, 55, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DDPLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))
                    .addComponent(DDPsalVp)
                    .addComponent(DDPmodo, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(161, 161, 161)
                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jScrollPane4)
                    .addComponent(DDP_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DDPTpoisson, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(DDPLtabla1, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addComponent(DDPlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DDPLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        Panel_PoissonLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DDPLcampos, DDPLtabla, DDPTpoisson, DDPlessfila});

        Panel_PoissonLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {jLabel15, jLabel16});

        Panel_PoissonLayout.setVerticalGroup(
            Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_PoissonLayout.createSequentialGroup()
                .addGap(8, 8, 8)
                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                        .addGroup(Panel_PoissonLayout.createSequentialGroup()
                            .addComponent(DDPmodo, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(DDPentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(jLabel15))
                                .addComponent(DDPLcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                .addComponent(jLabel16, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addComponent(DDPentLanda, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(DDPCalc)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                            .addComponent(DDPsalVp)
                            .addGap(228, 228, 228))
                        .addGroup(Panel_PoissonLayout.createSequentialGroup()
                            .addComponent(DDPTpoisson, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 373, Short.MAX_VALUE)))
                    .addGroup(Panel_PoissonLayout.createSequentialGroup()
                        .addComponent(DDP_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)))
                .addGroup(Panel_PoissonLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 140, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_PoissonLayout.createSequentialGroup()
                        .addComponent(DDPLtabla1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(5, 5, 5)
                        .addComponent(DDPLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DDPlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(267, 267, 267))
        );

        Panel_PoissonLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DDPLcampos, DDPLtabla, DDPTpoisson, DDPlessfila});

        Panel_PoissonLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {jLabel15, jLabel16});

        D_Dis.addTab("Poisson", Panel_Poisson);

        Func.addTab("Distribuciones Discretas", D_Dis);

        D_Con.setTabPlacement(javax.swing.JTabbedPane.LEFT);
        D_Con.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N

        DCUTabla.setAutoCreateRowSorter(true);
        DCUTabla.setModel(new ModeloTabla(null,this.GET.getC1()));
        DCUTabla.setColumnSelectionAllowed(true);
        DCUTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        DCUTabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        DCUTabla.setTableHeader(this.encabezado(this.DCUTabla)
        );
        jScrollPane5.setViewportView(DCUTabla);
        DCUTabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        jLabel18.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel18.setText("x :");

        jLabel19.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel19.setText("A :");

        jLabel20.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel20.setText("B :");

        DCUentX.setToolTipText("Introducir valores enteros positivos");
        DCUentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCUentXKeyTyped(evt);
            }
        });

        DCUentA.setToolTipText("Introducir valores enteros positivos, A<=x.");
        DCUentA.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCUentAKeyTyped(evt);
            }
        });

        DCUentB.setToolTipText("Introducir valores enteros positivos,B>=x.");
        DCUentB.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCUentBKeyTyped(evt);
            }
        });

        DCUsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCUsalVp.setText("Valor p :");

        DCUsalM.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCUsalM.setText("Media :");

        DCUsalDesv.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCUsalDesv.setText("T :");

        DCUcalc.setText("Calcular");
        DCUcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCUcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCUcalcActionPerformed(evt);
            }
        });

        DCULcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCULcampos.setToolTipText("Limpiar campos");
        DCULcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCULcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCULcamposActionPerformed(evt);
            }
        });

        DCULtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCULtabla.setToolTipText("Limpiar tabla");
        DCULtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCULtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCULtablaActionPerformed(evt);
            }
        });

        DCUlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        DCUlessfila.setToolTipText("Eliminar fila");
        DCUlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCUlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCUlessfilaActionPerformed(evt);
            }
        });

        DCUTuniformec.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCUTuniformec.setToolTipText("Teoria");
        DCUTuniformec.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCUTuniformec.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCUTuniformecActionPerformed(evt);
            }
        });

        DCUsalF.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCUsalF.setText("f(x) =");

        DCU_Cexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        DCU_Cexcel.setToolTipText("Guardar");
        DCU_Cexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCU_Cexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCU_CexcelActionPerformed(evt);
            }
        });

        DCU_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCU_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCU_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCU_GraficoLayout = new javax.swing.GroupLayout(DCU_Grafico);
        DCU_Grafico.setLayout(DCU_GraficoLayout);
        DCU_GraficoLayout.setHorizontalGroup(
            DCU_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCU_GraficoLayout.setVerticalGroup(
            DCU_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        DCU_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCU_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCU_AIvp.setToolTipText("Area de integracion");
        DCU_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        javax.swing.GroupLayout Panel_UContLayout = new javax.swing.GroupLayout(Panel_UCont);
        Panel_UCont.setLayout(Panel_UContLayout);
        Panel_UContLayout.setHorizontalGroup(
            Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_UContLayout.createSequentialGroup()
                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_UContLayout.createSequentialGroup()
                        .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DCUcalc)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addGroup(Panel_UContLayout.createSequentialGroup()
                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_UContLayout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCUsalVp, javax.swing.GroupLayout.PREFERRED_SIZE, 140, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DCUsalF)
                                    .addComponent(DCUsalM, javax.swing.GroupLayout.PREFERRED_SIZE, 140, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DCUsalDesv)))
                            .addGroup(Panel_UContLayout.createSequentialGroup()
                                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, Panel_UContLayout.createSequentialGroup()
                                        .addContainerGap()
                                        .addComponent(DCU_AIvp, 0, 80, Short.MAX_VALUE))
                                    .addGroup(Panel_UContLayout.createSequentialGroup()
                                        .addGap(6, 6, 6)
                                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                            .addComponent(jLabel18, javax.swing.GroupLayout.Alignment.TRAILING)
                                            .addComponent(jLabel19, javax.swing.GroupLayout.Alignment.TRAILING)
                                            .addComponent(jLabel20, javax.swing.GroupLayout.Alignment.TRAILING))
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                                            .addComponent(DCUentX, javax.swing.GroupLayout.DEFAULT_SIZE, 60, Short.MAX_VALUE)
                                            .addComponent(DCUentA)
                                            .addComponent(DCUentB))))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCULcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 130, Short.MAX_VALUE)))
                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jScrollPane5)
                    .addComponent(DCU_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DCUTuniformec, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addComponent(DCUlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DCULtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(DCU_Cexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        Panel_UContLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCULtabla, DCUTuniformec, DCUlessfila});

        Panel_UContLayout.setVerticalGroup(
            Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_UContLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DCU_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_UContLayout.createSequentialGroup()
                        .addComponent(DCUTuniformec, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(16, 16, 16)
                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                .addComponent(jLabel18)
                                .addComponent(DCUentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addComponent(DCULcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(12, 12, 12)
                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel19)
                            .addComponent(DCUentA, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel20)
                            .addComponent(DCUentB, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCUcalc)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCUsalVp)
                        .addGap(12, 12, 12)
                        .addComponent(DCUsalM)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DCUsalDesv)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DCUsalF))
                    .addComponent(DCU_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(Panel_UContLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane5, javax.swing.GroupLayout.PREFERRED_SIZE, 137, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_UContLayout.createSequentialGroup()
                        .addComponent(DCU_Cexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCULtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCUlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(20, 20, 20))
        );

        Panel_UContLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DCULtabla, DCUTuniformec, DCUlessfila});

        D_Con.addTab("Uniforme Continua", Panel_UCont);

        jLabel26.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel26.setText("Valor z :");

        DCNentZ.setToolTipText("Valores entre -4 y 4.");
        DCNentZ.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCNentZKeyTyped(evt);
            }
        });

        DCNcalcp.setText("Calcular");
        DCNcalcp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCNcalcp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCNcalcpActionPerformed(evt);
            }
        });

        DCNsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCNsalVp.setText("Valor p :");

        DCNLcamposz.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCNLcamposz.setToolTipText("Limpiar campos");
        DCNLcamposz.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCNLcamposz.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCNLcamposzActionPerformed(evt);
            }
        });

        DCNTnormal.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCNTnormal.setToolTipText("Teoria");
        DCNTnormal.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCNTnormal.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCNTnormalActionPerformed(evt);
            }
        });

        jLabel29.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel29.setText("Valor p :");

        DCNentP.setToolTipText("Valores entre 0 y 1.");
        DCNentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCNentPKeyTyped(evt);
            }
        });

        DCNLcamposp.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCNLcamposp.setToolTipText("Limpiar campos");
        DCNLcamposp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCNLcamposp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCNLcampospActionPerformed(evt);
            }
        });

        DCNcalcx.setText("Calcular");
        DCNcalcx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCNcalcx.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCNcalcxActionPerformed(evt);
            }
        });

        DCNsalVz.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCNsalVz.setText("Valor z :");

        jSeparator2.setOrientation(javax.swing.SwingConstants.VERTICAL);

        DCN_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCN_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCN_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCN_GraficoLayout = new javax.swing.GroupLayout(DCN_Grafico);
        DCN_Grafico.setLayout(DCN_GraficoLayout);
        DCN_GraficoLayout.setHorizontalGroup(
            DCN_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCN_GraficoLayout.setVerticalGroup(
            DCN_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        DCN_guia.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N

        DCN_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCN_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCN_AIvp.setToolTipText("Area de integracion");
        DCN_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCN_AIvz.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCN_AIvz.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "X<x", "X>x" }));
        DCN_AIvz.setToolTipText("Area de integracion");
        DCN_AIvz.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        javax.swing.GroupLayout Panel_NEstLayout = new javax.swing.GroupLayout(Panel_NEst);
        Panel_NEst.setLayout(Panel_NEstLayout);
        Panel_NEstLayout.setHorizontalGroup(
            Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_NEstLayout.createSequentialGroup()
                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addGap(48, 48, 48)
                        .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCNsalVz)
                            .addGroup(Panel_NEstLayout.createSequentialGroup()
                                .addComponent(jLabel29)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCNcalcx)
                                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                                        .addComponent(DCNentP, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(DCNLcamposp, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))
                            .addComponent(DCNsalVp)
                            .addGroup(Panel_NEstLayout.createSequentialGroup()
                                .addComponent(jLabel26)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                                        .addComponent(DCNentZ, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(DCNLcamposz, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCNcalcp)))))
                    .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, 237, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(DCN_AIvz, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(DCN_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator2, javax.swing.GroupLayout.PREFERRED_SIZE, 2, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addGap(37, 37, 37)
                        .addComponent(DCN_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap(39, Short.MAX_VALUE))
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addGap(340, 340, 340)
                        .addComponent(DCN_guia, javax.swing.GroupLayout.PREFERRED_SIZE, 111, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DCNTnormal, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap())))
        );

        Panel_NEstLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCNLcamposp, DCNLcamposz, DCNTnormal});

        Panel_NEstLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCN_AIvp, DCN_AIvz});

        Panel_NEstLayout.setVerticalGroup(
            Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_NEstLayout.createSequentialGroup()
                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jSeparator2))
                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                        .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_NEstLayout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(DCN_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(26, 26, 26)
                                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel26)
                                        .addComponent(DCNentZ, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCNLcamposz, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(12, 12, 12)
                                .addComponent(DCNcalcp)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCNsalVp)
                                .addGap(106, 106, 106)
                                .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCN_AIvz, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(39, 39, 39)
                                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCNLcamposp, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel29)
                                        .addComponent(DCNentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCNcalcx)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCNsalVz))
                            .addGroup(Panel_NEstLayout.createSequentialGroup()
                                .addGroup(Panel_NEstLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                                        .addContainerGap()
                                        .addComponent(DCNTnormal, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addGroup(Panel_NEstLayout.createSequentialGroup()
                                        .addGap(25, 25, 25)
                                        .addComponent(DCN_guia, javax.swing.GroupLayout.PREFERRED_SIZE, 26, javax.swing.GroupLayout.PREFERRED_SIZE)))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCN_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addGap(0, 87, Short.MAX_VALUE)))
                .addContainerGap())
        );

        Panel_NEstLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {DCNLcamposp, DCNLcamposz, DCNTnormal});

        D_Con.addTab("Normal Estándar", Panel_NEst);

        DCCLcampos1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCCLcampos1.setToolTipText("Limpiar campos");
        DCCLcampos1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCCLcampos1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCLcampos1ActionPerformed(evt);
            }
        });

        jLabel27.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel27.setText("Grados de libertad :");

        DCCLcamposp2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCCLcamposp2.setToolTipText("Limpiar campos");
        DCCLcamposp2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCCLcamposp2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCLcamposp2ActionPerformed(evt);
            }
        });

        DCCcalcx.setText("Calcular");
        DCCcalcx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCCcalcx.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCcalcxActionPerformed(evt);
            }
        });

        DCCcalcp.setText("Calcular");
        DCCcalcp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCCcalcp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCcalcpActionPerformed(evt);
            }
        });

        DCCentV2.setToolTipText("Valores entre 1 y 30.");
        DCCentV2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCentV2ActionPerformed(evt);
            }
        });
        DCCentV2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCCentV2KeyTyped(evt);
            }
        });

        DCCTchicuadrado.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCCTchicuadrado.setToolTipText("Teoria");
        DCCTchicuadrado.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCCTchicuadrado.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCCTchicuadradoActionPerformed(evt);
            }
        });

        DCCentV1.setToolTipText("Valores entre 1 y 30.");
        DCCentV1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCCentV1KeyTyped(evt);
            }
        });

        jLabel30.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel30.setText("Grados de libertad :");

        jLabel31.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel31.setText("x :");

        DCCentX.setToolTipText("Valores entre 0 y 60.");
        DCCentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCCentXKeyTyped(evt);
            }
        });

        jLabel32.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel32.setText("p :");

        DCCentP.setToolTipText("Valores entre 0 y 1.");
        DCCentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCCentPKeyTyped(evt);
            }
        });

        DCCsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCCsalVp.setText("Valor p :");

        DCCsalX.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCCsalX.setText("Valor x :");

        jSeparator4.setOrientation(javax.swing.SwingConstants.VERTICAL);

        DCC_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCC_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCC_AIvp.setToolTipText("Area de integracion");
        DCC_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCC_AIvx.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCC_AIvx.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "X<x", "X>x" }));
        DCC_AIvx.setToolTipText("Area de integracion");
        DCC_AIvx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCC_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCC_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCC_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCC_GraficoLayout = new javax.swing.GroupLayout(DCC_Grafico);
        DCC_Grafico.setLayout(DCC_GraficoLayout);
        DCC_GraficoLayout.setHorizontalGroup(
            DCC_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCC_GraficoLayout.setVerticalGroup(
            DCC_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_ChiCuadLayout = new javax.swing.GroupLayout(Panel_ChiCuad);
        Panel_ChiCuad.setLayout(Panel_ChiCuadLayout);
        Panel_ChiCuadLayout.setHorizontalGroup(
            Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                        .addContainerGap()
                        .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(jLabel27, javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(jLabel31, javax.swing.GroupLayout.Alignment.TRAILING))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(DCCentX, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, Panel_ChiCuadLayout.createSequentialGroup()
                                        .addComponent(DCCentV1, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(DCCLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCCcalcp, javax.swing.GroupLayout.Alignment.LEADING)))
                            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(DCCsalX, javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                                        .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                            .addComponent(jLabel30, javax.swing.GroupLayout.Alignment.TRAILING)
                                            .addComponent(jLabel32, javax.swing.GroupLayout.Alignment.TRAILING))
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                        .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                            .addComponent(DCCentV2, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                            .addComponent(DCCentP, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCCLcamposp2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                                .addGap(116, 116, 116)
                                .addComponent(DCCcalcx))
                            .addComponent(DCC_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                .addComponent(DCC_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addComponent(DCCsalVp))))
                    .addComponent(jSeparator3))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                        .addGap(680, 680, 680)
                        .addComponent(DCCTchicuadrado, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                        .addGap(39, 39, 39)
                        .addComponent(DCC_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );

        Panel_ChiCuadLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCC_AIvp, DCC_AIvx});

        Panel_ChiCuadLayout.setVerticalGroup(
            Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                        .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCCTchicuadrado, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                                .addComponent(DCC_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(15, 15, 15)
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel27)
                                        .addComponent(DCCentV1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCCLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel31)
                                    .addComponent(DCCentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCCcalcp)
                                .addGap(12, 12, 12)
                                .addComponent(DCCsalVp)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 88, Short.MAX_VALUE)
                        .addComponent(jSeparator3, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(26, 26, 26)
                        .addComponent(DCC_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_ChiCuadLayout.createSequentialGroup()
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCCentV2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DCCLcamposp2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_ChiCuadLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(DCCentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(jLabel32)))
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_ChiCuadLayout.createSequentialGroup()
                                .addComponent(jLabel30)
                                .addGap(44, 44, 44)))
                        .addComponent(DCCcalcx)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCCsalX)
                        .addGap(114, 114, 114))
                    .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                        .addComponent(jSeparator4)
                        .addContainerGap())))
            .addGroup(Panel_ChiCuadLayout.createSequentialGroup()
                .addGap(63, 63, 63)
                .addComponent(DCC_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(0, 0, Short.MAX_VALUE))
        );

        D_Con.addTab("Chi Cuadrada", Panel_ChiCuad);

        DCEentX.setToolTipText("Valores enteros positivos");
        DCEentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCEentXKeyTyped(evt);
            }
        });

        DCEentLanda1.setToolTipText("Valores mayores que 0.");
        DCEentLanda1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCEentLanda1KeyTyped(evt);
            }
        });

        jLabel34.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel34.setText("λ :");

        DCEcalcp.setText("Calcular");
        DCEcalcp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCEcalcp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCEcalcpActionPerformed(evt);
            }
        });

        DCEsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCEsalVp.setText("Valor p :");

        jLabel35.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel35.setText("Valor x :");

        DCELcampos1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCELcampos1.setToolTipText("Limpiar campos");
        DCELcampos1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCELcampos1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCELcampos1ActionPerformed(evt);
            }
        });

        DCETexponencial.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCETexponencial.setToolTipText("Teoria");
        DCETexponencial.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCETexponencial.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCETexponencialActionPerformed(evt);
            }
        });

        DCEsalX.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCEsalX.setText("Valor x :");

        jLabel36.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel36.setText("λ :");

        DCEentLanda2.setToolTipText("Valores mayores que 0.");
        DCEentLanda2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCEentLanda2KeyTyped(evt);
            }
        });

        DCEcalcx.setText("Calcular");
        DCEcalcx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCEcalcx.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCEcalcxActionPerformed(evt);
            }
        });

        DCELcampos2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCELcampos2.setToolTipText("Limpiar campos");
        DCELcampos2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCELcampos2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCELcampos2ActionPerformed(evt);
            }
        });

        DCEentP.setToolTipText("Valores entre 0 y 1.");
        DCEentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCEentPKeyTyped(evt);
            }
        });

        jLabel37.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel37.setText("Valor p :");

        jSeparator6.setOrientation(javax.swing.SwingConstants.VERTICAL);

        DCE_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCE_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCE_AIvp.setToolTipText("Area de integracion");
        DCE_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCE_AIvx.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCE_AIvx.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "X<x", "X>x" }));
        DCE_AIvx.setToolTipText("Area de integracion");
        DCE_AIvx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCE_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCE_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCE_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCE_GraficoLayout = new javax.swing.GroupLayout(DCE_Grafico);
        DCE_Grafico.setLayout(DCE_GraficoLayout);
        DCE_GraficoLayout.setHorizontalGroup(
            DCE_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCE_GraficoLayout.setVerticalGroup(
            DCE_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_ExpoLayout = new javax.swing.GroupLayout(Panel_Expo);
        Panel_Expo.setLayout(Panel_ExpoLayout);
        Panel_ExpoLayout.setHorizontalGroup(
            Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(DCE_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                .addComponent(jLabel35)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEentX, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_ExpoLayout.createSequentialGroup()
                                .addComponent(jLabel34)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEentLanda1, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCELcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGap(52, 52, 52)
                        .addComponent(DCEcalcp))
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGap(2, 2, 2)
                        .addComponent(DCEsalVp))
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                .addComponent(jLabel36)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEentLanda2, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                .addComponent(jLabel37)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEentP, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DCELcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DCEsalX)
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGap(52, 52, 52)
                        .addComponent(DCEcalcx))
                    .addComponent(DCE_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jSeparator5, javax.swing.GroupLayout.PREFERRED_SIZE, 229, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DCETexponencial, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap())
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGap(37, 37, 37)
                        .addComponent(DCE_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap(41, Short.MAX_VALUE))))
        );

        Panel_ExpoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCE_AIvp, DCE_AIvx});

        Panel_ExpoLayout.setVerticalGroup(
            Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addComponent(jSeparator6)
                        .addContainerGap())
                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCETexponencial, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(DCE_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                .addGap(32, 32, 32)
                                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCELcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                            .addComponent(jLabel35)
                                            .addComponent(DCEentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                        .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                            .addComponent(jLabel34)
                                            .addComponent(DCEentLanda1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEcalcp)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEsalVp)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 74, Short.MAX_VALUE)
                                .addComponent(jSeparator5, javax.swing.GroupLayout.PREFERRED_SIZE, 2, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCE_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(18, 18, 18)
                                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCELcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(DCEentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel37)))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_ExpoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(DCEentLanda2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(jLabel36))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCEcalcx)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCEsalX)
                                .addGap(117, 117, 117))
                            .addGroup(Panel_ExpoLayout.createSequentialGroup()
                                .addGap(31, 31, 31)
                                .addComponent(DCE_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))))))
        );

        D_Con.addTab("Exponencial", Panel_Expo);

        jLabel39.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel39.setText("Grados de libertad(n) :");

        DCFLcampos1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCFLcampos1.setToolTipText("Limpiar campos");
        DCFLcampos1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCFLcampos1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCFLcampos1ActionPerformed(evt);
            }
        });

        DCFentV1.setToolTipText("Valores entre 1 y 120.");
        DCFentV1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentV1KeyTyped(evt);
            }
        });

        DCFsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCFsalVp.setText("Valor p :");

        DCFentV2.setToolTipText("Valores entre 1 y 120.");
        DCFentV2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentV2KeyTyped(evt);
            }
        });

        jLabel40.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel40.setText("Grados de libertad(d) :");

        DCFentX.setToolTipText("Valores enteros entre 0 y 1500.");
        DCFentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentXKeyTyped(evt);
            }
        });

        jLabel42.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel42.setText("Grados de libertad(n) :");

        jLabel44.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel44.setText("Valor p :");

        DCFsalVx.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCFsalVx.setText("Valor x :");

        DCFentV3.setToolTipText("Valores entre 1 y 120.");
        DCFentV3.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentV3KeyTyped(evt);
            }
        });

        DCFLcampos2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCFLcampos2.setToolTipText("Limpiar campos");
        DCFLcampos2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCFLcampos2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCFLcampos2ActionPerformed(evt);
            }
        });

        DCFentV4.setToolTipText("Valores entre 1 y 120.");
        DCFentV4.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentV4KeyTyped(evt);
            }
        });

        jLabel43.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel43.setText("Grados de libertad(d) :");

        DCFentP.setToolTipText("Valores entre 0 y 1.");
        DCFentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCFentPKeyTyped(evt);
            }
        });

        DCFTfisher.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCFTfisher.setToolTipText("Teoria");
        DCFTfisher.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCFTfisher.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCFTfisherActionPerformed(evt);
            }
        });

        DCFcalcx.setText("Calcular");
        DCFcalcx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCFcalcx.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCFcalcxActionPerformed(evt);
            }
        });

        DCFcalcp.setText("Calcular");
        DCFcalcp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCFcalcp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCFcalcpActionPerformed(evt);
            }
        });

        jSeparator7.setOrientation(javax.swing.SwingConstants.VERTICAL);

        jLabel69.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel69.setText("Valor x :");

        DCF_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCF_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCF_AIvp.setToolTipText("Area de integracion");
        DCF_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCF_AIvx.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCF_AIvx.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "X<x", "X>x" }));
        DCF_AIvx.setToolTipText("Area de integracion");
        DCF_AIvx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCF_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCF_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCF_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCF_GraficoLayout = new javax.swing.GroupLayout(DCF_Grafico);
        DCF_Grafico.setLayout(DCF_GraficoLayout);
        DCF_GraficoLayout.setHorizontalGroup(
            DCF_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCF_GraficoLayout.setVerticalGroup(
            DCF_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_FFisherLayout = new javax.swing.GroupLayout(Panel_FFisher);
        Panel_FFisher.setLayout(Panel_FFisherLayout);
        Panel_FFisherLayout.setHorizontalGroup(
            Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_FFisherLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addGroup(Panel_FFisherLayout.createSequentialGroup()
                            .addComponent(jLabel69)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(DCFentX, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGroup(Panel_FFisherLayout.createSequentialGroup()
                            .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                .addComponent(DCFcalcp)
                                .addComponent(jLabel40))
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(DCFentV2, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addComponent(jLabel39)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCFentV1, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DCFLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(DCF_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(DCFsalVp)
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addComponent(jLabel42)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCFentV3, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(DCFLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addGroup(Panel_FFisherLayout.createSequentialGroup()
                            .addComponent(jLabel43)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(DCFentV4, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCFcalcx)
                            .addGroup(Panel_FFisherLayout.createSequentialGroup()
                                .addComponent(jLabel44)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCFentP, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))))
                    .addComponent(DCFsalVx)
                    .addComponent(DCF_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jSeparator8))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator7, javax.swing.GroupLayout.PREFERRED_SIZE, 2, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DCFTfisher, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap())
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addGap(23, 23, 23)
                        .addComponent(DCF_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap(40, Short.MAX_VALUE))))
        );

        Panel_FFisherLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCF_AIvp, DCF_AIvx});

        Panel_FFisherLayout.setVerticalGroup(
            Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_FFisherLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addComponent(jSeparator7)
                        .addContainerGap())
                    .addGroup(Panel_FFisherLayout.createSequentialGroup()
                        .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCFTfisher, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(DCF_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_FFisherLayout.createSequentialGroup()
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel39)
                                        .addComponent(DCFentV1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCFLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel40)
                                    .addComponent(DCFentV2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCFentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(jLabel69))
                                .addGap(19, 19, 19)
                                .addComponent(DCFcalcp)
                                .addGap(11, 11, 11)
                                .addComponent(DCFsalVp)
                                .addGap(65, 65, 65)
                                .addComponent(jSeparator8, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(14, 14, 14)
                                .addComponent(DCF_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel42)
                                        .addComponent(DCFentV3, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCFLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel43)
                                    .addComponent(DCFentV4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_FFisherLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel44)
                                    .addComponent(DCFentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCFcalcx)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 9, Short.MAX_VALUE)
                                .addComponent(DCFsalVx)
                                .addGap(67, 67, 67))
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_FFisherLayout.createSequentialGroup()
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addComponent(DCF_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(71, 71, 71))))))
        );

        D_Con.addTab("F de Fisher", Panel_FFisher);

        jSeparator15.setOrientation(javax.swing.SwingConstants.VERTICAL);

        jLabel45.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel45.setText("Grados de libertad :");

        jLabel46.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel46.setText("Valor x :");

        DCTsalVp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCTsalVp.setText("Valor p :");

        DCTentX.setToolTipText("Valores enteros positivos.");
        DCTentX.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCTentXKeyTyped(evt);
            }
        });

        DCTentV1.setToolTipText("Valores entre 1 y 120.");
        DCTentV1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCTentV1KeyTyped(evt);
            }
        });

        DCTcalcp.setText("Calcular");
        DCTcalcp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCTcalcp.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCTcalcpActionPerformed(evt);
            }
        });

        jLabel47.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel47.setText("Grados de libertad :");

        jLabel48.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel48.setText("Valor p :");

        DCTentP.setToolTipText("Valores entre 0 y 1.");
        DCTentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCTentPKeyTyped(evt);
            }
        });

        DCTentV2.setToolTipText("Valores entre 1 y 120.");
        DCTentV2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                DCTentV2KeyTyped(evt);
            }
        });

        DCTcalcx.setText("Calcular");
        DCTcalcx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCTcalcx.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCTcalcxActionPerformed(evt);
            }
        });

        DCTsalX.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCTsalX.setText("Valor x :");

        DCTLcampos1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCTLcampos1.setToolTipText("Limpiar campos");
        DCTLcampos1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCTLcampos1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCTLcampos1ActionPerformed(evt);
            }
        });

        DCTLcampos2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        DCTLcampos2.setToolTipText("Limpiar campos");
        DCTLcampos2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCTLcampos2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCTLcampos2ActionPerformed(evt);
            }
        });

        DCTTstudent.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        DCTTstudent.setToolTipText("Teoria");
        DCTTstudent.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        DCTTstudent.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                DCTTstudentActionPerformed(evt);
            }
        });

        DCT_AIvp.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCT_AIvp.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "P(X<x)", "P(X>x)" }));
        DCT_AIvp.setToolTipText("Area de integracion");
        DCT_AIvp.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCT_AIvx.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        DCT_AIvx.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "X<x", "X>x" }));
        DCT_AIvx.setToolTipText("Area de integracion");
        DCT_AIvx.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        DCT_Grafico.setBackground(new java.awt.Color(255, 255, 255));
        DCT_Grafico.setBorder(javax.swing.BorderFactory.createEtchedBorder());
        DCT_Grafico.setPreferredSize(new java.awt.Dimension(640, 395));

        javax.swing.GroupLayout DCT_GraficoLayout = new javax.swing.GroupLayout(DCT_Grafico);
        DCT_Grafico.setLayout(DCT_GraficoLayout);
        DCT_GraficoLayout.setHorizontalGroup(
            DCT_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 636, Short.MAX_VALUE)
        );
        DCT_GraficoLayout.setVerticalGroup(
            DCT_GraficoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 391, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout Panel_TStudentLayout = new javax.swing.GroupLayout(Panel_TStudent);
        Panel_TStudent.setLayout(Panel_TStudentLayout);
        Panel_TStudentLayout.setHorizontalGroup(
            Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_TStudentLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(DCT_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGap(8, 8, 8)
                        .addComponent(DCTsalVp))
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel45, javax.swing.GroupLayout.Alignment.TRAILING)
                            .addComponent(jLabel46, javax.swing.GroupLayout.Alignment.TRAILING))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCTcalcp)
                            .addGroup(Panel_TStudentLayout.createSequentialGroup()
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(DCTentX, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DCTentV1, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(DCTLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addGroup(Panel_TStudentLayout.createSequentialGroup()
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(jLabel47, javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(jLabel48, javax.swing.GroupLayout.Alignment.TRAILING))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(DCTentV2, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(DCTentP, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 68, javax.swing.GroupLayout.PREFERRED_SIZE)))
                            .addComponent(DCTsalX, javax.swing.GroupLayout.Alignment.LEADING))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(DCTLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGap(116, 116, 116)
                        .addComponent(DCTcalcx))
                    .addComponent(DCT_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jSeparator9))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator15, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(DCTTstudent, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap())
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGap(35, 35, 35)
                        .addComponent(DCT_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap(43, Short.MAX_VALUE))))
        );

        Panel_TStudentLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {DCT_AIvp, DCT_AIvx});

        Panel_TStudentLayout.setVerticalGroup(
            Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_TStudentLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_TStudentLayout.createSequentialGroup()
                        .addComponent(jSeparator15)
                        .addContainerGap())
                    .addGroup(Panel_TStudentLayout.createSequentialGroup()
                        .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(DCTTstudent, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(DCT_AIvp, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_TStudentLayout.createSequentialGroup()
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel45)
                                        .addComponent(DCTentV1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                    .addComponent(DCTLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(jLabel46)
                                    .addComponent(DCTentX, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCTcalcp)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCTsalVp)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addComponent(jSeparator9, javax.swing.GroupLayout.PREFERRED_SIZE, 2, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(18, 18, 18)
                                .addComponent(DCT_AIvx, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(DCTentV2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel47))
                                    .addComponent(DCTLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(Panel_TStudentLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(DCTentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(jLabel48))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCTcalcx)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(DCTsalX)
                                .addGap(97, 97, 97))
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_TStudentLayout.createSequentialGroup()
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 55, Short.MAX_VALUE)
                                .addComponent(DCT_Grafico, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(67, 67, 67))))))
        );

        D_Con.addTab("T de Student", Panel_TStudent);

        Func.addTab("Distribuciones Continuas", D_Con);

        Muest.setTabPlacement(javax.swing.JTabbedPane.LEFT);
        Muest.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N

        jSeparator10.setOrientation(javax.swing.SwingConstants.VERTICAL);

        MASFTabla1.setModel(new ModeloTabla(null,this.GET.getMF1()));
        MASFTabla1.setColumnSelectionAllowed(true);
        MASFTabla1.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        MASFTabla1.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        MASFTabla1.setTableHeader(this.encabezado(this.MASFTabla1)
        );
        jScrollPane6.setViewportView(MASFTabla1);
        MASFTabla1.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        jLabel21.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel21.setText("N :");

        MASFentN.setToolTipText("Valores enteros positivos");
        MASFentN.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentNKeyTyped(evt);
            }
        });

        jLabel22.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel22.setText("α :");

        MASFentA.setToolTipText("Valores entre 0 y 1");
        MASFentA.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentAKeyTyped(evt);
            }
        });

        jLabel23.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel23.setText("p :");

        MASFentP.setToolTipText("Valores entre 0 y 1");
        MASFentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentPKeyTyped(evt);
            }
        });

        jLabel50.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel50.setText("d :");

        MASFentD.setToolTipText("Valores entre 0 y 1");
        MASFentD.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentDKeyTyped(evt);
            }
        });

        MASFcalc.setText("Calcular");
        MASFcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFcalcActionPerformed(evt);
            }
        });

        MASFsaln.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        MASFsaln.setText("Submuestra n :");

        jLabel52.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel52.setText("Muestreo :");

        MASFTfinito.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        MASFTfinito.setToolTipText("Teoria");
        MASFTfinito.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFTfinito.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFTfinitoActionPerformed(evt);
            }
        });

        MASFLcampos1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASFLcampos1.setToolTipText("Limpiar campos");
        MASFLcampos1.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFLcampos1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFLcampos1ActionPerformed(evt);
            }
        });

        MASFentN1.setToolTipText("Valores enteros positivos");
        MASFentN1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentN1KeyTyped(evt);
            }
        });

        jLabel53.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel53.setText("N :");

        MASFentn.setToolTipText("Valores enteros positivos,N>n.");
        MASFentn.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASFentnKeyTyped(evt);
            }
        });

        jLabel54.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel54.setText("n :");

        MASFLcampos2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASFLcampos2.setToolTipText("Limpiar campos");
        MASFLcampos2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFLcampos2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFLcampos2ActionPerformed(evt);
            }
        });

        jLabel55.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel55.setText("Seleccion de la submuestra :");

        MASFTabla2.setModel(new ModeloTabla(null,this.GET.getMF2()));
        MASFTabla2.setColumnSelectionAllowed(true);
        MASFTabla2.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        MASFTabla2.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        MASFTabla2.setTableHeader(this.encabezado(this.MASFTabla2)
        );
        jScrollPane7.setViewportView(MASFTabla2);
        MASFTabla2.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        MASFselec.setText("Seleccion");
        MASFselec.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFselecActionPerformed(evt);
            }
        });

        MASFLtabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASFLtabla.setToolTipText("Limpiar tabla");
        MASFLtabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFLtabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFLtablaActionPerformed(evt);
            }
        });

        MASFlessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        MASFlessfila.setToolTipText("Eliminar fila");
        MASFlessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFlessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFlessfilaActionPerformed(evt);
            }
        });

        MASFCexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        MASFCexcel.setToolTipText("Guardar");
        MASFCexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFCexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFCexcelActionPerformed(evt);
            }
        });

        MASFCexcel2.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        MASFCexcel2.setToolTipText("Guardar");
        MASFCexcel2.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASFCexcel2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASFCexcel2ActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout Panel_ASFinitoLayout = new javax.swing.GroupLayout(Panel_ASFinito);
        Panel_ASFinito.setLayout(Panel_ASFinitoLayout);
        Panel_ASFinitoLayout.setHorizontalGroup(
            Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_ASFinitoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addComponent(jLabel21)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASFentN, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(MASFLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addComponent(jLabel22)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASFentA, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addComponent(jLabel23)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASFentP, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addComponent(jLabel50)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASFentD, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(MASFcalc)
                    .addComponent(jLabel52))
                .addGap(18, 18, 18)
                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(MASFsaln)
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addComponent(jScrollPane6, javax.swing.GroupLayout.PREFERRED_SIZE, 543, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(MASFlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(MASFLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(MASFCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(MASFTfinito, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(jSeparator10, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel55)
                            .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                                .addComponent(jScrollPane7, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                                .addGroup(javax.swing.GroupLayout.Alignment.LEADING, Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(MASFselec)
                                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                                .addComponent(jLabel53)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(MASFentN1, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                                .addComponent(jLabel54)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(MASFentn, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE)))
                                        .addGap(21, 21, 21)
                                        .addComponent(MASFLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))))
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addGap(62, 62, 62)
                        .addComponent(MASFCexcel2, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(114, 114, 114))
        );
        Panel_ASFinitoLayout.setVerticalGroup(
            Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jSeparator10, javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                .addComponent(MASFTfinito, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(61, 61, 61)
                                .addComponent(MASFLtabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(MASFlessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                .addComponent(jLabel55)
                                .addGap(18, 18, 18)
                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(MASFLcampos2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                            .addComponent(jLabel53)
                                            .addComponent(MASFentN1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                            .addComponent(jLabel54)
                                            .addComponent(MASFentn, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(MASFselec)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(jScrollPane7, javax.swing.GroupLayout.PREFERRED_SIZE, 357, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                .addComponent(jLabel52)
                                .addGap(40, 40, 40)
                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(MASFCexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                        .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                            .addComponent(MASFLcampos1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                                            .addGroup(Panel_ASFinitoLayout.createSequentialGroup()
                                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                    .addComponent(jLabel21)
                                                    .addComponent(MASFentN, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                    .addComponent(jLabel22)
                                                    .addComponent(MASFentA, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                    .addComponent(jLabel23)
                                                    .addComponent(MASFentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addGroup(Panel_ASFinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                    .addComponent(jLabel50)
                                                    .addComponent(MASFentD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(MASFcalc))
                                            .addComponent(jScrollPane6, javax.swing.GroupLayout.PREFERRED_SIZE, 412, javax.swing.GroupLayout.PREFERRED_SIZE))
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(MASFsaln)))))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASFCexcel2, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );

        Muest.addTab("Aleatorio Simple Finito", Panel_ASFinito);

        MASITabla.setModel(new ModeloTabla(null,this.GET.getMI()));
        MASITabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        MASITabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        MASITabla.setTableHeader(this.encabezado(this.MASITabla)
        );
        jScrollPane8.setViewportView(MASITabla);
        MASITabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        MASIentA.setToolTipText("Valores entre 0 y 1");
        MASIentA.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASIentAKeyTyped(evt);
            }
        });

        MASIsaln.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        MASIsaln.setText("Submuestra n :");

        MASIentD.setToolTipText("Valores entre 0 y 1");
        MASIentD.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASIentDKeyTyped(evt);
            }
        });

        MASIentP.setToolTipText("Valores entre 0 y 1");
        MASIentP.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASIentPKeyTyped(evt);
            }
        });

        jLabel57.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel57.setText("d :");

        jLabel58.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel58.setText("α :");

        jLabel59.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel59.setText("p :");

        MASILcampos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASILcampos.setToolTipText("Limpiar campos");
        MASILcampos.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASILcampos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASILcamposActionPerformed(evt);
            }
        });

        MASITinfinnito.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        MASITinfinnito.setToolTipText("Teoria");
        MASITinfinnito.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASITinfinnito.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASITinfinnitoActionPerformed(evt);
            }
        });

        MASILTabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASILTabla.setToolTipText("Limpiar Tabla");
        MASILTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASILTabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASILTablaActionPerformed(evt);
            }
        });

        MASILessfila.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        MASILessfila.setToolTipText("Eliminar fila");
        MASILessfila.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASILessfila.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASILessfilaActionPerformed(evt);
            }
        });

        MASIcalc.setText("Calcular");
        MASIcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASIcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASIcalcActionPerformed(evt);
            }
        });

        MASICexcel.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/guardar_16.png"))); // NOI18N
        MASICexcel.setToolTipText("Guardar");
        MASICexcel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASICexcel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASICexcelActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout Panel_ASInfinitoLayout = new javax.swing.GroupLayout(Panel_ASInfinito);
        Panel_ASInfinito.setLayout(Panel_ASInfinitoLayout);
        Panel_ASInfinitoLayout.setHorizontalGroup(
            Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_ASInfinitoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                        .addGap(1, 1, 1)
                        .addComponent(jLabel58)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASIentA, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(44, 44, 44)
                        .addComponent(MASILcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                        .addComponent(jLabel59)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASIentP, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                        .addComponent(jLabel57)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(MASIcalc)
                            .addComponent(MASIentD, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))))
                .addGap(29, 29, 29)
                .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(MASIsaln)
                    .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                        .addComponent(jScrollPane8, javax.swing.GroupLayout.PREFERRED_SIZE, 596, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 93, Short.MAX_VALUE)
                                .addComponent(MASITinfinnito, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                                .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(MASILessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(MASILTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(MASICexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(0, 0, Short.MAX_VALUE)))))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        Panel_ASInfinitoLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {MASILTabla, MASILcampos, MASITinfinnito});

        Panel_ASInfinitoLayout.setVerticalGroup(
            Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                .addGap(13, 13, 13)
                .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addComponent(jScrollPane8, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                            .addComponent(MASICexcel, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(MASILTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(MASILessfila, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addGroup(Panel_ASInfinitoLayout.createSequentialGroup()
                        .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel58)
                            .addComponent(MASIentA, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel59)
                            .addComponent(MASIentP, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_ASInfinitoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel57)
                            .addComponent(MASIentD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASIcalc))
                    .addComponent(MASILcampos, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(MASITinfinnito, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(26, 26, 26)
                .addComponent(MASIsaln)
                .addGap(0, 90, Short.MAX_VALUE))
        );

        Panel_ASInfinitoLayout.linkSize(javax.swing.SwingConstants.VERTICAL, new java.awt.Component[] {MASILTabla, MASILcampos, MASITinfinnito});

        Muest.addTab("Aleatorio Simple Infinito", Panel_ASInfinito);

        MASETabla = new javax.swing.JTable(){
            public boolean isCellEditable(int rowindex,int columnindex){
                if(columnindex==1)
                return false;
                else
                return true;
            }
        };
        MASETabla.setModel(new ModeloTabla(null,this.GET.getME1()));
        MASETabla.setColumnSelectionAllowed(true);
        MASETabla.setCursor(new java.awt.Cursor(java.awt.Cursor.TEXT_CURSOR));
        MASETabla.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        MASETabla.setTableHeader(this.encabezado(this.MASETabla)
        );
        jScrollPane9.setViewportView(MASETabla);
        MASETabla.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);

        MASELTabla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/limpiar_16.png"))); // NOI18N
        MASELTabla.setToolTipText("Limpiar tabla");
        MASELTabla.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASELTabla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASELTablaActionPerformed(evt);
            }
        });

        MASEAddE.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/add.png"))); // NOI18N
        MASEAddE.setToolTipText("Agregar estrato");
        MASEAddE.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASEAddE.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASEAddEActionPerformed(evt);
            }
        });

        MASELessE.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/less.png"))); // NOI18N
        MASELessE.setToolTipText("Eliminar estrato");
        MASELessE.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASELessE.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASELessEActionPerformed(evt);
            }
        });

        MASETestratificado.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/elementos_teoricos_16.png"))); // NOI18N
        MASETestratificado.setToolTipText("Teoria");
        MASETestratificado.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASETestratificado.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASETestratificadoActionPerformed(evt);
            }
        });

        MASEentn.setToolTipText("Valores enteros positivos, N>n");
        MASEentn.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyTyped(java.awt.event.KeyEvent evt) {
                MASEentnKeyTyped(evt);
            }
        });

        jLabel61.setFont(new java.awt.Font("sansserif", 1, 12)); // NOI18N
        jLabel61.setText("n :");

        MASEcalc.setText("Calcular");
        MASEcalc.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
        MASEcalc.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                MASEcalcActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout Panel_EstratLayout = new javax.swing.GroupLayout(Panel_Estrat);
        Panel_Estrat.setLayout(Panel_EstratLayout);
        Panel_EstratLayout.setHorizontalGroup(
            Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_EstratLayout.createSequentialGroup()
                .addContainerGap(202, Short.MAX_VALUE)
                .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_EstratLayout.createSequentialGroup()
                        .addComponent(jLabel61)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASEentn, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(124, 124, 124)
                        .addComponent(MASEcalc))
                    .addGroup(Panel_EstratLayout.createSequentialGroup()
                        .addComponent(jScrollPane9, javax.swing.GroupLayout.PREFERRED_SIZE, 464, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                .addComponent(MASEAddE, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addComponent(MASELTabla, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addComponent(MASELessE, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE))))
                .addGap(188, 188, 188)
                .addComponent(MASETestratificado, javax.swing.GroupLayout.PREFERRED_SIZE, 33, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );

        Panel_EstratLayout.linkSize(javax.swing.SwingConstants.HORIZONTAL, new java.awt.Component[] {MASEAddE, MASELTabla});

        Panel_EstratLayout.setVerticalGroup(
            Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(Panel_EstratLayout.createSequentialGroup()
                .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_EstratLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(MASETestratificado, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, Panel_EstratLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(MASELTabla, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASEAddE, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(MASELessE, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(Panel_EstratLayout.createSequentialGroup()
                        .addGap(29, 29, 29)
                        .addComponent(jScrollPane9, javax.swing.GroupLayout.PREFERRED_SIZE, 452, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(18, 18, 18)
                .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(Panel_EstratLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(jLabel61)
                        .addComponent(MASEentn, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(MASEcalc))
                .addContainerGap(24, Short.MAX_VALUE))
        );

        Muest.addTab("Estratificado", Panel_Estrat);

        Func.addTab("Muestreo Probabilistico", Muest);

        M_archivo.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/archivo_16.png"))); // NOI18N
        M_archivo.setText("Archivo");

        M_cerrar.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_F4, java.awt.event.InputEvent.ALT_MASK));
        M_cerrar.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/salir_16.png"))); // NOI18N
        M_cerrar.setText("Cerrar");
        M_cerrar.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                M_cerrarActionPerformed(evt);
            }
        });
        M_archivo.add(M_cerrar);

        jMenuBar1.add(M_archivo);

        M_herramientas.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/herramientas_16.png"))); // NOI18N
        M_herramientas.setText("Herramientas");

        M_calculadora.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/calculadora_16.png"))); // NOI18N
        M_calculadora.setText("Calculadora");
        M_calculadora.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                M_calculadoraActionPerformed(evt);
            }
        });
        M_herramientas.add(M_calculadora);

        M_TPantalla.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/Keyboard_16.png"))); // NOI18N
        M_TPantalla.setText("Teclado en Pantalla");
        M_TPantalla.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                M_TPantallaActionPerformed(evt);
            }
        });
        M_herramientas.add(M_TPantalla);

        jMenuBar1.add(M_herramientas);

        M_soporte.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/soporte_16.png"))); // NOI18N
        M_soporte.setText("Soporte");

        jMenuItem1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ImgVisual/creditos_16.png"))); // NOI18N
        jMenuItem1.setText("Créditos");
        jMenuItem1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem1ActionPerformed(evt);
            }
        });
        M_soporte.add(jMenuItem1);

        jMenuBar1.add(M_soporte);

        setJMenuBar(jMenuBar1);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(Func, javax.swing.GroupLayout.PREFERRED_SIZE, 1089, javax.swing.GroupLayout.PREFERRED_SIZE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(Func, javax.swing.GroupLayout.PREFERRED_SIZE, 581, javax.swing.GroupLayout.PREFERRED_SIZE))
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents
   
    private void M_calculadoraActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_M_calculadoraActionPerformed
    Runtime objrun=Runtime.getRuntime();
        try {
            objrun.exec("C:\\Windows\\System32\\calc.exe");
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(null,ex.getMessage());
        }
    }//GEN-LAST:event_M_calculadoraActionPerformed

    private void M_TPantallaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_M_TPantallaActionPerformed
        try {
            String url="C:\\Windows\\system32\\osk.exe";
            ProcessBuilder p=new ProcessBuilder();
            p.command("cmd.exe","/c",url);
            p.start();
        } 
        catch (IOException ex) {
            Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE,null,ex);
        }
    }//GEN-LAST:event_M_TPantallaActionPerformed

    private void formWindowOpened(java.awt.event.WindowEvent evt) {//GEN-FIRST:event_formWindowOpened
    iniciarParseador();
    }//GEN-LAST:event_formWindowOpened

    private void DDMTeoriaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDMTeoriaActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/multinomial.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url); 
    }//GEN-LAST:event_DDMTeoriaActionPerformed

    private void DDMCalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDMCalcActionPerformed
          if(DDMTabla.getModel().getRowCount()==0)
            JOptionPane.showMessageDialog(null, "La tabla esta vacia",null,JOptionPane.ERROR_MESSAGE);
            else{
                int N= 0;
        double pp=0;
                for (int i=0;i<DDMTabla.getModel().getRowCount();i++){
                    if((DDMTabla.getModel().getValueAt(i, 0)==null)||(DDMTabla.getModel().getValueAt(i, 1).toString()==null)){
                        JOptionPane.showMessageDialog(null, "Llene todos los campos",null,JOptionPane.ERROR_MESSAGE);
                        break;
                    }else{  
                        if(Integer.valueOf(DDMTabla.getModel().getValueAt(i, 0).toString())<=0){
                            JOptionPane.showMessageDialog(null, "Introducir un valor válido de x",null,JOptionPane.ERROR_MESSAGE);  
                        break;
                        }else
                    N+=Integer.valueOf(DDMTabla.getModel().getValueAt(i, 0).toString());
                        if(Double.valueOf(DDMTabla.getModel().getValueAt(i, 1).toString())<0||Double.valueOf(DDMTabla.getModel().getValueAt(i, 1).toString())>1){
                        JOptionPane.showMessageDialog(null, "Introducir un valor válido de p",null,JOptionPane.ERROR_MESSAGE);
                        break;
                        }else
                    pp+=Double.valueOf(DDMTabla.getModel().getValueAt(i, 1).toString());
                    }
                }
                    int x=1;
                    double p=1;
                    for (int i=0;i<DDMTabla.getModel().getRowCount();i++){
                        x*= f.fac(Integer.valueOf(DDMTabla.getModel().getValueAt(i,0).toString()));
                        p*=Math.pow(Double.valueOf(DDMTabla.getModel().getValueAt(i,1).toString()), Integer.valueOf(DDMTabla.getModel().getValueAt(i, 0).toString()));
                    }
                    double vp=this.redondeo(f.multinomialVp(N, x, p));
                    DDMVpsal.setText("Valor p : "+Double.toString(vp));
                    parse.exp("multinomialVp(x,"+Integer.toString(x)+","+Double.toString(p)+")");
                     double[] xx=parse.rango(0, N+1, N);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.evalP(xx, N);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDM, xx, yy, "P(X="+Double.toString(N)+")");
            }
       
    }//GEN-LAST:event_DDMCalcActionPerformed

    private void DDMLessTablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDMLessTablaActionPerformed
this.lessFila(this.DDMTabla);
    }//GEN-LAST:event_DDMLessTablaActionPerformed

    private void DDMAddTablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDMAddTablaActionPerformed
        Object[] o={null,null};
            ModeloTabla mt= (ModeloTabla) DDMTabla.getModel();
            mt.tabla();
            mt.addRow(o);
            DDMTabla.setModel(mt);
            componentesTabla(DDMTabla);
        this.lineasTabla(this.DDMTabla);
        this.validarC(this.DDMTabla);
    }//GEN-LAST:event_DDMAddTablaActionPerformed

    private void DDMLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDMLtablaActionPerformed
this.limpiarTabla2(this.DDMTabla);
this.graficaDDM.limpiar();
    }//GEN-LAST:event_DDMLtablaActionPerformed

    private void DDGLcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGLcamposActionPerformed
    DDGentX.setText(null);
    DDGentP.setText(null);
    this.graficaDDG.limpiar();
    }//GEN-LAST:event_DDGLcamposActionPerformed

    private void DDGTgeoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGTgeoActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/geometrica.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DDGTgeoActionPerformed

    private void DDGCalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGCalcActionPerformed
     if(DDGentX.getText().isEmpty()||DDGentP.getText().isEmpty())
          JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
          else{
            int x=0;
            double p=0;
              x+=Integer.valueOf(DDGentX.getText());
              p+=Double.valueOf(DDGentP.getText());
              if(x<=0)
                JOptionPane.showMessageDialog(null, "Valor incorrecto de x", null, JOptionPane.ERROR_MESSAGE);
                else
                    if(p<0||p>1)
                      JOptionPane.showMessageDialog(null, "Valor incorrecto de p", null, JOptionPane.ERROR_MESSAGE); 
                      else{
                        double vp=this.redondeo(f.geometricaVp(x, p));
                        double md=this.redondeo(f.geometricaMedia(p));
                        double vr=this.redondeo(f.geometricaVarianza(p));
                          DDGsalVp.setText("Valor p :"+Double.toString(vp));
                          DDGsalM.setText("Media :"+Double.toString(md));
                          DDGsalV.setText("Varianza :"+Double.toString(vr));
                          parse.exp("geometricaVp(x,"+Double.toString(p)+")");
                double[] xx=parse.rango(0, x+1, x);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.evalP(xx,x);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDG, xx, yy, "(P="+Double.toString(x)+")");
                String[] s={DDGentX.getText(),DDGentP.getText(),Double.toString(vp),Double.toString(md),Double.toString(vr)};
                    DefaultTableModel temp=(DefaultTableModel) DDGTabla.getModel();
                        temp.addRow(s);
                        DDGTabla.setModel(temp);
                        componentesTabla(DDGTabla);
                        this.lineasTabla(this.DDGTabla);
                    }            
             }
    }//GEN-LAST:event_DDGCalcActionPerformed

    private void DDHcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHcalcActionPerformed
     if(DDHentX.getText().isEmpty()||DDHentN.getText().isEmpty()||DDHentn.getText().isEmpty()||DDHentK.getText().isEmpty()){
               JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
             }
             else{
                  int x=Integer.parseInt(DDHentX.getText());
        int N=Integer.parseInt(DDHentN.getText());
        int n=Integer.parseInt(DDHentn.getText());
        int k=Integer.parseInt(DDHentK.getText());
                 if(x<0||N<0||n<0||k<0||x>k||x>N||x>n||n>N||k>N||n+k>N){
          JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
             }else {
                     double vp=this.redondeo(f.hipergeometricaVp(x, N, n, k));
                     double mnvp=this.redondeo(f.hipergeometricaVpMenor(x, N, n, k));
                     double myvp=this.redondeo(f.hipergeometricaVpMayor(x, N, n, k));
                     double md=this.redondeo(f.hipergeometricaMedia(N, n, k));
                     double vr=this.redondeo(f.hipergeometricaVarianza(N, n, k));
                    if(((String) DDHmodo.getSelectedItem()).equals("P(X=x)")){
                      DDHsalVp.setText("Valor p :"+Double.toString(vp));
                      parse.exp("hipergeometricaVp(x,"+Integer.toString(N)+","+Integer.toString(n)+","+Integer.toString(k)+")");
                double[] xx=parse.rango(0, x+1, x);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.evalP(xx,x);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDH, xx, yy, "(P="+Double.toString(x)+")");
                    }
                      else if(((String) DDHmodo.getSelectedItem()).equals("P(X≤x)")){
                             DDHsalVp.setText("Valor p :"+Double.toString(mnvp));
                             parse.exp("hipergeometricaVpMenor(x,"+Integer.toString(N)+","+Integer.toString(n)+","+Integer.toString(k)+")");
                double[] xx=parse.rango(0, x, 1);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDH, xx, yy, "P(X≤"+Double.toString(x)+")");
                      }
                         else if(((String) DDHmodo.getSelectedItem()).equals("P(X≥x)")){
                                DDHsalVp.setText("Valor p :"+Double.toString(myvp));
                                 parse.exp("hipergeometricaVpMayor(x,"+Integer.toString(N)+","+Integer.toString(n)+","+Integer.toString(k)+")");
                double[] xx=parse.rango(x, N, 1);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDH, xx, yy, "P(X≥)"+Double.toString(x)+")");
                         }
                        DDHsalM.setText("Media :"+Double.toString(md));
                        DDHsalV.setText("Varianza :"+Double.toString(vr));
                        String[] s={DDHentX.getText(),DDHentN.getText(),DDHentn.getText(),DDHentK.getText(),Double.toString(vp),Double.toString(mnvp),Double.toString(myvp),Double.toString(md),Double.toString(vr)};
                          DefaultTableModel temp=(DefaultTableModel) DDHTabla.getModel();
                                        temp.addRow(s);
                                        DDHTabla.setModel(temp);
                                        componentesTabla(DDHTabla);
                                       this.lineasTabla(this.DDHTabla);
             }
     }
    }//GEN-LAST:event_DDHcalcActionPerformed

    private void DDHLcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHLcamposActionPerformed
    DDHentX.setText(null);
    DDHentN.setText(null);
    DDHentn.setText(null);
    DDHentK.setText(null);
    this.graficaDDH.limpiar();
    }//GEN-LAST:event_DDHLcamposActionPerformed

    private void DDHLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHLtablaActionPerformed
this.limpiarTabla(this.DDHTabla);
    }//GEN-LAST:event_DDHLtablaActionPerformed

    private void DDHlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHlessfilaActionPerformed
this.lessFila(this.DDHTabla);
    }//GEN-LAST:event_DDHlessfilaActionPerformed

    private void DDHThiperActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHThiperActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/hipergeometrica.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DDHThiperActionPerformed

    private void DCUTuniformecActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCUTuniformecActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/uniforme.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCUTuniformecActionPerformed

    private void DCUlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCUlessfilaActionPerformed
this.lessFila(this.DCUTabla);
    }//GEN-LAST:event_DCUlessfilaActionPerformed

    private void DCULtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCULtablaActionPerformed
this.limpiarTabla(this.DCUTabla);
    }//GEN-LAST:event_DCULtablaActionPerformed

    private void DCULcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCULcamposActionPerformed
    DCUentX.setText(null);
    DCUentA.setText(null);
    DCUentB.setText(null);
    this.graficaDCU.limpiar();
    }//GEN-LAST:event_DCULcamposActionPerformed

    private void DCUcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCUcalcActionPerformed
   if(DCUentX.getText().isEmpty()||DCUentA.getText().isEmpty()||DCUentB.getText().isEmpty())
          JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
          else{
             int x=0;
    double a=0;
    double b=0;
              x+=Integer.valueOf(DCUentX.getText());
              a+=Double.valueOf(DCUentA.getText());
              b+=Double.valueOf(DCUentB.getText());
              if(x<a||x>b)
                      JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE); 
                      else{
                  double md=this.redondeo(f.UniformeMedia(a, b));
                  double T=this.redondeo(f.UniformeDes(a, b));
                  double F=this.redondeo(f.UniformeF(a, b));
                  if(DCU_AIvp.getSelectedItem().equals("P(X<x)")){
                      double vp=this.redondeo(f.UniformeVp(a, x));
                          DCUsalVp.setText("Valor p :"+Double.toString(vp));
                          parse.exp("uniformeF(x,y)");
                          double[] xx=parse.rango(0, x*2, 0.1);
                          double[] yy=new double[xx.length];
                          double[] xx1=parse.rango(0, x, 0.1);
                          double[] yy1=new double[xx1.length];
                 try {
                     yy=parse.evalU(xx, a, b);
                     yy1=parse.evalU(xx1, a, b);
                 } catch (Exception ex) {
                     Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                 }
        this.graficar(graficaDCU, xx, yy,"f(x)" );
        this.addgrafica(graficaDCU, xx1, yy1, "P(X<"+Double.toString(x)+")");
                  }else if(DCU_AIvp.getSelectedItem().equals("P(X>x)")){
                   double vp=this.redondeo(f.UniformeVp(x, b)); 
                   DCUsalVp.setText("Valor p :"+Double.toString(vp));
                          parse.exp("uniformeF(x,y)");
                          double[] xx=parse.rango(0, x*2, 0.1);
                          double[] yy=new double[xx.length];
                          double[] xx1=parse.rango(x, x*2, 0.1);
                          double[] yy1=new double[xx1.length];
                 try {
                     yy=parse.evalU(xx, a, b);
                     yy1=parse.evalU(xx1, a, b);
                 } catch (Exception ex) {
                     Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                 }
        this.graficar(graficaDCU, xx, yy, "f(x");
        this.addgrafica(graficaDCU, xx1, yy1, "P(X>"+Double.toString(x)+")");
                  }
                         DCUsalM.setText("Media :"+Double.toString(md));
                          DCUsalDesv.setText("T :"+Double.toString(T));
                          DCUsalF.setText("f(x)= "+Double.toString(F));
                        String[] s={DCUentX.getText(),DCUentA.getText(),DCUentB.getText(),Double.toString(this.redondeo(f.UniformeVp(a, b))),Double.toString(md),Double.toString(T),Double.toString(F)};
                        DefaultTableModel temp=(DefaultTableModel) DCUTabla.getModel();
                                        temp.addRow(s);
                                        DCUTabla.setModel(temp);
                                        componentesTabla(DCUTabla);
                                        this.lineasTabla(DCUTabla);
                                       }
             }
    }//GEN-LAST:event_DCUcalcActionPerformed

    private void DCNcalcpActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCNcalcpActionPerformed
        if(DCNentZ.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else{
             int z=0;
            z+=Integer.valueOf(DCNentZ.getText());
            if(z<-4||z>4)
                JOptionPane.showMessageDialog(null, "Valor incorrecto de z", null, JOptionPane.ERROR_MESSAGE);
            else{
                double vp=this.redondeo(f.NormalVp(z));
                double vpm=this.redondeo(1-f.NormalVp(z));
                if(DCN_AIvp.getSelectedItem().equals("P(X<x)")){
                DCNsalVp.setText("Valor p :"+Double.toString(vp));
                 parse.exp("normalF(x)");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(-6, z, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCN, xx, yy,"f(x)" );
                this.addgrafica(graficaDCN, xx1, yy1,"P(X<"+Double.toString(z)+")" );
                }else if(DCN_AIvp.getSelectedItem().equals("P(X>x)")){
                DCNsalVp.setText("Valor p :"+Double.toString(vpm));
                 parse.exp("normalF(x)");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                 double[] xx1=parse.rango(z, 6, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCN, xx, yy, "f(x)");
                this.addgrafica(graficaDCN, xx1, yy1,"P(X>"+Double.toString(z)+")" );
                }
            }
        }
    }//GEN-LAST:event_DCNcalcpActionPerformed

    private void DCNLcamposzActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCNLcamposzActionPerformed
    DCNentZ.setText(null);
    this.graficaDCN.limpiar();
    }//GEN-LAST:event_DCNLcamposzActionPerformed

    private void DCNLcampospActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCNLcampospActionPerformed
    DCNentP.setText(null);
     this.graficaDCN.limpiar();
    }//GEN-LAST:event_DCNLcampospActionPerformed

    private void DCNcalcxActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCNcalcxActionPerformed
   if(DCNentP.getText().isEmpty()){
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
    }else{
         double p=0;
            p+=Double.valueOf(DCNentP.getText());
            if(p<0||p>1){
                JOptionPane.showMessageDialog(null, "Valor incorrecto de p", null, JOptionPane.ERROR_MESSAGE);
            }else{
                if(DCN_AIvz.getSelectedItem().equals("X<x")){
                    double vx=this.redondeo(f.NormalBiseccion(p));
                  DCNsalVz.setText("Valor x : "+Double.toString(vx));
                  parse.exp("normalF(x)");
                  double[] xx=parse.rango(-6, 6, 0.1);
                  double[] yy=new double[xx.length];
                  double[] xx1=parse.rango(-6, vx, 0.1);
                double[] yy1=new double[xx1.length];
                    try {
                        yy = parse.eval(xx);
                        yy1=parse.eval(xx1);
                    } catch (Exception ex) {
                        Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                    }
                  this.graficar(graficaDCN, xx, yy, "f(x)");
                  this.addgrafica(graficaDCN, xx1, yy1,"P(X<"+Double.toString(vx)+")" );
                }else if(DCN_AIvz.getSelectedItem().equals("X>x")){
                 double vx=this.redondeo(f.NormalBiseccion(1-p));
                  DCNsalVz.setText("Valor x : "+Double.toString(vx));
                  parse.exp("normalF(x)");
                  double[] xx=parse.rango(-6, 6, 0.1);
                  double[] yy=new double[xx.length];
                  double[] xx1=parse.rango(vx, 6, 0.1);
                double[] yy1=new double[xx1.length];
                    try {
                        yy = parse.eval(xx);
                        yy1=parse.eval(xx1);
                    } catch (Exception ex) {
                        Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                    }
                  this.graficar(graficaDCN, xx, yy, "f(x)"); 
                  this.addgrafica(graficaDCN, xx1, yy1,"P(X>"+Double.toString(vx)+")" );
                }
            }
        }
    }//GEN-LAST:event_DCNcalcxActionPerformed

    private void DCNTnormalActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCNTnormalActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/normal.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCNTnormalActionPerformed

    private void DCCLcampos1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCLcampos1ActionPerformed
    DCCentV1.setText(null);
    DCCentX.setText(null);
     this.graficaDCC.limpiar();
    }//GEN-LAST:event_DCCLcampos1ActionPerformed

    private void DCCLcamposp2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCLcamposp2ActionPerformed
    DCCentV2.setText(null);
    DCCentP.setText(null);
     this.graficaDCC.limpiar();
    }//GEN-LAST:event_DCCLcamposp2ActionPerformed

    private void DCCcalcxActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCcalcxActionPerformed
    if(DCCentV2.getText().isEmpty()||DCCentP.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
             double p=0;
        double v2=0;
            v2+=Double.valueOf(DCCentV2.getText());
            p+=Double.valueOf(DCCentP.getText());
            if(v2<1||v2>30||p<0||p>1){
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            }else{
                if(DCC_AIvx.getSelectedItem().equals("X<x")){
                double vx=this.redondeo(f.JiBiseccion(p, v2));
                DCCsalX.setText("Valor x :"+Double.toString(vx));
                parse.exp("jiF(x,"+Double.toString(v2)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, vx, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCC, xx, yy, "f(x)");
                this.addgrafica(graficaDCC, xx1, yy1, "P(X<"+Double.toString(vx)+")");
                }else if(DCC_AIvx.getSelectedItem().equals("X>x")){
                double vxm=this.redondeo(f.JiBiseccion(1-p, v2));
                DCCsalX.setText("Valor x :"+Double.toString(vxm));
                parse.exp("jiF(x,"+Double.toString(v2)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vxm, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCC, xx, yy, "f(x)");
                this.addgrafica(graficaDCC, xx1, yy1, "P(X>"+Double.toString(vxm)+")");
            }
        } 
    }
    }//GEN-LAST:event_DCCcalcxActionPerformed

    private void DCCcalcpActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCcalcpActionPerformed
    if(DCCentV1.getText().isEmpty()||DCCentX.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
             double x=0;
        double v=0;
            v+=Double.valueOf(DCCentV1.getText());
            x+=Double.valueOf(DCCentX.getText());
            if(v<1||v>30||x<0||x>60){
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            }else{
                if(DCC_AIvp.getSelectedItem().equals("P(X<x)")){
                double vp=this.redondeo(f.JiVp(x, v));
                DCCsalVp.setText("Valor p :"+Double.toString(vp));
                parse.exp("jiF(x,"+Double.toString(v)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, x, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCC, xx, yy, "f(x)");
                this.addgrafica(graficaDCC, xx1, yy1, "P(X<"+Double.toString(x)+")");
                }else if(DCC_AIvp.getSelectedItem().equals("P(X>x)")){
                double vpm=this.redondeo(1-f.JiVp(x, v));
                DCCsalVp.setText("Valor p :"+Double.toString(vpm));
                parse.exp("jiF(x,"+Double.toString(v)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCC, xx, yy, "f(x)");
                this.addgrafica(graficaDCC, xx1, yy1, "P(X>"+Double.toString(x)+")");
                }
                
            }
        } 
    }//GEN-LAST:event_DCCcalcpActionPerformed

    private void DCCTchicuadradoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCTchicuadradoActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/chi.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCCTchicuadradoActionPerformed

    private void DCCentV2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCCentV2ActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_DCCentV2ActionPerformed

    private void DCEcalcpActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCEcalcpActionPerformed
        if(DCEentLanda1.getText().isEmpty()||DCEentX.getText().isEmpty())
                JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
            else{
                double at=0;
        int x=0;
              at+=Double.valueOf(DCEentLanda1.getText());
              x+=Double.valueOf(DCEentX.getText());
              if(at<=0||x<=0||x>30)
                  JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
              else{
                  if(DCE_AIvp.getSelectedItem().equals("P(X<x)")){
                  double vp=this.redondeo(1-f.ExponencialVp(x, at));
                  DCEsalVp.setText("Valor p :"+Double.toString(vp));
                  parse.exp("expF(x,"+Double.toString(at)+")");
                   double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, x, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCE, xx, yy, "f(x)");
                this.addgrafica(graficaDCE, xx1, yy1, "P(X<"+Double.toString(x));
                  }else if(DCE_AIvp.getSelectedItem().equals("P(X>x)")){
                  double vp=this.redondeo(f.ExponencialVp(x, at));  
                  DCEsalVp.setText("Valor p :"+Double.toString(vp));
                  parse.exp("expF(x,"+Double.toString(at)+")");
                   double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 30, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCE, xx, yy, "f(x)");
                this.addgrafica(graficaDCE, xx1, yy1, "P(X>"+Double.toString(x));
                  }
               
              }
            }
    }//GEN-LAST:event_DCEcalcpActionPerformed

    private void DCELcampos1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCELcampos1ActionPerformed
    DCEentLanda1.setText(null);
    DCEentX.setText(null);
     this.graficaDCE.limpiar();
    }//GEN-LAST:event_DCELcampos1ActionPerformed

    private void DCETexponencialActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCETexponencialActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/exponencial.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCETexponencialActionPerformed

    private void DCEcalcxActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCEcalcxActionPerformed
    if(DCEentLanda2.getText().isEmpty()||DCEentP.getText().isEmpty())
                JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
            else{
                 double at=0;
        double p=0;
              at+=Double.valueOf(DCEentLanda2.getText());
              p+=Double.valueOf(DCEentP.getText());
              if(at<=0||p<0||p>1)
                  JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
              else{
                  if(DCE_AIvx.getSelectedItem().equals("X<x")){
                  double vx=this.redondeo(1-f.ExponencialVx(p, at));
                  DCEsalX.setText("Valor x :"+Double.toString(vx));
                  parse.exp("expF(x,"+Double.toString(at)+")");
                   double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, vx, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCE, xx, yy, "f(x)");
                this.addgrafica(graficaDCE, xx1, yy1, "P(X<"+Double.toString(vx));
                  }else if(DCE_AIvx.getSelectedItem().equals("X>x")){
                  double vx=this.redondeo(f.ExponencialVx(p, at));  
                  DCEsalX.setText("Valor x :"+Double.toString(vx));
                  parse.exp("expF(x,"+Double.toString(at)+")");
                   double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vx, 30, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCE, xx, yy, "f(x)");
                this.addgrafica(graficaDCE, xx1, yy1, "P(X>"+Double.toString(vx));
                  }
              }
            }
    }//GEN-LAST:event_DCEcalcxActionPerformed

    private void DCELcampos2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCELcampos2ActionPerformed
    DCEentLanda2.setText(null);
    DCEentP.setText(null);
     this.graficaDCE.limpiar();
    }//GEN-LAST:event_DCELcampos2ActionPerformed

    private void DCFLcampos1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCFLcampos1ActionPerformed
    DCFentV1.setText(null);
    DCFentV2.setText(null);
    DCFentX.setText(null);
     this.graficaDCF.limpiar();
    }//GEN-LAST:event_DCFLcampos1ActionPerformed

    private void DCFLcampos2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCFLcampos2ActionPerformed
    DCFentV3.setText(null);
    DCFentV4.setText(null);
    DCFentP.setText(null);
     this.graficaDCF.limpiar();
    }//GEN-LAST:event_DCFLcampos2ActionPerformed

    private void DCFTfisherActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCFTfisherActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/Ffisher.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCFTfisherActionPerformed

    private void DCFcalcpActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCFcalcpActionPerformed
    if(DCFentV1.getText().isEmpty()||DCFentV2.getText().isEmpty()||DCFentX.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
            int x=0;
        int v1=0;
        int v2=0;
            v1+=Integer.valueOf(DCFentV1.getText());
            v2+=Integer.valueOf(DCFentV2.getText());
            x+=Integer.valueOf(DCFentX.getText());
            if(v1<1||v1>120||v2<1||v2>120||x<0)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            else{
                if(DCF_AIvp.getSelectedItem().equals("P(X<x)")){
                if((v1==1)&&(v2==1)){
                double vp=this.redondeo(f.FdeFisherVpp(x));
                DCFsalVp.setText("Valor p :"+Double.toString(vp));
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, x, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(x)+")");
                }else if((v1==1)&&(v2>1)){
                double vp=this.redondeo(f.FdeFisherVp(x, v1, v2));
                DCFsalVp.setText("Valor p :"+Double.toString(vp));
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, x, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                     yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(x)+")");
                }else{
                double vp=this.redondeo(f.FdeFisherVp1(x, v1, v2));
                DCFsalVp.setText("Valor p :"+Double.toString(vp)); 
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, x, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                     yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(x)+")");
                }    
                }else if(DCF_AIvp.getSelectedItem().equals("P(X>x)")){
                if((v1==1)&&(v2==1)){
                double vp=this.redondeo(1-f.FdeFisherVpp(x));
                DCFsalVp.setText("Valor p :"+Double.toString(vp));
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(x)+")");
                }else if((v1==1)&&(v2>1)){
                double vp=this.redondeo(1-f.FdeFisherVp(x, v1, v2));
                DCFsalVp.setText("Valor p :"+Double.toString(vp));
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(x)+")");
                }else{
                double vp=this.redondeo(1-f.FdeFisherVp1(x, v1, v2));
                DCFsalVp.setText("Valor p :"+Double.toString(vp)); 
                 parse.exp("fisherF(x,"+Integer.toString(v1)+","+Integer.toString(v2)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(x)+")");
                }    
                }
            }
        }
    }//GEN-LAST:event_DCFcalcpActionPerformed

    private void DCFcalcxActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCFcalcxActionPerformed
       if(DCFentV3.getText().isEmpty()||DCFentV4.getText().isEmpty()||DCFentP.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
             double p=0;
        int v3=0;
        int v4=0;
            v3+=Integer.valueOf(DCFentV3.getText());
            v4+=Integer.valueOf(DCFentV4.getText());
            p+=Double.valueOf(DCFentP.getText());
            if(v3<1||v3>120||v4<1||v4>120||p<0||p>1)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            else{
               if(DCF_AIvx.getSelectedItem().equals("X<x")){
                if((v3==1)&&(v4==1)){
                double vx=this.redondeo(f.FdeFisherVx(1-p));
                DCFsalVx.setText("Valor x :"+Double.toString(vx));
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, vx, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(vx)+")");
                }else if((v3==1)&&(v4>1)){
                double vx=this.redondeo(f.FdeFisherBiseccion(p, v3, v4));
                DCFsalVx.setText("Valor x :"+Double.toString(vx));
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, vx, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                     yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(vx)+")");
                }else{
                double vx=this.redondeo(f.FdeFisherBiseccion(p, v3, v4));
                DCFsalVx.setText("Valor x :"+Double.toString(vx)); 
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(0, vx, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                     yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X<"+Double.toString(vx)+")");
                }    
                }else if(DCF_AIvx.getSelectedItem().equals("X>x")){
                if((v3==1)&&(v4==1)){
                double vx=this.redondeo(f.FdeFisherVx(1-p));
                DCFsalVx.setText("Valor x :"+Double.toString(vx));
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vx, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(vx)+")");
                }else if((v3==1)&&(v4>1)){
                double vx=this.redondeo(f.FdeFisherBiseccion(p, v3, v4));
                DCFsalVx.setText("Valor x :"+Double.toString(vx));
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vx, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(vx)+")");
                }else{
                double vx=this.redondeo(f.FdeFisherBiseccion(p, v3, v4));
                DCFsalVx.setText("Valor x :"+Double.toString(vx)); 
                 parse.exp("fisherF(x,"+Integer.toString(v3)+","+Integer.toString(v4)+")");
                 double[] xx=parse.rango(0, 30, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vx, 30, 0.1);
                double[] yy1=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCF, xx, yy, "f(x)");
                this.addgrafica(graficaDCF, xx1, yy1, "P(X>"+Double.toString(vx)+")");
                }    
                }
        } 
        }
    }//GEN-LAST:event_DCFcalcxActionPerformed

    private void DCTcalcpActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCTcalcpActionPerformed
    if(DCTentV1.getText().isEmpty()||DCTentX.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
             int x=0;
        int v=0;
            v+=Integer.valueOf(DCTentV1.getText());
            x+=Integer.valueOf(DCTentX.getText());
            if(v<1||v>120||x<=0)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            else{
                if(DCT_AIvp.getSelectedItem().equals("P(X<x)")){
                double vp=this.redondeo(f.TstudentVp(x, v));
                DCTsalVp.setText("Valor p :"+Double.toString(vp));
                parse.exp("tstudentF(x,"+Integer.toString(v)+")");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(-6, x, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCT, xx, yy, "f(x)");
                this.addgrafica(graficaDCT, xx1, yy1, "P(X<"+Double.toString(x));
                }else if(DCT_AIvp.getSelectedItem().equals("P(X>x)")){
                double vp=this.redondeo(1-f.TstudentVp(x, v));
                DCTsalVp.setText("Valor p :"+Double.toString(vp));
                parse.exp("tstudentF(x,"+Integer.toString(v)+")");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(x, 6, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCT, xx, yy, "f(x)");
                this.addgrafica(graficaDCT, xx1, yy1, "P(X>"+Double.toString(x)); 
                }
            }
          
        } 
    }//GEN-LAST:event_DCTcalcpActionPerformed

    private void DCTcalcxActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCTcalcxActionPerformed
   if(DCTentV2.getText().isEmpty()||DCTentP.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
        else {
            double p=0;
        int v=0;
            v+=Integer.valueOf(DCTentV2.getText());
            p+=Double.valueOf(DCTentP.getText());
            if(v<=0||p<=0||p>=1)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            else{
                if(DCT_AIvx.getSelectedItem().equals("X<x")){
                double vx=this.redondeo(f.TstudentBiseccion(p, v));
                DCTsalX.setText("Valor x :"+Double.toString(vx));
                parse.exp("tstudentF(x,"+Integer.toString(v)+")");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(-6, vx, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCT, xx, yy, "f(x)");
                this.addgrafica(graficaDCT, xx1, yy1, "f(X<"+Double.toString(vx));
                }else if(DCT_AIvx.getSelectedItem().equals("X>x")){
                double vxm=this.redondeo(f.TstudentBiseccion(1-p, v));
                DCTsalX.setText("Valor x :"+Double.toString(vxm));
                parse.exp("tstudentF(x,"+Integer.toString(v)+")");
                double[] xx=parse.rango(-6, 6, 0.1);
                double[] yy=new double[xx.length];
                double[] xx1=parse.rango(vxm, 6, 0.1);
                double[] yy1=new double[xx1.length];
                try {
                    yy=parse.eval(xx);
                    yy1=parse.eval(xx1);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDCT, xx, yy, "f(x)");
                this.addgrafica(graficaDCT, xx1, yy1, "f(X>"+Double.toString(vxm)); 
                }
            }
        } 
    }//GEN-LAST:event_DCTcalcxActionPerformed

    private void DCTLcampos1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCTLcampos1ActionPerformed
    DCTentV1.setText(null);
    DCTentX.setText(null);
     this.graficaDCT.limpiar();
    }//GEN-LAST:event_DCTLcampos1ActionPerformed

    private void DCTLcampos2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCTLcampos2ActionPerformed
    DCTentV2.setText(null);
    DCTentP.setText(null);
     this.graficaDCT.limpiar();
    }//GEN-LAST:event_DCTLcampos2ActionPerformed

    private void DCTTstudentActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCTTstudentActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/Tstudent.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DCTTstudentActionPerformed

    private void MASFTfinitoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFTfinitoActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/finito.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_MASFTfinitoActionPerformed

    private void MASFLcampos1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFLcampos1ActionPerformed
    MASFentN.setText(null);
    MASFentA.setText(null);
    MASFentP.setText(null);
    MASFentD.setText(null);
    }//GEN-LAST:event_MASFLcampos1ActionPerformed

    private void MASFLcampos2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFLcampos2ActionPerformed
    MASFentN1.setText(null);
    MASFentn.setText(null);
    this.limpiarTabla(this.MASFTabla2);
    }//GEN-LAST:event_MASFLcampos2ActionPerformed

    private void MASILcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASILcamposActionPerformed
    MASIentA.setText(null);
    MASIentP.setText(null);
    MASIentD.setText(null);
    }//GEN-LAST:event_MASILcamposActionPerformed

    private void MASITinfinnitoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASITinfinnitoActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/infinito.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_MASITinfinnitoActionPerformed

    private void MASELTablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASELTablaActionPerformed
    this.limpiarTabla2(this.MASETabla);
    MASEentn.setText(null);
    }//GEN-LAST:event_MASELTablaActionPerformed

    private void MASEAddEActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASEAddEActionPerformed
   Object[] o={null,null};
            DefaultTableModel temp=(DefaultTableModel) MASETabla.getModel();
            temp.addRow(o);
            MASETabla.setModel(temp);
            componentesTabla(MASETabla);
            this.lineasTabla(MASETabla);
            this.validarC(this.MASETabla);
    }//GEN-LAST:event_MASEAddEActionPerformed

    private void MASELessEActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASELessEActionPerformed
this.lessFila(this.MASETabla);
    }//GEN-LAST:event_MASELessEActionPerformed

    private void MASETestratificadoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASETestratificadoActionPerformed
    URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/estratificado.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_MASETestratificadoActionPerformed

    private void MASFcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFcalcActionPerformed
    if(MASFentN.getText().isEmpty()||MASFentA.getText().isEmpty()||MASFentP.getText().isEmpty()||MASFentD.getText().isEmpty())
                JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
            else{
                 int N=0;
    double at=0;
    double p=0;
    double d=0;
              N+=Integer.valueOf(MASFentN.getText());
              at+=Double.valueOf(MASFentA.getText());
              p+=Double.valueOf(MASFentP.getText());
              d+=Double.valueOf(MASFentD.getText());
              if(N<0||at<0||at>1||p<0||p>1||d<0||d>1)
                  JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
              else{
                  int m=(int) Math.round(f.MASFinito(N, at, p, d));
                  MASFsaln.setText("Submuestra n :"+Integer.toString(m));
                  String[] s={MASFentN.getText(),MASFentA.getText(),MASFentP.getText(),MASFentD.getText(),Integer.toString(m)};
                        DefaultTableModel temp=(DefaultTableModel) MASFTabla1.getModel();
                                        temp.addRow(s);
                                        MASFTabla1.setModel(temp);
                                        componentesTabla(MASFTabla1);
                                        this.lineasTabla(MASFTabla1);
                                       }
            }
    }//GEN-LAST:event_MASFcalcActionPerformed

    private void MASFLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFLtablaActionPerformed
this.limpiarTabla(this.MASFTabla1);
    }//GEN-LAST:event_MASFLtablaActionPerformed

    private void MASFlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFlessfilaActionPerformed
this.lessFila(this.MASFTabla1);
    }//GEN-LAST:event_MASFlessfilaActionPerformed

    private void MASFselecActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFselecActionPerformed
   if((MASFentN1.getText().isEmpty())||(MASFentn.getText().isEmpty()))
        JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
    else{
         int N=0;   
    int n=0;
    DefaultTableModel temp=(DefaultTableModel) MASFTabla2.getModel();
    int aux=MASFTabla2.getModel().getRowCount();
    int c=aux;
        N+=Integer.parseInt(MASFentN1.getText());
        n+=Integer.parseInt(MASFentn.getText());
    
    if(N<0||n<0)
        JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
    if(aux>0){
    for(int i=0;i<aux;i++){
        temp.removeRow(c-1);
        c--;
    }
    }
 for(int i=0;i<n;i++){
    temp.addRow(new Object[]{ Integer.toString( Math.round(f.MASFinitoSubM(N))) , 0 });
 }
    MASFTabla2.setModel(temp);
    componentesTabla(MASFTabla2);
    this.lineasTabla(MASFTabla2);
 }
    }//GEN-LAST:event_MASFselecActionPerformed

    private void MASILTablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASILTablaActionPerformed
this.limpiarTabla(this.MASITabla);
    }//GEN-LAST:event_MASILTablaActionPerformed

    private void MASILessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASILessfilaActionPerformed
 this.lessFila(this.MASITabla);
    }//GEN-LAST:event_MASILessfilaActionPerformed

    private void MASEcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASEcalcActionPerformed
   if(MASEentn.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
        else{
            double N=0;
   double n=0;
   double t=0;
   int c=MASETabla.getModel().getRowCount();
   double[] list=new double[c];
   DefaultTableModel temp=(DefaultTableModel) MASETabla.getModel();
            n+=Double.valueOf(MASEentn.getText());
         if(n<0){
    JOptionPane.showMessageDialog(null, "Valor incorrecto de n",null ,    JOptionPane.ERROR_MESSAGE);      
        }else{ 
             for(int i=0;i<c;i++){
                if(temp.getValueAt(i, 0).toString().isEmpty()){
                    JOptionPane.showMessageDialog(this, null, "Llene todos los campos vacios", JOptionPane.ERROR_MESSAGE);
                 }else{
                     t=Double.valueOf(temp.getValueAt(i,0).toString());
                 if(t<0){
                     JOptionPane.showMessageDialog(null, "Valor incorrecto de N", null, JOptionPane.ERROR_MESSAGE);
                     break;
                 }else{
                     N+=t;
                     list[i]=t;
                }
             }
             }
             for(int i=0;i<c;i++){
                 temp.setValueAt(Integer.toString((int)(Math.round(f.MEstratificado(n, N, list[i])))), i, 1);
                 }
             MASETabla.setModel(temp);
             componentesTabla(MASETabla);
             this.lineasTabla(MASETabla);
         
        }
         }
    }//GEN-LAST:event_MASEcalcActionPerformed

    private void MASIcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASIcalcActionPerformed
     if(MASIentA.getText().isEmpty()||MASIentP.getText().isEmpty()||MASIentD.getText().isEmpty())
                JOptionPane.showMessageDialog(null, "Llene los campos", null, JOptionPane.ERROR_MESSAGE);
            else{
                 double at=0;
    double p=0;
    double d=0;
              at+=Double.valueOf(MASIentA.getText());
              p+=Double.valueOf(MASIentP.getText());
              d+=Double.valueOf(MASIentD.getText());
              if(at<0||at>1||p<0||p>1||d<0||d>1)
                  JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
              else{
                  int m=(int) (Math.round(f.MASInfinito(at, p, d)));
                  MASIsaln.setText("Submuestra n :"+Integer.toString(m));
                  String[] s={MASIentA.getText(),MASIentP.getText(),MASIentD.getText(),Integer.toString(m)};
                  DefaultTableModel temp=(DefaultTableModel) MASITabla.getModel();
                                        temp.addRow(s);
                                        MASITabla.setModel(temp);
                                        componentesTabla(MASITabla);
                                        this.lineasTabla(MASITabla);
                                       }
            }
    }//GEN-LAST:event_MASIcalcActionPerformed

    private void DDPlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPlessfilaActionPerformed
this.lessFila(this.DDPTabla);
    }//GEN-LAST:event_DDPlessfilaActionPerformed

    private void DDPLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPLtablaActionPerformed
this.limpiarTabla(this.DDPTabla);
    }//GEN-LAST:event_DDPLtablaActionPerformed

    private void DDPTpoissonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPTpoissonActionPerformed
   URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/poisson.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DDPTpoissonActionPerformed

    private void DDPLcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPLcamposActionPerformed
        DDPentX.setText(null);
        DDPentLanda.setText(null);
        this.graficaDDP.limpiar();
    }//GEN-LAST:event_DDPLcamposActionPerformed

    private void DDPCalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPCalcActionPerformed
if(DDPentX.getText().isEmpty()||DDPentLanda.getText().isEmpty())
            JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
            else{
                 int x=0;
                 double at=0;
                x+=Integer.valueOf(DDPentX.getText());
                at+=Double.valueOf(DDPentLanda.getText());
                if(x<=0||at<=0)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
                else{
                    double vp=this.redondeo(f.poissonVp(x, at));
                    double mnvp=this.redondeo(f.poissonVpMenor(x, at));
                    double myvp=this.redondeo(f.poissonVpMayor(x, at));
                    if(((String) DDPmodo.getSelectedItem()).equals("P(X=x)")){
                    DDPsalVp.setText("Valor p :"+Double.toString(vp));
                     parse.exp("poissonVp(x,"+Double.toString(at)+")");
                double[] xx=parse.rango(0, x+1, x);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.evalP(xx,x);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDP, xx, yy, "P(X="+Double.toString(x)+")");
                    }
                    else if(((String) DDPmodo.getSelectedItem()).equals("P(X≤x)")){
                    DDPsalVp.setText("Valor p :"+Double.toString(mnvp));
                    parse.exp("poissonVpMenor(x,"+Double.toString(at)+")");
                double[] xx=parse.rango(0, x, 1);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDP, xx, yy, "P(X≤"+Double.toString(x)+")");
                    }
                    else if(((String) DDPmodo.getSelectedItem()).equals("P(X≥x)")){
                    DDPsalVp.setText("Valor p :"+Double.toString(myvp));
                    parse.exp("poissonVpMayor(x,"+Double.toString(at)+")");
                double[] xx=parse.rango(x, x*2, 1);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.eval(xx);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDP, xx, yy, "P(X≥"+Double.toString(x)+")");
                    }
                    String[] s={DDPentX.getText(),DDPentLanda.getText(),Double.toString(vp),Double.toString(mnvp),Double.toString(myvp)};
                    DefaultTableModel temp=(DefaultTableModel) DDPTabla.getModel();
                        temp.addRow(s);
                        DDPTabla.setModel(temp);
                        componentesTabla(DDPTabla);
                        this.lineasTabla(DDPTabla);
                    }
                }
    }//GEN-LAST:event_DDPCalcActionPerformed

    private void jMenuItem1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem1ActionPerformed
   cred.setLocationRelativeTo(this);
        cred.setVisible(true);
    }//GEN-LAST:event_jMenuItem1ActionPerformed

    private void M_cerrarActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_M_cerrarActionPerformed
    System.exit(0);
    }//GEN-LAST:event_M_cerrarActionPerformed

    private void DDGLessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGLessfilaActionPerformed
this.lessFila(this.DDGTabla);
    }//GEN-LAST:event_DDGLessfilaActionPerformed

    private void DDGLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGLtablaActionPerformed
this.limpiarTabla(this.DDGTabla);
    }//GEN-LAST:event_DDGLtablaActionPerformed

    private void DDGentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDGentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDGentXKeyTyped

    private void DDGentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDGentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDGentPKeyTyped

    private void DDHentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDHentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDHentXKeyTyped

    private void DDHentNKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDHentNKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDHentNKeyTyped

    private void DDHentnKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDHentnKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDHentnKeyTyped

    private void DDHentKKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDHentKKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDHentKKeyTyped

    private void DDPentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDPentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDPentXKeyTyped

    private void DDPentLandaKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDPentLandaKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDPentLandaKeyTyped

    private void DCUentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCUentXKeyTyped
     validarN(evt);
    }//GEN-LAST:event_DCUentXKeyTyped

    private void DCUentAKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCUentAKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCUentAKeyTyped

    private void DCUentBKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCUentBKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCUentBKeyTyped

    private void DCNentZKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCNentZKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCNentZKeyTyped

    private void DCNentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCNentPKeyTyped
   validarN(evt);
    }//GEN-LAST:event_DCNentPKeyTyped

    private void DCCentV1KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCCentV1KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCCentV1KeyTyped

    private void DCCentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCCentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCCentXKeyTyped

    private void DCCentV2KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCCentV2KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCCentV2KeyTyped

    private void DCCentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCCentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCCentPKeyTyped

    private void DCEentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCEentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCEentXKeyTyped

    private void DCEentLanda1KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCEentLanda1KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCEentLanda1KeyTyped

    private void DCEentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCEentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCEentPKeyTyped

    private void DCEentLanda2KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCEentLanda2KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCEentLanda2KeyTyped

    private void DCFentV1KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentV1KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentV1KeyTyped

    private void DCFentV2KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentV2KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentV2KeyTyped

    private void DCFentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentXKeyTyped

    private void DCFentV3KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentV3KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentV3KeyTyped

    private void DCFentV4KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentV4KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentV4KeyTyped

    private void DCFentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCFentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCFentPKeyTyped

    private void DCTentV1KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCTentV1KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCTentV1KeyTyped

    private void DCTentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCTentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCTentXKeyTyped

    private void DCTentV2KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCTentV2KeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCTentV2KeyTyped

    private void DCTentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DCTentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DCTentPKeyTyped

    private void MASFentNKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentNKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASFentNKeyTyped

    private void MASFentAKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentAKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASFentAKeyTyped

    private void MASFentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASFentPKeyTyped

    private void MASFentDKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentDKeyTyped
     validarN(evt);
    }//GEN-LAST:event_MASFentDKeyTyped

    private void MASFentN1KeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentN1KeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASFentN1KeyTyped

    private void MASFentnKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASFentnKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASFentnKeyTyped

    private void MASIentAKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASIentAKeyTyped
   validarN(evt);
    }//GEN-LAST:event_MASIentAKeyTyped

    private void MASIentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASIentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASIentPKeyTyped

    private void MASIentDKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASIentDKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASIentDKeyTyped

    private void MASEentnKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_MASEentnKeyTyped
    validarN(evt);
    }//GEN-LAST:event_MASEentnKeyTyped

    private void DDBNentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBNentXKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDBNentXKeyTyped

    private void DDBNLcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNLcamposActionPerformed
    DDBNentX.setText(null);
    DDBNentR.setText(null);
    DDBNentP.setText(null);
    this.graficaDDBN.limpiar();
    }//GEN-LAST:event_DDBNLcamposActionPerformed

    private void DDBNentRKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBNentRKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDBNentRKeyTyped

    private void DDBNentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBNentPKeyTyped
    validarN(evt);
    }//GEN-LAST:event_DDBNentPKeyTyped

    private void DDBNcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNcalcActionPerformed
 if(DDBNentX.getText().isEmpty()||DDBNentR.getText().isEmpty()||DDBNentP.getText().isEmpty())
          JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
          else{
            double x=0;
            double r=0;
            double p=0;
              x+=Double.valueOf(DDBNentX.getText());
              r+=Double.valueOf(DDBNentR.getText());
              p+=Double.valueOf(DDBNentP.getText());
              if(x<=0||r<=0||p<0||p>1)
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
                else{
                  double vp=this.redondeo(f.binomialNVp(x, r, p));
                  double md=this.redondeo(f.binomialNMedia(r, p));
                  double vr=this.redondeo(f.binomialNVarianza(r, p));
                          DDBNsalVp.setText("Valor p :"+Double.toString(vp));
                          DDBNsalM.setText("Media :"+Double.toString(md));
                          DDBNsalV.setText("Varianza :"+Double.toString(vr));
                          parse.exp("binomialNVp(x,"+Double.toString(r)+","+Double.toString(p)+")");
                double[] xx=parse.rango(0, x+1, x);
                double[] yy=new double[xx.length];
                try {
                    yy=parse.evalP(xx, x);
                } catch (Exception ex) {
                    Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                }
                this.graficar(graficaDDBN, xx, yy, "(P="+Double.toString(x)+")");
                String[] s={DDBNentX.getText(),DDBNentR.getText(),DDBNentP.getText(),Double.toString(vp),Double.toString(md),Double.toString(vr)};
                    DefaultTableModel temp=(DefaultTableModel) DDBNTabla.getModel();
                        temp.addRow(s);
                        DDBNTabla.setModel(temp);
                        componentesTabla(DDBNTabla);
                        this.lineasTabla(this.DDBNTabla);
                    }            
             }
    }//GEN-LAST:event_DDBNcalcActionPerformed

    private void DDBNCexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNCexcelActionPerformed
    this.exportar(this.DDBNTabla, "Binomial negativa");
    }//GEN-LAST:event_DDBNCexcelActionPerformed

    private void DDBNLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNLtablaActionPerformed
this.limpiarTabla(this.DDBNTabla);
    }//GEN-LAST:event_DDBNLtablaActionPerformed

    private void DDBNlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNlessfilaActionPerformed
this.lessFila(this.DDBNTabla);
    }//GEN-LAST:event_DDBNlessfilaActionPerformed

    private void DDBNTbimonialNActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBNTbimonialNActionPerformed
   URL url = null;
            try {
                url = new URL(getClass().getResource("/teoriahtml/binomialN.html").toURI().toString());
            } catch (URISyntaxException | MalformedURLException ex ) {
                Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
            }
            teoria(url);
    }//GEN-LAST:event_DDBNTbimonialNActionPerformed

    private void DDMTablaKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDMTablaKeyTyped
  
    }//GEN-LAST:event_DDMTablaKeyTyped

    private void DDGCexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDGCexcelActionPerformed
    this.exportar(this.DDGTabla, "Geométrica");
    }//GEN-LAST:event_DDGCexcelActionPerformed

    private void DDHCexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDHCexcelActionPerformed
    this.exportar(this.DDHTabla, "Hipergeométrica");
    }//GEN-LAST:event_DDHCexcelActionPerformed

    private void DDPLtabla1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDPLtabla1ActionPerformed
    this.exportar(this.DDPTabla, "Poisson");
    }//GEN-LAST:event_DDPLtabla1ActionPerformed

    private void DDBCexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBCexcelActionPerformed
        this.exportar(this.DDBTabla, "Binomial");
    }//GEN-LAST:event_DDBCexcelActionPerformed

    private void DDBTbimonialNActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBTbimonialNActionPerformed
        URL url = null;
        try {
            url = new URL(getClass().getResource("/teoriahtml/binomial.html").toURI().toString());
        } catch (URISyntaxException | MalformedURLException ex ) {
            Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
        }
        teoria(url);
    }//GEN-LAST:event_DDBTbimonialNActionPerformed

    private void DDBlessfilaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBlessfilaActionPerformed
        this.lessFila(this.DDBTabla);
    }//GEN-LAST:event_DDBlessfilaActionPerformed

    private void DDBLtablaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBLtablaActionPerformed
        this.limpiarTabla(this.DDBTabla);
    }//GEN-LAST:event_DDBLtablaActionPerformed

    private void DDBLcamposActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBLcamposActionPerformed
        DDBentX.setText(null);
        DDBentN.setText(null);
        DDBentP.setText(null);
        this.graficaDDB.limpiar();
    }//GEN-LAST:event_DDBLcamposActionPerformed

    private void DDBcalcActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DDBcalcActionPerformed

        if(DDBentN.getText().isEmpty()||DDBentP.getText().isEmpty()||DDBentX.getText().isEmpty()){
            JOptionPane.showMessageDialog(null, "Llene todos los campos", null, JOptionPane.ERROR_MESSAGE);
        }
        else{
            int x=Integer.parseInt(DDBentX.getText());
            int n=Integer.parseInt(DDBentN.getText());
            double p=Double.parseDouble(DDBentP.getText());
            if(x<0||n<0||p<0||p>1){
                JOptionPane.showMessageDialog(null, "Valores incorrectos", null, JOptionPane.ERROR_MESSAGE);
            }else if(x>n){
                JOptionPane.showMessageDialog(null, "x no debe exeder a n", null, JOptionPane.ERROR_MESSAGE);
            }else{
                double vp=this.redondeo(f.binomialVp(x, n, p));
                double mnvp=this.redondeo(f.binomialVpMenor(x,n,p));
                double myvp=this.redondeo(f.binomialVpMayor(x,n,p));
                double md=this.redondeo(f.binomialMedia(n,p));
                double vr=this.redondeo(f.binomialVarianza(n,p));
                if(((String) DDBmodo.getSelectedItem()).equals("P(X=x)")){
                    DDBsalVp.setText("Valor p : "+Double.toString(vp));
                    parse.exp("binomialVp(x,"+Integer.toString(n)+","+Double.toString(p)+")");
                    double[] xx=parse.rango(0, x+1, x);
                    double[] yy=new double[xx.length];
                    try {
                        yy=parse.evalP(xx, x);
                    } catch (Exception ex) {
                        Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    graficar(this.graficaDDB,xx,yy,"P(X="+Integer.toString(x)+")");
                }
                else if(((String) DDBmodo.getSelectedItem()).equals("P(X≤x)")){
                    DDBsalVp.setText("Valor p : "+Double.toString(mnvp));
                    parse.exp("binomialVpMenor(x,"+Integer.toString(n)+","+Double.toString(p)+")");
                    double[] xx=parse.rango(0, x, 1);
                    double[] yy=new double[xx.length];
                    try {
                        yy=parse.eval(xx);
                    } catch (Exception ex) {
                        Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    graficar(this.graficaDDB,xx,yy,"P(X≤"+Integer.toString(x)+")");
                }
                else if(((String) DDBmodo.getSelectedItem()).equals("P(X≥x)")){
                    DDBsalVp.setText("Valor p : "+Double.toString(myvp));
                    parse.exp("binomialVpMayor(x,"+Integer.toString(n)+","+Double.toString(p)+")");
                    double[] xx=parse.rango(x, n, 1);
                    double[] yy=new double[xx.length];
                    try {
                        yy=parse.eval(xx);
                    } catch (Exception ex) {
                        Logger.getLogger(Interfaz.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    graficar(this.graficaDDB,xx,yy,"P(X≥"+Integer.toString(x)+")");
                }
                DDBsalM.setText("Media : "+Double.toString(md));
                DDBsalV.setText("Varianza : "+Double.toString(vr));
                String[] s={DDBentX.getText(),DDBentN.getText(),DDBentP.getText(),Double.toString(vp),Double.toString(mnvp),Double.toString(myvp),Double.toString(md),Double.toString(vr)};
                DefaultTableModel temp=(DefaultTableModel) DDBTabla.getModel();
                temp.addRow(s);
                DDBTabla.setModel(temp);
                componentesTabla(DDBTabla);
                this.lineasTabla(DDBTabla);
            }
        }
    }//GEN-LAST:event_DDBcalcActionPerformed

    private void DDBentPKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBentPKeyTyped
        validarN(evt);
    }//GEN-LAST:event_DDBentPKeyTyped

    private void DDBentNKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBentNKeyTyped
        validarN(evt);
    }//GEN-LAST:event_DDBentNKeyTyped

    private void DDBentXKeyTyped(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_DDBentXKeyTyped
        validarN(evt);
    }//GEN-LAST:event_DDBentXKeyTyped

    private void DCU_CexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_DCU_CexcelActionPerformed
    this.exportar(this.DCUTabla, "Uniforme");
    }//GEN-LAST:event_DCU_CexcelActionPerformed

    private void MASFCexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFCexcelActionPerformed
    this.exportar(this.MASFTabla1, "MAS finito");
    }//GEN-LAST:event_MASFCexcelActionPerformed

    private void MASFCexcel2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASFCexcel2ActionPerformed
    this.exportar(this.MASFTabla2, "Submuestra");
    }//GEN-LAST:event_MASFCexcel2ActionPerformed

    private void MASICexcelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MASICexcelActionPerformed
    this.exportar(this.MASITabla, "MAS infinito");
    }//GEN-LAST:event_MASICexcelActionPerformed
          
    /**
     * @param args the command line arguments
     */
    public static void main(String args[]) {
        /* Set the Nimbus look and feel */
        //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
        /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
         * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html 
         */
        try {
            for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    javax.swing.UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException | javax.swing.UnsupportedLookAndFeelException ex) {
            java.util.logging.Logger.getLogger(Interfaz.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        }
        //</editor-fold>

        /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new Interfaz().setVisible(true);
            }
        });
    }

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton DCCLcampos1;
    private javax.swing.JButton DCCLcamposp2;
    private javax.swing.JButton DCCTchicuadrado;
    private javax.swing.JComboBox DCC_AIvp;
    private javax.swing.JComboBox DCC_AIvx;
    private javax.swing.JPanel DCC_Grafico;
    private javax.swing.JButton DCCcalcp;
    private javax.swing.JButton DCCcalcx;
    private javax.swing.JTextField DCCentP;
    private javax.swing.JTextField DCCentV1;
    private javax.swing.JTextField DCCentV2;
    private javax.swing.JTextField DCCentX;
    private javax.swing.JLabel DCCsalVp;
    private javax.swing.JLabel DCCsalX;
    private javax.swing.JButton DCELcampos1;
    private javax.swing.JButton DCELcampos2;
    private javax.swing.JButton DCETexponencial;
    private javax.swing.JComboBox DCE_AIvp;
    private javax.swing.JComboBox DCE_AIvx;
    private javax.swing.JPanel DCE_Grafico;
    private javax.swing.JButton DCEcalcp;
    private javax.swing.JButton DCEcalcx;
    private javax.swing.JTextField DCEentLanda1;
    private javax.swing.JTextField DCEentLanda2;
    private javax.swing.JTextField DCEentP;
    private javax.swing.JTextField DCEentX;
    private javax.swing.JLabel DCEsalVp;
    private javax.swing.JLabel DCEsalX;
    private javax.swing.JButton DCFLcampos1;
    private javax.swing.JButton DCFLcampos2;
    private javax.swing.JButton DCFTfisher;
    private javax.swing.JComboBox DCF_AIvp;
    private javax.swing.JComboBox DCF_AIvx;
    private javax.swing.JPanel DCF_Grafico;
    private javax.swing.JButton DCFcalcp;
    private javax.swing.JButton DCFcalcx;
    private javax.swing.JTextField DCFentP;
    private javax.swing.JTextField DCFentV1;
    private javax.swing.JTextField DCFentV2;
    private javax.swing.JTextField DCFentV3;
    private javax.swing.JTextField DCFentV4;
    private javax.swing.JTextField DCFentX;
    private javax.swing.JLabel DCFsalVp;
    private javax.swing.JLabel DCFsalVx;
    private javax.swing.JButton DCNLcamposp;
    private javax.swing.JButton DCNLcamposz;
    private javax.swing.JButton DCNTnormal;
    private javax.swing.JComboBox DCN_AIvp;
    private javax.swing.JComboBox DCN_AIvz;
    private javax.swing.JPanel DCN_Grafico;
    private javax.swing.JLabel DCN_guia;
    private javax.swing.JButton DCNcalcp;
    private javax.swing.JButton DCNcalcx;
    private javax.swing.JTextField DCNentP;
    private javax.swing.JTextField DCNentZ;
    private javax.swing.JLabel DCNsalVp;
    private javax.swing.JLabel DCNsalVz;
    private javax.swing.JButton DCTLcampos1;
    private javax.swing.JButton DCTLcampos2;
    private javax.swing.JButton DCTTstudent;
    private javax.swing.JComboBox DCT_AIvp;
    private javax.swing.JComboBox DCT_AIvx;
    private javax.swing.JPanel DCT_Grafico;
    private javax.swing.JButton DCTcalcp;
    private javax.swing.JButton DCTcalcx;
    private javax.swing.JTextField DCTentP;
    private javax.swing.JTextField DCTentV1;
    private javax.swing.JTextField DCTentV2;
    private javax.swing.JTextField DCTentX;
    private javax.swing.JLabel DCTsalVp;
    private javax.swing.JLabel DCTsalX;
    private javax.swing.JButton DCULcampos;
    private javax.swing.JButton DCULtabla;
    private javax.swing.JTable DCUTabla;
    private javax.swing.JButton DCUTuniformec;
    private javax.swing.JComboBox DCU_AIvp;
    private javax.swing.JButton DCU_Cexcel;
    private javax.swing.JPanel DCU_Grafico;
    private javax.swing.JButton DCUcalc;
    private javax.swing.JTextField DCUentA;
    private javax.swing.JTextField DCUentB;
    private javax.swing.JTextField DCUentX;
    private javax.swing.JButton DCUlessfila;
    private javax.swing.JLabel DCUsalDesv;
    private javax.swing.JLabel DCUsalF;
    private javax.swing.JLabel DCUsalM;
    private javax.swing.JLabel DCUsalVp;
    public javax.swing.JButton DDBCexcel;
    private javax.swing.JButton DDBLcampos;
    private javax.swing.JButton DDBLtabla;
    public javax.swing.JButton DDBNCexcel;
    private javax.swing.JButton DDBNLcampos;
    private javax.swing.JButton DDBNLtabla;
    public javax.swing.JTable DDBNTabla;
    private javax.swing.JButton DDBNTbimonialN;
    private javax.swing.JPanel DDBN_Grafico;
    private javax.swing.JButton DDBNcalc;
    private javax.swing.JTextField DDBNentP;
    private javax.swing.JTextField DDBNentR;
    private javax.swing.JTextField DDBNentX;
    private javax.swing.JButton DDBNlessfila;
    private javax.swing.JLabel DDBNsalM;
    private javax.swing.JLabel DDBNsalV;
    private javax.swing.JLabel DDBNsalVp;
    public javax.swing.JTable DDBTabla;
    private javax.swing.JButton DDBTbimonialN;
    private javax.swing.JPanel DDB_Grafico;
    private javax.swing.JButton DDBcalc;
    private javax.swing.JTextField DDBentN;
    private javax.swing.JTextField DDBentP;
    private javax.swing.JTextField DDBentX;
    private javax.swing.JButton DDBlessfila;
    private javax.swing.JComboBox DDBmodo;
    private javax.swing.JLabel DDBsalM;
    private javax.swing.JLabel DDBsalV;
    private javax.swing.JLabel DDBsalVp;
    private javax.swing.JButton DDGCalc;
    private javax.swing.JButton DDGCexcel;
    private javax.swing.JButton DDGLcampos;
    private javax.swing.JButton DDGLessfila;
    private javax.swing.JButton DDGLtabla;
    private javax.swing.JTable DDGTabla;
    private javax.swing.JButton DDGTgeo;
    private javax.swing.JPanel DDG_Grafico;
    private javax.swing.JTextField DDGentP;
    private javax.swing.JTextField DDGentX;
    private javax.swing.JLabel DDGsalM;
    private javax.swing.JLabel DDGsalV;
    private javax.swing.JLabel DDGsalVp;
    private javax.swing.JButton DDHCexcel;
    private javax.swing.JButton DDHLcampos;
    private javax.swing.JButton DDHLtabla;
    private javax.swing.JTable DDHTabla;
    private javax.swing.JButton DDHThiper;
    private javax.swing.JPanel DDH_Grafico;
    private javax.swing.JButton DDHcalc;
    private javax.swing.JTextField DDHentK;
    private javax.swing.JTextField DDHentN;
    private javax.swing.JTextField DDHentX;
    private javax.swing.JTextField DDHentn;
    private javax.swing.JButton DDHlessfila;
    private javax.swing.JComboBox DDHmodo;
    private javax.swing.JLabel DDHsalM;
    private javax.swing.JLabel DDHsalV;
    private javax.swing.JLabel DDHsalVp;
    private javax.swing.JButton DDMAddTabla;
    private javax.swing.JButton DDMCalc;
    private javax.swing.JButton DDMLessTabla;
    private javax.swing.JButton DDMLtabla;
    private javax.swing.JTable DDMTabla;
    private javax.swing.JButton DDMTeoria;
    private javax.swing.JLabel DDMVpsal;
    private javax.swing.JPanel DDM_Grafico;
    private javax.swing.JButton DDPCalc;
    private javax.swing.JButton DDPLcampos;
    private javax.swing.JButton DDPLtabla;
    private javax.swing.JButton DDPLtabla1;
    private javax.swing.JTable DDPTabla;
    private javax.swing.JButton DDPTpoisson;
    private javax.swing.JPanel DDP_Grafico;
    private javax.swing.JTextField DDPentLanda;
    private javax.swing.JTextField DDPentX;
    private javax.swing.JButton DDPlessfila;
    private javax.swing.JComboBox DDPmodo;
    private javax.swing.JLabel DDPsalVp;
    private javax.swing.JTabbedPane D_Con;
    private javax.swing.JTabbedPane D_Dis;
    private javax.swing.JTabbedPane Func;
    private javax.swing.JButton MASEAddE;
    private javax.swing.JButton MASELTabla;
    private javax.swing.JButton MASELessE;
    private javax.swing.JTable MASETabla;
    private javax.swing.JButton MASETestratificado;
    private javax.swing.JButton MASEcalc;
    private javax.swing.JTextField MASEentn;
    private javax.swing.JButton MASFCexcel;
    private javax.swing.JButton MASFCexcel2;
    private javax.swing.JButton MASFLcampos1;
    private javax.swing.JButton MASFLcampos2;
    private javax.swing.JButton MASFLtabla;
    private javax.swing.JTable MASFTabla1;
    private javax.swing.JTable MASFTabla2;
    private javax.swing.JButton MASFTfinito;
    private javax.swing.JButton MASFcalc;
    private javax.swing.JTextField MASFentA;
    private javax.swing.JTextField MASFentD;
    private javax.swing.JTextField MASFentN;
    private javax.swing.JTextField MASFentN1;
    private javax.swing.JTextField MASFentP;
    private javax.swing.JTextField MASFentn;
    private javax.swing.JButton MASFlessfila;
    private javax.swing.JLabel MASFsaln;
    private javax.swing.JButton MASFselec;
    private javax.swing.JButton MASICexcel;
    private javax.swing.JButton MASILTabla;
    private javax.swing.JButton MASILcampos;
    private javax.swing.JButton MASILessfila;
    private javax.swing.JTable MASITabla;
    private javax.swing.JButton MASITinfinnito;
    private javax.swing.JButton MASIcalc;
    private javax.swing.JTextField MASIentA;
    private javax.swing.JTextField MASIentD;
    private javax.swing.JTextField MASIentP;
    private javax.swing.JLabel MASIsaln;
    private javax.swing.JMenuItem M_TPantalla;
    private javax.swing.JMenu M_archivo;
    private javax.swing.JMenuItem M_calculadora;
    private javax.swing.JMenuItem M_cerrar;
    private javax.swing.JMenu M_herramientas;
    private javax.swing.JMenu M_soporte;
    private javax.swing.JTabbedPane Muest;
    private javax.swing.JPanel Panel_ASFinito;
    private javax.swing.JPanel Panel_ASInfinito;
    private javax.swing.JPanel Panel_Bino;
    private javax.swing.JPanel Panel_Bino_Neg;
    private javax.swing.JPanel Panel_ChiCuad;
    private javax.swing.JPanel Panel_Estrat;
    private javax.swing.JPanel Panel_Expo;
    private javax.swing.JPanel Panel_FFisher;
    private javax.swing.JPanel Panel_Geo;
    private javax.swing.JPanel Panel_Hipergeo;
    private javax.swing.JPanel Panel_Multino;
    private javax.swing.JPanel Panel_NEst;
    private javax.swing.JPanel Panel_Poisson;
    private javax.swing.JPanel Panel_TStudent;
    private javax.swing.JPanel Panel_UCont;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel12;
    private javax.swing.JLabel jLabel13;
    private javax.swing.JLabel jLabel14;
    private javax.swing.JLabel jLabel15;
    private javax.swing.JLabel jLabel16;
    private javax.swing.JLabel jLabel17;
    private javax.swing.JLabel jLabel18;
    private javax.swing.JLabel jLabel19;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel20;
    private javax.swing.JLabel jLabel21;
    private javax.swing.JLabel jLabel22;
    private javax.swing.JLabel jLabel23;
    private javax.swing.JLabel jLabel26;
    private javax.swing.JLabel jLabel27;
    private javax.swing.JLabel jLabel29;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel30;
    private javax.swing.JLabel jLabel31;
    private javax.swing.JLabel jLabel32;
    private javax.swing.JLabel jLabel34;
    private javax.swing.JLabel jLabel35;
    private javax.swing.JLabel jLabel36;
    private javax.swing.JLabel jLabel37;
    private javax.swing.JLabel jLabel39;
    private javax.swing.JLabel jLabel40;
    private javax.swing.JLabel jLabel42;
    private javax.swing.JLabel jLabel43;
    private javax.swing.JLabel jLabel44;
    private javax.swing.JLabel jLabel45;
    private javax.swing.JLabel jLabel46;
    private javax.swing.JLabel jLabel47;
    private javax.swing.JLabel jLabel48;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel50;
    private javax.swing.JLabel jLabel52;
    private javax.swing.JLabel jLabel53;
    private javax.swing.JLabel jLabel54;
    private javax.swing.JLabel jLabel55;
    private javax.swing.JLabel jLabel57;
    private javax.swing.JLabel jLabel58;
    private javax.swing.JLabel jLabel59;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel61;
    private javax.swing.JLabel jLabel69;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel70;
    private javax.swing.JLabel jLabel71;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JMenuBar jMenuBar1;
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane11;
    private javax.swing.JScrollPane jScrollPane12;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JScrollPane jScrollPane7;
    private javax.swing.JScrollPane jScrollPane8;
    private javax.swing.JScrollPane jScrollPane9;
    private javax.swing.JSeparator jSeparator1;
    private javax.swing.JSeparator jSeparator10;
    private javax.swing.JSeparator jSeparator15;
    private javax.swing.JSeparator jSeparator2;
    private javax.swing.JSeparator jSeparator3;
    private javax.swing.JSeparator jSeparator4;
    private javax.swing.JSeparator jSeparator5;
    private javax.swing.JSeparator jSeparator6;
    private javax.swing.JSeparator jSeparator7;
    private javax.swing.JSeparator jSeparator8;
    private javax.swing.JSeparator jSeparator9;
    // End of variables declaration//GEN-END:variables
Graficos graficaDDB=new Graficos(null,"x","y");
Graficos graficaDDBN=new Graficos(null,"x","y");
Graficos graficaDDM=new Graficos(null,"x","y");
Graficos graficaDDG=new Graficos(null,"x","y");
Graficos graficaDDH=new Graficos(null,"x","y");
Graficos graficaDDP=new Graficos(null,"x","y");
Graficos graficaDCU=new Graficos(null,"x","y");
Graficos graficaDCN=new Graficos(null,"x","y");
Graficos graficaDCC=new Graficos(null,"x","y");
Graficos graficaDCE=new Graficos(null,"x","y");
Graficos graficaDCF=new Graficos(null,"x","y");
Graficos graficaDCT=new Graficos(null,"x","y");
}

