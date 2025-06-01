package gmm;

import java.util.PriorityQueue;
import java.util.Random;

/**
 * This class represents a node in the search tree being
 * explored by the A* search algorithm.
 * @author bhushan
 */
public class Node implements Comparable<Node>
{
	int r; //the item corresponding to this node
	int j; //the depth of this node
	float V; //the V_j for this node
	float remDk; //lower bound on sum of remaining V_j values

	Node parent; //pointer to parent of this node
	Node[] children; //children of this node
	float theta; //field used only when GMM = true
	float cost; //total cost from root node up to this node
	float remCost; //lower bound on remaining cost
	float L; //L = cost + remCost

	public static int size = 72; //avg size in bytes for a Node
	
	public int compareTo(Node node)
	{
		if(this.L < node.L)
			return -1;
		else if(this.L > node.L)
			return 1;
		else
			return 0;
	}
	
	//peripheral code for determining the average size of a Node object
	public static void main(String[] args)
	{
		int count = 1000000;
		Node someNode = new Node();
		PriorityQueue<Node> priorityQ = new PriorityQueue<Node>();
		Random rng = new Random();
		Runtime runtime = ExptsManager.runtime;
		ExptsManager.freeMemory();
		long heap1 = runtime.totalMemory() - runtime.freeMemory();
		for(int i = 0;i < count;i++)
		{
			Node node = new Node();
			node.L = rng.nextFloat();
			node.parent = someNode;
			node.children = new Node[1];
			node.children[0] = someNode;
			priorityQ.add(node);
		}
		ExptsManager.freeMemory();
		long heap2 = runtime.totalMemory() - runtime.freeMemory();
		float size = (float)(heap2 - heap1)/count;
		System.out.println("Avg Node Size = " + size + " bytes.");
		//to ensure that priorityQ is not garbage collected
		for(int i = 0;i < 10;i++)
			priorityQ.poll();

	}
}