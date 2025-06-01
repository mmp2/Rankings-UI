package gmm;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Arrays;

public class ExptsManager
{
	public static Runtime runtime = Runtime.getRuntime();
	
	public static void freeMemory()
	{
		for(int i = 0;i < 2;i++)
		{
			runtime.gc();
			runtime.runFinalization();
			Thread.yield();
		}
	}
	
	/**
	 * @param pi1
	 * @param pi2
	 * @return the Kendall distance between rankings pi1 and pi2.
	 */
	public static int getDistance(int[] pi1,int[] pi2) throws Exception
	{
		if(pi1.length != pi2.length)
		{
			String message = "Kendall distance can only be determined between " +
						 	 "rankings on the same set of objects.";
			throw new Exception(message);
		}
		HashMap<Integer,Integer> hm = new HashMap<Integer,Integer>();
		for(int i = 0;i < pi1.length;i++)
		{
			Integer key = new Integer(pi1[i]);
			Integer value = new Integer(i+1);
			hm.put(key,value);
		}
		int[] pi = new int[pi2.length];
		for(int i = 0;i < pi2.length;i++)
		{
			Integer value = hm.get(new Integer(pi2[i]));
			pi[i] = value.intValue();
		}
		int result = 0;
		for(int i = 0;i < pi.length;i++)
			for(int j = (i+1);j < pi.length;j++)
				if(pi[i] > pi[j])
					result++;
		return result;
	}
	
	/**
	 * @param sum the sum of sample points.
	 * @param sumOfSquares the sum of squares of sample points.
	 * @param sampleSize the number of sample points.
	 * @return the standard deviation.
	 */
	public static float getStdDev(float sum,float sumOfSquares,int sampleSize)
	{
		float mean = sum/sampleSize;
		float variance = (sumOfSquares/sampleSize) - (mean*mean);
		if(variance < 0.0f)
			variance = 0.0f;
		return (float)Math.sqrt(variance);
	}
	
	/*public static String getQuantiles(float[] arr)
	{
		int len = arr.length;
		int quarter = len/4;
		float median = arr[2*quarter-1];
		float lower = arr[quarter-1];
		lower = median - lower;
		float upper = arr[3*quarter-1];
		upper = upper - median;
		String result = "" + median + "\t(-" + lower;
		result = result + ") (+" + upper + ")";
		return result;
	}*/
	
	public static void main(String[] args) throws IOException
	{
		if(args.length < 3)
		{
			System.out.print("Command-line arguments needed: ");
			System.out.println("parameters file, output file and dump file. Exiting.");
			System.exit(1);
		}
		
		//set default parameter values
		boolean GMM = true;
		boolean isBoot = true;
		int iters = 20;
		int beamwidth = 1000;
		String method = "AStar";
		//read parameters file
		BufferedReader in = new BufferedReader(new FileReader(args[0]));
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
			if(name.equals("GMM"))
			{
				if(value.equals("true"))
					GMM = true;
				else
					GMM = false;
			}
			else if(name.equals("iterations"))
				iters = Integer.parseInt(value);
			else if(name.equals("beamwidth"))
				beamwidth = Integer.parseInt(value);
			else if(name.equals("method"))
				method = value;
			line = in.readLine();
		}
		in.close();
		
		InputGenerator ig = new InputGenerator(args[0]);
		int n = ig.get_n(); //the no of items being ranked
		int nBoot = ig.get_nBoot();//no of bootstrap samples
		if(nBoot==1)
		{
		    isBoot = false;
		}
		else
		{
		    isBoot = true;
		}
		boolean QFromModel = ig.generatesQFromModel();
		int[] pi_true = null;
		if(QFromModel)
		{
			pi_true = new int[n];
			for(int j = 0;j < n;j++)
				pi_true[j] = (j+1);
		}
		
		//open the dump file
		PrintWriter dump = new PrintWriter(new FileWriter(args[2]));
		dump.println("Input");
		dump.println();
		in = new BufferedReader(new FileReader(args[0]));
		line = in.readLine();
		while(line != null)
		{
			dump.println(line);
			line = in.readLine();
		}
		in.close();
		dump.println("--------------------");
		
		float nodesGen = 0;
		float nodesGen_sos = 0; //the suffix _sos indicates "sum of squares"
		float nodesGenAsMult = 0;
		float nodesGenAsMult_sos = 0;
		float finishedinAStar = 0;
		float searchSteps_fv = 0;
		float searchSteps_fv_sos = 0;
		
		float time_as = 0;
		float time_as_sos = 0;
		float time_css = 0;
		float time_css_sos = 0;
		float time_fv = 0;
		float time_fv_sos = 0;
		float time_rand = 0;
		float time_rand_sos = 0;
		float time_dk = 0;
		float time_dk_sos = 0;
		
