package gmm;

import java.util.Random;
import java.util.Date;

/**
 * This class implements a random GMM estimator. It generates
 * permutations at random, and from these permutations and their
 * reverses, it picks the one which maximizes the likelihood. Following
 * Cohen, Schapire and Singer, we generate 10n random permutations,
 * where n is the number of items being ranked.
 * @author bhushan
 */
public class RandomEstimator extends GMMEstimator
{
	private Random rng;
	private int[] piBest; //the best ranking seen so far
	private float logLBest; //the logL value corresponding to piBest
		
	public RandomEstimator(boolean GMM,float[][] Q)
	{
		super(GMM,Q);
		rng = new Random();
		piBest = new int[n];
		logLBest = 0;
	}
	
	public void run() throws Exception
	{
		Date startTime = new Date();
		generateRanking(pi);
		computeVjs();
		computeThetas();
		computeLogL();
		logLBest = logL;
		for(int i = 0;i < n;i++)
			piBest[i] = pi[i];
		int[] tmp = new int[n];
		int totalRankings = 10*n;
		for(int j = 0;j < totalRankings;j++)
		{
			generateRanking(pi);
			computeVjs();
			computeThetas();
			computeLogL();
			if(logL < logLBest)
			{
				logLBest = logL;
				for(int i = 0;i < n;i++)
					piBest[i] = pi[i];
			}
			//now consider the reverse of pi
			reverseRanking(pi,tmp);
			computeVjs();
			computeThetas();
			computeLogL();
			if(logL < logLBest)
			{
				logLBest = logL;
				for(int i = 0;i < n;i++)
					piBest[i] = pi[i];
			}
		}
		Date endTime = new Date();
		runningTime = endTime.getTime() - startTime.getTime();
		for(int i = 0;i < n;i++)
			pi[i] = piBest[i];
		computeVjs();
		computeThetas();
		computeLogL();
	}
	
	/**
	 * @param ranking the array in which a randomly generated
	 * ranking is returned.
	 */
	private void generateRanking(int[] ranking)
	{
		int[] V = new int[n];
		for(int j = 1;j < n;j++)
			V[j] = rng.nextInt(n+1-j);
		ranking[0] = n;
		for(int j = (n-1);j > 0;j--)
		{
			//V[j] is the index at which we want to insert j
			int index = n-j-1;
			while(index >= V[j])
			{
				ranking[index+1] = ranking[index];
				index--;
			}
			ranking[V[j]] = j;
		}
	}
	
	/**
	 * @param ranking the ranking to reverse
	 * @param scratchPad
	 */
	private void reverseRanking(int[] ranking,int[] scratchPad)
	{
		for(int i = 0;i < n;i++)
			scratchPad[i] = ranking[n-1-i];
		for(int i = 0;i < n;i++)
			ranking[i] = scratchPad[i];
	}
}