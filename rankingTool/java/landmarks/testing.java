import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;
import java.util.Scanner;

public class testing {
	static boolean debug = false;

	public static void main(String[] args) throws IOException {
		int pmax=100;
		int restarts=250;
		/*
		for(int i=0;i<args.length;i++) {
			String[] input=args[i].split("=", 2);
			if(input[0].equals("infile")) {
				inFile=input[1];
			}
			if(input[0].equals("outfile")) {
				outFile=input[1];
			}
		}
		*/
		String defaultArgs="-ltest infile=Restaurants_Example/Output/Landmarks/landmarks.txt outfile=Restaurants_Example/Output/Landmarks/landmarks_out.txt nboot=1 n=12";

        String inFile=null;
		String outFile=null;
		int nboot=1;
		int n_items=12;

        if(args.length==0) {
			args="no input".split(" ");
		}

		if(args[0].equals("-ltest")){
		    for(int i=1;i<args.length;i++) {
				String[] input=args[i].split("=", 2);
				if(input[0].equals("infile")) {
				    inFile = input[1];
				} else if (input[0].equals("outfile")) {
					outFile = input[1];
				} else if(input[0].equals("nboot")){
				    nboot=Integer.parseInt(input[1]);
				} else if(input[0].equals("n")){
				    n_items=Integer.parseInt(input[1]);
				} else {
					System.out.println("Unknown parameter: "+input[0]);
				}
			}
		}
		fitToFile(inFile, outFile, n_items, pmax, restarts, nboot);
	}

	public static void synthTest(String folder, int N, int n, int m, double tl, double th, int rmax, int kmax, int imax)
			throws IOException {
		Random rand = new Random();
		for (int r = 0; r < rmax; r++) {
			char[] code = new char[4];
			for (int j = 0; j < 4; j++)
				code[j] = (char) (rand.nextInt(26) + 'A');

			String codeStr = new String(code);

			String filehead = "SLGMM_test_N" + N + "_n" + n + "_m" + m + "_tl" + Math.round(tl * 100) + "_th"
					+ Math.round(th * 100) + "_" + codeStr + ".txt";
			System.out.println("Running file: " + folder + filehead);

			int[] permDef = new int[n + m];
			for (int k = 0; k < n + m; k++)
				permDef[k] = k;

			int[] lmloc = new int[m];
			for (int k = 0; k < m; k++)
				lmloc[k] = n + k;

			double[] oneThetas = new double[n + m - 1];
			for (int k = 0; k < oneThetas.length; k++)
				oneThetas[k] = 1;

			int[] permSamp = samplePerm(permDef, oneThetas, lmloc, rand);
			double[] thetas = new double[n + m - 1];
			for (int z = 0; z < thetas.length; z++)
				thetas[z] = tl + rand.nextDouble() * (th - tl);

			synthTest(permSamp, thetas, n, m, N, kmax, imax, folder + filehead, rand);
		}
	}

	public static void synthTest(int[] perm, double[] thetas, int n, int m, int N, int kmax, int imax, String file,
			Random rand) throws IOException {
		int[] lmloc = new int[m];
		int p = 0;
		for (int i = 0; i < n + m; i++) {
			if (perm[i] == n + p) {
				lmloc[p++] = i;
			}
		}

		// Find LMs for current perm - for sampling
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - n >= 0)
				lmloc[perm[i] - n] = i;

		int[][] perms = new int[N][n + m];
		for (int k = 0; k < N; k++)
			perms[k] = samplePerm(perm, thetas, lmloc, rand);
		// Sampling Complete

		// True values
		double[] fitMeta = fitPerm(perm, n, perms);

		double[] thetasTrue = new double[n + m - 1];
		System.arraycopy(fitMeta, 1, thetasTrue, 0, n + m - 1);
		double LLTrue = fitMeta[0];

		// Initialize things
		double[] oneThetas = new double[thetas.length];
		for (p = 0; p < oneThetas.length; p++)
			oneThetas[p] = 1;

		BufferedWriter true_writer = new BufferedWriter(new FileWriter(file));

		true_writer.append("TRUETHETA: " + Arrays.toString(thetasTrue) + "\n");
		true_writer.append("TRUEPERM: " + Arrays.toString(perm) + "\n");
		true_writer.append("TRUELOGL: " + LLTrue + "\n");
		// true_writer.close();
		
		