		float dist_css = 0;
		float dist_css_sos = 0;
		float dist_fv = 0;
		float dist_fv_sos = 0;
		float dist_rand = 0;
		float dist_rand_sos = 0;
		float dist_dk = 0;
		float dist_dk_sos = 0;
		
		float dftm_as = 0; //dftm stands for "distance from true mode"
		float dftm_as_sos = 0;
		float dftm_css = 0;
		float dftm_css_sos = 0;
		float dftm_fv = 0;
		float dftm_fv_sos = 0;
		float dftm_rand = 0;
		float dftm_rand_sos = 0;
		float dftm_dk = 0;
		float dftm_dk_sos = 0;
		
		float cost_as = 0;
		float cost_as_sos = 0;
		float cost_css = 0;
		float cost_css_sos = 0;
		float cost_fv = 0;
		float cost_fv_sos = 0;
		float cost_rand = 0;
		float cost_rand_sos = 0;
		float cost_dk = 0;
		float cost_dk_sos = 0;
		
		//measures for which we want the median values too
		float[] nodesGenAsMultArray = new float[iters];
		float[] time_as_array = new float[iters];
		
		int i = 0;
		int ib = 0;
		float val = 0;
		try
		{
			for(i = 0;i < iters;i++)
			{
				dump.println("Iteration " + (i+1) + "\n");
				freeMemory();
				if(isBoot)
				{
				    if(method.equals("AStar"))
				    {
				        dump.println("AStar");
				        for(ib = 1; ib<= nBoot; ib++)
				        {
				            float[][] Q = ig.getMatrixQ(ib);
				            AStar astar = new AStar(GMM,Q,1,beamwidth);
				            astar.run();
				            astar.printLearnedModel(dump);
				        }
				    }
				    else if (method.equals("GreedyCSS"))
				    {
				        dump.println("\nCSS");
				        for(ib = 1; ib<= nBoot; ib++)
				        {
				            float[][] Q = ig.getMatrixQ(ib);
				            GreedyCSS css = new GreedyCSS(GMM,Q);
				            css.run();
				            css.printLearnedModel(dump);
				        }
				    }
				    else if (method.equals("FV"))
				    {
				        dump.println("\nFV");
				        for(ib = 1; ib<= nBoot; ib++)
				        {
				            float[][] Q = ig.getMatrixQ(ib);
				            FVHeuristic fv = new FVHeuristic(GMM,Q);
				            fv.run();
				            fv.printLearnedModel(dump);
				        }
				    }
				    else if (method.equals("Rand"))
				    {
				        dump.println("\nRand");
				        for(ib = 1; ib<= nBoot; ib++)
				        {
				            float[][] Q = ig.getMatrixQ(ib);
				            RandomEstimator rand = new RandomEstimator(GMM,Q);
				            rand.run();
				            rand.printLearnedModel(dump);
				        }
				    }
				    else if (method.equals("GreedyDK") && !GMM)
				    {
					    dump.println("\nDK");
					    for(ib = 1; ib<= nBoot; ib++)
				        {
				            float[][] Q = ig.getMatrixQ(ib);
					        GreedyDK dk = new GreedyDK(GMM,Q);
					        dk.run();
					        dk.printLearnedModel(dump);
				        }
				    }
				    freeMemory();
				}
				else
				{
				    float[][] Q = ig.getMatrixQ(1);
				    AStar astar = new AStar(GMM,Q,1,beamwidth);
				    astar.run();
				    if (method.equals("AStar"))
				    {
				        dump.println("AStar");
				        val = astar.getNodesGenerated();
				        nodesGen += val;
				        nodesGen_sos += (val*val);
				        dump.println("Nodes Generated: " + val);
				        val = astar.getNodesGeneratedAsMultiple();
				        nodesGenAsMult += val;
				        nodesGenAsMult_sos += (val*val);
				        dump.println("Nodes Generated as Multiple: " + val);
				        nodesGenAsMultArray[i] = val;
				        if(!astar.finishedWithBeam())
					        finishedinAStar += 1.0f;
				        else
					        dump.println("Reverted to beam search.");
				        val = astar.getRunningTime();
				        time_as += val;
				        time_as_sos += (val*val);
				        dump.println("Running Time: " + val);
				        time_as_array[i] = val;
				        int[] pi_as = astar.getPi();
				        if(QFromModel)
				        {
					        val = getDistance(pi_true,pi_as);
					        dftm_as += val;
					        dftm_as_sos += (val*val);
					        dump.println("Distance from True Mode: " + val);
				        }
				        val = astar.getLogL();
				        cost_as += val;
				        cost_as_sos += (val*val);
				        dump.println("Cost: " + val);
				        astar.printLearnedModel(dump);
				    }
				    else if (method.equals("GreedyCSS"))
				    {
				        GreedyCSS css = new GreedyCSS(GMM,Q);
				        css.run();
				        dump.println("\nCSS");
				        val = css.getRunningTime();
				        time_css += val;
				        time_css_sos += (val*val);
				        int[] pi_css = css.getPi();
				        int[] pi_as = astar.getPi();
				        val = getDistance(pi_as,pi_css);
				        dist_css += val;
				        dist_css_sos += (val*val);
				        dump.println("Distance from Optimal Mode: " + val);
				        if(QFromModel)
				        {
					        val = getDistance(pi_true,pi_css);
					        dftm_css += val;
					        dftm_css_sos += (val*val);
					        dump.println("Distance from True Mode: " + val);
				        }
				        val = css.getLogL();
				        cost_css += val;
				        cost_css_sos += (val*val);
				        dump.println("Cost: " + val);
				        css.printLearnedModel(dump);
				    }
				    else if (method.equals("FV"))
				    {
				        FVHeuristic fv = new FVHeuristic(GMM,Q);
				        fv.run();
				        dump.println("\nFV");
				        val = fv.getLocalSearchSteps();
				        searchSteps_fv += val;
				        searchSteps_fv_sos += (val*val);
				        val = fv.getRunningTime();
				        time_fv += val;
				        time_fv_sos += (val*val);
				        int[] pi_fv = fv.getPi();
				        int[] pi_as = astar.getPi();
				        val = getDistance(pi_as,pi_fv);
				        dist_fv += val;
				        dist_fv_sos += (val*val);
				        dump.println("Distance from Optimal Mode: " + val);
				        if(QFromModel)
				        {
					        val = getDistance(pi_true,pi_fv);
					        dftm_fv += val;
					        dftm_fv_sos += (val*val);
					        dump.println("Distance from True Mode: " + val);
				        }
				        val = fv.getLogL();
				        cost_fv += val;
				        cost_fv_sos += (val*val);
				        dump.println("Cost: " + val);
				        fv.printLearnedModel(dump);
				    }
				    else if (method.equals("Rand"))
				    {
				        RandomEstimator rand = new RandomEstimator(GMM,Q);
				        rand.run();
				        dump.println("\nRand");
				        val = rand.getRunningTime();
				        time_rand += val;
				        time_rand_sos += (val*val);
				        int[] pi_rand = rand.getPi();
				        int[] pi_as = astar.getPi();
				        val = getDistance(pi_as,pi_rand);
				        dist_rand += val;
				        dist_rand_sos += (val*val);
				        dump.println("Distance from Optimal Mode: " + val);
				        if(QFromModel)
				        {
					        val = getDistance(pi_true,pi_rand);
					        dftm_rand += val;
					        dftm_rand_sos += (val*val);
					        dump.println("Distance from True Mode: " + val);
				        }
				        val = rand.getLogL();
				        cost_rand += val;
				        cost_rand_sos += (val*val);
				        dump.println("Cost: " + val);
				        rand.printLearnedModel(dump);
				    }
				    else if (method.equals("GreedyDK") && !GMM)
				    {
					    freeMemory();
					    GreedyDK dk = new GreedyDK(GMM,Q);
					    dk.run();
					    dump.println("\nDK");
					    val = dk.getRunningTime();
					    time_dk += val;
					    time_dk_sos += (val*val);
					    int[] pi_dk = dk.getPi();
					    int[] pi_as = astar.getPi();
					    val = getDistance(pi_as,pi_dk);
					    dist_dk += val;
					    dist_dk_sos += (val*val);
					    dump.println("Distance from Optimal Mode: " + val);
					    if(QFromModel)
					    {
						    val = getDistance(pi_true,pi_dk);
						    dftm_dk += val;
						    dftm_dk_sos += (val*val);
						    dump.println("Distance from True Mode: " + val);
					    }
					    val = dk.getLogL();
					    cost_dk += val;
					    cost_dk_sos += (val*val);
					    dump.println("Cost: " + val);
					    dk.printLearnedModel(dump);
				    }
				    freeMemory();
				}
			}
			dump.println();
			//dump.println("Q:");
		    //for (int k=1;k<Q.length;k++){
			//    dump.println(Arrays.toString(Q[k]));
			//}
		}
		catch(Exception e)
		{
			PrintWriter out = new PrintWriter(new FileWriter(args[1]));
			i++;
			out.println("Iteration " + i);
			out.println(e.getMessage());
			e.printStackTrace(out);
			out.println("Exiting.");
			out.close();
			System.exit(1);
		}

