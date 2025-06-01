package model;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;

//NOTE TO SELF: Make sure properly dividing the log likelihood by N 
//(Use total N - accurate)
//(Use factor N - equal weight)
//(Use weightened N???)
//This is done when setting LRCounts and vbar, both in the fit command
// and in the general loglikelihood command

public class CRIM extends AbstractModel {
	int factors;
	// These are the training data values, assume training data is always loaded
	int[][][] groupIDs_pi0;// factor, item, index in group list
	int[][][] groupIDs_copy;
	double[][][] Qobs_pi0;// factor, i, j
	int[] N_pi0;// factor
	int[][][] train_perms;

	// Fit variables - reuse to save object creation
	Datagram[][][] fitDatagrams;// nitems, depth, break point
	int[][][][] DPGroupCounts;// group counts in shape of datagram, for building LRCounts

	// Not initialized unless explicitly called.
	// Need to implement testing/training split - main data is used for training
	int[][][] testing_groupIDs_pi0;
	int[][][] testing_groupIDs_copy;
	double[][][] testing_Qobs_pi0;
	int[] testing_N_pi0;

	int[][][] validation_groupIDs_pi0;
	int[][][] validation_groupIDs_copy;
	double[][][] validation_Qobs_pi0;
	int[] validation_N_pi0;

	static double deltaCutoff = 0.000001;

	CRIM(int[][][] groupIDs, double test_perc, double valid_perc){
		this(groupIDs, test_perc, valid_perc, new Random().nextInt());
	}
	
	CRIM(int[][][] groupIDs, double test_perc, double valid_perc, int randSeed) {
		// Input, group IDs by [factor][N][nitem]
		// test_perc, valid_perc values between [0,100] to determine
		// sample size breakdown
		double train_perc = 100 - test_perc - valid_perc;
		if (train_perc < 0 || train_perc > 100 || test_perc < 0 || test_perc > 100 || valid_perc < 0
				|| valid_perc > 100) {
			System.out.println("Invalid training sample size");
			return;
		}

		// General items
		factors = groupIDs.length;
		nitems = groupIDs[0][0].length;

		// Qobs
		Qobs_pi0 = new double[factors][nitems][nitems];
		testing_Qobs_pi0 = new double[factors][nitems][nitems];
		validation_Qobs_pi0 = new double[factors][nitems][nitems];

		// GroupIDs_split
		int[][][] groupIDs_train = new int[factors][][];
		int[][][] groupIDs_test = new int[factors][][];
		int[][][] groupIDs_valid = new int[factors][][];
		// GroupIDs_suff_stats
		groupIDs_pi0 = new int[factors][][];
		testing_groupIDs_pi0 = new int[factors][][];
		validation_groupIDs_pi0 = new int[factors][][];
		train_perms=new int[factors][][];

		// N
		N_pi0 = new int[factors + 1];
		testing_N_pi0 = new int[factors + 1];
		validation_N_pi0 = new int[factors + 1];
		for (int f = 0; f < factors; f++) {
			int N = groupIDs[f].length;
			testing_N_pi0[f] = (int) Math.round(N * test_perc / 100.0);
			validation_N_pi0[f] = (int) Math.round(N * valid_perc / 100.0);
			N_pi0[f] = N - testing_N_pi0[f] - validation_N_pi0[f];
			testing_N_pi0[factors] += testing_N_pi0[f];
			validation_N_pi0[factors] += validation_N_pi0[f];
			N_pi0[factors] += N_pi0[f];
			groupIDs_train[f] = new int[N_pi0[f]][nitems];
			groupIDs_test[f] = new int[testing_N_pi0[f]][nitems];
			groupIDs_valid[f] = new int[validation_N_pi0[f]][nitems];
			train_perms[f] = new int[N_pi0[f]][nitems];
		}

		// test_block
		/* System.out.println("Data Breakdown:");
		System.out.print("Training: ");
		for (int f = 0; f < factors; f++)
			System.out.print(N_pi0[f] + " ");
		System.out.print("\nTesting: ");
		for (int f = 0; f < factors; f++)
			System.out.print(testing_N_pi0[f] + " ");
		System.out.print("\nValidation: ");
		for (int f = 0; f < factors; f++)
			System.out.print(validation_N_pi0[f] + " ");
		System.out.print("\n");

		// Random seed - print to output
		System.out.println("Sample seed: " + randSeed);
        */
        Random rand = new Random(randSeed);

		// Divide groupIDs into 3 parts
		for (int f = 0; f < factors; f++) {
			int N = groupIDs[f].length;
			int[] samples = new int[N];
			int swap, ri;
			for (int n = 0; n < N; n++)
				samples[n] = n;
			for (int n = 0; n < N; n++) {
				ri = rand.nextInt(N);
				swap = samples[ri];
				samples[ri] = samples[n];
				samples[n] = swap;
			}
			for (int n = 0; n < N_pi0[f]; n++) {
				groupIDs_train[f][n] = groupIDs[f][samples[n]];
				for(int i=0;i<nitems;i++)
					train_perms[f][n][groupIDs_train[f][n][i]]=i;
			}
			for (int n = 0; n < testing_N_pi0[f]; n++)
				groupIDs_test[f][n] = groupIDs[f][samples[N_pi0[f] + n]];
			for (int n = 0; n < validation_N_pi0[f]; n++)
				groupIDs_valid[f][n] = groupIDs[f][samples[N_pi0[f] + testing_N_pi0[f] + n]];
		}

		init_suff_stats(groupIDs_train, groupIDs_pi0, Qobs_pi0);
		init_suff_stats(groupIDs_test, testing_groupIDs_pi0, testing_Qobs_pi0);
		init_suff_stats(groupIDs_valid, validation_groupIDs_pi0, validation_Qobs_pi0);
		groupIDs_copy = new int[factors][][];
		testing_groupIDs_copy = new int[factors][][];
		validation_groupIDs_copy = new int[factors][][];
		for (int f = 0; f < factors; f++) {
			groupIDs_copy[f] = new int[nitems][groupIDs_pi0[f][0].length];
			testing_groupIDs_copy[f] = new int[nitems][testing_groupIDs_pi0[f][0].length];
			validation_groupIDs_copy[f] = new int[nitems][validation_groupIDs_pi0[f][0].length];
		}
	}

	public int[][] sample1(Node node, Random rand) {
		int[][] permutation = new int[factors][nitems];
		for (int f = 0; f < factors; f++)
			for (int n = 0; n < nitems; n++)
				permutation[f][n]=-1;
		for (int f = 0; f < factors; f++)
			sample1(node, permutation[f], 0, f, rand);
		int tmp;
		for (int f = 0; f < factors; f++)
			for (int n = 0; n < nitems/2; n++) {
				tmp=permutation[f][n];
				permutation[f][n]=permutation[f][nitems-1-n];
				permutation[f][nitems-1-n]=tmp;
			}
		return permutation;
	}
	
