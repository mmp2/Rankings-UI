package model;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;
import java.util.Scanner;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

public class RIM_main {
	public static void main(String[] args) throws IOException {
		
		long startTime = System.currentTimeMillis();

		/* Sushi data test with included test input example */
		String defaultRimArgs="-permtest file=data/sushi/SushiClean.txt ptest=.3 pvalidation=.2 iters=1000 temp=.03 dataSeed=400 runtimeSeed=400 nboot=1";
		/* Synthetic Test with included synthetic test input example */
		String defaultSynthArgs="-synthtest n=12 thetalow=.5 thetahigh=2 Ntrain=100 iters=150 temp=.02";
		/* Input predefined tree */
		String defaultTreeArgs="-importrim rim=([0.7],0,([1.1],([0.9],1,([0.2],([1.0],2,3),4)),([0.3],([0.9],([0.8],5,6),7),([1.0],8,9))))";

		// For faking input from command line
		//args=defaultSynthArgs.split(" ");
		//args=defaultPermArgs.split(" ");
		//args=defaultTreeArgs.split(" ");
		
		if(args.length==0) {
			args="no input".split(" ");
		}
		
		if(args[0].equals("-synthtest")) {
			//Default settings
			int n=15;
			double thetalow=.5;
			double thetahigh=1.2;
			int Ntrain=5000;
			int iters=1000;
			double temp=.02;
			Random rand=new Random();
			int randSeed=rand.nextInt();
			
			for(int i=1;i<args.length;i++) {
				String[] input=args[i].split("=", 2);
				if(input[0].equals("n"))
					n=Integer.parseInt(input[1]);
				else if(input[0].equals("thetalow"))
					thetalow=Double.parseDouble(input[1]);
				else if(input[0].equals("thetahigh"))
					thetahigh=Double.parseDouble(input[1]);
				else if(input[0].equals("iters"))
					iters=Integer.parseInt(input[1]);
				else if(input[0].equals("Ntrain"))
					Ntrain=Integer.parseInt(input[1]);
				else if(input[0].equals("temp"))
					temp=Double.parseDouble(input[1]);
				else if(input[0].equals("randseed"))
					randSeed=Integer.parseInt(input[1]);
				else {
					System.out.println("Unknown parameter: "+input[0]);
				}
			}
			System.out.println("Running synthetic test with following parameters");
			System.out.println("n="+n+"; thetalow="+thetalow+"; thetahigh="+thetahigh+"; Ntrain="+Ntrain+
					"; iters="+iters+"; temp="+temp+"; randSeed="+randSeed);
			SimpleTest(n,thetalow,thetahigh,Ntrain,iters,temp,randSeed);
		} else if(args[0].equals("-permtest")) {
			//Default settings
			String filename=null;
			double ptest=0;
			double pvalidation=0;
			int iters=1000;
			double temp=0.2;
			Random rand=new Random();
			int runtimeSeed=rand.nextInt();
			int nboot=1;
			int dataSeed=rand.nextInt();
			
			for(int i=1;i<args.length;i++) {
				String[] input=args[i].split("=", 2);
				if(input[0].equals("file")) {
					filename=input[1];
					File infile=new File(filename);
					Scanner lineScanner = new Scanner(infile);
					int N=0;
					while(lineScanner.hasNext()) {
						lineScanner.next();
						N++;
					}
					//System.out.println("Successfully read file \""+filename+"\" with N="+N+" total permutations");
				} else if (input[0].equals("ptest")) {
					ptest=Double.parseDouble(input[1]);
				} else if (input[0].equals("pvalidation")) {
					pvalidation=Double.parseDouble(input[1]);
				} else if (input[0].equals("iters")) {
					iters=Integer.parseInt(input[1]);
				} else if (input[0].equals("temp")) {
					temp=Double.parseDouble(input[1]);
				} else if (input[0].equals("dataSeed")) {
					dataSeed=Integer.parseInt(input[1]);
				} else if (input[0].equals("runtimeSeed")) {
					runtimeSeed=Integer.parseInt(input[1]);
				} else if(input[0].equals("nboot")){
				    nboot=Integer.parseInt(input[1]);
				} else {
					System.out.println("Unknown parameter: "+input[0]);
				}
			}
			//System.out.println("Running permutation test with following parameters");
			//System.out.println("file="+filename+"; ptest="+ptest+"; pvalidation="+pvalidation+"; iters="+iters+"; temp="+temp+"; runtimeSeed="+runtimeSeed+"; dataSeed="+dataSeed);
			PermTest(filename, ptest, pvalidation, temp, dataSeed, iters, runtimeSeed, nboot);
		}else if(args[0].equals("-importrim")) {
			String treeString=null;
			String[] input=args[1].split("=", 2);
			if(input[0].equals("rim")) {
				treeString=input[1];
			}
			System.out.println("Importing the following RIM");
			System.out.println(treeString);
			ImportTree(treeString);
		} else {
			System.out.println("No valid test selected");
			System.out.println("Example commands:");
			System.out.println(defaultSynthArgs);
			System.out.println("Or");
			System.out.println(defaultRimArgs);
			System.out.println("Or");
			System.out.println(defaultTreeArgs);
		}


		long endTime = System.currentTimeMillis();
		long runTime = (endTime - startTime);
		long seconds=runTime/1000;
		System.out.println("Total runtime approximately "+seconds+" seconds");
		if(seconds<60)
			System.out.println("Total runtime approximately "+seconds+" seconds");
		else if(seconds<3600)
			System.out.println("Total runtime approximately "+seconds/60+" minutes");
		else
			System.out.println("Total runtime approximately "+seconds/3600+" hours");
	}

