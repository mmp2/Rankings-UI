package gmm.clique;

public class MinCliquesFinder
{
	private int n;
	private float[][] G;
	
	private int currentK;
	private float[] minCliqueWeight;
	private int[][] clique;
	private float[] weight;
	
	public MinCliquesFinder(float[][] Q)
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
		
		currentK = 1;
		minCliqueWeight = new float[n+1];
		minCliqueWeight[1] = 0.0f;
	}

	private void startMinCliqueFinding()
	{
		int count = n*(n-1)/2;
		clique = new int[count][];
		for(int i = 0;i < count;i++)
			clique[i] = new int[2];
		weight = new float[count];
		int index = 0;
		for(int i = 1;i <= n;i++)
			for(int j = (i+1);j <= n;j++)
			{
				clique[index][0] = i;
				clique[index][1] = j;
				weight[index] = G[i][j];
				index++;
			}
		currentK = 2;
		float min = Float.MAX_VALUE;
		for(int i = 0;i < count;i++)
			if(weight[i] < min)
				min = weight[i];
		minCliqueWeight[2] = min;
	}
	
	private void freeMemory(Runtime runtime)
	{
		for(int i = 0;i < 2;i++)
		{
			runtime.gc();
			runtime.runFinalization();
			Thread.yield();
		}
	}
	
	private void findMinCliques()
	{
		startMinCliqueFinding();
		Runtime runtime = Runtime.getRuntime();
		for(int k = 3;k <= n;k++)
		{
			freeMemory(runtime);
			long currentBytes = runtime.totalMemory() - runtime.freeMemory();
			long requiredBytes = currentBytes*(n+1)/k;
			if(requiredBytes > runtime.maxMemory())
				break;
			int count = clique.length;
			int newCount = (int)((n-k+1)*(long)count/k);
			int[][] newClique = new int[newCount][];
			for(int i = 0;i < newCount;i++)
				newClique[i] = new int[k];
			float[] newWeight = new float[newCount];
			int index = 0;
			for(int i = 0;i < count;i++)
				for(int j = (clique[i][k-2]+1);j <= n;j++)
				{
					for(int x = 0;x <= (k-2);x++)
						newClique[index][x] = clique[i][x];
					newClique[index][k-1] = j;
					newWeight[index] = weight[i];
					for(int x = 0;x <= (k-2);x++)
						newWeight[index] += G[j][clique[i][x]];
					index++;
				}
			currentK = k;
			float min = Float.MAX_VALUE;
			for(int i = 0;i < index;i++)
				if(newWeight[i] < min)
					min = newWeight[i];
			minCliqueWeight[k] = min;
			clique = newClique;
			weight = newWeight;
		}
	}
	
	public float[] getMinCliqueWeights()
	{
		findMinCliques();
		float[] result = new float[1+currentK];
		for(int i = 1;i <= currentK;i++)
			result[i] = minCliqueWeight[i];
		return result;
	}
	
	public void clear()
	{
		clique = null;
		weight = null;
		freeMemory(Runtime.getRuntime());
	}
}