		dump.println("-----------------------------");
		dump.println("-----------------------------");
		dump.close();
		PrintWriter out = new PrintWriter(new FileWriter(args[1]));
		//we first copy the input parameters into the results file.
		out.println("Input");
		out.println();
		in = new BufferedReader(new FileReader(args[0]));
		line = in.readLine();
		while(line != null)
		{
			out.println(line);
			line = in.readLine();
		}
		in.close();
		out.println("--------------------------------------");
		
		out.println("Output");
		out.println();
		out.print("Nodes Generated: " + nodesGen/iters + "\t +- ");
		out.println(getStdDev(nodesGen,nodesGen_sos,iters));
		out.print("Nodes Generated as Multiple: " + nodesGenAsMult/iters + "\t +- ");
		out.println(getStdDev(nodesGenAsMult,nodesGenAsMult_sos,iters));
		out.println("Fraction Finished in A*: " + finishedinAStar/iters);
		out.print("Local Search Steps in FV: " + searchSteps_fv/iters + "\t +- ");
		out.println(getStdDev(searchSteps_fv,searchSteps_fv_sos,iters));
		out.println();
		out.println("Running Times (in milliseconds):");
		out.print("AStar: " + time_as/iters + "\t +- ");
		out.println(getStdDev(time_as,time_as_sos,iters));
		out.print("CSS: " + time_css/iters + "\t +- ");
		out.println(getStdDev(time_css,time_css_sos,iters));
		out.print("FV: " + time_fv/iters + "\t +- ");
		out.println(getStdDev(time_fv,time_fv_sos,iters));
		out.print("Random: " + time_rand/iters + "\t +- ");
		out.println(getStdDev(time_rand,time_rand_sos,iters));
		if(!GMM)
		{
			out.print("DK: " + time_dk/iters + "\t +- ");
			out.println(getStdDev(time_dk,time_dk_sos,iters));
		}
		out.println();
		out.println("Kendall Distance from Optimal Mode:");
		out.print("CSS: " + dist_css/iters + "\t +- ");
		out.println(getStdDev(dist_css,dist_css_sos,iters));
		out.print("FV: " + dist_fv/iters + "\t +- ");
		out.println(getStdDev(dist_fv,dist_fv_sos,iters));
		out.print("Random: " + dist_rand/iters + "\t +- ");
		out.println(getStdDev(dist_rand,dist_rand_sos,iters));
		if(!GMM)
		{
			out.print("DK: " + dist_dk/iters + "\t +- ");
			out.println(getStdDev(dist_dk,dist_dk_sos,iters));
		}
		out.println();
		if(QFromModel)
		{
			out.println("Kendall Distance from True Mode:");
			out.print("AStar: " + dftm_as/iters + "\t +- ");
			out.println(getStdDev(dftm_as,dftm_as_sos,iters));
			out.print("CSS: " + dftm_css/iters + "\t +- ");
			out.println(getStdDev(dftm_css,dftm_css_sos,iters));
			out.print("FV: " + dftm_fv/iters + "\t +- ");
			out.println(getStdDev(dftm_fv,dftm_fv_sos,iters));
			out.print("Random: " + dftm_rand/iters + "\t +- ");
			out.println(getStdDev(dftm_rand,dftm_rand_sos,iters));
			if(!GMM)
			{
				out.print("DK: " + dftm_dk/iters + "\t +- ");
				out.println(getStdDev(dftm_dk,dftm_dk_sos,iters));
			}
			out.println();
		}
		out.println("Cost:");
		out.print("AStar: " + cost_as/iters + "\t +- ");
		out.println(getStdDev(cost_as,cost_as_sos,iters));
		out.print("CSS: " + cost_css/iters + "\t +- ");
		out.println(getStdDev(cost_css,cost_css_sos,iters));
		out.print("FV: " + cost_fv/iters + "\t +- ");
		out.println(getStdDev(cost_fv,cost_fv_sos,iters));
		out.print("Random: " + cost_rand/iters + "\t +- ");
		out.println(getStdDev(cost_rand,cost_rand_sos,iters));
		if(!GMM)
		{
			out.print("DK: " + cost_dk/iters + "\t +- ");
			out.println(getStdDev(cost_dk,cost_dk_sos,iters));
		}
		out.println();
		/*out.println("Median Values: ");
		Arrays.sort(nodesGenAsMultArray);
		Arrays.sort(time_as_array);
		out.println("Nodes Generated as Multiple: " + getQuantiles(nodesGenAsMultArray));
		out.println("AStar Running Time: " + getQuantiles(time_as_array));*/
		out.close();
	}
}