/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package Clases;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author 666
 */
public class FuncionesTest {
    
    public FuncionesTest() {
    }
    
    @BeforeClass
    public static void setUpClass() {
    }
    
    @AfterClass
    public static void tearDownClass() {
    }
    
    @Before
    public void setUp() {
    }
    
    @After
    public void tearDown() {
    }
     public double redondeo(double x){
        return Math.rint(x*10000)/10000;
    }
    /**
     * Test of binomialVp method, of class Funciones.
     */
    @Test
    public void testBinomialVp() {
        System.out.println("binomialVp");
        double x = 5.0;
        double n = 10.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.2461;
        double result = this.redondeo(instance.binomialVp(x, n, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
       if(result!=expResult){
            fail("The test case is a prototype.");
       }
    }

    /**
     * Test of binomialVpMenor method, of class Funciones.
     */
    @Test
    public void testBinomialVpMenor() {
        System.out.println("binomialVpMenor");
        double x = 5.0;
        double n = 10.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.623;
        double result = this.redondeo(instance.binomialVpMenor(x, n, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialVpMayor method, of class Funciones.
     */
    @Test
    public void testBinomialVpMayor() {
        System.out.println("binomialVpMayor");
        double x = 5.0;
        double n = 10.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.623;
        double result = this.redondeo(instance.binomialVpMayor(x, n, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialMedia method, of class Funciones.
     */
    @Test
    public void testBinomialMedia() {
        System.out.println("binomialMedia");
        double n = 10.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 5.0;
        double result = this.redondeo(instance.binomialMedia(n, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialVarianza method, of class Funciones.
     */
    @Test
    public void testBinomialVarianza() {
        System.out.println("binomialVarianza");
        double n = 10.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 2.5;
        double result = this.redondeo(instance.binomialVarianza(n, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialNVp method, of class Funciones.
     */
    @Test
    public void testBinomialNVp() {
        System.out.println("binomialNVp");
        double x = 3.0;
        double r = 2.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.125;
        double result = this.redondeo(instance.binomialNVp(x, r, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialNMedia method, of class Funciones.
     */
    @Test
    public void testBinomialNMedia() {
        System.out.println("binomialNMedia");
        double r = 2.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 2.0;
        double result = this.redondeo(instance.binomialNMedia(r, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of binomialNVarianza method, of class Funciones.
     */
    @Test
    public void testBinomialNVarianza() {
        System.out.println("binomialNVarianza");
        double r = 2.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 4.0;
        double result = this.redondeo(instance.binomialNVarianza(r, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of multinomialVp method, of class Funciones.
     */
    @Test
    public void testMultinomialVp() {
        System.out.println("multinomialVp");
        double N = 5.0;
        double x = 120.0;
        double p = 0.03125;
        Funciones instance = new Funciones();
        double expResult = 0.0312;
        double result = this.redondeo(instance.multinomialVp(N, x, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of geometricaVp method, of class Funciones.
     */
    @Test
    public void testGeometricaVp() {
        System.out.println("geometricaVp");
        double x = 5.0;
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.0312;
        double result = this.redondeo(instance.geometricaVp(x, p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of geometricaMedia method, of class Funciones.
     */
    @Test
    public void testGeometricaMedia() {
        System.out.println("geometricaMedia");
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 2.0;
        double result = this.redondeo(instance.geometricaMedia(p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of geometricaVarianza method, of class Funciones.
     */
    @Test
    public void testGeometricaVarianza() {
        System.out.println("geometricaVarianza");
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 2.0;
        double result = this.redondeo(instance.geometricaVarianza(p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of hipergeometricaVp method, of class Funciones.
     */
    @Test
    public void testHipergeometricaVp() {
        System.out.println("hipergeometricaVp");
        double x = 2.0;
        double N = 6.0;
        double n = 3.0;
        double k = 2.0;
        Funciones instance = new Funciones();
        double expResult = 0.2;
        double result = this.redondeo(instance.hipergeometricaVp(x, N, n, k));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of hipergeometricaVpMenor method, of class Funciones.
     */
    @Test
    public void testHipergeometricaVpMenor() {
        System.out.println("hipergeometricaVpMenor");
        double x = 2.0;
        double N = 6.0;
        double n = 3.0;
        double k = 2.0;
        Funciones instance = new Funciones();
        double expResult = 1.0;
        double result = this.redondeo(instance.hipergeometricaVpMenor(x, N, n, k));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of hipergeometricaVpMayor method, of class Funciones.
     */
    @Test
    public void testHipergeometricaVpMayor() {
        System.out.println("hipergeometricaVpMayor");
        double x = 2.0;
        double N = 6.0;
        double n = 3.0;
        double k = 2.0;
        Funciones instance = new Funciones();
        double expResult = 0.2;
        double result = this.redondeo(instance.hipergeometricaVpMayor(x, N, n, k));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of hipergeometricaMedia method, of class Funciones.
     */
    @Test
    public void testHipergeometricaMedia() {
        System.out.println("hipergeometricaMedia");
        double N = 6.0;
        double n = 3.0;
        double k = 2.0;
        Funciones instance = new Funciones();
        double expResult = 1.0;
        double result = this.redondeo(instance.hipergeometricaMedia(N, n, k));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of hipergeometricaVarianza method, of class Funciones.
     */
    @Test
    public void testHipergeometricaVarianza() {
        System.out.println("hipergeometricaVarianza");
        double N = 6.0;
        double n = 3.0;
        double k = 2.0;
        Funciones instance = new Funciones();
        double expResult = 0.4;
        double result = this.redondeo(instance.hipergeometricaVarianza(N, n, k));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of poissonVp method, of class Funciones.
     */
    @Test
    public void testPoissonVp() {
        System.out.println("poissonVp");
        double x = 5.0;
        double at = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.0031;
        double result = this.redondeo(instance.poissonVp(x, at));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of poissonVpMenor method, of class Funciones.
     */
    @Test
    public void testPoissonVpMenor() {
        System.out.println("poissonVpMenor");
        double x = 5.0;
        double at = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.9994;
        double result = this.redondeo(instance.poissonVpMenor(x, at));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of poissonVpMayor method, of class Funciones.
     */
    @Test
    public void testPoissonVpMayor() {
        System.out.println("poissonVpMayor");
        double x = 5.0;
        double at = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.0037;
        double result = this.redondeo(instance.poissonVpMayor(x, at));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of UniformeF method, of class Funciones.
     */
    @Test
    public void testUniformeF() {
        System.out.println("UniformeF");
        double a = 1.0;
        double b = 5.0;
        Funciones instance = new Funciones();
        double expResult = 0.25;
        double result = this.redondeo(instance.UniformeF(a, b));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of UniformeVp method, of class Funciones.
     */
    @Test
    public void testUniformeVp() {
        System.out.println("UniformeVp");
        double a = 1.0;
        double b = 3.0;
        Funciones instance = new Funciones();
        double expResult = 1.0;
        double result = this.redondeo(instance.UniformeVp(a, b));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of UniformeMedia method, of class Funciones.
     */
    @Test
    public void testUniformeMedia() {
        System.out.println("UniformeMedia");
        double a = 1.0;
        double b = 5.0;
        Funciones instance = new Funciones();
        double expResult = 3.0;
        double result = this.redondeo(instance.UniformeMedia(a, b));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of UniformeDes method, of class Funciones.
     */
    @Test
    public void testUniformeDes() {
        System.out.println("UniformeDes");
        double a = 1.0;
        double b = 5.0;
        Funciones instance = new Funciones();
        double expResult = 1.7321;
        double result = this.redondeo(instance.UniformeDes(a, b));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of NormalF method, of class Funciones.
     */
   
    /**
     * Test of NormalVp method, of class Funciones.
     */
    @Test
    public void testNormalVp() {
        System.out.println("NormalVp");
        double z = 2.0;
        Funciones instance = new Funciones();
        double expResult = 0.9772;
        double result = this.redondeo(instance.NormalVp(z));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
        if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of NormalBiseccion method, of class Funciones.
     */
    @Test
    public void testNormalBiseccion() {
        System.out.println("NormalBiseccion");
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 0.0;
        double result = this.redondeo(instance.NormalBiseccion(p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of ExponencialF method, of class Funciones.
     */
 
    /**
     * Test of ExponencialVp method, of class Funciones.
     */
    @Test
    public void testExponencialVp() {
        System.out.println("ExponencialVp");
        double x = 4.0;
        double a = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.0183;
        double result = this.redondeo(1-instance.ExponencialVp(x, a));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of ExponencialVx method, of class Funciones.
     */
    @Test
    public void testExponencialVx() {
        System.out.println("ExponencialVx");
        double p = 0.5;
        double a = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.3069;
        double result = this.redondeo(1-instance.ExponencialVx(p, a));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of JiF method, of class Funciones.
     */
  
    /**
     * Test of JiVp method, of class Funciones.
     */
    @Test
    public void testJiVp() {
        System.out.println("JiVp");
        double x = 1.0;
        double v = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.3173;
        double result = this.redondeo(instance.JiVp(x, v));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of JiBiseccion method, of class Funciones.
     */
    @Test
    public void testJiBiseccion() {
        System.out.println("JiBiseccion");
        double p = 0.5;
        double v = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.4553;
        double result = this.redondeo(instance.JiBiseccion(p, v));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of TstudentF method, of class Funciones.
     */
  
    /**
     * Test of TstudentVp method, of class Funciones.
     */
    @Test
    public void testTstudentVp() {
        System.out.println("TstudentVp");
        double x = 1.0;
        double v = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.9836;
        double result = this.redondeo(instance.TstudentVp(x, v));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of TstudentBiseccion method, of class Funciones.
     */
    @Test
    public void testTstudentBiseccion() {
        System.out.println("TstudentBiseccion");
        double p = 0.5;
        double v = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.4812;
        double result = this.redondeo(instance.TstudentBiseccion(p, v));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherF method, of class Funciones.
     */
   
    /**
     * Test of FdeFisherVp method, of class Funciones.
     */
    @Test
    public void testFdeFisherVp() {
        System.out.println("FdeFisherVp");
        double x = 1.0;
        double v1 = 1.0;
        double v2 = 5.0;
        Funciones instance = new Funciones();
        double expResult = 0.4971;
        double result = this.redondeo(instance.FdeFisherVp(x, v1, v2));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherVp1 method, of class Funciones.
     */
    @Test
    public void testFdeFisherVp1() {
        System.out.println("FdeFisherVp1");
        double x = 1.0;
        double v1 = 5.0;
        double v2 = 5.0;
        Funciones instance = new Funciones();
        double expResult = 0.5755;
        double result = this.redondeo(instance.FdeFisherVp1(x, v1, v2));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherVpp method, of class Funciones.
     */
    @Test
    public void testFdeFisherVpp() {
        System.out.println("FdeFisherVpp");
        double x = 1.0;
        Funciones instance = new Funciones();
        double expResult = 0.5;
        double result = this.redondeo(instance.FdeFisherVpp(x));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherVx method, of class Funciones.
     */
    @Test
    public void testFdeFisherVx() {
        System.out.println("FdeFisherVx");
        double p = 0.5;
        Funciones instance = new Funciones();
        double expResult = 1.0;
        double result = this.redondeo(instance.FdeFisherVx(p));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherBiseccion method, of class Funciones.
     */
    @Test
    public void testFdeFisherBiseccion() {
        System.out.println("FdeFisherBiseccion");
        double p = 0.5;
        double v1 = 1.0;
        double v2 = 5.0;
        Funciones instance = new Funciones();
        double expResult = 0.9407;
        double result = this.redondeo(instance.FdeFisherBiseccion(p, v1, v2));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of FdeFisherBiseccion1 method, of class Funciones.
     */
   
    /**
     * Test of MASFinito method, of class Funciones.
     */
    @Test
    public void testMASFinito() {
        System.out.println("MASFinito");
        int N = 10;
        double alp = 0.5;
        double p = 0.3;
        double d = 0.1;
        Funciones instance = new Funciones();
        double expResult = 10.0;
        double result = (int)(Math.round(instance.MASFinito(N, alp, p, d)));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of MASFinitoSubM method, of class Funciones.
     */
   
    /**
     * Test of MASInfinito method, of class Funciones.
     */
    @Test
    public void testMASInfinito() {
        System.out.println("MASInfinito");
        double alp = 0.5;
        double p = 0.3;
        double d = 0.2;
        Funciones instance = new Funciones();
        double expResult = 2.0;
        double result = (int)(Math.round(instance.MASInfinito(alp, p, d)));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }

    /**
     * Test of MEstratificado method, of class Funciones.
     */
    @Test
    public void testMEstratificado() {
        System.out.println("MEstratificado");
        double n = 2.0;
        double N = 5.0;
        double Nh = 5.0;
        Funciones instance = new Funciones();
        double expResult = 2.0;
        double result = (int)(Math.round(instance.MEstratificado(n, N, Nh)));
        assertEquals(expResult, result, 0.0);
        // TODO review the generated test code and remove the default call to fail.
         if(result!=expResult){
            fail("The test case is a prototype.");
        }
    }
    
}
