package Utiles;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


import Clases.Funciones;
import com.bestcode.mathparser.IFunction;
import com.bestcode.mathparser.IMathParser;
import com.bestcode.mathparser.IParameter;
import com.bestcode.mathparser.MathParserFactory;
import com.bestcode.mathparser.OneParamFunc;
import com.bestcode.mathparser.TwoParamFunc;
/**
 *
 * @author 666
 */
public class Parsear {
IMathParser parseador = MathParserFactory.create();
Funciones f=new Funciones();
	public Funciones m_Funciones;
public Parsear(){
}
public double redondeo(double x){
        return Math.rint(x*10000)/10000;
    }
public void exp(String def) {
     parseador.setExpression(def);
}
public double[] evalP(double[] xx,double x)throws Exception{
int n=xx.length;
    double[] r=new double[n];
    for(int i=0;i<n;i++){
        if(xx[i]==x){
        r[i]=redondeo(eval(xx[i]));
        }
    }
    return r;    
}
public double eval(double x) throws Exception{
    double r=Double.NaN;
    parseador.setX(x);
    r=parseador.getValue();
    return redondeo(r);
    }
public double[] eval(double[] x) throws Exception{
    int n=x.length;
    double[] r=new double[n];
    for(int i=0;i<n;i++){
        r[i]=eval(x[i]);
    }
    return r;
    }
public double evalU(double x,double a,double b)throws Exception{
 double r=Double.NaN;
    parseador.setX(a);
    parseador.setY(b);
    if((x<=a)||(x>=b))
        r=0;
    else
        r=parseador.getValue();
    return redondeo(r);    
}
public double[] evalU(double[] x,double a,double b) throws Exception{
    int n=x.length;
    double[] r=new double[n];
    for(int i=0;i<n;i++){
        r[i]=evalU(x[i],a,b);
    }
    return r;
    }
public double[] rango(double x0,double xn,double d){
int n=(int) (Math.abs((xn-x0)/d));
double[] r=new double[n+1];
for(int i=0;i<n+1;i++){
    r[i]=x0;
    x0+=d;
}
return r;
}
/*definir expresion*/
/*discretas*/
public void defBinomialVp(){
        try {
      parseador.createFunc("binomialVp", new binomialVp());
        } catch (Exception e) {
        }
    }
public void defBinomialVpMayor(){
     try {
      parseador.createFunc("binomialVpMayor", new binomialVpMayor());
        } catch (Exception e) {
        }
    }
public void defBinomialVpMenor(){
     try {
      parseador.createFunc("binomialVpMenor", new binomialVpMenor());
        } catch (Exception e) {
        }
    }
public void defBinomialNVp(){
try {
      parseador.createFunc("binomialNVp", new binomialNVp());
        } catch (Exception e) {
        }    
}
public void defMultinomialVp(){
        try {
      parseador.createFunc("multinomialVp", new multinomialVp());
        } catch (Exception e) {
        }
    }
public void defGeometricaVp(){
        try {
      parseador.createFunc("geometricaVp", new geometricaVp());
        } catch (Exception e) {
        }
    }
public void defHipergeometricaVp(){
        try {
      parseador.createFunc("hipergeometricaVp", new hipergeometricaVp());
        } catch (Exception e) {
        }
    }
public void defHipergeometricaVpMayor(){
        try {
      parseador.createFunc("hipergeometricaVpMayor", new hipergeometricaVpMayor());
        } catch (Exception e) {
        }
    }
public void defHipergeometricaVpMenor(){
        try {
      parseador.createFunc("hipergeometricaVpMenor", new hipergeometricaVpMenor());
        } catch (Exception e) {
        }
    } 
public void defPoissonVp(){
        try {
      parseador.createFunc("poissonVp", new poissonVp());
        } catch (Exception e) {
        }
    }
public void defPoissonVpMayor(){
        try {
      parseador.createFunc("poissonVpMayor", new poissonVpMayor());
        } catch (Exception e) {
        }
    }
public void defPoissonVpMenor(){
        try {
      parseador.createFunc("poissonVpMenor", new poissonVpMenor());
        } catch (Exception e) {
        }
    }
/*continuas*/
public void defUniformeF(){
  try {
      parseador.createFunc("uniformeF", new uniformeF());
        } catch (Exception e) {
        }   
}
public void defNormalF(){
try {
    parseador.createFunc("normalF", new normalF());
        } catch (Exception e) {
        }       
}
public void defExpF(){
try {
    parseador.createFunc("expF", new expF());
        } catch (Exception e) {
        }       
}
public void defJiF(){
try {
    parseador.createFunc("jiF", new jiF());
        } catch (Exception e) {
        }       
}
public void defTstudentF(){
try {
    parseador.createFunc("tstudentF", new tstudentF());
        } catch (Exception e) {
        }       
}
public void defFisherF(){
try {
    parseador.createFunc("fisherF", new fisherF());
        } catch (Exception e) {
        }       
}

/*clases abstractas*/
/*discretas*/

public class binomialVp implements IFunction {
   @Override
   public double run(IParameter[] p){
     return f.binomialVp(p[0].getValue(),p[1].getValue(),p[2].getValue());
   }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
    }
public class binomialVpMayor implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.binomialVpMayor( p[0].getValue(), p[1].getValue(), p[2].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
  }
public class binomialVpMenor implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.binomialVpMenor( p[0].getValue(), p[1].getValue(), p[2].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
  }
public class binomialNVp implements IFunction{