	private static void ImportTree(String treeString) {
		/*
		 * Imports a tree of the form ([theta],node,node)
		 */
		int nitems=1;
		for(char c:treeString.toCharArray())
			if(c=='[')
				nitems++;
		int[][][] empty = new int[1][1][nitems];
		for (int k = 0; k < nitems; k++)
			empty[0][0][k] = k;

		CRIM utiltree = new CRIM(empty, 0, 0);
		utiltree.root=utiltree.treeFromString(treeString);
		System.out.println(utiltree);

		int[] items = new int[nitems];
		for(int i=1;i<nitems;i++)
			items[i]=i;

		System.out.println("Marginal P");
		printDoubleArray(utiltree.root.getP(items, 0));
		System.out.println("Marginal Q");
		printDoubleArray(utiltree.root.getFullQ()[0]);

		int Ntrain=50000;
		Random rand = new Random();
		int[][][] samplePerms=new int[1][Ntrain][nitems];
		int[][][] gids = utiltree.sampleGIDs(utiltree.root, samplePerms, rand);

		CRIM testfit = new CRIM(gids, 0, 0);
		System.out.println("Large sample Qhat");
		double[][] Qcopy=new double[nitems][nitems];
		for(int i=0;i<nitems;i++)
			for(int j=0;j<nitems;j++)
				Qcopy[i][j]=testfit.Qobs_pi0[0][i][j]/Ntrain;
		printDoubleArray(Qcopy);

	}


