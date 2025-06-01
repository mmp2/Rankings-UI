package gmm;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Random;
import java.util.regex.Pattern;

/**
 * This class generates instances of the input matrix Q.
 * @author bhushan
 */

public class InputGenerator
{
	private int n; //no of items being ranked
	private int N; //no of rankings in the sample
	private boolean GMM; //true indicates Generalized Mallow's Model
	private int decay; //1 indicates linear decay, 2 indicates exponential
	private int nBoot; //no of bootstrap samples
	private String inputType;
	/* "model" indicates input comes from sampling from the model itself.
	 * "random" indicates entries in the Q matrix are generated randomly.
	 * "filename.xyz" indicates the ranking dataset is in the specified file.
	 */
	private float[] theta; //theta[i] is theta_i
		
	private float[][] expThetaSums;
	private Random rng;
	
	public int get_n() { return n; }

	public int get_nBoot() {return nBoot; }
	
	public int getN() { return N; }
	
	public boolean isGMM() { return GMM; }
	
	public boolean generatesQFromModel() 
	{ 
		if(inputType.equals("model"))
			return true;
		else
			return false;
	}
	
	public InputGenerator(String paramsFile)
	{
		try
		{
			BufferedReader in = new BufferedReader(new FileReader(paramsFile));
			String line = in.readLine();
			while(line != null)
			{
				int index = line.indexOf('=');
				if(index == -1)
				{
					line = in.readLine();
					continue;
				}
				String name = line.substring(0,index);
				name = name.trim();
				index++;
				String value = 	line.substring(index);
				value = value.trim();
				if(name.equals("n"))
					n = Integer.parseInt(value);
				else if(name.equals("N"))
					N = Integer.parseInt(value);
				else if(name.equals("GMM"))
				{
					if(value.equals("true"))
						GMM = true;
					else
						GMM = false;
				}
				else if(name.equals("nBoot"))
				{
				    nBoot = Integer.parseInt(value);
				}
				else if(name.equals("theta"))
				{
					theta = new float[n];
					expThetaSums = new float[n][];
					theta[1] = Float.parseFloat(value);
				}
				else if(name.equals("decay"))
				{
					if(value.equals("linear"))
						decay = 1;
					else
						decay = 2;
				}
				else if(name.equals("inputType"))
					inputType = value;
				line = in.readLine();
			}
			in.close();
			initializeThetas();
			initializeExpThetaSums();
			rng = new Random();
		}
		catch(FileNotFoundException fnfe)
		{
			System.out.println("Parameters file not found.");
			fnfe.printStackTrace();
			System.exit(1);
		}
		catch(IOException ioe)
		{
			ioe.printStackTrace();
			System.exit(1);	
		}
	}
	
	private void initializeThetas()
	{
		if(!GMM) //single theta
			for(int i = 2;i < theta.length;i++)
				theta[i] = theta[1];
		else
		{
			if(decay == 1) //linear decay
				for(int j = 2;j < theta.length;j++)
				{
					float tmp = (j-1)*0.50f;
					tmp /= (n-2);
					tmp = 1 - tmp;
					theta[j] = tmp*theta[1];
				}
			else //exponential decay
				for(int j = 2;j < theta.length;j++)
				{
					float tmp = (j-1)/(float)(n-2);
					tmp = (float)Math.pow(0.01,tmp);
					theta[j] = tmp*theta[1];
				}
		}
	}
	
	private void initializeExpThetaSums()
	{
		for(int j = 1;j < n;j++)
		{
			int numTerms = n-j+1;
			expThetaSums[j] = new float[numTerms];
			double ratio = Math.exp((-1)*theta[j]);
			double gp = 1.0;
			expThetaSums[j][0] = 1.0f;
			for(int i = 1;i < numTerms;i++)
			{
				gp *= ratio;
				expThetaSums[j][i] = expThetaSums[j][i-1] + (float)gp;
			}
		}
	}
	
	/**
	 * @param j
	 * @return a value for $V_j$ from the set {0,1,...,n-j} where the
	 * probability of returning $i$ is proportional to $e^(-i*theta_j)$.
	 */
	public int generateVj(int j)
	{
		int max = n-j;
		float rnd = rng.nextFloat();
		rnd *= expThetaSums[j][max];
		int result = -1;
		for(int i = 0;i <= max;i++)
			if(rnd < expThetaSums[j][i])
			{
				result = i;
				break;
			}
		return result;
	}
	
