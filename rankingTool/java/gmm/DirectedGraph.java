package gmm;

import java.util.Arrays;

public class DirectedGraph
{
	private int n; //the number of nodes in the graph
	private short[][] E; //the adjacency matrix representing the graph
	/* E[i][j] = 1 means an edge goes from i to j.
	 * E[i][j] = -1 means an edge goes from j to i.
	 * E[i][j] = 0 means no edge exists between i and j.
	 */
	
	/**
	 * Creates an empty graph with the specified number of nodes.
	 */
	public DirectedGraph(int numberOfNodes)
	{
		n = numberOfNodes;
		E = new short[n+1][];
		for(int i = 1;i <= n;i++)
		{
			E[i] = new short[n+1];
			for(int j = 1;j <= n;j++)
				E[i][j] = 0;
		}
		//it is convenient to make the diagonal 1.
		for(int i = 1;i <= n;i++)
			E[i][i] = 1;
	}
	
	/**
	 * Adds the specified edge to the graph, and others that might be needed
	 * to maintain transitive closure. If the graph already contains this edge
	 * or its reverse, nothing is done.
	 * @param from
	 * @param to
	 */
	public void add(int from,int to)
	{
		int u = from;
		int v = to;
		if(E[u][v] != 0)
			return;
		for(int i = 1;i <= n;i++)
			if(E[i][u] == 1)
			{
				for(int j = 1;j <= n;j++)
					if(E[v][j] == 1)
					{
						E[i][j] = 1;
						E[j][i] = -1;
					}
			}
	}
	
	/**
	 * Assumes that an edge exists between any pair of nodes i and j.
	 * Won't return the correct answer otherwise.
	 * @return an int array containing the nodes in topologically sorted order.
	 */
	public int[] getTopologicalSort()
	{
		ItemRank[] iRanks = new ItemRank[n];
		for(int i = 1;i <= n;i++)
		{
			iRanks[i-1] = new ItemRank();
			iRanks[i-1].item = i;
			iRanks[i-1].avgRank = incomingEdgeCount(i);
		}
		Arrays.sort(iRanks);
		int[] result = new int[n];
		for(int i = 0;i < n;i++)
			result[i] = iRanks[i].item;
		return result;
	}
	
	private int incomingEdgeCount(int item)
	{
		int result = 0;
		for(int i = 1;i <= n;i++)
			if(E[i][item] == 1)
				result++;
		return result;
	}
}