package gmm;

/**
 * This class represents a node in the search tree being
 * explored by the greedy CSS algorithm.
 * @author bhushan
 */
public class NodeCSS
{
	int r; //the item corresponding to this node
	int j; //the depth of this node
	float V; //the V_j for this node
	NodeCSS parent; //pointer to parent of this node
	NodeCSS[] children; //children of this node
}
