package gmm;

public class HeuristicComputer
{
	private int n;
	private float[][] G;
	
	private int k; //the depth of the node for which heuristic is being computed
	private boolean[] available;
	private float[] minCliqueWeight;	
	private int[] rank;
	private float[] sum;
	private float[] lowerBound;

	public static float W = 1.0f; //weight added to each edge of G
	public static float R = 1.03f; //approximation ratio
	
	public HeuristicComputer(float[][] Q)
	{
		n = Q[1].length - 1;
		G = new float[n+1][];
		for(int i = 1;i <= n;i++)
		{
			G[i] = new float[n+1];
			for(int j = 1;j <= n;j++)
				G[i][j] = 0.0f;
		}
		for(int i = 1;i <= n;i++)
			for(int j = (i+1);j <= n;j++)
			{
				float tmp = Q[i][j];
				if(tmp > 0.5)
					tmp = 1 - tmp;
				G[i][j] = tmp;
				G[j][i] = tmp;
			}
		
		k = 0;
		available = new boolean[n+1];
		minCliqueWeight = new float[n+1]; 		
		rank = new int[n+1];
		sum = new float[n+1]; 		
		lowerBound = new float[n+1];
	}

	private void initGreedy()
	{
		int v1 = 0;
		int v2 = 0;
		float min = Float.MAX_VALUE;
		for(int i = 1;i <= n;i++)
			for(int j = (i+1);j <= n;j++)
				if(available[i] && available[j])
				{
					if(G[i][j] < min)
					{
						min = G[i][j];
						v1 = i;
						v2 = j;
					}
				}
		minCliqueWeight[2] = min;
		rank[n-1] = v1;
		rank[n] = v2;
		available[v1] = false;
		available[v2] = false;
		for(int i = 1;i <= n;i++)
			if(available[i])
				sum[i] = G[i][v1] + G[i][v2];
	}
	
	private void runGreedy(Node node)
	{
		k = node.j;
		for(int i = 1;i <= n;i++)
			available[i] = true;
		while(node != null)
		{
			available[node.r] = false;
			node = node.parent;
		}
		initGreedy();
		for(int j = 3;j <= (n-k);j++)
		{
			float min = Float.MAX_VALUE;
			int v = 0;
			for(int i = 1;i <= n;i++)
				if(available[i])
					if(sum[i] < min)
					{
						min = sum[i];
						v = i;
					}
			minCliqueWeight[j] = minCliqueWeight[j-1] + min;
			rank[n-j+1] = v;
			available[v] = false;	
			for(int i = 1;i <= n;i++)
				if(available[i])
					sum[i] += G[i][v];
		}
	}
	
	public float getHeuristicValue(Node node,GMMEstimator gmme)
	{
		runGreedy(node);
		for(int j = (k+1);j < n;j++)
		{
			lowerBound[j] = (1-R)*(n-j+1)*(n-j)*W/2;
			lowerBound[j] += (R*minCliqueWeight[n-j+1]);
		}
		lowerBound[n] = 0.0f;
		float result = 0.0f;
		for(int j =(k+1);j < n;j++)
			result += gmme.minValueOfFj(j,(lowerBound[j]-lowerBound[j+1]));
		return result;
	}
	
	public float[] getMinCliqueWeights()
	{
		Node node = new Node();
		node.r = 0;
		node.j = 0;
		node.V = 0;
		node.remDk = 0;
		node.parent = null;
		node.children = null;
		runGreedy(node);
		return minCliqueWeight;
	}
}