package gmm;

import java.util.Arrays;
import java.util.Date;

/**
 * This class implements the Mallows Model estimator based on the
 * greedy algorithm of Davenport and Kalagnanam for finding the
 * modal ranking (the consensus ranking). It doesn't handle the
 * Generalized Mallows Model.
 * @author bhushan
 */
public class GreedyDK extends GMMEstimator
{
	public GreedyDK(boolean GMM,float[][] Q)
	{
		super(GMM,Q);
	}
	
	public void run() throws Exception
	{
		Date startTime = new Date();
		int total = (n*(n-1))/2;
		Edge[] edges = new Edge[total];
		int index = 0;
		for(int i = 1;i < n;i++)
			for(int j = (i+1);j <= n;j++)
			{
				//create majority graph edge between i and j
				if(Q[i][j] >= 0.5f)
					edges[index] = new Edge(i,j,(Q[i][j]-Q[j][i]));
				else
					edges[index] = new Edge(j,i,(Q[j][i]-Q[i][j]));
				index++;
			}
		Arrays.sort(edges);
		DirectedGraph dg = new DirectedGraph(n);
		for(int i = 0;i < edges.length;i++)
			dg.add(edges[i].from,edges[i].to);
		int[] ranking = dg.getTopologicalSort();
		for(int i = 0;i < n;i++)
			pi[i] = ranking[i];
		Date endTime = new Date();
		runningTime = endTime.getTime() - startTime.getTime();
		computeVjs();
		computeThetas();
		computeLogL();
	}
	
	//This class represents an edge of a weighted directed graph.
	class Edge implements Comparable<Edge>
	{
		int from;
		int to;
		float weight;
		
		public Edge(int from,int to,float weight)
		{
			this.from = from;
			this.to = to;
			this.weight = weight;
		}
		
		public int compareTo(Edge other)
		{
			if(this.weight > other.weight)
				return -1;
			else if(this.weight < other.weight)
				return 1;
			else
				return 0;
		}
	}
}