        @Override
        public double run(IParameter[] p) {
            return f.binomialNVp(p[0].getValue(), p[1].getValue(), p[2].getValue());
        }

        @Override
        public int getNumberOfParams() {
            return 3;
        }
    
}
public class multinomialVp implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.multinomialVp(p[0].getValue(), p[1].getValue(), p[2].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
  }
public class geometricaVp extends TwoParamFunc{
        @Override
        public double run(IParameter[] p) {
        return f.geometricaVp(p[0].getValue(), p[1].getValue());
        }
  } 
public class hipergeometricaVp implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.hipergeometricaVp(p[0].getValue(), p[1].getValue(), p[2].getValue(), p[3].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 4;
        }
  }
public class hipergeometricaVpMayor implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.hipergeometricaVpMayor(p[0].getValue(), p[1].getValue(), p[2].getValue(), p[3].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
  }
public class hipergeometricaVpMenor implements IFunction{
        @Override
        public double run(IParameter[] p) {
        return f.hipergeometricaVpMenor(p[0].getValue(), p[1].getValue(), p[2].getValue(), p[3].getValue());
        }
        @Override
        public int getNumberOfParams() {
            return 3;
        }
  }
public class poissonVp extends TwoParamFunc{
        @Override
        public double run(IParameter[] p) {
        return f.poissonVp(p[0].getValue(),p[1].getValue());
        }
  }
public class poissonVpMayor extends TwoParamFunc{
        @Override
        public double run(IParameter[] p) {
        return f.poissonVp(p[0].getValue(),p[1].getValue());
        }
  }
public class poissonVpMenor extends TwoParamFunc{
        @Override
        public double run(IParameter[] p) {
        return f.poissonVp(p[0].getValue(),p[1].getValue());
        }
  }
/*continuas*/
public class uniformeF extends TwoParamFunc{

        @Override
        public double run(IParameter[] p) {
            return f.UniformeF(p[0].getValue(), p[1].getValue());
        }
    
}
public class normalF extends OneParamFunc{

        @Override
        public double run(IParameter[] p) {
            return f.NormalF(p[0].getValue());
        }
    
}
public class expF extends TwoParamFunc{

        @Override
        public double run(IParameter[] p) {
            return f.ExponencialF(p[0].getValue(), p[1].getValue());
        }
    
}
public class jiF extends TwoParamFunc{

        @Override
        public double run(IParameter[] p) {
            return f.JiF(p[0].getValue(), p[1].getValue());
        }
    
}
public class tstudentF extends TwoParamFunc{

        @Override
        public double run(IParameter[] p) {
            return f.TstudentF(p[0].getValue(), p[1].getValue());
        }
    
}
public class fisherF implements IFunction{

        @Override
        public double run(IParameter[] p) {
            return f.FdeFisherF(p[0].getValue(), p[1].getValue(), p[2].getValue());
        }

        @Override
        public int getNumberOfParams() {
            return 3;
        }
    
}
}
