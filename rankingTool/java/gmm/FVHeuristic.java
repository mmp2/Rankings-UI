package gmm;

import java.util.Arrays;
import java.util.Date;

/**
 * This class implements the GMM estimator based on the Fligner-Verducci
 * heuristic described in "Multistage Ranking Models".
 * @author bhushan
 */
public class FVHeuristic extends GMMEstimator
{
	private int localSearchSteps;
	private int[] piCur; //the current ranking in the local search
	private float[] VCur; //the V_j values for piCur
	private float[] thetaCur; //the theta_j values for piCur
	private float logLCur; //the logL value for piCur
	
	public FVHeuristic(boolean GMM,float[][] Q)
	{
		super(GMM,Q);
		localSearchSteps = 0;
		piCur = new int[n];
		VCur = new float[n];
		thetaCur = new float[n];
		logLCur = 0;
	}
	
	public int getLocalSearchSteps() { return localSearchSteps; }
	
	public void run() throws Exception
	{
		Date startTime = new Date();
		estimateInitialPi();
		computeVjs();
		computeThetas();
		computeLogL();
		piCur[0] = pi[0];
		for(int i = 1;i < n;i++)
		{
			piCur[i] = pi[i];
			VCur[i] = V[i];
			thetaCur[i] = theta[i];
		}
		logLCur = logL;
		while(true)
		{
			int index = getBestNeighbor();
			if(index == -1)
				break;
			for(int i = 0;i < n;i++)
				pi[i] = piCur[i];
			pi[index] = piCur[index+1];
			pi[index+1] = piCur[index];
			computeVjs();
			computeThetas();
			computeLogL();
			piCur[0] = pi[0];
			for(int i = 1;i < n;i++)
			{
				piCur[i] = pi[i];
				VCur[i] = V[i];
				thetaCur[i] = theta[i];
			}
			logLCur = logL;
			localSearchSteps++;
		}
		Date endTime = new Date();
		runningTime = endTime.getTime() - startTime.getTime();
		pi[0] = piCur[0];
		for(int i = 1;i < n;i++)
		{
			pi[i] = piCur[i];
			V[i] = VCur[i];
			theta[i] = thetaCur[i];
		}
		logL = logLCur;
	}

	private void estimateInitialPi()
	{
		ItemRank[] iRanks = new ItemRank[n];
		for(int i = 1;i <= n;i++)
		{
			float rank = 0.0f;
			for(int j = 1;j <= n;j++)
				rank += Q[j][i];
			iRanks[i-1] = new ItemRank();
			iRanks[i-1].item = i;
			iRanks[i-1].avgRank = rank;
		}
		Arrays.sort(iRanks);
		for(int i = 0;i < n;i++)
			pi[i] = iRanks[i].item;
	}
	
	/**
	 * @return index such that the best neighbor of the ranking piCur is
	 * obtained by swapping piCur[index] and piCur[index+1]. Returns -1
	 * if none of the neighbors is better than piCur. 
	 */
	private int getBestNeighbor()
	{
		int result = -1;
		float bestLogL = logLCur;
		for(int index = 0;index <= (n-2);index++)
		{
			for(int i = 0;i < n;i++)
				pi[i] = piCur[i];
			pi[index] = piCur[index+1];
			pi[index+1] = piCur[index];
			computeVjs();
			//compute thetas
			if(GMM)
			{
				for(int j = 1;j < n;j++)
				{
					if(V[j] == VCur[j])
						theta[j] = thetaCur[j];
					else
						theta[j] = minimizeFj(j,V[j]);
				}		
			}
			else
			{
				float D = getAvgDk();
				float val = minimizeF(D);
				for(int j = 1;j < n;j++)
					theta[j] = val;
				
			}
			computeLogL();
			if(logL < bestLogL)
			{
				bestLogL = logL;
				result = index;
			}
		}
		return result;
	}
}