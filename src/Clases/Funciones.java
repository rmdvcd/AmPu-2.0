package Clases;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



/**
 *
 * @author 666
 */
public class Funciones {
  public Funciones(){
  }
  /*factoriales*/
  public  double fac(double n){
      if(n>1)
          return n*fac(n-1);
      else
          return 1;
  }
  public double fac2(double n){
      if(n>1)
          return n*fac2(n-2);
      else
          return 1;
  }
  public double comb(double a, double b){
      return fac(a)/(fac(b)*fac(a-b));
  }
  /*Distribuciones discretas*/
  /*Distribucion binomial*/
  public double binomialVp(double x,double n,double p){
  return comb(n,x)*Math.pow(p,x)*Math.pow(1-p,n-x);   
  }     
   public double binomialVpMenor(double x,double n,double p){
  double pp=0;
  for(int i=0;i<=x;i++){
  pp+=binomialVp(i,n,p);
  }
  return  pp;
  }     
  public double binomialVpMayor(double x,double n,double p){
  double pp=0;
  for(double i=x;i<=n;i++){
  pp+=binomialVp(i,n,p);
  }
  return  pp;
  }     
  public double binomialMedia(double n,double p){
  return n*p;    
  } 
  public double binomialVarianza(double n,double p){
  return binomialMedia(n,p)*(1-p);    
  } 
  /*Distribucion binomial negativa*/
  public double binomialNVp(double x, double r, double p){
  return comb(r+x-1,x)*Math.pow(p, r)*Math.pow(1-p, x);
  }
  public double binomialNMedia(double r,double p){
  return  r*((1-p)/p);   
  }
  public double binomialNVarianza(double r,double p){
  return r*((1-p)/Math.pow(p, 2));    
  }
  /*Distribucion multinomial*/
  public double multinomialVp(double N,double x,double p){
  return (fac(N)/x) *p;
  }
  /*Distribucion geometrica*/
  public double geometricaVp(double x,double p){
  return p*Math.pow(1-p,x-1);    
  }
  public double geometricaMedia(double p){
  return (1/p);    
  }
  public double geometricaVarianza(double p){
  return (1-p)/Math.pow(p,2);    
  }
  /*Distribucion hipergeometrica*/
  public double hipergeometricaVp(double x,double N,double n,double k){
  return comb(k,x)*comb(N-k,n-x)/comb(N,n);    
  }
  public double hipergeometricaVpMenor(double x,double N,double n,double k){
  double p=0;
  for(int i=0;i<=x;i++){
  p+=hipergeometricaVp(i,N,n,k);   
  }
  return p;
  }
  public double hipergeometricaVpMayor(double x,double N,double n,double k){
  double p=0;
  for(double i=x;i<=k;i++){
  p+=hipergeometricaVp(i,N,n,k);    
  }
  return p;
  }
  public double hipergeometricaMedia(double N,double n,double k){
  return n*k/N;    
  }
  public double hipergeometricaVarianza(double N,double n,double k){
  return ((N-n)/(N-1))*(n*k/N)*(1-k/N);    
  }
  /*Distribucion poisson*/
  public double poissonVp(double x,double at){
  return Math.pow(Math.E,-at)*Math.pow(at,x)/fac(x);    
  }
  public double poissonVpMenor(double x,double at){
  double p=0;  
  for(double i=0;i<=x;i++){
  p+=poissonVp(i,at);
  }
  return p;
  }
  public double poissonVpMayor(double x,double at){
  double p=0;  
  for(double i=x;i<=130;i++){
  p+=poissonVp(i,at);
  }
  return p;
  } 
  /*Distribuciones continuas*/
  /*Distribucion Uniforme continua*/
  public double UniformeF(double a, double b){
  return 1/(b-a);    
  }
  /*no coincide*/
  public double UniformeVp(double a, double b){
  double n=500;   
  double h=(b-a)/n;
  double E=UniformeF(a,b)+UniformeF(a,b);
  double I=0;
  int i=1;
  while(i<n){
  I+=UniformeF(a+i*h,b+i*h);
  i+=2;
  }
  double P=0;
  i=2;
  while(i<n){
  P+=UniformeF(a+i*h,b+i*h);
  i+=2;
  }
  return h*(E+4*I+2*P)/3;    
  }
  public double UniformeMedia(double a, double b){
  return (a+b)/2;    
  }
  public double UniformeDes(double a, double b){
  return Math.sqrt(Math.pow(a+b,2)/12);
  }
  /*Normal estandar*/
  public double NormalF(double x){
  return (1/Math.sqrt(2*Math.PI))*Math.pow(Math.E,-0.5*(x*x));
  }
  public double NormalVp(double z){
  double a=-20;  
  int n=4000;
  double h=(z-a)/n;
  double E=NormalF(a)+NormalF(z);
  double I=0;
  int i=1;
  while(i<n){
  I+=NormalF(a+i*h);
  i+=2;
  }    
  double P=0;
  i=2;    
  while(i<n){
  P+=NormalF(a+i*h);
  i+=2;
  }
  return h*(E+4*I+2*P)/3;             
  }
  public double NormalBiseccion(double p){
  double a=-4;
  double b=4;
  double e=0.00001;
  double x=(a+b)/2;
  while (b-a>e){
  if(NormalVp(x)>p){
  b=x;
  }else
  {
  a=x;
  }
  x=(a+b)/2;
  }    
  return Math.abs(x);    
  }
  /*Exponencial*/
  public double ExponencialF(double x,double a){    
    return a*  Math.pow(  Math.E,-a*x );           
        }
  public  double ExponencialVp(double x,double a){   
  return 1-Math.pow(Math.E,-a*x);   
  } 
  public  double ExponencialVx(double p,double a){   
  return Math.log(1-p)/Math.log(Math.pow(Math.E,-a));   
  }  
  /*Ji cuadrada*/
  public double JiF(double x,double v){
      if(x==0){
          return 1;
      }else {
  if(v==1){
  return (1/(Math.pow(2,v/2)*Math.sqrt(Math.PI)))*Math.pow(x,v/2-1)*Math.exp(-x/2);
  }else{
      if(v%2==1){
  double impar=Math.sqrt(Math.PI)*fac2(v-2)/Math.pow(2,(v-1)/2);
  return  (1/(Math.pow(2,v/2)*impar))*Math.pow(x,v/2-1)*Math.exp(-x/2);
  }else{
  double par =fac(v/2-1);
  return (1/(Math.pow(2,v/2) *par))*Math.pow(x,v/2-1)*Math.exp(-x/2);
  }
  }
      }
  }
  public double JiVp(double x,double v){
  int b=60;  
  int n=5000;
  double h=(b-x)/n;
  double E=JiF(v,x)+JiF(v,b);
  double I=0;
  int i=1;
  while(i<n){
  I+=JiF((x+i*h),v);
  i+=2;
  }
  double P=0;
  i=2;
  while(i<n){
  P+=JiF((x+i*h),v);
  i+=2;
  }
  return h*(E+4*I+2*P)/3;
  }
  public double JiBiseccion(double p,double v){
  double a=0;
  double b=60;
  double e=0.0001;
  double x=(a+b)/2;
  while (b-a>e){
  if( JiVp( x,v)<p){
  b=x;
  }
  else{
  a=x;
  }
  x=(a+b)/2;
  }
  return Math.abs(x);
  }
  /*T de student*/
  public double TstudentF(double x,double v){
  double f=0;
  if(v==1){
  f+=1/(Math.PI*Math.sqrt(v))*Math.pow(1+x*x,-1);
  }else{ 
    if(v>1&&v%2==1){
     double par=fac((v+1)/2-1);   
     double impar=Math.sqrt(Math.PI)*fac2(v-2)/Math.pow(2,(v-1)/2);
     f+=par/(impar*Math.sqrt(Math.PI*v))*Math.pow(1+x*x/v,-(v+1)/2);
     }
     else{
     double impar=Math.sqrt(Math.PI)*fac2(v-1)/Math.pow(2,(v)/2);
     double par=fac(v/2-1);
     f+=impar/(par*Math.sqrt(Math.PI*v))*Math.pow(1+x*x/v,-(v+1)/2);
     }
     } 
    return f;
    }
  public double TstudentVp(double x,double v){
  double integral=0;  
  if(v==1){
    int a=-649;  
    int n=5000;
    double h=(x-a)/n;
    double E=TstudentF(a,v)+TstudentF(x,v);
    double I=0;
    int i=1;
    while(i<n){
    I+=TstudentF((int) (a+i*h),v );
    i+=2;
    }
    double P=0;
    i=2;
    while(i<n){
    P+=TstudentF( (int) (a+i*h),v);
    i+=2;
    }
    integral+=h*(E+4*I+2*P)/3+4.8061256267515777E-4;
    }  
    else{
      int a=-649;  
      int n=8000;
      double h=(x-a)/n;
      double E=TstudentF(a,v)+TstudentF(x,v);
      double I=0;
      int i=1;
      while(i<n){
      I+=TstudentF((int) (a+i*h),v);
      i+=2;
      }
      double P=0;
      i=2;
      while(i<n){
      P+=TstudentF((int) (a+i*h),v);
      i+=2;
      }
      integral =h*(E+4*I+2*P)/3;
      }
      return integral;
      }
  public double TstudentBiseccion(double p,double v){
    double a=-649;
    double b=649;
    double e=0.0001;
    double x=(a+b)/2;
    while (b-a>e  ){
    if(TstudentVp(x,v)>p){
    b=x;
    }else{
    a=x;
    }
    x=(a+b)/2;
    }
    return Math.abs(x);
    }
  /*F de fisher*/
  public double FdeFisherF(double x, double v1,double v2){
  double fun=0;
  if(x==0)
      fun=1;
  else{
  if(v1==1&&v2==1){                      
        fun=( 1/Math.PI)*( Math.pow(x,-0.5)/(1+x)  );
        }
        else if( v1==1&&v2>1&&v2%2==0){
             double impar=Math.sqrt(Math.PI)*fac2(v2-1)/Math.pow(2,(v2)/2); 
             fun=impar*Math.pow(1/v2,0.5)/( Math.sqrt(Math.PI)*fac(v2/2-1)  )*Math.pow(x,-0.5)/Math.pow(1+x/v2,(1+v2)/2);               
             }
             else if( v1==1&&v2>1&&v2%2==1){
                  double impar=Math.sqrt(Math.PI)*fac2(v2-2)/Math.pow(2,(v2-1)/2); 
                  fun=fac((1+v2)/2-1)*Math.pow(1/v2,0.5)/( Math.sqrt(Math.PI)*impar  )*Math.pow(x,-0.5)/Math.pow(1+x/v2,(1+v2)/2);            
                  }
                  else if(v1>1&&v1%2==0&&v2==1){
                       double impar=Math.sqrt(Math.PI)*fac2(v1-1)/Math.pow(2,(v1)/2);          
                       fun=impar*Math.pow(v1,v1/2)/( Math.sqrt(Math.PI)*fac(v1/2-1) )*Math.pow(x,v1/2-1)/Math.pow(1+v1*x,(v1+1)/2);   
                       }
                       else if (v1>1&&v1%2==1&&v2==1){
                            double impar=Math.sqrt(Math.PI)*fac2(v1-2)/Math.pow(2,(v1-1)/2); 
                            fun=fac((v1+1)/2-1)*Math.pow(v1,v1/2)/(  impar*Math.sqrt(Math.PI) )*Math.pow(x,v1/2-1)/Math.pow(1+v1*x,(v1+1)/2);    
                            }
                            else if (v1>1&&v1%2==0&&v2>1&&v2%2==0){
                                 fun=fac((v1+v2)/2-1)*Math.pow(v1/v2,v1/2)/(fac(v1/2-1)*fac(v2/2-1) )*Math.pow(x,v1/2-1)/Math.pow(1+v1*x/v2,(v1+v2)/2);
                                 }
                                 else if(v1>1&&v1%2==1&&v2>1&&v2%2==1  ){
                                      double impar1=Math.sqrt(Math.PI)*fac2(v1-2)/Math.pow(2,(v1-1)/2);
                                      double impar2=Math.sqrt(Math.PI)*fac2(v2-2)/Math.pow(2,(v2-1)/2); 
                                      fun=fac((v1+v2)/2-1)*Math.pow(v1/v2,v1/2)/(impar1*impar2)  *Math.pow(x,v1/2-1)/Math.pow(1+v1*x/v2,(v1+v2)/2);
                                      }
                                      else if(v1>1&&v1%2==0&&v2>1&&v2%2==1){
                                           double impar1=Math.sqrt(Math.PI)*fac2(v1+v2-2)/Math.pow(2,(v1+v2-1)/2); 
                                           double impar2=Math.sqrt(Math.PI)*fac2(v2-2)/Math.pow(2,(v2-1)/2);      
                                           fun=impar1*Math.pow(v1/v2,v1/2)/(fac(v1/2-1)*impar2 )*Math.pow(x,v1/2-1)/Math.pow(1+v1*x/v2,(v1+v2)/2);
                                           }
                                           else if(v1>1&&v1%2==1&&v2>1&&v2%2==0  ){
                                                double impar1=Math.sqrt(Math.PI)*fac2(v1+v2-2)/Math.pow(2,(v1+v2-1)/2); 
                                                double impar2=Math.sqrt(Math.PI)*fac2(v1-2)/Math.pow(2,(v1-1)/2); 
                                                fun=impar1*Math.pow(v1/v2,v1/2)/(impar2*fac(v2/2-1))*Math.pow(x,v1/2-1)/Math.pow(1+v1*x/v2,(v1+v2)/2);
                                                }  
  }
  return fun;
  }
public double FdeFisherVp(double x,double v1,double v2){
    double integral=0;
    if(v1==1&&v2==2){  
    int b=1500;
    int n=8000;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(b,v1,v2);
    double I=0;
    int i=1;
    while(i<n){
    I+=FdeFisherF( (int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
    while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3+6.58890878054862E-4;
     }else if(v1==1&&v2==3){  
    int b=1500;
    int n=8000;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(b,v1,v2);
    double I=0;
    int i=1;
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
    while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3+3.7794020593350055E-5;
    }else if(v1==1&&v2==4){  
    int b=1500;
    int n=8000;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(b,v1,v2);
    double I=0;
    int i=1;
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
    while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3+2.6510610681276145E-6;
     }else if(v1==1&&v2==5){  
    int b=1500;
    int n=8000;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(b,v1,v2);
    double I=0;
    int i=1; 
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
    while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3+2.1590002957283347E-7;
     }else if(v1==1&&v2==6){  
    int b=1500;
    int n=8000;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(x,v1,v2);
    double I=0;
    int i=1; 
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
    while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3+1.9752090162053734E-8;
    }
    else{  
    int b=5000;
    int n=8500;
    double h=(b-x)/n;
    double E=FdeFisherF(x,v1,v2)+FdeFisherF(x,v1,v2);
    double I=0;
    int i=1; 
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
     while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=h*(E+4*I+2*P)/3;
    }
    return integral; 
    }
 public double FdeFisherVp1(double x,double v1,double v2){
    double integral=0; 
    double a=0;
    int n=5000;
    double h=(x-a)/n;
    double E=FdeFisherF(a,v1,v2)+FdeFisherF(x,v1,v2);
    double I=0;
    int i=1;
    while(i<n){
    I+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }    
    double P=0;
    i=2;    
     while(i<n){
    P+=FdeFisherF((int) (x+i*h),v1,v2);
    i+=2;    
    }       
    integral+=1-h*(E+4*I+2*P)/3;
    if(integral<0){
    integral=0;
    }
    return integral;
    }
 public double  FdeFisherVpp(double  x){
    return 1-( 1/Math.PI)*Math.atan(Math.sqrt(x))*2;
    }
 public double  FdeFisherVx(double  p){
 return Math.pow(Math.tan(Math.PI*p/2),2);  
 }
 public  double FdeFisherBiseccion(double p,double v1,double v2){
  double a=0;
    double b=1500;
    double e=0.0001;
    double x=(a+b)/2;
   while (      b-a>e   ){
    if( FdeFisherVp(x,v1,v2)<p){
    b=x;
    }else{
    a=x;
    }
    x=(a+b)/2;
    }
    
    return x;   
 }
 public double FdeFisherBiseccion1(double p,double v1,double v2){
 double a=0;
    double b=1500;
    double e=0.0001;
    double x=(a+b)/2;
   while (      b-a>e   ){
    if( FdeFisherVp1(x,v1,v2)<p){
    b=x;
    }else{
    a=x;
    }
    x=(a+b)/2;
    }
    
    return x;       
 }
 /*Muestreos*/
 /*Aleatorio simple finito*/
 public double MASFinito(int N,double alp,double p,double d){
   return Math.pow(NormalBiseccion(1-alp/2)/d,2)*p*(1-p)/(1+(1/N)*Math.pow(NormalBiseccion(1-alp/2)/d,2)*p*(1-p)-1/N);  
 }
 public int MASFinitoSubM(int N){
 return (int) (Math.random()*N); 
 }
 /*Aleatorio simple infinito*/
 public double MASInfinito(double alp,double p,double d){
 return Math.pow(NormalBiseccion(1-alp/2)/d,2 )*p*(1-p);    
 }
 /*Estratificado*/
public double MEstratificado(double n,double N,double Nh){
return Nh*n/N;    
}

}
