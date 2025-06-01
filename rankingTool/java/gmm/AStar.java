package gmm;

import java.util.PriorityQueue;
import java.util.Date;
import java.util.ArrayList;

/**
 * This class implements the A* search for finding the
 * maximum likelihood parameters for GMM.
 * @author bhushan
 */
public class AStar extends GMMEstimator
{
	private int heurFunc; //identifies which heuristic function to use
	/* heurFunc = 0 indicates baseline heuristic (0 in both cases)
	 * heurFunc = 1 indicates summing min{Q[i][j],Q[j][i]} for all applicable pairs (i,j) 
	 * for the !GMM case, and the extension based on this bound for the GMM case.
	 */
	private int beamWidth; //beam width to be used in beam search
	
	private int nodesGenerated; //no of nodes generated in the search
	private PriorityQueue<Node> priorityQ;
	private int nodesLimit;
	// When nodesGenerated hits this limit, the search reverts to a beam search.
	private boolean revertToBeam;
	private HeuristicComputer heurComputer;
	
	public AStar(boolean GMM,float[][] Q,int heuristic,int bw)
	{
		super(GMM,Q);
		heurFunc = heuristic;
		beamWidth = bw;
		nodesGenerated = 0;
		priorityQ = new PriorityQueue<Node>();
		computeNodesLimit();
		revertToBeam = false;
		heurComputer = new HeuristicComputer(Q);
	}
	
	private void computeNodesLimit()
	{
		Runtime runtime = ExptsManager.runtime;
		long maxBytes = runtime.maxMemory();
		int nodesRemaining = beamWidth*(n-2);
		nodesRemaining += 2;
		nodesRemaining *= (n+1);
		nodesRemaining /= 2;
		long bytesRemaining = nodesRemaining * Node.size;
		//200 MB should be enough for the other stuff
		bytesRemaining += (200*1024*1024);
		nodesLimit = (int)(maxBytes-bytesRemaining)/Node.size;
	}
	
	public int getNodesGenerated() { return nodesGenerated; }
	
	/**
	 * @return the number of nodes generated as a multiple of the minimum possible number.
	 */
	public float getNodesGeneratedAsMultiple()
	{
		float minPossible = n*(n+1)/2.0f;
		float result = nodesGenerated/minPossible;
		return result;
	}
	
	public boolean finishedWithBeam() { return revertToBeam; }
	
	public void run() throws Exception
	{
		Date startTime = new Date();
		Node root = createRootNode();
		expandRootNode(root);
		Node next = null;
		while(!revertToBeam)
		{
			next = priorityQ.poll();
			if(next.j == (n-1))
				break;
			expandNode(next);
			if(nodesGenerated >= nodesLimit)
				revertToBeam = true;
		}
		if(revertToBeam)
		{
			System.out.println("Reverting to beam search.");
			ArrayList<Node> beam = new ArrayList<Node>();
			outer: while(true)
			{
				beam.clear();
				for(int i = 0;i < beamWidth;i++)
				{
					next = priorityQ.poll();
					if(next != null)
					{
						if(next.j == (n-1))
							break outer;
						else
							beam.add(next);
					}
				}
				priorityQ.clear();
				for(Node node : beam)
					expandNode(node);
			}
		}
		Node sibling = next.parent.children[0];
		if(sibling.r == next.r)
			sibling = next.parent.children[1];
		pi[n-1] = sibling.r;
		int depth = n-1;
		while(depth > 0)
		{
			pi[depth-1] = next.r;
			V[depth] = next.V;
			next = next.parent;
			depth--;
		}
		Date endTime = new Date();
		runningTime = endTime.getTime() - startTime.getTime();
		computeThetas();
		computeLogL();
		priorityQ.clear();
	}
	
	/**
	 * @param startJ
	 * @param endJ
	 * @param target
	 * @return thetaJ such that sumOfLnPsiJPrime(startJ,endJ,thetaJ) = target, where
	 * sumOfLnPsiJPrime(startJ,endJ,0) < target must hold.
	 */
	/*private float solveSumOfLnPsiJPrime(int startJ,int endJ,float target)
	{
		float lower = 0.0f;
		float upper = 1.0f;
		int iters = 0;
		while(sumOfLnPsiJPrime(startJ,endJ,upper) < target)
		{
			upper *= 2.0f;
			iters++;
			if(iters > maxIters)
				return Float.POSITIVE_INFINITY; //return infinity
		}
		float diff = upper-lower;
		while(diff > 0.01f)
		{
			float mid = (lower+upper)/2;
			if(sumOfLnPsiJPrime(startJ,endJ,mid) < target)
				lower = mid;
			else
				upper = mid;
			diff /= 2;
		}
		float result = (lower+upper)/2;
		return result;
	}*/
	
