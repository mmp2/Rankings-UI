package gmm;

import java.util.Date;

/**
 * This class implements the GMM estimator based on
 * the greedy search algorithm of Cohen, Schapire and Singer.
 * @author bhushan
 */
public class GreedyCSS extends GMMEstimator
{
	public GreedyCSS(boolean GMM,float[][] Q)
	{
		super(GMM,Q);
	}
	
	public void run() throws Exception
	{
		Date startTime = new Date();
		NodeCSS root = createRootNode();
		expandRootNode(root);
		NodeCSS next = getBestChild(root);
		while(next.j != (n-1))
		{
			expandNode(next);
			next = getBestChild(next);
		}
		NodeCSS sibling = next.parent.children[0];
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
	}
	
	//creates and returns the root node.
	private NodeCSS createRootNode()
	{
		NodeCSS root = new NodeCSS();
		root.r = 0;
		root.j = 0;
		root.V = 0.0f;
		root.parent = null;
		root.children = null;
		return root;
	}
	
	private void expandRootNode(NodeCSS root)
	{
		root.children = new NodeCSS[n];
		for(int i = 1;i <= n;i++)
		{
			NodeCSS node = new NodeCSS();
			node.r = i;
			node.j = 1;
			float val = 0.0f;
			for(int j = 1;j <= n;j++)
				val += Q[j][i];
			node.V = val;
			node.parent = root;
			node.children = null;
			root.children[i-1] = node;
		}
	}
	
	//Works only for a node that has a parent node.
	private void expandNode(NodeCSS node)
	{
		NodeCSS parent = node.parent;
		NodeCSS[] sibling = parent.children;
		node.children = new NodeCSS[sibling.length-1];
		int index = 0;
		for(int i = 0;i < sibling.length;i++)
		{
			if(sibling[i].r == node.r)
				continue;
			NodeCSS child = new NodeCSS();
			child.r = sibling[i].r;
			child.j = node.j + 1;
			child.V = sibling[i].V - Q[node.r][child.r];
			child.parent = node;
			child.children = null;
			node.children[index] = child;
			index++;
		}
	}
	
	/**
	 * @param node
	 * @return the child of the argument node that has the smallest V value.
	 */
	private NodeCSS getBestChild(NodeCSS node)
	{
		NodeCSS result = node.children[0];
		float min = result.V;
		for(int i = 1;i < node.children.length;i++)
		{
			NodeCSS tmpNode = node.children[i];
			if(tmpNode.V < min)
			{
				min = tmpNode.V;
				result = tmpNode;
			}
		}
		return result;
	}
}