	private static void PermTest(String filename, double ptest, double pvalidation, double temp,
	                             int dataSeed, int iters, int runtimeSeed, int nboot) throws FileNotFoundException{
		/*
		 * Fits a model to set a permutations (imported from filename)
		 * @param	filename	path to file containing CSV permutations
		 * @param	ptest	proportion of data to be used for testing (double [0,1))
		 * @param	pvalidation	proportion of data to be used for validation (double [0,1))
		 * @param	iters	Number of iterations of the search procedure
		 * @param	temp	Temperature for simulated annealing
		 * @param	dataSeed	Seed used for splitting the data - identical ptest/pvalidation and dataSeed values should produce the same datasplit
		 * @param	runtimeSeed	Seed used for sampling new models while fitting
		 * @return 	Void, prints out barQ and barP
		 * ptest
		 */
		File infile=new File(filename);
		Scanner lineScanner = new Scanner(infile);
		int N=1;
		int nitems=lineScanner.nextLine().split(" ").length;
		while(lineScanner.hasNextLine()) {
			lineScanner.nextLine();
			N++;
		}
		//System.out.println("Input data with with Ntotal="+N+"; nitems="+nitems);

        int bsize = N/nboot;
        lineScanner = new Scanner(infile);
        for (int ib=1; ib<=nboot; ib++){
            int[][][] perms=new int[1][bsize][nitems];
		    for(int i=0;i<bsize;i++) {
			    String[] items=lineScanner.nextLine().split(" ");
			    for(int j=0;j<nitems;j++)
				    perms[0][i][j]=Integer.parseInt(items[j])-1;
		    }
		    int[][][] GIDs=permToGID(perms);

		    CRIM fitter=new CRIM(GIDs, ptest*100, pvalidation*100, dataSeed);
		    fitter.fit0(iters, temp, new Random(runtimeSeed));

		    System.out.println(fitter);
		    System.out.println(-fitter.loglikelihood(fitter.root, fitter.N_pi0, fitter.Qobs_pi0, fitter.groupIDs_pi0, fitter.groupIDs_copy));
        }
		/*System.out.println(fitter);
		System.out.println("Log likelihoods");
		System.out.println("Training: "+fitter.loglikelihood(fitter.root, fitter.N_pi0, fitter.Qobs_pi0, fitter.groupIDs_pi0, fitter.groupIDs_copy));
		System.out.println("Testing: "+fitter.loglikelihood(fitter.root, fitter.testing_N_pi0, fitter.testing_Qobs_pi0, fitter.testing_groupIDs_pi0, fitter.testing_groupIDs_copy));
		System.out.println("Validation: "+fitter.loglikelihood(fitter.root, fitter.validation_N_pi0, fitter.validation_Qobs_pi0, fitter.validation_groupIDs_pi0, fitter.validation_groupIDs_copy));
	    */
	}
	
	private static void SimpleTest(int nitems, double thetalow, double thetahigh, int Ntrain, int iters, double temp, int randSeed) {
		/*
		 * Creates a random synthetic model, samples from it, and attempts to refit it.
		 * @param	nitems	Number of items to be ordered in the model
		 * @param	thetalow	Lowest value for sampling theta (uniform (thetalow, thetahigh))
		 * @param	thetahigh	Highest value for sampling theta (uniform (thetalow, thetahigh))
		 * @param	iters	Number of iterations of the search procedure
		 * @param	temp	Temperature for simulated annealing
		 * @param	randSeed	random seed used for sampling and fitting the data
		 * @return 	void, prints the resulting model found
		 */
		System.out.println("Running simple synthetic test");
		System.out.println("n: "+nitems+"; N: "+Ntrain);
		System.out.println("Theta range: ["+thetalow+", "+thetahigh+"]");

		Random rand=new Random(randSeed);
		CRIM sampler=createRandomTree(nitems,thetalow,thetahigh,rand);
		
		System.out.println(sampler);
		
		int[][][] samplePerms=new int[1][Ntrain][nitems];
		int[][][] gids = sampler.sampleGIDs(sampler.root, samplePerms, rand);
		
		//System.out.println(Arrays.toString(samplePerms[0][0]));
		//System.out.println(Arrays.toString(gids[0][0]));
		
		CRIM testfit = new CRIM(gids, 0, 0);
		testfit.fit0(iters, temp, rand);
		System.out.println(testfit);
		System.out.println("Qhat");
		printDoubleArray(testfit.Qobs_pi0[0]);
	}
	
	static CRIM createRandomTree(int nitems, double thetalow, double thetahigh, Random rand) {
		/*
		 * Creates a random synthetic model, samples from it, and attempts to refit it.
		 * @param	nitems	Number of items to be ordered in the model
		 * @param	thetalow	Lowest value for sampling theta (uniform (thetalow, thetahigh))
		 * @param	thetahigh	Highest value for sampling theta (uniform (thetalow, thetahigh))
		 * @param	rand	random seed used for sampling the data
		 * @return 	CRIM, a model with a random tree saved as the root
		 */
		int[][][] empty = new int[1][1][nitems];
		for (int k = 0; k < nitems; k++)
			empty[0][0][k] = k;

		CRIM randtree = new CRIM(empty, 0, 0);

		CRIM.Node[] nodes = new CRIM.Node[nitems];
		for (int k = 0; k < nitems; k++)
			nodes[k] = randtree.new Node(k);

		int ind;
		double[] thet = { 0 };
		for (int k = nitems - 1; k > 0; k--) {
			ind = rand.nextInt(k);
			// CHOOSE THE THETAS
			thet[0] = (thetahigh-thetalow)*rand.nextDouble() + thetalow;
			nodes[ind] = randtree.new Node(nodes[ind], nodes[++ind], thet);
			while (ind < k)
				nodes[ind] = nodes[++ind];
		}
		randtree.root = nodes[0];
		return(randtree);
	}
	