	//creates and returns the root node.
	private Node createRootNode()
	{
		Node root = new Node();
		root.r = 0;
		root.j = 0;
		root.V = 0;
		
		float val = 0.0f;
		for(int i = 1;i <= n;i++)
			for(int j = (i+1);j <= n;j++)
			{
				float tmp = Q[i][j];
				if(tmp > 0.5)
					tmp = 1 - tmp;
				val += tmp;
			}
		root.remDk = val;
		root.parent = null;
		root.children = null;
		
		root.theta = 0;
		root.cost = 0;
		if(this.heurFunc == 0) //baseline heuristic
			root.remCost = 0;
		else if(this.heurFunc == 1)
		{
			if(!GMM)
				root.remCost = root.remDk;
			else
			{
				root.remCost = heurComputer.getHeuristicValue(root,this);
			}
		}
		root.L = root.cost + root.remCost;
		nodesGenerated++;
		return root;
	}
	
	private void expandRootNode(Node root)
	{
		root.children = new Node[n];
		for(int i = 1;i <= n;i++)
		{
			Node node = new Node();
			node.r = i;
			node.j = 1;
			float val = 0.0f;
			for(int j = 1;j <= n;j++)
				val += Q[j][i];
			node.V = val;
			
			val = 0.0f;
			for(int j = 1;j <= n;j++)
			{
				float tmp = Q[i][j];
				if(tmp > 0.5)
					tmp = 1 - tmp;
				val += tmp;
			}
			node.remDk = root.remDk - val;
			node.parent = root;
			node.children = null;
			
			if(GMM)
			{
				node.theta = minimizeFj(1,node.V);
				if(node.theta == Float.POSITIVE_INFINITY)
					node.cost = Float.POSITIVE_INFINITY;
				else
				{
					node.cost = node.theta*node.V;
					node.cost += (float)Math.log(PsiJ(1,node.theta));
				}
			}
			else
				node.cost = node.V;
			if(this.heurFunc == 0) //baseline heuristic
				node.remCost = 0;
			else if(this.heurFunc == 1)	
			{
				if(!GMM)
					node.remCost = node.remDk;
				else
				{
					node.remCost = heurComputer.getHeuristicValue(node,this);
				}
			}
			node.L = node.cost + node.remCost;
			//finished initializing node
			root.children[i-1] = node;
			if(node.L != Float.POSITIVE_INFINITY)
				priorityQ.add(node);
		}
		nodesGenerated += n;
	}
	
	/**
	 *  The argument node is expanded, and its children are added to the 
	 *  priority queue. Works only for a node that has a parent node.
	 * @param node the node to expand.
	 */
	private void expandNode(Node node)
	{
		Node parent = node.parent;
		Node[] sibling = parent.children;
		node.children = new Node[sibling.length-1];
		int index = 0;
		for(int i = 0;i < sibling.length;i++)
		{
			if(sibling[i].r == node.r)
				continue;
			Node child = new Node();
			child.r = sibling[i].r;
			child.j = node.j + 1;
			child.V = sibling[i].V - Q[node.r][child.r];
			
			float deduct = 0.0f;
			for(int j = 0;j < sibling.length;j++)
			{
				if(sibling[j].r == node.r)
					continue;
				float tmp = Q[child.r][sibling[j].r];
				if(tmp > 0.5)
					tmp = 1 - tmp;
				deduct += tmp;
			}
			child.remDk = node.remDk - deduct;
			child.parent = node;
			child.children = null;
			
			if(GMM)
			{
				child.theta = minimizeFj(child.j,child.V);
				if(child.theta == Float.POSITIVE_INFINITY)
					child.cost = Float.POSITIVE_INFINITY;
				else
				{
					child.cost = node.cost;
					child.cost += (child.theta*child.V);
					child.cost += (float)Math.log(PsiJ(child.j,child.theta));
				}
			}
			else
				child.cost = node.cost + child.V;
			if(child.j == (n-1))
				child.remCost = 0;
			else if(this.heurFunc == 0) //baseline heuristic
				child.remCost = 0;
			else if(this.heurFunc == 1)
			{
				if(!GMM)
					child.remCost = child.remDk;
				else
				{
					child.remCost = heurComputer.getHeuristicValue(child,this);
				}
			}
			child.L = child.cost + child.remCost;
			//finished initializing child
			node.children[index] = child;
			index++;
			if(child.L != Float.POSITIVE_INFINITY)
				priorityQ.add(child);
		}
		nodesGenerated += index;
	}
}