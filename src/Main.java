
import visual.pant_inicio;
/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author 666
 */
public class Main {
public Main(){
    
}
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
         try {
            for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    javax.swing.UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException | javax.swing.UnsupportedLookAndFeelException ex) {
            java.util.logging.Logger.getLogger(pant_inicio.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        }
       pant_inicio pi=new pant_inicio();
       pi.setLocationRelativeTo(null);
       pi.setVisible(true);
    }
    
}