	static double[] standardVlCDF(int ritems, double theta){
		double[] ret=new double[ritems+1];
		double total=0;
		for(int i=0;i<=ritems;i++) {
			ret[i]=Math.exp(-i*theta);
			total+=ret[i];
		}
		for(int i=0;i<=ritems;i++)
			ret[i]/=total;
		for(int j=1;j<=ritems;j++) 
			ret[j]+=ret[j-1];
		return ret;
	}
	
	static double getVl(int left, int[] rightinds, double[][] Q) {
		double ret=0;
		for(int r:rightinds)
			ret+=Q[r][left];
		return ret;
	}
	
	static double[][] getLRCount(int left, int[] rightinds, int[][] GIDs) {
		/*
		 * Not uses in standard RIM
		 */
		double[][] ret=new double[2][rightinds.length+1];
		int R;
		for(int n=0;n<GIDs.length;n++) {
			R=0;
			for(int r:rightinds) {
				if(GIDs[n][left]==GIDs[n][r])
					R++;
			}
			ret[1][R]++;
		}
		return(ret);
	}
	
	static double getThetaStandard(double[][] LRCount, double vlbar, CRIM model) {
		/*
		 * LRCount term not used in standard RIM, otherwise finds the optimal theta for a given set of parameters
		 */
		double[][] dlZ=new double[2][LRCount[0].length];
		double[][] Z=new double[2][LRCount[0].length];
		//HARD CODED FOR n=10000
		double epsilon=0.0001;
		if(model.dLogLikelihood(dlZ, LRCount, vlbar, 0.0001, 10000.0)<0) {
			return 0;
		}
		else {
			double thetal=0;
			double thetah=1;
			while(model.dLogLikelihood(dlZ, LRCount, vlbar, thetah, 10000.0)>0)
				thetah*=2;
			while(thetah-thetal>epsilon) {
				if(model.dLogLikelihood(dlZ, LRCount, vlbar, (thetah+thetal)/2, 10000.0)/2>0)
					thetal=(thetah+thetal)/2;
				else
					thetah=(thetah+thetal)/2;
			}
			return((thetah+thetal)/2);
		}
	}	

	private static void printLines(String cmd, InputStream ins) throws Exception {
		String line = null;
		BufferedReader in = new BufferedReader(new InputStreamReader(ins));
		while ((line = in.readLine()) != null) {
			System.out.println(cmd + " " + line);
		}
	}

	private static void runProcess(String command) throws Exception {
	    @SuppressWarnings({"deprecation"})
		Process pro = Runtime.getRuntime().exec(command);
		printLines(command + " stdout:", pro.getInputStream());
		printLines(command + " stderr:", pro.getErrorStream());
		pro.waitFor();
		System.out.println(command + " exitValue() " + pro.exitValue());
	}

	public static void printDoubleArray(double[][] toprint) {
		for (double[] pline : toprint)
			System.out.println(Arrays.toString(pline));
	}

	public static int[][][] splitGroups(int[] left, int[] right) {
		int[][][] ret = new int[2][][];

		ret[0] = new int[right.length][left.length + 1];
		ret[1] = new int[right.length][right.length - 1];

		for (int r = 0; r < right.length; r++) {
			System.arraycopy(left, 0, ret[0][r], 0, left.length);
			ret[0][r][left.length] = right[r];
			System.arraycopy(right, 0, ret[1][r], 0, r);
			if (r < right.length - 1)
				System.arraycopy(right, r + 1, ret[1][r], r, right.length - r - 1);
		}

		return (ret);
	}

	public static int[][][] permToGID(int[][][] permutations) {
		int[][][] gids=new int[permutations.length][][];
		for(int f = 0; f < permutations.length; f++)
			gids[f]=new int[permutations[f].length][permutations[0][0].length];
		for (int f = 0; f < permutations.length; f++)
			for(int k=0; k<permutations[0].length;k++)	
				for (int n = 0; n < permutations[0][0].length; n++) 
					gids[f][k][permutations[f][k][n]]=n;
		return(gids);
	}
}