	public void sample(Node node, int[][][] permutations, Random rand) {
		for (int f = 0; f < factors; f++)
			for(int k=0; k<permutations[0].length;k++)
				for (int n = 0; n < nitems; n++)
					permutations[f][k][n]=-1;
		for (int f = 0; f < factors; f++)
			for(int k=0; k<permutations[f].length;k++)
				sample1(node, permutations[f][k], 0, f, rand);
		int tmp;
	}
	
	public int[][][] sampleGIDs(Node node, int[][][] permutations, Random rand) {
		sample(node,permutations,rand);
		return(this.permToGID(permutations));
	}
	
	public int[][][] permToGID(int[][][] permutations) {
		int[][][] gids=new int[permutations.length][][];
		for(int f = 0; f < factors; f++)
			gids[f]=new int[permutations[f].length][nitems];
		for (int f = 0; f < factors; f++)
			for(int k=0; k<permutations[0].length;k++)	
				for (int n = 0; n < nitems; n++) 
					gids[f][k][permutations[f][k][n]]=n;
		return(gids);
	}

	private void sample1(Node node, int[] permutation, int i, int f, Random rand) {
		if (node.isleaf) {
			permutation[i] = node.item;
		} else {
			int L, R;
			if (node.params.thetas[f] >= 0) {
				sample1((Node) node.left, permutation, i, f, rand);
				sample1((Node) node.right, permutation, i + node.L, f, rand);
				L = node.L;
				R = node.R;
			} else {
				sample1((Node) node.right, permutation, i, f, rand);
				sample1((Node) node.left, permutation, i + node.R, f, rand);
				L = node.R;
				R = node.L;
			}
			// Inverting above, so use abs value of theta (i.e. exp(-|theta|))
			set_Z(node.Z_tmp, Math.abs(node.params.thetas[f]));
			// L items on the left starting at i, and R items on the right starting at i+L
			int l, r;
			int lstart=i;
			int rstart=i+L;
			for (l = 0; l < L; l++) {
				double[] cdf = new double[R + 1];
				if (l == L - 1)
					for (r = 0; r <= R; r++) {
						if (r<node.Z_tmp.length)
							cdf[r] = node.Z_tmp[r][1];
						else
							cdf[r] = node.Z_tmp[1][r];
					}
				else {
					if (R<node.Z_tmp.length && L - l - 1<node.Z_tmp[0].length)
						cdf[0] = node.Z_tmp[R][L - l - 1];
					else
						cdf[0] = node.Z_tmp[L - l - 1][R];
					//double qL = Math.exp(-Math.abs(node.params.thetas[f]) * (L - l - 1));
					double qL = Math.exp(-Math.abs(node.params.thetas[f]) * (L-l));
					double qrL = qL;
					for (r = 1; r <= R; r++) {
						if (R - r<node.Z_tmp.length && L - l - 1<node.Z_tmp[0].length) {
							cdf[r] = cdf[r - 1] + qrL * node.Z_tmp[R - r][L - l - 1];
						}
						else {
							cdf[r] = cdf[r - 1] + qrL * node.Z_tmp[L - l - 1][R - r];
						}
						//cdf[r] = cdf[r - 1] + qrL * node.Z_tmp[R - r][L - l - 1];
						qrL *= qL;
					}
				}
				double max = cdf[R];
				double u = max * rand.nextDouble();
				int v;
				for (v = 0; cdf[v] < u; v++);
				R-=v;
				//System.out.println(Arrays.toString(cdf)+" "+v+" "+Math.exp(-node.params.thetas[f]));
				
				for(int vi=0;vi<v;vi++) {
					int tmp=permutation[rstart];
					for(int li=0;li<L-l;li++)
						permutation[rstart-li]=permutation[rstart-li-1];
					permutation[lstart]=tmp;
					rstart++;lstart++;
				}
				lstart++;
			}
		}
	}

	public void init_suff_stats(int[][][] groupIDs_in, int[][][] groupIDs_out, double[][][] Qobs) {
		int[][][] gcounts = new int[factors][][];
		for (int f = 0; f < factors; f++)
			gcounts[f] = new int[nitems][groupIDs_in[f].length];
		// Fills the Qmatrix and counts the size of each group
		for (int f = 0; f < factors; f++) {
			for (int n = 0; n < groupIDs_in[f].length; n++) {
				for (int i = 0; i < nitems - 1; i++) {
					for (int j = i + 1; j < nitems; j++) {
						if (groupIDs_in[f][n][i] < groupIDs_in[f][n][j])
							Qobs[f][i][j]++;
						if (groupIDs_in[f][n][i] > groupIDs_in[f][n][j])
							Qobs[f][j][i]++;
					}
					gcounts[f][groupIDs_in[f][n][i]][n]++;
				}
			}
		}
		// Counts the number of groups that are larger than 1
		int[] ngroups = new int[factors];
		for (int f = 0; f < factors; f++) {
			for (int n = 0; n < groupIDs_in[f].length; n++) {
				for (int i = 0; i < nitems; i++) {
					if (gcounts[f][i][n] > 1)
						ngroups[f]++;
				}
			}
		}
		// For the number of groups larger than 1, note membership for each item (0/1)
		// LRcounts can be tabulated by from subset-row-sums over groupIDs_pi0[C]
		// Note that groupIDs_pi0 is transposed from groupIDs to allow passing
		// group membership for each item while groupIDs allows passing single perms
		// groupIDs_out = new int[factors][][];
		for (int f = 0; f < factors; f++) {
			groupIDs_out[f] = new int[nitems][ngroups[f]];
			int gng = 0; // group number counter
			for (int n = 0; n < groupIDs_in[f].length; n++) {
				for (int i = 0; i < nitems; i++) {
					if (gcounts[f][i][n] > 1) {
						for (int j = 0; j < nitems; j++)
							if (groupIDs_in[f][n][j] == i)
								groupIDs_out[f][j][gng] = 1;
						gng++;
					}
				}
			}
		}
	}

	public Node node_from_DP(Datagram dgin, int[] permutation) {
		if (dgin.n > 0) {
			Node left = node_from_DP(fitDatagrams[dgin.c - 1][dgin.m][0], permutation);
			Node right = node_from_DP(fitDatagrams[dgin.n - dgin.c][dgin.m + dgin.c][0], permutation);
			Node ret = new Node(left, right, dgin.theta);
			return (ret);
		} else {
			Node ret = new Node(permutation[dgin.m]);
			return (ret);
		}
	}
	
	public void fit_pis_init(int[][] perm) {
		DPGroupCounts = new int[factors][nitems][][];
		for (int n = 0; n < nitems; n++) {
			for (int f = 0; f < factors; f++)
				DPGroupCounts[f][n] = new int[nitems - n][groupIDs_pi0[f][0].length];
		}

		fitDatagrams = new Datagram[nitems][][];
		for (int n = 0; n < nitems; n++)
			fitDatagrams[n] = new Datagram[nitems - n][n + 1];
		for (int m = 0; m < nitems; m++)
			fitDatagrams[0][m][0] = new Datagram(0, m, 0);
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++) {
					fitDatagrams[n][m][c] = new Datagram(n, m, c, c, n - c + 1);
					fitDatagrams[n][m][c].N = N_pi0;
				}
		
