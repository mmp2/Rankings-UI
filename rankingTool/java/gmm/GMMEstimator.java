package gmm;

import java.io.PrintWriter;

/**
 * This abstract class represents a estimator of the Generalized Mallows
 * Model. It contains generic functionality that any estimator will need.
 * Any particular estimator must inherit from this class.
 * @author bhushan
 */
public abstract class GMMEstimator
{
	protected boolean GMM;
	protected float[][] Q; //the input Q matrix
	protected int n; //the number of items being ranked
	
	protected int[] pi; //the estimated modal ranking
	protected float[] theta; //theta[i] is theta_i
	protected float[] V; //V[j] is the average V_j for pi
	protected float logL; //-1/N times the log likelihood
	protected long runningTime; //time taken in milliseconds to estimate pi
	
	protected static int maxIters = 50;
	
	public GMMEstimator(boolean GMM,float[][] Q)
	{
		this.GMM = GMM;
		this.Q = Q;
		n = Q[1].length - 1;
		pi = new int[n];
		theta = new float[n];
		V = new float[n];
		logL = 0;
		runningTime = 0;
	}
	
	/**
	 * This method causes the estimator to run, and estimate the GMM parameters.
	 * Any estimator must provide a concrete implementation of this method.
	 */
	public abstract void run() throws Exception;
	
	/**
	 * @return the estimated modal ranking.
	 */
	public int[] getPi() { return pi; }
	
	/**
	 * @return the average Kendall distance of estimated modal ranking pi
	 * from the rankings in the sample.
	 */
	public float getAvgDk()
	{
		float result = 0.0f;
		for(int j = 1;j < n;j++)
			result += V[j];
		return result;
	}
	
	public float getLogL() { return logL; }
	
	public long getRunningTime() { return runningTime; }
	
	public void printLearnedModel(PrintWriter out)
	{
		out.print("Modal Ranking: ");
		for(int i = 0;i < n;i++)
			out.print(pi[i] + " ");
		out.println();
		if(!GMM)
			out.print("theta value: " + theta[1]);
		else
		{
			out.print("theta values: ");
			for(int j = 1;j < n;j++)
				out.print(theta[j] + " ");
		}
		out.println();
	}

	protected float PsiJ(int j,float thetaJ)
	{
		if(thetaJ == 0.0f)
			return (float)(n-j+1);
		double val = (n-j+1)*thetaJ;
		val = Math.exp((-1)*val);
		double result = 1 - val;
		result /= (1 - Math.exp((-1)*thetaJ));
		return (float)result;
	}
	
	/**
	 * @param j
	 * @param thetaJ
	 * @return the derivative of ln psi_j(thetaJ), or g_j'(thetaJ).
	 */
	protected float lnPsiJPrime(int j,float thetaJ)
	{
		if(thetaJ == 0.0f)
			return (-1)*(n-j)/2;
		float psi = PsiJ(j,thetaJ);
		double val = (n-j+1)*thetaJ;
		//val = Math.exp((-1)*val);
		val = Math.exp(val);
		double prime = (n-j+1) / (val - 1) - 1 / (Math.exp(thetaJ)-1);
		//val *= (n-j);
		//val *= (n-j+1);
		//double psiPrime = 1+val-psi;
		//psiPrime  /= (1 - Math.exp((-1)*thetaJ));
		//float result = (float)psiPrime/psi;
		float result = (float)prime;
		return result;
	}

	protected float getLowerTheta(int j, float thetaJ)
	{
	    float Qmin = 1.0f;
	    float Qmax = 0.0f;
	    float result = 0.0f;
        for(int i = 1; i < n; i++)
            for(int k = i+1; k<= n; k++)
            {
                float temp1 = Q[i][k];
                float temp2 = Q[i][k];
                if(temp1 < 0.5f)
                    temp1 = 1.0f - temp1;
                if(temp1 > 0.5f)
                    temp2 = 1.0f - temp2;
                if(temp1 <= Qmin)
                    Qmin = temp1;
                if(temp2 >= Qmax)
                    Qmax = temp2;
            }
        if(j==n-1)
            result += Math.log(Qmin/(1.0f-Qmin));
        else
            result += Math.log(Qmin/(1.0f-Qmin));
        return result;
	}

