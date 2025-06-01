package gmm.clique;

import java.io.*;
import java.util.Date;
import gmm.ExptsManager;
import gmm.InputGenerator;
import gmm.HeuristicComputer;

public class ApproxRatioFinder
{
	public static void main(String[] args) throws IOException
	{
		if(args.length < 3)
		{
			System.out.print("Command-line arguments needed: ");
			System.out.println("parameters file, output file and iterations count. Exiting.");
			System.exit(1);
		}
		
		int iters = Integer.parseInt(args[2]);
		InputGenerator ig = new InputGenerator(args[0]);
		int n = ig.get_n();
		float[] R = new float[1+n];
		float[] R_sos = new float[1+n];
		for(int k = 1;k <= n;k++)
		{
			R[k] = 0;
			R_sos[k] = 0;
		}
		int maxK = n;
		float[] offsets = new float[1+n];
		for(int k = 1;k <= n;k++)
			offsets[k] = k*(k-1)*HeuristicComputer.W/2.0f;

		Date startTime = new Date();
		for(int i = 0;i < iters;i++)
		{
			float[][] Q = ig.getMatrixQ();
			MinCliquesFinder mcf = new MinCliquesFinder(Q);
			float[] opt = mcf.getMinCliqueWeights();
			mcf.clear();
			HeuristicComputer hc = new HeuristicComputer(Q);
			float[] approx = hc.getMinCliqueWeights();
			if((1+maxK) > opt.length)
				maxK = opt.length - 1;
			for(int k = 2;k <= maxK;k++)
			{
				float r = (offsets[k]-opt[k])/(offsets[k]-approx[k]);
				R[k] += r;
				R_sos[k] += (r*r);
			}
		}
		Date endTime = new Date();
		
		PrintWriter out = new PrintWriter(new FileWriter(args[1]));
		out.println("Input");
		out.println();
		BufferedReader in = new BufferedReader(new FileReader(args[0]));
		String line = in.readLine();
		while(line != null)
		{
			out.println(line);
			line = in.readLine();
		}
		in.close();
		out.println("--------------------------------------");
		out.println("Output");
		out.println();
		out.println("k\tApproximation Ratio\tStd Dev");
		for(int k = 2;k <= maxK;k++)
		{
			out.print(k + "\t" + R[k]/iters + "\t");
			out.println(ExptsManager.getStdDev(R[k],R_sos[k],iters));
		}
		out.println();
		float runningTime = (endTime.getTime() - startTime.getTime())/((float)iters);
		out.println("Time per iteration (seconds): " + runningTime/1000.0f);
		out.close();
	}
}