		fit_pis(perm);
	}	
	
	public void fit_pis(int[][] perm) {
		Node tmp;
		double tmp_ll=-Double.MAX_VALUE;
		double best_ll=-Double.MAX_VALUE;
		for(int i=0;i<perm.length;i++) {
			init_DPGroupCounts(perm[i]);
			init_Datagrams(perm[i]);
			DPSearch(fitDatagrams, CRIM::DPMaximize);
			tmp=node_from_DP(fitDatagrams[nitems - 1][0][0], perm[i]);
			tmp_ll=loglikelihood(tmp, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
			if(tmp_ll>best_ll) {
				best_ll=tmp_ll;
				root=tmp;
			}
			if(i%50==0)
				System.out.println("Fitting pi number "+i);
		}
		System.out.println("Best tree:");
		System.out.println(root);
		System.out.println("Loglike:");
		System.out.println(best_ll);
	}

	public void fit(int iters, String fileout, double temp) throws IOException {
		/*
		 * Currently unused - allows output of every step of the run to a file 
		 */
		Random rand=new Random();
		boolean gmm=false;
		DPGroupCounts = new int[factors][nitems][][];
		for (int n = 0; n < nitems; n++) {
			for (int f = 0; f < factors; f++)
				DPGroupCounts[f][n] = new int[nitems - n][groupIDs_pi0[f][0].length];
		}

		fitDatagrams = new Datagram[nitems][][];
		for (int n = 0; n < nitems; n++)
			fitDatagrams[n] = new Datagram[nitems - n][n + 1];
		for (int m = 0; m < nitems; m++)
			fitDatagrams[0][m][0] = new Datagram(0, m, 0);
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++) {
					fitDatagrams[n][m][c] = new Datagram(n, m, c, c, n - c + 1);
					fitDatagrams[n][m][c].N = N_pi0;
				}

		int[] perm = new int[nitems];
		double[] rowSumQ = new double[nitems];

		for (int i = 0; i < nitems; i++) {
			for (int j = 0; j < nitems; j++)
				for (int f = 0; f < factors; f++)
					rowSumQ[i] += Qobs_pi0[f][i][j];
			perm[i] = i;
		}
		double tmpd;
		int tmpi;
		for (int i = 0; i < nitems; i++)
			for (int j = 0; j < nitems - 1 - i; j++)
				if (rowSumQ[j] < rowSumQ[j + 1]) {
					tmpd = rowSumQ[j];
					tmpi = perm[j];
					rowSumQ[j] = rowSumQ[j + 1];
					rowSumQ[j + 1] = tmpd;
					perm[j] = perm[j + 1];
					perm[j + 1] = tmpi;
				}

		double[] factorCDF = new double[factors];
		factorCDF[0] = N_pi0[0] / N_pi0[factors];
		for (int f = 1; f < factors; f++)
			factorCDF[f] = factorCDF[f - 1] + N_pi0[f] / N_pi0[factors];

		init_DPGroupCounts(perm);
		init_Datagrams(perm);
		DPSearch(fitDatagrams, CRIM::DPMaximize);

		Node best_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
		Node sample_node = best_node;
		Node tmp_node = best_node;
		double best_ll = loglikelihood(best_node, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
				testing_groupIDs_copy);
		double tmp_ll_train = loglikelihood(best_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
		if (testing_N_pi0[0] == 0)
			best_ll = tmp_ll_train;
		double sample_ll = best_ll;
		double tmp_ll = sample_ll;

		double best_ll_train = tmp_ll_train;
		double tmp_ll_valid = loglikelihood(best_node, validation_N_pi0, validation_Qobs_pi0,
				validation_groupIDs_pi0, validation_groupIDs_copy);
		double best_ll_valid = tmp_ll_valid;
		String outline = tmp_ll_train + " " + tmp_ll + " " + tmp_ll_valid + " " + tmp_node;
		Node best_gmm;
		double gmm_ll_train, gmm_ll_test, gmm_ll_valid;
		if(gmm) {
			DPGMMSearch(fitDatagrams);
			best_gmm = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
			gmm_ll_train=loglikelihood(best_gmm,N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
			gmm_ll_test = loglikelihood(best_gmm,  testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
					testing_groupIDs_copy);
			gmm_ll_valid = loglikelihood(best_gmm, validation_N_pi0, validation_Qobs_pi0,
					validation_groupIDs_pi0, validation_groupIDs_copy);
			outline += " "+gmm_ll_train+" "+gmm_ll_test+" "+gmm_ll_valid+" "+best_gmm+"\n";
		}
		else {
			outline += "\n";
		}
		//System.out.println("Starting fit of " + iters + " rankings");
		//System.out.println(outline);
		BufferedWriter outfile_writer = new BufferedWriter(new FileWriter(fileout));
		outfile_writer.append(outline);
		int fac = 0;
		double fac_rand;
		int k=0;
		for (int i = 0; i < iters; i++) {
			if(!Arrays.equals(tmp_node.getCanonicalPerm(fac),perm) && k<10) {
				perm=tmp_node.getCanonicalPerm(fac);
				i--;k++;
			}
			else {
				k=0;
				fac_rand = rand.nextDouble();
				fac = 0;
				if (factors > 1)
					for (fac = 0; fac_rand < factorCDF[fac]; fac++);
				// Sample new permutation
				perm = sample1(sample_node, rand)[fac];
			}
			// Reinitialize all relevant fit data structures
			init_DPGroupCounts(perm);
			init_Datagrams(perm);
			// Fit new model
			DPSearch(fitDatagrams, CRIM::DPMaximize);
			tmp_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
			// Find all likelihoods
			tmp_ll = loglikelihood(tmp_node, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
					testing_groupIDs_copy);
			tmp_ll_train = loglikelihood(tmp_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
			if (testing_N_pi0[0] == 0)
				tmp_ll = tmp_ll_train;
			tmp_ll_valid = loglikelihood(tmp_node, validation_N_pi0, validation_Qobs_pi0, validation_groupIDs_pi0,
					validation_groupIDs_copy);
			outline = tmp_ll_train + " " + tmp_ll + " " + tmp_ll_valid + " " + tmp_node;
			if(gmm) {
				DPGMMSearch(fitDatagrams);
				best_gmm = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
				gmm_ll_train=loglikelihood(best_gmm,N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
				gmm_ll_test = loglikelihood(best_gmm, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
						testing_groupIDs_copy);
				gmm_ll_valid = loglikelihood(best_gmm, validation_N_pi0, validation_Qobs_pi0,
						validation_groupIDs_pi0, validation_groupIDs_copy);
				outline += " "+gmm_ll_train+" "+gmm_ll_test+" "+gmm_ll_valid+" "+best_gmm+"\n";
			}
			else {
				outline += "\n";
			}
			outfile_writer.append(outline);
			if (i % 25 == 1) {
				outfile_writer.flush();
				//System.out.println("Wrote " + i);
			}
			if (tmp_ll > sample_ll || Math.exp(temp * (tmp_ll - sample_ll)) < rand.nextDouble()) {
				sample_node = tmp_node;
				sample_ll = tmp_ll;
				if (tmp_ll > best_ll) {
					best_node = tmp_node;
					best_ll = tmp_ll;
					best_ll_train = tmp_ll_train;
					best_ll_valid = tmp_ll_valid;
				}
			}
		}
		outline = best_ll_train + " " + best_ll + " " + best_ll_valid + " " + best_node;
		outfile_writer.append(outline);
		outfile_writer.flush();
		outfile_writer.close();
		System.out.println("Best model:");
		System.out.println(outline);
		System.out.println("Best Perm:"+k);
		System.out.println(Arrays.toString(best_node.getCanonicalPerm(0)));
		root = best_node;
	}

	public void fit0(int iters, double temp, Random rand){
		//Only uses training data
		DPGroupCounts = new int[factors][nitems][][];
		for (int n = 0; n < nitems; n++) {
			for (int f = 0; f < factors; f++)
				DPGroupCounts[f][n] = new int[nitems - n][groupIDs_pi0[f][0].length];
		}

		fitDatagrams = new Datagram[nitems][][];
		for (int n = 0; n < nitems; n++)
			fitDatagrams[n] = new Datagram[nitems - n][n + 1];
		for (int m = 0; m < nitems; m++)
			fitDatagrams[0][m][0] = new Datagram(0, m, 0);
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++) {
					fitDatagrams[n][m][c] = new Datagram(n, m, c, c, n - c + 1);
					fitDatagrams[n][m][c].N = N_pi0;
				}

		int[] perm = new int[nitems];
		double[] rowSumQ = new double[nitems];

		for (int i = 0; i < nitems; i++) {
			for (int j = 0; j < nitems; j++)
				for (int f = 0; f < factors; f++)
					rowSumQ[i] += Qobs_pi0[f][i][j];
			perm[i] = i;
		}
		double tmpd;
		int tmpi;
		for (int i = 0; i < nitems; i++)
			for (int j = 0; j < nitems - 1 - i; j++)
				if (rowSumQ[j] < rowSumQ[j + 1]) {
					tmpd = rowSumQ[j];
					tmpi = perm[j];
					rowSumQ[j] = rowSumQ[j + 1];
					rowSumQ[j + 1] = tmpd;
					perm[j] = perm[j + 1];
					perm[j + 1] = tmpi;
				}

		double[] factorCDF = new double[factors];
		factorCDF[0] = N_pi0[0] / N_pi0[factors];
		for (int f = 1; f < factors; f++)
			factorCDF[f] = factorCDF[f - 1] + N_pi0[f] / N_pi0[factors];

		init_DPGroupCounts(perm);
		init_Datagrams(perm);
		DPSearch(fitDatagrams, CRIM::DPMaximize);

		Node best_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
		Node sample_node = best_node;
		Node tmp_node = best_node;
		double best_ll = loglikelihood(best_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
		double sample_ll = best_ll;
		double tmp_ll = sample_ll;

		int fac = 0;
		double fac_rand;
		int k=0;
		for (int i = 0; i < iters; i++) {
			//Recheck again with canonical perm, cap at 10 repetitions to avoid hangups
			if(!Arrays.equals(tmp_node.getCanonicalPerm(fac),perm) && k<10) {
				perm=tmp_node.getCanonicalPerm(fac);
				i--;k++;
			}
			else {
				k=0;
				fac_rand = rand.nextDouble();
				fac = 0;
				if (factors > 1)
					for (fac = 0; fac_rand < factorCDF[fac]; fac++);
				// Sample new permutation
				perm = sample1(sample_node, rand)[fac];
			}
			// Reinitialize all relevant fit data structures
			init_DPGroupCounts(perm);
			init_Datagrams(perm);
			// Fit new model
			DPSearch(fitDatagrams, CRIM::DPMaximize);
			tmp_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
			// Find all likelihoods
			tmp_ll = loglikelihood(tmp_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);

			if (tmp_ll > sample_ll || Math.exp(temp * (tmp_ll - sample_ll)) < rand.nextDouble()) {
				//Keep new node for sampling if better or passes annealing check
				sample_node = tmp_node;
				sample_ll = tmp_ll;
				//Only update best if better
				if (tmp_ll > best_ll) {
					best_node = tmp_node;
					best_ll = tmp_ll;
				}
			}
		}
		root = best_node;
	}

	public void fit_GMM(){
		DPGroupCounts = new int[factors][nitems][][];
		for (int n = 0; n < nitems; n++) {
			for (int f = 0; f < factors; f++)
				DPGroupCounts[f][n] = new int[nitems - n][groupIDs_pi0[f][0].length];
		}

		fitDatagrams = new Datagram[nitems][][];
		for (int n = 0; n < nitems; n++)
			fitDatagrams[n] = new Datagram[nitems - n][n + 1];
		for (int m = 0; m < nitems; m++)
			fitDatagrams[0][m][0] = new Datagram(0, m, 0);
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++) {
					fitDatagrams[n][m][c] = new Datagram(n, m, c, c, n - c + 1);
					fitDatagrams[n][m][c].N = N_pi0;
				}

		int[] perm = new int[nitems];
		double[] rowSumQ = new double[nitems];

		for (int i = 0; i < nitems; i++) { perm[i] = i; }

		double[] factorCDF = new double[factors];
		factorCDF[0] = N_pi0[0] / N_pi0[factors];
		for (int f = 1; f < factors; f++)
			factorCDF[f] = factorCDF[f - 1] + N_pi0[f] / N_pi0[factors];

		init_DPGroupCounts(perm);
		init_Datagrams(perm);
		DPSearch(fitDatagrams, CRIM::DPMaximize);

		Node best_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
		Node sample_node = best_node;
		Node tmp_node = best_node;
		double best_ll = loglikelihood(best_node, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
				testing_groupIDs_copy);
		double tmp_ll_train = loglikelihood(best_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
		if (testing_N_pi0[0] == 0)
			best_ll = tmp_ll_train;
		double sample_ll = best_ll;
		double tmp_ll = sample_ll;

		double best_ll_train = tmp_ll_train;
		double tmp_ll_valid = loglikelihood(best_node, validation_N_pi0, validation_Qobs_pi0,
				validation_groupIDs_pi0, validation_groupIDs_copy);
		double best_ll_valid = tmp_ll_valid;
		String outline = tmp_ll_train + " " + tmp_ll + " " + tmp_ll_valid + " " + tmp_node;
		Node best_gmm;
		double gmm_ll_train, gmm_ll_test, gmm_ll_valid;
		DPGMMSearch(fitDatagrams);
		best_gmm = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
		gmm_ll_train=loglikelihood(best_gmm,N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
		gmm_ll_test = loglikelihood(best_gmm,  testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0, testing_groupIDs_copy);
		gmm_ll_valid = loglikelihood(best_gmm, validation_N_pi0, validation_Qobs_pi0,
					validation_groupIDs_pi0, validation_groupIDs_copy);
		root = best_node;
	}

	
	public void fit_alpha(int iters, String fileout, double temp) throws IOException {
		boolean gmm=true;
		DPGroupCounts = new int[factors][nitems][][];
		for (int n = 0; n < nitems; n++) {
			for (int f = 0; f < factors; f++)
				DPGroupCounts[f][n] = new int[nitems - n][groupIDs_pi0[f][0].length];
		}

		fitDatagrams = new Datagram[nitems][][];
		for (int n = 0; n < nitems; n++)
			fitDatagrams[n] = new Datagram[nitems - n][n + 1];
		for (int m = 0; m < nitems; m++)
			fitDatagrams[0][m][0] = new Datagram(0, m, 0);
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++) {
					fitDatagrams[n][m][c] = new Datagram(n, m, c, c, n - c + 1);
					fitDatagrams[n][m][c].N = N_pi0;
				}

		int[] perm = new int[nitems];
		double[] rowSumQ = new double[nitems];

		for (int i = 0; i < nitems; i++) {
			//for (int j = 0; j < nitems; j++)
			//	for (int f = 0; f < factors; f++)
			//		rowSumQ[i] += Qobs_pi0[f][i][j];
			perm[i] = i;
		}
		/*double tmpd;
		int tmpi;
		for (int i = 0; i < nitems; i++)
			for (int j = 0; j < nitems - 1 - i; j++)
				if (rowSumQ[j] < rowSumQ[j + 1]) {
					tmpd = rowSumQ[j];
					tmpi = perm[j];
					rowSumQ[j] = rowSumQ[j + 1];
					rowSumQ[j + 1] = tmpd;
					perm[j] = perm[j + 1];
					perm[j + 1] = tmpi;
				}
		 */

		// Random seed - print to output
		Random rand = new Random();
		int seed = rand.nextInt();
		rand = new Random();
		System.out.println("Permutation seed: " + seed);

		double[] factorCDF = new double[factors];
		factorCDF[0] = N_pi0[0] / N_pi0[factors];
		for (int f = 1; f < factors; f++)
			factorCDF[f] = factorCDF[f - 1] + N_pi0[f] / N_pi0[factors];

		init_DPGroupCounts(perm);
		init_Datagrams(perm);
		DPSearch(fitDatagrams, CRIM::DPMaximize);

		Node best_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
		Node sample_node = best_node;
		Node tmp_node = best_node;
		double best_ll = loglikelihood(best_node, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
				testing_groupIDs_copy);
		double tmp_ll_train = loglikelihood(best_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
		if (testing_N_pi0[0] == 0)
			best_ll = tmp_ll_train;
		double sample_ll = best_ll;
		double tmp_ll = sample_ll;

		double best_ll_train = tmp_ll_train;
		double tmp_ll_valid = loglikelihood(best_node, validation_N_pi0, validation_Qobs_pi0,
				validation_groupIDs_pi0, validation_groupIDs_copy);
		double best_ll_valid = tmp_ll_valid;
		String outline = tmp_ll_train + " " + tmp_ll + " " + tmp_ll_valid + " " + tmp_node;
		Node best_gmm;
		double gmm_ll_train, gmm_ll_test, gmm_ll_valid;
		if(gmm) {
			DPGMMSearch(fitDatagrams);
			best_gmm = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
			gmm_ll_train=loglikelihood(best_gmm,N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
			gmm_ll_test = loglikelihood(best_gmm,  testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
					testing_groupIDs_copy);
			gmm_ll_valid = loglikelihood(best_gmm, validation_N_pi0, validation_Qobs_pi0,
					validation_groupIDs_pi0, validation_groupIDs_copy);
			outline += " "+gmm_ll_train+" "+gmm_ll_test+" "+gmm_ll_valid+" "+best_gmm+"\n";
		}
		else {
			outline += "\n";
		}
		//System.out.println("Starting fit of " + iters + " rankings");
		//System.out.println(outline);
		BufferedWriter outfile_writer = new BufferedWriter(new FileWriter(fileout));
		outfile_writer.append(outline);
		int fac = 0;
		double fac_rand;
		int k=0;
		for (int i = 0; i < iters; i++) {
			if(!Arrays.equals(tmp_node.getCanonicalPerm(fac),perm) && k<10) {
				perm=tmp_node.getCanonicalPerm(fac);
				i--;k++;
			}
			else {
				k=0;
				fac_rand = rand.nextDouble();
				fac = 0;
				if (factors > 1)
					for (fac = 0; fac_rand < factorCDF[fac]; fac++);
				// Sample new permutation
				perm = sample1(sample_node, rand)[fac];
			}
			// Reinitialize all relevant fit data structures
			init_DPGroupCounts(perm);
			init_Datagrams(perm);
			// Fit new model
			DPSearch(fitDatagrams, CRIM::DPMaximize);
			tmp_node = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
			// Find all likelihoods
			tmp_ll = loglikelihood(tmp_node, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
					testing_groupIDs_copy);
			tmp_ll_train = loglikelihood(tmp_node, N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
			if (testing_N_pi0[0] == 0)
				tmp_ll = tmp_ll_train;
			tmp_ll_valid = loglikelihood(tmp_node, validation_N_pi0, validation_Qobs_pi0, validation_groupIDs_pi0,
					validation_groupIDs_copy);
			outline = tmp_ll_train + " " + tmp_ll + " " + tmp_ll_valid + " " + tmp_node;
			if(gmm) {
				DPGMMSearch(fitDatagrams);
				best_gmm = node_from_DP(fitDatagrams[nitems - 1][0][0], perm);
				gmm_ll_train=loglikelihood(best_gmm,N_pi0, Qobs_pi0, groupIDs_pi0, groupIDs_copy);
				gmm_ll_test = loglikelihood(best_gmm, testing_N_pi0, testing_Qobs_pi0, testing_groupIDs_pi0,
						testing_groupIDs_copy);
				gmm_ll_valid = loglikelihood(best_gmm, validation_N_pi0, validation_Qobs_pi0,
						validation_groupIDs_pi0, validation_groupIDs_copy);
				outline += " "+gmm_ll_train+" "+gmm_ll_test+" "+gmm_ll_valid+" "+best_gmm+"\n";
			}
			else {
				outline += "\n";
			}
			outfile_writer.append(outline);
			if (i % 25 == 1) {
				outfile_writer.flush();
				//System.out.println("Wrote " + i);
			}
			if (tmp_ll > sample_ll || Math.exp(temp * (tmp_ll - sample_ll)) < rand.nextDouble()) {
				sample_node = tmp_node;
				sample_ll = tmp_ll;
				if (tmp_ll > best_ll) {
					best_node = tmp_node;
					best_ll = tmp_ll;
					best_ll_train = tmp_ll_train;
					best_ll_valid = tmp_ll_valid;
				}
			}
		}
		outline = best_ll_train + " " + best_ll + " " + best_ll_valid + " " + best_node;
		outfile_writer.append(outline);
		outfile_writer.flush();
		outfile_writer.close();
		System.out.println("Best model:");
		System.out.println(outline);
		System.out.println("Best Perm:");
		System.out.println(Arrays.toString(best_node.getCanonicalPerm(0)));
		root = best_node;
	}
	
	double loglikelihood(Node node, int[] N, double[][][] Qobs, int[][][] gIDs, int[][][] gIDs_copy) {
		int ind = 0;
		int[][] piInds = new int[nitems][nitems + 1];
		return loglikelihood(node, N, Qobs, gIDs, gIDs_copy, piInds, ind);
	}

	private double loglikelihood(Node node, int[] N, double[][][] Qobs, int[][][] gIDs, int[][][] gIDs_copy,
			int[][] piInds, int ind) {
		if (node.isleaf) {
			for (int f = 0; f < factors; f++)
				System.arraycopy(gIDs[f][node.item], 0, gIDs_copy[f][ind], 0, gIDs[f][node.item].length);
			piInds[ind][0] = 1;
			piInds[ind][1] = node.item;
			return 0.0;
		} else {
			double ll = 0;
			ll += loglikelihood((Node) node.left, N, Qobs, gIDs, gIDs_copy, piInds, ind);
			ll += loglikelihood((Node) node.right, N, Qobs, gIDs, gIDs_copy, piInds, ind + 1);
			for (int f = 0; f < factors; f++) {
				// Set node.LRCounts_tmp
				for (int l = 0; l < node.LRCounts_tmp.length; l++)
					for (int r = 0; r < node.LRCounts_tmp[0].length; r++)
						node.LRCounts_tmp[l][r] = 0;
				for (int n = 0; n < gIDs_copy[f][ind].length; n++) {
					node.LRCounts_tmp[gIDs_copy[f][ind][n]][gIDs_copy[f][ind + 1][n]]++;
					gIDs_copy[f][ind][n] += gIDs_copy[f][ind + 1][n];
				}
				for (int l = 0; l < node.LRCounts_tmp.length; l++)
					for (int r = 0; r < node.LRCounts_tmp[0].length; r++)
						node.LRCounts_tmp[l][r] /= N[factors];
				// Set v
				double vbar = 0;
				// if(node.params.thetas[f]>0)
				for (int l = 1; l <= piInds[ind][0]; l++)
					for (int r = 1; r <= piInds[ind + 1][0]; r++)
						vbar += Qobs[f][piInds[ind + 1][r]][piInds[ind][l]];
				// else
				// for(int l=1;l<=piInds[ind][0];l++)
				// for(int r=1;r<=piInds[ind+1][0];r++)
				// vbar+=Qobs[f][piInds[ind][l]][piInds[ind+1][r]];
				vbar /= N[factors];
				ll += logLikelihood(node.Z_tmp, node.LRCounts_tmp, vbar, node.params.thetas[f],
						(double) N[f] / N[factors]);
			}
			for (int r = 0; r < piInds[ind + 1][0]; r++) {
				piInds[ind][piInds[ind][0] + 1 + r] = piInds[ind + 1][r + 1];
			}
			piInds[ind][0] += piInds[ind + 1][0];
			return ll;
		}
	}

	public void init_Datagrams(int[] perm) {
		// Shouldn't need to set row to 0 as it never gets raised.
		// for(int n=0;n<nitems;n++) {
		// fitDatagrams[0][n][0].logLikeTotal=0;
		// }
		init_Datagrams_Q_brute(perm);
		init_Datagrams_LRCount(perm);
	}

	public void init_Datagrams_LRCount(int[] perm) {
		// Replace this with a faster version.
		for (int n = 1; n < nitems; n++) {
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++)
					for (int f = 0; f < factors; f++) {
						for (int l = 0; l < fitDatagrams[n][m][c].LRCounts[0].length; l++)
							for (int r = 0; r < fitDatagrams[n][m][c].LRCounts[0][0].length; r++)
								fitDatagrams[n][m][c].LRCounts[f][l][r] = 0;
						if (c < n - c + 1)
							fill_LRCounts(fitDatagrams[n][m][c].LRCounts[f], DPGroupCounts[f][c - 1][m],
									DPGroupCounts[f][n - c][m + c], N_pi0[factors]);
						else
							fill_LRCounts(fitDatagrams[n][m][c].LRCounts[f], DPGroupCounts[f][n - c][m + c],
									DPGroupCounts[f][c - 1][m], N_pi0[factors]);
					}
		}
	}

	public void fill_LRCounts(double[][] LRCounts, int[] lGroups, int[] rGroups, int N) {
		for (int i = 0; i < lGroups.length; i++)
			LRCounts[lGroups[i]][rGroups[i]]++;
		for (int l = 1; l < LRCounts.length; l++)
			for (int r = 0; r < l; r++) {
				LRCounts[r][l] += LRCounts[l][r];
				LRCounts[l][r] = 0;
			}
		// Normalize
		for (int l = 0; l < LRCounts.length; l++)
			for (int r = 0; r < LRCounts[0].length; r++)
				LRCounts[l][r] /= N;
	}

	public void init_Datagrams_Q_brute(int[] perm) {
		// Replace this with a faster version.
		for (int n = 1; n < nitems; n++)
			for (int m = 0; m < nitems - n; m++)
				for (int c = 1; c <= n; c++)
					for (int f = 0; f < factors; f++) {
						fitDatagrams[n][m][c].Vobs[f] = 0;
						for (int l = m; l < m + c; l++)
							for (int r = m + c; r <= m + n; r++)
								fitDatagrams[n][m][c].Vobs[f] += Qobs_pi0[f][perm[r]][perm[l]];
						fitDatagrams[n][m][c].Vobs[f] /= N_pi0[factors];
					}
	}

	public void init_DPGroupCounts(int[] perm) {
		for (int f = 0; f < factors; f++) {
			for (int n = 0; n < nitems; n++)
				System.arraycopy(groupIDs_pi0[f][perm[n]], 0, DPGroupCounts[f][0][n], 0,
						groupIDs_pi0[f][perm[n]].length);
			for (int n = 1; n < nitems; n++) {
				for (int m = 0; m < nitems - n; m++) {
					for (int k = 0; k < DPGroupCounts[f][0][m].length; k++) {
						DPGroupCounts[f][n][m][k] = DPGroupCounts[f][n - 1][m][k] + DPGroupCounts[f][0][n + m][k];
					}
				}
			}
		}
	}

	public static void likelihood(AbstractDatagram adg, AbstractDatagram adg2, AbstractDatagram adg3) {
		Datagram dg = (Datagram) adg;
		System.out.println("do a likelihood please");
	}

	public static void DPMaximize(AbstractDatagram[] adgs) {
		// THIS HAS HARD CODED LEARN RATES
		// WHERE TO PUT??
		double lLogLike = ((Datagram) adgs[1]).logLikeTotal;
		double rLogLike = ((Datagram) adgs[2]).logLikeTotal;
		double step = 0;
		double nstep = 0;
		Datagram dg = (Datagram) adgs[0];
		for (int f = 0; f < dg.Vobs.length; f++) {
			double dw = (double) dg.N[f] / dg.N[dg.N.length - 1];
			step = dLogLikelihood(dg.dZtmp, dg.LRCounts[f], dg.Vobs[f], dg.theta[f], dw);
			while (Math.abs(step) > deltaCutoff) {
				while (step < 0 && Math.abs(step) > deltaCutoff) {
					nstep = dLogLikelihood(dg.dZtmp, dg.LRCounts[f], dg.Vobs[f], dg.theta[f] + step, dw);
					if (nstep < 0) {
						dg.theta[f] += step;
						step = nstep;
					} else
						step /= 2;
				}
				while (step > 0 && Math.abs(step) > deltaCutoff) {
					nstep = dLogLikelihood(dg.dZtmp, dg.LRCounts[f], dg.Vobs[f], dg.theta[f] + step, dw);
					if (nstep > 0) {
						dg.theta[f] += step;
						step = nstep;
					} else
						step /= 2;
				}
			}
			dg.logLike[f] = logLikelihood(dg.Ztmp, dg.LRCounts[f], dg.Vobs[f], dg.theta[f], dw);
		}
		dg.logLikeTotal = lLogLike + rLogLike;
		for (int f = 0; f < dg.Vobs.length; f++) {
			dg.logLikeTotal += dg.logLike[f];
			dg.logLikeLocal += dg.logLike[f];
		}
	}

	public static void likelihood(AbstractDatagram adg) {
		Datagram dg = (Datagram) adg;
		System.out.println("do a likelihood please");
	}

	public class Datagram extends AbstractDatagram {
		// int factors;// How many factors are being used?
		// Do we need the whole matrix? Can we init Vobs and call it a day?
		// double[][][] Qobs;//Observed Q matrix
		double[] Vobs;// For summing over Qobs
		double[][][] LRCounts;// Fold?
		double[] theta;// Save one for each factor
		double[] logLike;// Save for each factor
		double[][] Ztmp;// For temporarily storing Z values
		double[][] dZtmp;// For temporarily storing dZ values
		int[] N;

		Datagram(int n0, int m0, int c0) {
			super(n0, m0, c0);
			logLikeTotal = 0;
			logLikeLocal = 0;
		}

		Datagram(int n0, int m0, int c0, int L, int R) {
			super(n0, m0, c0);
			// Always assume L<=R, it's symmetric and will
			// save on calculations
			Vobs = new double[factors];
			theta = new double[factors];
			logLike = new double[factors];
			if (R < L) {
				int tmp = R;
				R = L;
				L = tmp;
			}
			Ztmp = new double[L + 1][R + 1];
			dZtmp = new double[L + 1][R + 1];
			LRCounts = new double[factors][L + 1][R + 1];
			N = new int[factors + 1];
		}
	}

	public class Node extends AbstractNode {
		Parameter params;
		double[][] LRCounts_tmp;
		double[][] Z_tmp;

		public class Parameter extends AbstractParameter {
			double[] thetas;

			Parameter(double[] thetasIn) {
				thetas = thetasIn.clone();
			}

			public String toString() {
				String paramstring = "[" + params.thetas[0];
				for (int i = 1; i < params.thetas.length; i++)
					paramstring += ";" + params.thetas[i];
				paramstring += "]";
				return (paramstring);
			}
		}

		Node(int item) {
			super(item);
		}

		Node(Node left, Node right, double[] theta) {
			this.left = left;
			this.L = this.left.LR;
			this.right = right;
			this.R = this.right.LR;
			this.LR = this.L + this.R;
			this.isleaf = false;
			this.item = -1;
			Parameter tmp = new Parameter(theta);
			this.params = tmp;
			this.LRCounts_tmp = new double[L + 1][R + 1];
			this.Z_tmp = new double[L + 1][R + 1];
		}

		public int[] getCanonicalPerm(int factor) {
			int[] permOut = new int[LR];
			if (isleaf == true)
				permOut[0] = item;
			else {
				if(params.thetas[factor]>=0) {
					System.arraycopy(((Node) left).getCanonicalPerm(factor), 0, permOut, 0, L);
					System.arraycopy(((Node) right).getCanonicalPerm(factor), 0, permOut, L, R);
				} else {
					System.arraycopy(((Node) right).getCanonicalPerm(factor), 0, permOut, 0, R);
					System.arraycopy(((Node) left).getCanonicalPerm(factor), 0, permOut, R, L);
				}
			}
			return permOut;
		}
		
		public int[] getNoncanonicalPerm() {
			int[] permOut = new int[LR];
			getNoncanonicalPerm(permOut, 0);
			return (permOut);
		}

		public void getNoncanonicalPerm(int[] permOut, int ind) {
			if (isleaf == true)
				permOut[ind] = item;
			else {
				((Node) left).getNoncanonicalPerm(permOut, ind);
				((Node) right).getNoncanonicalPerm(permOut, ind + L);
			}
		}

		public int[][] setThetas() {
			// int[][][] groupIDs_pi0;// factor, item, index in group list
			// int[][][] groupIDs_copy;
			// double[][][] Qobs_pi0;// factor, i, j
			// int[] N_pi0;// factor
			if (isleaf == true) {
				int[][] retGC = new int[factors][];
				for (int f = 0; f < factors; f++) {
					retGC[f] = groupIDs_pi0[f][item].clone();
				}
				return (retGC);
			} else {
				// set up suff statistics
				int[][] lGC = ((Node) left).setThetas();
				int[][] rGC = ((Node) right).setThetas();
				int[][] retGC = new int[factors][];
				double[][][] LRCounts = new double[factors][L + 1][R + 1];
				for (int f = 0; f < factors; f++) {
					retGC[f] = new int[lGC[f].length];
					for (int n = 0; n < lGC[f].length; n++) {
						retGC[f][n] = lGC[f][n] + rGC[f][n];
						LRCounts[f][lGC[f][n]][rGC[f][n]]++;
					}
					for (int l = 0; l <= L; l++)
						for (int r = 0; r <= R; r++)
							LRCounts[f][l][r] /= N_pi0[factors];
				}
				int[] linds = ((Node) left).getNoncanonicalPerm();
				int[] rinds = ((Node) right).getNoncanonicalPerm();
				double[] vbar = new double[factors];
				for (int f = 0; f < factors; f++) {
					for (int l = 0; l < linds.length; l++)
						for (int r = 0; r < rinds.length; r++) {
							vbar[f] += Qobs_pi0[f][rinds[r]][linds[l]];
						}
					vbar[f] /= N_pi0[factors];
				}

				// end suff statistcs
				// opt step
				double step = 0;
				double nstep = 0;
				double llcurrent;
				double llnew;
				for (int f = 0; f < factors; f++) {
					params.thetas[f]=0;
					double dw = (double) N_pi0[f] / N_pi0[factors];
					step = dLogLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f], dw);
					llcurrent=logLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f], dw);
					
					while (Math.abs(step) > deltaCutoff) {
						while (step < 0 && Math.abs(step) > deltaCutoff) {
							llnew=logLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f]+step, dw);
							if(llnew > llcurrent) {
								params.thetas[f] += step;
								llcurrent=llnew;
								step=dLogLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f], dw);
							} else
								step /= 2;
						}
						while (step > 0 && Math.abs(step) > deltaCutoff) {
							llnew=logLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f]+step, dw);
							if(llnew > llcurrent) {
								params.thetas[f] += step;
								llcurrent=llnew;
								step=dLogLikelihood(Z_tmp, LRCounts[f], vbar[f], params.thetas[f], dw);
							} else
								step /= 2;
						}
					}
				}
				return (retGC);
			}
		}

		public double[][] getQ(int[] items, int fac) {
			if (isleaf == true) {
				for (int i = 0; i < items.length; i++) {
					if (items[i] == item) {
						double[][] retQ = new double[1][1];
						retQ[0][0] = 0;
						return (retQ);
					}
				}
				return (null);
			}
			double theta = params.thetas[fac];
			double[][] Pl, Pr;
			if (theta < 0) {
				Pl = ((Node) right).getP(items, fac);
				Pr = ((Node) left).getP(items, fac);
			} else {
				Pl = ((Node) left).getP(items, fac);
				Pr = ((Node) right).getP(items, fac);
			}
			if (Pl == null)
				return (((Node) right).getQ(items, fac));
			else if (Pr == null)
				return (((Node) left).getQ(items, fac));
			else {
				int subL = Pl.length;
				int subR = Pr.length;
				double[][] Qtil = getQtilde(subL, subR, Math.abs(theta));
				double[][] Q = new double[subL][subR];
				for (int i = 0; i < subL; i++)
					for (int j = 0; j < subR; j++)
						for (int l = 0; l < subL; l++)
							for (int r = 0; r < subR; r++)
								Q[i][j] += Pl[i][l] * Pr[j][r] * Qtil[l][r];
				return (Q);
			}
		}
		
		
		public double[][][] getFullQ() {
			int[] items = new int[nitems];
			for (int k = 0; k < nitems; k++)
				items[k] = k;
			return(getFullQ(items));
		}
		
		public double[][][] getFullQ(int[] items) {
			double[][][] FullQ=new double[factors][LR][LR];
			if (isleaf == true) {
				return(FullQ);
			}
			double[] theta = params.thetas;
			for(int f=0;f<factors;f++) {
				double[][] Pl, Pr;
				double[][] Ql, Qr;
				if (theta[f] < 0) {
					Pl = ((Node) right).getP(items, f);
					Pr = ((Node) left).getP(items, f);
					Ql = ((Node) right).getFullQ(items)[f];
					Qr = ((Node) left).getFullQ(items)[f];
				} else {
					Pl = ((Node) left).getP(items, f);
					Pr = ((Node) right).getP(items, f);
					Ql = ((Node) left).getFullQ(items)[f];
					Qr = ((Node) right).getFullQ(items)[f];
				}
				int subL = Pl.length;
				int subR = Pr.length;
				double[][] Qtil = getQtilde(subL, subR, Math.abs(theta[f]));
				double[][] Q = new double[subL][subR];
				for (int i = 0; i < subL; i++)
					for (int j = 0; j < subR; j++)
						for (int l = 0; l < subL; l++)
							for (int r = 0; r < subR; r++)
								Q[i][j] += Pl[i][l] * Pr[j][r] * Qtil[l][r];
				for(int i=0;i<subL;i++)
					for(int j=0;j<subR;j++) {
						FullQ[f][i][subL+j]=Q[i][j];
						FullQ[f][subL+j][i]=1-Q[i][j];
					}	
				for(int i=0;i<subL;i++)
					for(int j=0;j<subL;j++) {
						FullQ[f][i][j]=Ql[i][j];
					}	
				for(int i=0;i<subR;i++)
					for(int j=0;j<subR;j++) {
						FullQ[f][subL+i][subL+j]=Qr[i][j];
					}	
				}
			return (FullQ);
		}

		public double[][] getP(int[] items, int fac) {
			if (isleaf == true) {
				for (int i = 0; i < items.length; i++) {
					if (items[i] == item) {
						double[][] retP = new double[1][1];
						retP[0][0] = 1;
						return (retP);
					}
				}
				return (null);
			}
			double theta = params.thetas[fac];
			double[][] Pl, Pr;
			if (theta < 0) {
				Pl = ((Node) right).getP(items, fac);
				Pr = ((Node) left).getP(items, fac);
			} else {
				Pl = ((Node) left).getP(items, fac);
				Pr = ((Node) right).getP(items, fac);
			}
			if (Pl == null)
				return (Pr);
			else if (Pr == null)
				return (Pl);
			else {
				int subL = Pl.length;
				int subR = Pr.length;
				double[][] retP = new double[subL + subR][subL + subR];
				double[][] Ptil = getPtilde(subL, subR, theta);
				for (int e = 0; e < subL; e++) {
					for (int j = 0; j < subL + subR; j++) {
						for (int k = 0; k <= j && k < subL; k++) {
							retP[e][j] += Pl[e][k] * Ptil[k][j];
						}
					}
				}
				for (int e = 0; e < subR; e++) {
					for (int j = 0; j < subL + subR; j++) {
						for (int k = 0; k <= j && k < subR; k++) {
							retP[subL + e][j] += Pr[e][k] * Ptil[subL + k][j];
						}
					}
				}
				return (retP);
			}
		}

		public String toString() {
			// Must override if object does not have print function
			if (this.isleaf == true)
				return Integer.toString(this.item);
			return "(" + this.left.toString() + "," + this.right.toString() + "|" + this.params.toString() + ")";
		}
		
		public String getStructString() {
			if (this.isleaf == true)
				return Integer.toString(this.item);
			return "(" + ((Node) this.left).getStructString() + "," + ((Node) this.right).getStructString() + ")";
		}
	}
	
	public String toString() {
		//String output="Structure: "+this.root.getStructString()+"\n";
		//output+="Thetas: "+this.root;
		String output=this.root.getStructString()+"\n";
		output+=this.root;
		return(output);
	}

	public Node treeFromString(String treeString) {
		//Assumes format node=([theta],node,node)
		
		/* If leaf, parse to int, return */
		if(treeString.indexOf(',')==-1) {
			return(new Node(Integer.parseInt(treeString)));
		} 
		
		/* Note: Currently designed for a single theta parameter */
		int thetaend=treeString.indexOf(',');
		double[] theta=new double[1];
		theta[0]=Double.parseDouble(treeString.substring(2,thetaend-1));
		
		int parenflux=0;
		int lstart=thetaend+1; int lend=lstart;
		while(treeString.charAt(lend)!=',' || parenflux!=0) {
			if(treeString.charAt(lend)=='(')
				parenflux++;
			if(treeString.charAt(lend)==')')
				parenflux--;
			lend++;
		}
		String lstring=treeString.substring(lstart,lend);
		Node lnode=treeFromString(lstring);
		String rstring=treeString.substring(lend+1,treeString.length()-1);
		Node rnode=treeFromString(rstring);
		
		return(new Node(lnode,rnode,theta));
	}
}
