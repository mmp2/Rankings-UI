package gmm;

public class ItemRank implements Comparable<ItemRank>
{
	int item; 
	float avgRank; //the rank for the item
	
	public int compareTo(ItemRank other)
	{
		if(this.avgRank < other.avgRank)
			return -1;
		else if(this.avgRank > other.avgRank)
			return 1;
		else
			return 0;
	}
}