		for (int k = 0; k < kmax; k++) {
			int[] permSamp = samplePerm(perm, oneThetas, lmloc, rand);
			int[] permAnneal = permSamp.clone();
			int[] permBest = permSamp.clone();

			int[] lmlocAnneal = new int[m];

			double[] thetasSamp = oneThetas.clone();
			double[] thetasAnneal = thetasSamp.clone();
			double[] thetasBest = thetasSamp.clone();

			double LLBest = LLTrue * N;
			double LLAnneal = LLTrue * N;
			double LLSamp = LLTrue * N;
			
			int trueCount = 0;
			int bestCount = 0;
			int steps=0;

			for (int i = 0; i < imax; i++) {
				//System.out.println("iteration " + i);
				// Set LM Locs for the current annealed sample
				for (int z = 0; z < perm.length; z++)
					if (permAnneal[z] - n >= 0)
						lmlocAnneal[permAnneal[z] - n] = z;

				permSamp = samplePerm(permAnneal, thetasAnneal, lmlocAnneal, rand);

				// True values
				double[] sampMeta = fitPerm(permSamp, n, perms);
				steps++;

				System.arraycopy(sampMeta, 1, thetasSamp, 0, n + m - 1);
				LLSamp = sampMeta[0];
				
				boolean bestNeighbor = false;
				while (!bestNeighbor) {
					int[] permNeighbor = permSamp.clone();
					double[] thetasNeighbor = thetasSamp.clone();
					double LLNeighbor = LLSamp;

					// Now we cycle through
					int[] permSwap = permSamp.clone();
					int swaptmp;
					for (int z = 0; z < n + m - 1; z++) {
						if (permSwap[z] < n || permSwap[z + 1] < n) {
							swaptmp = permSwap[z];
							permSwap[z] = permSwap[z + 1];
							permSwap[z + 1] = swaptmp;
							double[] metaSwap = fitPerm(permSwap, n, perms);
							steps++;
							if (metaSwap[0] > LLNeighbor) {
								permNeighbor = permSwap.clone();
								LLNeighbor = metaSwap[0];
								System.arraycopy(metaSwap, 1, thetasNeighbor, 0, n + m - 1);
							}
							permSwap[z + 1] = permSwap[z];
							permSwap[z] = swaptmp;
						}
					}
					if (LLNeighbor == LLSamp)
						bestNeighbor = true;
					else {
						permSamp = permNeighbor.clone();
						thetasSamp = thetasNeighbor.clone();
						LLSamp = LLNeighbor;
					}
				}
				if (LLSamp == LLTrue) {
					trueCount++;
				}
				if (LLSamp == LLBest) {
					bestCount++;
				}
				if (LLSamp > LLBest) {
					LLBest = LLSamp;
					permBest = permSamp.clone();
					thetasBest = thetasSamp.clone();
					bestCount = 1;

					permAnneal = permSamp.clone();
					thetasAnneal = thetasSamp.clone();
					LLAnneal = LLSamp;
				} else if (LLSamp > LLAnneal || Math.exp(0.02 * (LLSamp - LLAnneal)) < rand.nextDouble()) {
					permAnneal = permSamp.clone();
					thetasAnneal = thetasSamp.clone();
					LLAnneal = LLSamp;
				}
			}
			true_writer.append("RESAMPLE TEST " + k + "\n");
			true_writer.append("BESTPERM: " + Arrays.toString(permBest) + "\n");
			true_writer.append("BESTTHETA: " + Arrays.toString(thetasBest) + "\n");
			true_writer.append("BESTLOGL: " + LLBest + "\n");
			true_writer.append("ENCOUNTERS BEST: "+" "+bestCount+"\n");
			true_writer.append("STEPS: "+steps+"\n\n");
			
		}
		true_writer.close();
	}

	public static void synthTestBatch(String folder) throws IOException {

		int imax = 10; // Max number of annealing steps
		int kmax = 5; // Max restarts
		//int rmax = 25; // Repetitions
		int rmax = 5; // Repetitions

		//int[] Ns = { 100, 200, 400, 800, 1600, 3200 };
		//int[] Ns = { 200, 400, 800, 1600, 3200 };
		int[] Ns = { 3200 };
		//int[] ns = { 4, 8, 12, 16, 20 };
		int[] ns = { 4, 12, 16 };
		int[] ms = { 2, 4, 6 };
		double[] thetal = { .75 };
		double[] thetah = { .90 };
		for (int N : Ns) {
			for (int n : ns) {
				for (int m : ms) {
					for (int t = 0; t < thetal.length; t++) {
						synthTest(folder, N, n, m, thetal[t], thetah[t], rmax, kmax, imax);
					}
					System.out.println("Finished N="+N+" n="+n+" m="+m);
				}
			}
		}
		
	}

	public static void jesterBatchNoLM() throws IOException {
		// JESTER DATASET
		Random rand = new Random();

		int[] groups = { 1, 2, 3, 4, 5, 6, 7, 8 };
		int[] lmvals = { 25, 5 };

		String folder = "C:\\Users\\Anna\\Dropbox\\AdaptiveRim\\data\\Jester\\subsets\\";
		String filehead = "jester-perms-3lm-n";

		String outfilehead = "C:\\Users\\Anna\\Dropbox\\AdaptiveRim\\data\\output\\Jester\\output_";
		

		// Search parameters
		int pmax = 50;
		int restarts = 50;

		// n=10 for first 4 groups, 15 for subsequent
		int nval = 10;
		for (int g : groups)
			for (int l : lmvals) {
				if (g > 4)
					nval = 15;
				String outfile = outfilehead + "g" + g + "l" + l + "n" + nval + ".txt";
				BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
				for (int k = 0; k < restarts; k++) {
					String fnamefull = folder + "g" + g + "\\" + filehead + nval + "-g" + g + "-" + l + "-1.csv";
					int[][] perms = importPermsNoLM(fnamefull, nval);

					double[][] output = fitPermsNoLM(perms, pmax, rand);
					int[] perm = new int[nval];
					double[] thetas = new double[nval - 1];
					for (int i = 0; i < nval; i++) {
						perm[i] = (int) output[0][i];
						if (i < nval - 1)
							thetas[i] = output[1][i];
					}

					writer.append(Arrays.toString(perm) + "\n");
					writer.append(Arrays.toString(thetas) + "\n");

					String fnamefull2 = folder + "g" + g + "\\" + filehead + nval + "-g" + g + "-" + l + "-2.csv";
					String fnamefull3 = folder + "g" + g + "\\" + filehead + nval + "-g" + g + "-" + l + "-3.csv";
					String fnamefull4 = folder + "g" + g + "\\" + filehead + nval + "-g" + g + "-" + l + "-4.csv";
					int[][] perms2 = importPermsNoLM(fnamefull2, nval);
					int[][] perms3 = importPermsNoLM(fnamefull3, nval);
					int[][] perms4 = importPermsNoLM(fnamefull4, nval);

					writer.append(output[1][nval - 1] + " " + getLLNoLM(perm, thetas, perms2) + " "
							+ getLLNoLM(perm, thetas, perms3) + " " + getLLNoLM(perm, thetas, perms4) + "\n");
				}
				writer.close();
			}
	}

	public static void fitToFile(String filename, String outfile, int n_items, int pmax, int restarts, int nboot) throws IOException {
		Random rand = new Random();

		BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
		
		for (int k = 0; k < restarts; k++) {	
			int[][][] perms = importPerms(filename,nboot);


            int item_total = perms[0][0].length;
            int bsize = perms[0].length/item_total;
            int n_total = nboot*bsize;


			double[][][] output= new double[nboot][][];

			for (int ib=0; ib<nboot; ib++){
				output[ib] = fitPerms(perms[ib], n_items, pmax, rand);
			}

			int[] perm = new int[item_total];
			double[] thetas = new double[item_total-1];
			for (int ib = 0; ib < nboot; ib++){
				for (int i = 0; i < item_total; i++) {
				    perm[i] = (int) output[ib][0][i];
			        if (i < item_total-1)
				        thetas[i] = output[ib][1][i];
                }
				if (nboot!=1){
			        if(k==restarts-1)
			            writer.append(Arrays.toString(perm) + "\n");
			    }else{
			        writer.append(Arrays.toString(perm) + "\n");
			        writer.append(Arrays.toString(thetas) + "\n");
			        writer.append(output[0][1][item_total-1]+"\n");
			    }
            }
	    }
		writer.close();
	}


	public static int[][][] importPerms(String filename, int nboot) throws FileNotFoundException {
		Scanner lineScanner = new Scanner(new File(filename));
		Scanner itemScanner = new Scanner(lineScanner.nextLine());
		int N;
		int n;
		for (n = 0; itemScanner.hasNext(); n++)
			itemScanner.next();
		for (N = 1; lineScanner.hasNext(); N++)
			lineScanner.nextLine();
		itemScanner.close();
		lineScanner.close();

        int bsize = N/nboot;
		int[][][] perms = new int[nboot][bsize][n];
		lineScanner = new Scanner(new File(filename));
		int i = 0;
		int j = 0;
		int ib = 0;
		while (lineScanner.hasNext()) {
			j = 0;
			ib = i/bsize;
			itemScanner = new Scanner(lineScanner.nextLine());
			while (itemScanner.hasNext())
				perms[ib][i-ib*bsize][j++] = Integer.valueOf(itemScanner.next()) - 1;
			itemScanner.close();
			i++;
		}
		lineScanner.close();
		return (perms);
	}

	public static int[][] importPermsNoLM(String filename, int nitems) throws FileNotFoundException {
		Scanner lineScanner = new Scanner(new File(filename));
		Scanner itemScanner = new Scanner(lineScanner.nextLine());
		int N;
		int n = nitems;
		for (N = 1; lineScanner.hasNext(); N++)
			lineScanner.nextLine();
		itemScanner.close();
		lineScanner.close();

		int[][] perms = new int[N][n];
		lineScanner = new Scanner(new File(filename));
		int i = 0;
		int j = 0;
		int next;
		while (lineScanner.hasNext()) {
			j = 0;
			itemScanner = new Scanner(lineScanner.nextLine());
			while (itemScanner.hasNext()) {
				next = Integer.valueOf(itemScanner.next()) - 1;
				if (next < nitems)
					perms[i][j++] = next;
			}
			itemScanner.close();
			i++;
		}
		lineScanner.close();
		return (perms);
	}

	public static double[][] fitPerms(int[][] perms, int nitems, int pmax, Random rand) {
		int n = perms[0].length;
		int N = perms.length;

		// Initialize things
		double[] oneThetas = new double[n - 1];
		for (int p = 0; p < oneThetas.length; p++)
			oneThetas[p] = 1;

		int[] lmloc = new int[n - nitems];
		for (int i = 0; i < n; i++)
			if (perms[0][i] - nitems >= 0)
				lmloc[perms[0][i] - nitems] = i;

		int[] permSamp = samplePerm(perms[0], oneThetas, lmloc, rand);
		int[] permAnneal = permSamp.clone();
		int[] permBest = permSamp.clone();

		int[] lmlocAnneal = new int[n - nitems];

		double[] thetasSamp = oneThetas.clone();
		double[] thetasAnneal = thetasSamp.clone();
		double[] thetasBest = thetasSamp.clone();

		double LLBest = -1000 * N;
		double LLAnneal = -1000 * N;
		double LLSamp = -1000 * N;

		int p = 0;
		boolean fin = false;
		while (!fin) {
			p++;
			if (p >= pmax)
				fin = true;
			for (int i = 0; i < n; i++)
				if (permAnneal[i] - nitems >= 0)
					lmlocAnneal[permAnneal[i] - nitems] = i;
			permSamp = samplePerm(permAnneal, thetasAnneal, lmlocAnneal, rand);

			// True values
			double[] sampMeta = fitPerm(permSamp, nitems, perms);

			System.arraycopy(sampMeta, 1, thetasSamp, 0, n - 1);
			LLSamp = sampMeta[0];

			if (LLSamp > LLBest) {
				boolean repeat = true;
				while (repeat) {
					repeat = false;
					permBest = permSamp.clone();
					thetasBest = thetasSamp.clone();
					LLBest = LLSamp;

					// Now we cycle through
					int[] permSwap = permSamp.clone();
					int swaptmp;
					for (int i = 0; i < n - 1; i++) {
						if (permSwap[i] < nitems || permSwap[i + 1] < nitems) {
							swaptmp = permSwap[i];
							permSwap[i] = permSwap[i + 1];
							permSwap[i + 1] = swaptmp;
							double[] metaSwap = fitPerm(permSwap, nitems, perms);
							if (metaSwap[0] > LLSamp) {
								repeat = true;
								System.arraycopy(metaSwap, 1, thetasSamp, 0, n - 1);
								LLSamp = metaSwap[0];
								permSamp = permSwap.clone();

								permAnneal = permSamp.clone();
								thetasAnneal = thetasSamp.clone();
								LLAnneal = LLSamp;
							}
							permSwap[i + 1] = permSwap[i];
							permSwap[i] = swaptmp;
						}
					}
				}
			} else if (LLSamp > LLAnneal || Math.exp(0.02 * (LLSamp - LLAnneal)) < rand.nextDouble()) {
				permAnneal = permSamp.clone();
				thetasAnneal = thetasSamp.clone();
				LLAnneal = LLSamp;
			}
		}

		double[][] ret = new double[2][n + 1];
		// Return is
		// perm, trueLL
		// thetas, LL, p
		for (int i = 0; i < n; i++)
			ret[0][i] = permBest[i];
		System.arraycopy(thetasBest, 0, ret[1], 0, n - 1);
		ret[0][n] = 0;
		ret[1][n - 1] = LLBest;
		ret[1][n] = p;
		return (ret);
	}

	public static double[][] fitPermsNoLM(int[][] perms, int pmax, Random rand) {
		int n = perms[0].length;
		int N = perms.length;

		// Initialize things
		double[] oneThetas = new double[n - 1];
		for (int p = 0; p < oneThetas.length; p++)
			oneThetas[p] = 1;

		int[] permSamp = samplePermNoLM(perms[0], oneThetas, rand);
		int[] permAnneal = permSamp.clone();
		int[] permBest = permSamp.clone();

		double[] thetasSamp = oneThetas.clone();
		double[] thetasAnneal = thetasSamp.clone();
		double[] thetasBest = thetasSamp.clone();

		double LLBest = -1000 * N;
		double LLAnneal = -1000 * N;
		double LLSamp = -1000 * N;

		int p = 0;
		boolean fin = false;
		while (!fin) {
			p++;
			if (p >= pmax)
				fin = true;
			permSamp = samplePermNoLM(permAnneal, thetasAnneal, rand);

			// True values
			double[] sampMeta = fitPermNoLM(permSamp, perms);

			System.arraycopy(sampMeta, 1, thetasSamp, 0, n - 1);
			LLSamp = sampMeta[0];

			if (LLSamp > LLBest) {
				boolean repeat = true;
				while (repeat) {
					repeat = false;
					permBest = permSamp.clone();
					thetasBest = thetasSamp.clone();
					LLBest = LLSamp;

					// Now we cycle through
					int[] permSwap = permSamp.clone();
					int swaptmp;
					for (int i = 0; i < n - 1; i++) {
						swaptmp = permSwap[i];
						permSwap[i] = permSwap[i + 1];
						permSwap[i + 1] = swaptmp;
						double[] metaSwap = fitPermNoLM(permSwap, perms);
						if (metaSwap[0] > LLSamp) {
							repeat = true;
							System.arraycopy(metaSwap, 1, thetasSamp, 0, n - 1);
							LLSamp = metaSwap[0];
							permSamp = permSwap.clone();

							permAnneal = permSamp.clone();
							thetasAnneal = thetasSamp.clone();
							LLAnneal = LLSamp;
						}
						permSwap[i + 1] = permSwap[i];
						permSwap[i] = swaptmp;
					}
				}
			} else if (LLSamp > LLAnneal || Math.exp(0.02 * (LLSamp - LLAnneal)) < rand.nextDouble()) {
				permAnneal = permSamp.clone();
				thetasAnneal = thetasSamp.clone();
				LLAnneal = LLSamp;
			}
		}

		double[][] ret = new double[2][n + 1];
		// Return is
		// perm, trueLL
		// thetas, LL, p
		for (int i = 0; i < n; i++)
			ret[0][i] = permBest[i];
		System.arraycopy(thetasBest, 0, ret[1], 0, n - 1);
		ret[0][n] = 0;
		ret[1][n - 1] = LLBest;
		ret[1][n] = p;
		return (ret);
	}

	public static double[][] runTest2(int[] perm, double[] thetas, int nitems, int N, Random rand) {
		int n = perm.length;

		int[] lmloc = new int[perm.length - nitems];

		// Find LMs for current perm - for sampling
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - nitems >= 0)
				lmloc[perm[i] - nitems] = i;

		int[][] perms = new int[N][n];
		for (int k = 0; k < N; k++)
			perms[k] = samplePerm(perm, thetas, lmloc, rand);
		// Sampling Complete

		// True values
		double[] fitMeta = fitPerm(perm, nitems, perms);

		double[] thetasTrue = new double[n - 1];
		System.arraycopy(fitMeta, 1, thetasTrue, 0, n - 1);
		double LLTrue = fitMeta[0];

		// Initialize things
		double[] oneThetas = new double[thetas.length];
		for (int p = 0; p < oneThetas.length; p++)
			oneThetas[p] = 1;
		int[] permSamp = samplePerm(perm, oneThetas, lmloc, rand);
		int[] permAnneal = permSamp.clone();
		int[] permBest = permSamp.clone();

		int[] lmlocAnneal = new int[perm.length - nitems];

		double[] thetasSamp = oneThetas.clone();
		double[] thetasAnneal = thetasSamp.clone();
		double[] thetasBest = thetasSamp.clone();

		double LLBest = LLTrue * N;
		double LLAnneal = LLTrue * N;
		double LLSamp = LLTrue * N;

		int pmax = 5000;
		int p = 0;
		boolean fin = false;
		while (!fin) {
			p++;
			if (p >= pmax)
				fin = true;
			for (int i = 0; i < perm.length; i++)
				if (permAnneal[i] - nitems >= 0)
					lmlocAnneal[permAnneal[i] - nitems] = i;
			permSamp = samplePerm(permAnneal, thetasAnneal, lmlocAnneal, rand);

			// True values
			double[] sampMeta = fitPerm(permSamp, nitems, perms);

			System.arraycopy(sampMeta, 1, thetasSamp, 0, n - 1);
			LLSamp = sampMeta[0];

			if (LLSamp > LLBest) {
				boolean repeat = true;
				while (repeat) {
					repeat = false;
					permBest = permSamp.clone();
					thetasBest = thetasSamp.clone();
					LLBest = LLSamp;

					// Now we cycle through
					int[] permSwap = permSamp.clone();
					int swaptmp;
					for (int i = 0; i < n - 1; i++) {
						if (permSwap[i] < nitems || permSwap[i + 1] < nitems) {
							swaptmp = permSwap[i];
							permSwap[i] = permSwap[i + 1];
							permSwap[i + 1] = swaptmp;
							double[] metaSwap = fitPerm(permSwap, nitems, perms);
							if (metaSwap[0] > LLSamp) {
								repeat = true;
								System.arraycopy(metaSwap, 1, thetasSamp, 0, n - 1);
								LLSamp = metaSwap[0];
								permSamp = permSwap.clone();

								permAnneal = permSamp.clone();
								thetasAnneal = thetasSamp.clone();
								LLAnneal = LLSamp;
							}
							permSwap[i + 1] = permSwap[i];
							permSwap[i] = swaptmp;
						}
					}
				}
				if (LLBest >= LLTrue)
					fin = true;
			} else if (LLSamp > LLAnneal || Math.exp(0.02 * (LLSamp - LLAnneal)) < rand.nextDouble()) {
				permAnneal = permSamp.clone();
				thetasAnneal = thetasSamp.clone();
				LLAnneal = LLSamp;
			}
		}

		double[][] ret = new double[2][n + 1];
		// Return is
		// perm, trueLL
		// thetas, LL, p
		for (int i = 0; i < n; i++)
			ret[0][i] = permBest[i];
		System.arraycopy(thetasBest, 0, ret[1], 0, n - 1);
		ret[0][n] = LLTrue;
		ret[1][n - 1] = LLBest;
		ret[1][n] = p;
		return (ret);
	}

	public static double getLL(int[] perm, double[] thetas, int nitems, int[][] perms) {
		int[] lmloc = new int[perm.length - nitems];
		// Find LMs for current perm
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - nitems >= 0)
				lmloc[perm[i] - nitems] = i;

		int n = perm.length;
		int N = perms.length;

		// For marking when an item at an index contains landmarks
		int[][] lmflags = new int[N][n - 1];
		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];
		// For saving all landmark locations for each node/perm
		int[][][] lmvals = new int[N][lmloc.length - 1][];
		for (int i = 0; i < N; i++)
			for (int j = 0; j < lmloc.length - 1; j++) {
				lmvals[i][j] = new int[lmloc.length - j];
			}

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocess(lmflags, svals, lmvals, lmloc, invPi0);
		return (likelihood2(lmflags, svals, lmvals, thetas));
	}

	public static double getLLNoLM(int[] perm, double[] thetas, int[][] perms) {
		int n = perm.length;
		int N = perms.length;

		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocessNoLM(svals, invPi0);
		return (likelihoodNoLM(svals, thetas, N));
	}

	public static double getLLNoLM(int[] perm, double[] thetas, int nitems, int[][] perms) {
		int[] lmloc = new int[perm.length - nitems];
		// Find LMs for current perm
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - nitems >= 0)
				lmloc[perm[i] - nitems] = i;

		int n = perm.length;
		int N = perms.length;

		// For marking when an item at an index contains landmarks
		int[][] lmflags = new int[N][n - 1];
		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];
		// For saving all landmark locations for each node/perm
		int[][][] lmvals = new int[N][lmloc.length - 1][];
		for (int i = 0; i < N; i++)
			for (int j = 0; j < lmloc.length - 1; j++) {
				lmvals[i][j] = new int[lmloc.length - j];
			}

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocess(lmflags, svals, lmvals, lmloc, invPi0);
		return (likelihood2(lmflags, svals, lmvals, thetas));
	}

	public static double[] fitPerm(int[] perm, int nitems, int[][] perms) {
		int[] lmloc = new int[perm.length - nitems];
		// Find LMs for current perm
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - nitems >= 0)
				lmloc[perm[i] - nitems] = i;

		int n = perm.length;
		int N = perms.length;

		// For marking when an item at an index contains landmarks
		int[][] lmflags = new int[N][n - 1];
		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];
		// For saving all landmark locations for each node/perm
		int[][][] lmvals = new int[N][lmloc.length - 1][];
		for (int i = 0; i < N; i++)
			for (int j = 0; j < lmloc.length - 1; j++) {
				lmvals[i][j] = new int[lmloc.length - j];
			}

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocess(lmflags, svals, lmvals, lmloc, invPi0);
		double[] thetas = fitTheta2(lmflags, svals, lmvals);
		double LL = likelihood2(lmflags, svals, lmvals, thetas);

		double[] ret = new double[thetas.length + 1];
		ret[0] = LL;
		System.arraycopy(thetas, 0, ret, 1, thetas.length);
		return ret;
	}

	public static double[] fitPermNoLM(int[] perm, int[][] perms) {
		int n = perm.length;
		int N = perms.length;

		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocessNoLM(svals, invPi0);
		double[] thetas = fitThetaNoLM(svals, N);
		double LL = likelihoodNoLM(svals, thetas, N);

		double[] ret = new double[thetas.length + 1];
		ret[0] = LL;
		System.arraycopy(thetas, 0, ret, 1, thetas.length);
		return ret;
	}

	public static double likelihood2(int[][] lmflags, int[] svals, int[][][] lmvals, double[] thetas) {
		int N = lmflags.length;

		int nleft = thetas.length + 1;
		double logl = 0;

		for (int k = 0; k < thetas.length; k++) {
			double[] pdf_un = new double[nleft + 1];
			for (int p = 0; p < nleft; p++) {
				pdf_un[p] = Math.pow(thetas[k], p);
				pdf_un[nleft] += pdf_un[p];
			}

			double num = 0;
			for (int i = 0; i < N; i++) {
				if (lmflags[i][k] >= 0) {
					num = 0;
					// Creates denom and adds all terms for landmark numerator in loglike
					for (int m = 0; m < lmvals[i][lmflags[i][k]].length; m++) {
						num += pdf_un[lmvals[i][lmflags[i][k]][m]];
					}
					logl += Math.log(num);
				}
			}
			logl += svals[k] * Math.log(thetas[k]);
			logl -= N * Math.log(pdf_un[nleft]);
			nleft--;
		}

		return logl / N;
	}

	public static double likelihoodNoLM(int[] svals, double[] thetas, int N) {
		int nleft = thetas.length + 1;
		double logl = 0;

		for (int k = 0; k < thetas.length; k++) {
			double[] pdf_un = new double[nleft + 1];
			for (int p = 0; p < nleft; p++) {
				pdf_un[p] = Math.pow(thetas[k], p);
				pdf_un[nleft] += pdf_un[p];
			}

			logl += svals[k] * Math.log(thetas[k]);
			logl -= N * Math.log(pdf_un[nleft]);
			nleft--;
		}

		return logl / N;
	}

	public static double dTheta2(int[][] lmflags, int[] svals, int[][][] lmvals, int ind, double theta) {
		int N = lmflags.length;
		int n = svals.length + 1;
		int nleft = n - ind;
		double[] pdf_un = new double[nleft + 1];
		for (int p = 0; p < nleft; p++) {
			pdf_un[p] = Math.pow(theta, p);
			pdf_un[nleft] += pdf_un[p];
		}
		double[] dpdf_un = new double[nleft + 1];
		for (int p = 0; p < nleft; p++) {
			dpdf_un[p] = p * Math.pow(theta, p - 1);
			dpdf_un[nleft] = dpdf_un[p];
		}
		double denom = 0;
		double logl = 0;
		int lmind = 0;
		for (int i = 0; i < N; i++) {
			if (lmflags[i][ind] >= 0) {
				denom = 0;
				// Creates denom and adds all terms for landmark numerator in loglike
				for (int k = 0; k < lmvals[i][lmflags[i][ind]].length; k++) {
					denom += pdf_un[lmvals[i][lmflags[i][ind]][k]];
				}
				for (int k = 0; k < lmvals[i][lmflags[i][ind]].length; k++) {
					logl += dpdf_un[lmvals[i][lmflags[i][ind]][k]] / denom;
				}
			}
		}
		logl += svals[ind] / theta;
		logl -= N * ((nleft - 1) * Math.pow(theta, nleft) - nleft * Math.pow(theta, nleft - 1) + 1)
				/ ((theta - 1) * (Math.pow(theta, nleft) - 1));

		return logl;
	}

	public static double dThetaNoLM(int[] svals, int ind, double theta, int N) {
		int n = svals.length + 1;
		int nleft = n - ind;
		double logl = 0;

		logl += svals[ind] / theta;
		logl -= N * ((nleft - 1) * Math.pow(theta, nleft) - nleft * Math.pow(theta, nleft - 1) + 1)
				/ ((theta - 1) * (Math.pow(theta, nleft) - 1));

		return logl;
	}

	public static double[] fitThetaNoLM(int[] svals, int N) {
		double loglike = 0;
		int nleft = svals.length + 1;
		int n = svals.length + 1;
		double tmpsum = 0;
		double[] thetas = new double[svals.length];

		for (int k = 0; k < n - 1; k++) {
			double low = 10e-7;
			double high = 1 - low;
			if (dThetaNoLM(svals, k, low, N) < 0) {
				high = low;
				thetas[k] = low;
			}
			if (dThetaNoLM(svals, k, high, N) > 0) {
				low = high;
				thetas[k] = high;
			}
			while (high - low > 10e-7) {
				thetas[k] = (high + low) / 2;
				if (dThetaNoLM(svals, k, thetas[k], N) > 0)
					low = thetas[k];
				else
					high = thetas[k];
			}
		}

		return thetas;
	}

	public static double[] fitTheta2(int[][] lmflags, int[] svals, int[][][] lmvals) {
		double loglike = 0;
		int nleft = svals.length + 1;
		int N = lmflags.length;
		int n = svals.length + 1;
		double tmpsum = 0;
		double[] thetas = new double[svals.length];

		for (int k = 0; k < n - 1; k++) {
			double low = 10e-7;
			double high = 1 - low;
			if (dTheta2(lmflags, svals, lmvals, k, low) < 0) {
				high = low;
				thetas[k] = low;
			}
			if (dTheta2(lmflags, svals, lmvals, k, high) > 0) {
				low = high;
				thetas[k] = high;
			}
			while (high - low > 10e-7) {
				thetas[k] = (high + low) / 2;
				if (dTheta2(lmflags, svals, lmvals, k, thetas[k]) > 0)
					low = thetas[k];
				else
					high = thetas[k];
			}
		}

		return thetas;
	}

	public static void preprocess(int[][] lmflags, int[] svals, int[][][] lmvals, int[] lmloc, int[][] invPi0) {
		int N = lmflags.length;
		int n = invPi0[0].length;
		int lmn = lmloc.length;
		int[] lmind = new int[N];
		for (int i = 0; i < N; i++) {
			for (int k = 0; k < n - 1; k++) {
				if (lmind[i] < lmn - 1 && invPi0[i][k] == lmloc[lmind[i]]) {
					// Landmark
					for (int j = 0; j < lmn - lmind[i]; j++) {
						// Copy to landmark suff stats and flag
						lmvals[i][lmind[i]][j] = lmloc[j + lmind[i]];
						lmflags[i][k] = lmind[i];
						// Downshift landmarks as appropriate
						for (int p = 0; p < k; p++)
							if (invPi0[i][p] < lmloc[j + lmind[i]])
								lmvals[i][lmind[i]][j]--;
					}
					lmind[i]++;
				} else {
					// Flag as -1
					lmflags[i][k] = -1;
					// Calc s contribution
					svals[k] += invPi0[i][k];
					for (int p = 0; p < k; p++) {
						if (invPi0[i][p] < invPi0[i][k])
							svals[k]--;
					}
				}
			}
		}
	}

	public static void preprocessNoLM(int[] svals, int[][] invPi0) {
		int N = invPi0.length;
		int n = invPi0[0].length;
		for (int i = 0; i < N; i++) {
			for (int k = 0; k < n - 1; k++) {
				// Calc s contribution
				svals[k] += invPi0[i][k];
				for (int p = 0; p < k; p++) {
					if (invPi0[i][p] < invPi0[i][k])
						svals[k]--;
				}
			}
		}
	}

	public static double likelihood0(int[] perm, int[] invPerm, int[][] data0, int[][] invData0, int[][] lmlocs0,
			double[] thetas, int nitems) {
		System.out.println("Perm");
		System.out.println(Arrays.toString(perm));
		int[][] data = getArrayCopy_int2(data0);
		int[][] invData = getArrayCopy_int2(invData0);
		int[][] lmlocs = getArrayCopy_int2(lmlocs0);
		double loglike = 0;
		int nleft = perm.length;
		double tmpsum = 0;
		int nlm = lmlocs[0].length;
		int N = data.length;

		for (int k = 0; k < 1; k++) {
			double[] pdf_un = new double[nleft + 1];
			for (int p = 0; p < nleft; p++) {
				pdf_un[p] = Math.pow(thetas[k], p);
				pdf_un[nleft] += pdf_un[p];
			}
			if (debug)
				System.out.println(Arrays.toString(pdf_un));
			for (int i = 0; i < N; i++) {
				if (data[i][k] >= nitems && data[i][k] < perm.length - 1) {
					tmpsum = 0;
					for (int p = 0; p < nlm; p++)
						if (lmlocs[k][p] >= 0) {
							tmpsum += Math.pow(thetas[k], lmlocs[k][p]);
							if (debug)
								System.out.print("s=" + lmlocs[k][p] + " ");
						}
					loglike += Math.log(tmpsum);
					if (debug)
						System.out.println();
				} else {
					loglike += invPerm[data[i][k]] * Math.log(thetas[k]);
					if (debug)
						System.out.println("s=" + invPerm[data[i][k]] + " ");
				}
				// Decrement things here
			}
			loglike -= N * Math.log(pdf_un[nleft]);
		}

		return loglike;
	}

	public static double[] fitTheta0(int[] perm, int[] invPerm, int[][] data0, int[][] invData0, int[][] lmlocs0,
			int nitems) {
		System.out.println("Perm");
		System.out.println(Arrays.toString(perm));
		int[][] data = getArrayCopy_int2(data0);
		int[][] invData = getArrayCopy_int2(invData0);
		int[][] lmlocs = getArrayCopy_int2(lmlocs0);
		double loglike = 0;
		int nleft = perm.length;
		double tmpsum = 0;
		int nlm = lmlocs[0].length;
		int N = data.length;
		double[] thetas = new double[perm.length - 1];
		int[] lminds = new int[N];
		thetas[0] = .5;
		int s = 0;

		for (int k = 0; k < 1; k++) {
			s = 0;
			for (int i = 0; i < N; i++) {
				if (data[i][k] >= nitems && data[i][k] < perm.length - 1) {
					tmpsum = 0;
					lminds[i] = 1;
				} else {
					s += invPerm[data[i][k]];
					lminds[i] = 0;
				}
			}
			double low = 10e-7;
			double high = 1 - low;
			if (dTheta(low, s, lminds, lmlocs, nleft) < 0) {
				high = low;
				thetas[k] = low;
			}
			if (dTheta(high, s, lminds, lmlocs, nleft) > 0) {
				low = high;
				thetas[k] = high;
			}
			while (high - low > 10e-7) {
				thetas[k] = (high + low) / 2;
				if (dTheta(thetas[k], s, lminds, lmlocs, nleft) > 0)
					low = thetas[k];
				else if (dTheta(thetas[k], s, lminds, lmlocs, nleft) < 0)
					high = thetas[k];
			}
		}
		System.out.println(Arrays.toString(thetas));

		return thetas;
	}

	public static double dTheta(double theta, int s, int[] lminds, int[][] lmlocs, int nleft) {
		int N = lminds.length;
		int l = lmlocs[0].length;
		double[] pdf_un = new double[nleft + 1];
		for (int p = 0; p < nleft; p++) {
			pdf_un[p] = Math.pow(theta, p);
			pdf_un[nleft] += pdf_un[p];
		}
		double[] dpdf_un = new double[nleft + 1];
		for (int p = 0; p < nleft; p++) {
			dpdf_un[p] = p * Math.pow(theta, p - 1);
			dpdf_un[nleft] = dpdf_un[p];
		}
		double denom = 0;
		double logl = 0;
		for (int i = 0; i < N; i++) {
			if (lminds[i] == 1) {
				denom = 0;
				// Creates denom and adds all terms for landmark numerator in loglike
				for (int k = l - 1; k >= 0 && lmlocs[i][k] >= 0; k--) {
					denom += pdf_un[lmlocs[i][k]];
				}
				for (int k = l - 1; k >= 0 && lmlocs[i][k] >= 0; k--) {
					logl += dpdf_un[lmlocs[i][k]] / denom;
				}
			}
		}
		logl += s / theta;
		logl -= N * ((nleft - 1) * Math.pow(theta, nleft) - nleft * Math.pow(theta, nleft - 1) + 1)
				/ ((theta - 1) * (Math.pow(theta, nleft) - 1));
		// logl-=N*((nleft-1)*Math.pow(theta, nleft)-nleft*Math.pow(theta,
		// nleft-1)+1)/Math.pow(theta-1, 2);
		// logl-=N*dpdf_un[nleft]/pdf_un[nleft];

		return logl;
	}

	public static int[][] getArrayCopy_int2(int[][] toCopy) {
		int[][] ret = new int[toCopy.length][toCopy[0].length];
		for (int i = 0; i < toCopy.length; i++)
			System.arraycopy(toCopy[i], 0, ret[i], 0, toCopy[i].length);
		return (ret);
	}

	public static void top(int[][] in, int n) {
		for (int i = 0; i < n; i++)
			System.out.println(Arrays.toString(in[i]));
	}

	public static double[] getsCDF_unnorm(double theta, int n) {
		double[] CDF_unnorm = new double[n];
		CDF_unnorm[0] = 1;
		for (int i = 1; i < n; i++)
			CDF_unnorm[i] = CDF_unnorm[i - 1] + Math.pow(theta, i);
		return CDF_unnorm;
	}

	public static int[] samplePerm(int[] pi0_tocopy, double[] thetas, int[] lmlocs_tocopy, Random rand) {
		int[] pi0 = new int[pi0_tocopy.length];
		System.arraycopy(pi0_tocopy, 0, pi0, 0, pi0_tocopy.length);
		int[] lmlocs = new int[lmlocs_tocopy.length];
		System.arraycopy(lmlocs_tocopy, 0, lmlocs, 0, lmlocs_tocopy.length);
		int[] ses = new int[pi0.length - 1];
		for (int i = 0; i < ses.length; i++) {
			ses[i] = sampleS(thetas[i], pi0.length - i, rand);
		}

		// Portmanteau!
		int[] samperm = new int[pi0.length];

		for (int i = 0; i < ses.length; i++) {
			for (int j = 0; j < lmlocs.length; j++) {
				if (ses[i] == lmlocs[j]) {
					ses[i] = lmlocs[0];
					System.arraycopy(lmlocs, 1, lmlocs, 0, lmlocs.length - 1);
					lmlocs[lmlocs.length - 1] = -1;
				}
			}
			for (int j = 0; j < lmlocs.length; j++)
				if (ses[i] < lmlocs[j])
					lmlocs[j]--;
			samperm[i] = pi0[ses[i]];
			System.arraycopy(pi0, ses[i] + 1, pi0, ses[i], pi0.length - ses[i] - 1);
			pi0[pi0.length - 1] = -1;
		}
		samperm[samperm.length - 1] = pi0[0];

		return samperm;
	}

	public static int[] samplePermNoLM(int[] pi0_tocopy, double[] thetas, Random rand) {
		int[] pi0 = new int[pi0_tocopy.length];
		System.arraycopy(pi0_tocopy, 0, pi0, 0, pi0_tocopy.length);
		int[] ses = new int[pi0.length - 1];
		for (int i = 0; i < ses.length; i++) {
			ses[i] = sampleS(thetas[i], pi0.length - i, rand);
		}

		// Portmanteau!
		int[] samperm = new int[pi0.length];

		for (int i = 0; i < ses.length; i++) {
			samperm[i] = pi0[ses[i]];
			System.arraycopy(pi0, ses[i] + 1, pi0, ses[i], pi0.length - ses[i] - 1);
			pi0[pi0.length - 1] = -1;
		}
		samperm[samperm.length - 1] = pi0[0];

		return samperm;
	}

	public static int sampleS(double theta, int n, Random rand) {
		double[] CDF_unnorm = getsCDF_unnorm(theta, n);

		double s_rng = rand.nextDouble() * CDF_unnorm[n - 1];
		int s;
		for (s = 0; s_rng > CDF_unnorm[s]; s++)
			;

		return s;
	}

	public static int[] sampleManyS(double theta, int n, int N, Random rand) {
		double[] CDF_unnorm = getsCDF_unnorm(theta, n);

		double s_rng = rand.nextDouble() * CDF_unnorm[n - 1];

		int[] manys = new int[N];
		int s;
		for (int k = 0; k < N; k++) {
			for (s = 0; s_rng > CDF_unnorm[s]; s++)
				;
			manys[k] = s;
		}
		return manys;
	}

	public static void runTest(int[] perm, double[] thetas, int nitems, int N, Random rand) {
		int n = perm.length;

		int[] lmloc = new int[perm.length - nitems];
		// Find LMs for current perm
		for (int i = 0; i < perm.length; i++)
			if (perm[i] - nitems >= 0)
				lmloc[perm[i] - nitems] = i;

		int[][] perms = new int[N][n];
		for (int k = 0; k < N; k++)
			perms[k] = samplePerm(perm, thetas, lmloc, rand);

		// TEST!
		fitPerm(perm, nitems, perms);

		// For marking when an item at an index contains landmarks
		int[][] lmflags = new int[N][n - 1];
		// For saving all svals as we calculate landmark variables
		int[] svals = new int[n - 1];
		// For saving all landmark locations for each node/perm
		int[][][] lmvals = new int[N][lmloc.length - 1][];
		for (int i = 0; i < N; i++)
			for (int j = 0; j < lmloc.length - 1; j++) {
				lmvals[i][j] = new int[lmloc.length - j];
			}

		// Relevant to the specific perm
		int[][] invPi0 = new int[N][n];
		int[] invpi = new int[n];
		for (int i = 0; i < n; i++)
			invpi[perm[i]] = i;
		for (int i = 0; i < N; i++)
			for (int j = 0; j < n; j++)
				invPi0[i][j] = invpi[perms[i][j]];

		preprocess(lmflags, svals, lmvals, lmloc, invPi0);
		double[] thetasTrue = fitTheta2(lmflags, svals, lmvals);
		System.out.println(likelihood2(lmflags, svals, lmvals, thetasTrue));

		double LLTrue = likelihood2(lmflags, svals, lmvals, thetasTrue);

		// Initialize things
		double[] oneThetas = new double[thetas.length];
		for (int p = 0; p < oneThetas.length; p++)
			oneThetas[p] = 1;
		int[] permSamp = samplePerm(perm, oneThetas, lmloc, rand);
		int[] permAnneal = permSamp.clone();
		int[] permBest = permSamp.clone();

		int[] lmlocSamp = new int[perm.length - nitems];
		for (int i = 0; i < perm.length; i++)
			if (permSamp[i] - nitems >= 0)
				lmlocSamp[permSamp[i] - nitems] = i;
		int[] lmlocAnneal = lmlocSamp.clone();
		// int[] lmlocBest=lmlocSamp.clone();

		double[] thetasSamp = oneThetas.clone();
		double[] thetasAnneal = thetasSamp.clone();
		double[] thetasBest = thetasSamp.clone();

		double LLBest = LLTrue * N;
		double LLAnneal = LLTrue * N;
		double LLSamp = LLTrue * N;

		int pmax = 5000;
		for (int p = 0; p < pmax; p++) {
			permSamp = samplePerm(permAnneal, thetasAnneal, lmlocAnneal, rand);
			// int[] lmlocSamp=new int[perm.length-nitems];
			// Find LMs for current perm
			for (int i = 0; i < perm.length; i++)
				if (permSamp[i] - nitems >= 0)
					lmlocSamp[permSamp[i] - nitems] = i;

			// For marking when an item at an index contains landmarks
			int[][] lmflagsSamp = new int[N][n - 1];
			// For saving all svals as we calculate landmark variables
			int[] svalsSamp = new int[n - 1];
			// For saving all landmark locations for each node/perm
			int[][][] lmvalsSamp = new int[N][lmloc.length - 1][];
			for (int i = 0; i < N; i++)
				for (int j = 0; j < lmloc.length - 1; j++) {
					lmvalsSamp[i][j] = new int[lmloc.length - j];
				}
			// Relevant to the specific perm
			int[][] invPi0Samp = new int[N][n];
			int[] invpiSamp = new int[n];
			for (int i = 0; i < n; i++)
				invpiSamp[permSamp[i]] = i;
			for (int i = 0; i < N; i++)
				for (int j = 0; j < n; j++)
					invPi0Samp[i][j] = invpiSamp[perms[i][j]];

			preprocess(lmflagsSamp, svalsSamp, lmvalsSamp, lmlocSamp, invPi0Samp);
			thetasSamp = fitTheta2(lmflagsSamp, svalsSamp, lmvalsSamp);

			LLSamp = likelihood2(lmflagsSamp, svalsSamp, lmvalsSamp, thetasSamp);
			if (LLSamp > LLAnneal || Math.exp(0.02 * (LLSamp - LLAnneal)) < rand.nextDouble()) {
				permAnneal = permSamp.clone();
				thetasAnneal = thetasSamp.clone();
				LLAnneal = LLSamp;
				lmlocAnneal = lmlocSamp.clone();
				System.out.println("Annealed");
			}
			if (LLSamp > LLBest) {
				permBest = permSamp.clone();
				thetasBest = thetasSamp.clone();
				LLBest = LLSamp;
				System.out.println("New Best");
				if (LLBest == LLTrue)
					p = pmax;
			}
		}
		System.out.println("True");
		System.out.println(LLTrue);
		System.out.println(Arrays.toString(perm));
		System.out.println(Arrays.toString(thetasTrue));
		System.out.println("Best");
		System.out.println(LLBest);
		System.out.println(Arrays.toString(permBest));
		System.out.println(Arrays.toString(thetasBest));
		System.out.println("Anneal");
		System.out.println(LLAnneal);
		System.out.println(Arrays.toString(permAnneal));
		System.out.println(Arrays.toString(thetasAnneal));
	}
}