	protected float sumOfLnPsiJPrime(int startJ,int endJ,float thetaJ)
	{
		float result = 0.0f;
		for(int j = startJ;j <= endJ;j++)
			result += lnPsiJPrime(j,thetaJ);
		return result;
	}
	
	/**
	 * @param j
	 * @param Vj
	 * @return the value of theta_j >= 0 that minimizes the function f_j that comes
	 * up in GMM (multiple thetas case).
	 */
	protected float minimizeFj(int j,float Vj)
	{
		if(Vj >= (float)(n-j)/2)
			return 0.0f;
		//do a binary search to find the result
		float target = (-1)*Vj;
		float lower = 0.0f;
		float upper = 1.0f;
		int iters = 0;
		while(lnPsiJPrime(j,upper) < target)
		{
			upper *= 2.0f;
			iters++;
			if(iters > maxIters)
				return Float.POSITIVE_INFINITY; //return infinity
		}
		float diff = upper-lower;
		while(diff > 0.01f) //0.005f
		{
			float mid = (lower+upper)/2;
			if(lnPsiJPrime(j,mid) < target)
				lower = mid;
			else
				upper = mid;
			diff /= 2;
		}
		float result = (lower+upper)/2;
		return result;
	}
	
	/**
	 * @param j
	 * @param Vj
	 * @return the minimum value of the function f_j that comes up in GMM.
	 */
	public float minValueOfFj(int j,float Vj)
	{
		float thetaJ = minimizeFj(j,Vj);
		if(thetaJ == Float.POSITIVE_INFINITY)
			return 0.0f;
		float result = thetaJ*Vj;
		result += (float)Math.log(PsiJ(j,thetaJ));
		return result;
	}

	/**
	 * @param D
	 * @return the value of theta >= 0 that minimizes the function f that comes
	 * up in the Mallows Model (single theta case).
	 */
	protected float minimizeF(float D)
	{
		float bound = n*(n-1)/4.0f;
		if(D >= bound)
			return 0.0f;
		//do a binary search to find the result
		float target = (-1)*D;
		float lower = 0.0f;
		float upper = 1.0f;
		int iters = 0;
		while(sumOfLnPsiJPrime(1,(n-1),upper) < target)
		{
			upper *= 2.0f;
			iters++;
			if(iters > maxIters)
				return Float.POSITIVE_INFINITY; //return infinity
		}
		float diff = upper-lower;
		while(diff > 0.005f) //0.005f
		{
			float mid = (lower+upper)/2;
			if(sumOfLnPsiJPrime(1,(n-1),mid) < target)
				lower = mid;
			else
				upper = mid;
			diff /= 2;
		}
		float result = (lower+upper)/2;
		return result;
	}

	/**
	 * Sets the V_j values. Must be called by a subclass
	 * only after it has estimated the modal ranking pi.
	 */
	protected void computeVjs()
	{
		for(int i = 1;i < n;i++)
		{
			float val = 0.0f;
			for(int j = i;j < n;j++)
				val += Q[pi[j]][pi[i-1]];
			V[i] = val;
		}
	}
	
	/**
	 * Sets the theta values. Must be called by a subclass
	 * only after it has set the V_j values.
	 */
	protected void computeThetas()
	{
		if(GMM)
		{
			for(int j = 1;j < n;j++)
				theta[j] = minimizeFj(j,V[j]);
		}
		else
		{
			float D = getAvgDk();
			float val = minimizeF(D);
			for(int j = 1;j < n;j++)
				theta[j] = val;
		}
	}
	
	/**
	 * Must be called by a subclass only after the theta values have been set.
	 */
	protected void computeLogL()
	{
		logL = 0.0f;
		for(int j = 1;j < n;j++)
		{
			logL += (theta[j]*V[j]);
			logL += (float)Math.log(PsiJ(j,theta[j]));
		}
	}


	
	public float getLogLForQ(float[][] argQ)
	{
		float result = 0.0f;
		for(int j = 1;j < n;j++)
		{
			float Vj = 0.0f;
			for(int i = (j+1);i <= n;i++)
				Vj += argQ[pi[i-1]][pi[j-1]];
			result += (theta[j]*Vj);
			result += (float)Math.log(PsiJ(j,theta[j]));
		}
		return result;
	}
}