	/**
	 * @return a ranking generated according to the GMM represented by
	 * this InputGenerator. The modal ranking is assumed to be (1,2,...,n).
	 */
	public void generateRanking(int[] ranking)
	{
		int[] V = new int[n];
		for(int j = 1;j < n;j++)
			V[j] = generateVj(j);
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
	
	private float[][] getRandomMatrixQ()
	{
		float[][] Q = new float[n+1][];
		for(int i = 1;i <= n;i++)
		{
			Q[i] = new float[n+1];
			for(int j = 1;j <= n;j++)
				Q[i][j] = 0.0f;
		}
		for(int i = 1;i <= n;i++)
			for(int j = (i+1);j <= n;j++)
			{
				float rand = rng.nextFloat();
				Q[i][j] = 0.001f + (rand*0.998f);
				Q[j][i] = 1 - Q[i][j];
			}
		return Q;
	}
	
	/*private String reverseString(String str)
	{
		int len = str.length();
		char[] chars = new char[len];
		for(int i = 0;i < chars.length;i++)
			chars[i] = str.charAt((len-1)-i);
		return new String(chars);
	}*/
	
	private float[][][] readQFromFile(String fileName) throws FileNotFoundException,IOException
	{
		float[][][] Q = new float[nBoot+1][n+1][];
		for(int ib = 1; ib <= nBoot;ib++)
		{
		    for(int i = 1;i <= n;i++)
		    {
			    Q[ib][i] = new float[n+1];
			    for(int j = 1;j <= n;j++)
				    Q[ib][i][j] = 0.0f;
		    }
		}

		int[] ranking = new int[n];
		Pattern wsPattern = Pattern.compile("\\s+");
		int r = 0;
		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = in.readLine();
		while(line != null)
		{
		    int ib = r/N + 1;
			r++;
			line = line.trim();
			String[] tokens = wsPattern.split(line);
			if(tokens.length != n)
			{
				System.out.println("Line " + r + " of rankings file has an error. Exiting.");
				System.exit(1);
			}
			for(int i = 0;i < n;i++)
				ranking[i] = Integer.parseInt(tokens[i]);
			for(int i = 0;i < n;i++)
				for(int j = (i+1);j < n;j++)
					Q[ib][ranking[i]][ranking[j]] += 1.0f;
			line = in.readLine();
		}
		in.close();
		for(int ib = 1; ib <= nBoot; ib++)
		{
		    for(int i = 1;i <= n;i++)
			    for(int j = 1;j <= n;j++)
				    Q[ib][i][j] /= N;
		    for(int i = 1;i <= n;i++)
			    for(int j = 1;j <= n;j++)
			    {
				    if(Q[ib][i][j] < 0.00001)
					    Q[ib][i][j] = 0.00001f;
				    else if(Q[ib][i][j] > 0.99999)
					    Q[ib][i][j] = 0.99999f;
			    }
		}
		return Q;
	}
	
	/**
	 * @return an instance of the Q matrix. Q[i][j] is the probability
	 * that i is preferred to j in the ranking data.
	 */
	public float[][] getMatrixQ(int ib)
	{
		if(inputType.equals("random"))
		{
			float[][] randQ = getRandomMatrixQ();
			return randQ;
		}
		else if(inputType.equals("model"))
		{
			float[][] Q = new float[n+1][];
			for(int i = 1;i <= n;i++)
			{
				Q[i] = new float[n+1];
				for(int j = 1;j <= n;j++)
					Q[i][j] = 0.0f;
			}
			int[] ranking = new int[n];
			for(int k = 0;k < N;k++)
			{
				generateRanking(ranking);
				for(int i = 0;i < n;i++)
					for(int j = (i+1);j < n;j++)
						Q[ranking[i]][ranking[j]] += 1.0f;
			}
			for(int i = 1;i <= n;i++)
				for(int j = 1;j <= n;j++)
					Q[i][j] /= N;
			for(int i = 1;i <= n;i++)
				for(int j = 1;j <= n;j++)
				{
					if(Q[i][j] < 0.00001)
						Q[i][j] = 0.00001f;
					else if(Q[i][j] > 0.99999)
						Q[i][j] = 0.99999f;
				}
			return Q;
		}
		else
		{
			try
			{
				float[][][] inputQ = readQFromFile(inputType);
				return inputQ[ib];
			}
			catch(FileNotFoundException fnfe)
			{
				System.out.println("Rankings dataset file not found. Exiting.");
				fnfe.printStackTrace();
				System.exit(1);
			}
			catch(IOException ioe)
			{
				ioe.printStackTrace();
				System.exit(1);	
			}
		}
		return null; //will never execute, just to keep the compiler happy
	}
	
	public void displayMatrixQ(float[][] Q)
	{
		for(int i = 1;i <= n;i++)
		{
			for(int j = 1;j <= n;j++)
				System.out.print(Q[i][j] + "\t");
			System.out.println();
		}
	}
	
	//for testing only
	/*public static void main(String[] args)
	{
		InputGenerator ig = new InputGenerator("gmm/params.txt");
		boolean GMM = ig.isGMM();
		float[][] Q = ig.getMatrixQ();
		AStar aStar = new AStar(GMM,Q,1);
		aStar.run();
		System.out.println("Nodes Generated: " + aStar.getNodesGenerated());
		System.out.println("Avg D_k: " + aStar.getAvgDk());
		System.out.println("Running Time in ms: " + aStar.getRunningTime());
	}*/
}