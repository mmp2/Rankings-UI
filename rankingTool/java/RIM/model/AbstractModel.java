package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

import model.CRIM.Node;
//import CRIM.Node;

public abstract class AbstractModel {
	Node root;
	int nitems;

	AbstractModel() {
		
	}

	public void DPSearch(AbstractDatagram[][][] datagrams, Consumer<AbstractDatagram[]> datagramSetter) {
		AbstractDatagram[] dgs = new AbstractDatagram[3];
		for (int n = 1; n < datagrams.length; n++) {
			for (int m = 0; m < datagrams[n].length; m++)
				for (int c = 1; c < datagrams[n][m].length; c++) {
					dgs[0] = datagrams[n][m][c];
					dgs[1] = datagrams[c - 1][m][0];
					dgs[2] = datagrams[n - c][m + c][0];
					datagramSetter.accept(dgs);
				}
			for (int m = 0; m < datagrams[n].length; m++) {
				datagrams[n][m][0] = datagrams[n][m][1];
				for (int c = 2; c < datagrams[n][m].length; c++)
					if (datagrams[n][m][0].logLikeTotal < datagrams[n][m][c].logLikeTotal)
						datagrams[n][m][0] = datagrams[n][m][c];
			}
		}
	}
	
	public void DPGMMSearch(AbstractDatagram[][][] datagrams) {
		for (int n = 3; n < datagrams.length; n++) {
			for (int m = 0; m < datagrams[n].length; m++) {
				int last=datagrams[n][m].length-1;
				datagrams[n][m][1].logLikeTotal=datagrams[n][m][1].logLikeLocal +
													datagrams[0][m][0].logLikeTotal +
													datagrams[n-1][m+1][0].logLikeTotal;
				
				datagrams[n][m][last].logLikeTotal=datagrams[n][m][last].logLikeLocal +
													datagrams[last-1][m][0].logLikeTotal +
													datagrams[n-last][m+last][0].logLikeTotal;
				datagrams[n][m][0] = datagrams[n][m][1];
				if(datagrams[n][m][last].logLikeTotal>datagrams[n][m][0].logLikeTotal)
					datagrams[n][m][0] = datagrams[n][m][last];
			}
		}
	}

	static void set_Z(double[][] Z, double theta) {
		// This is an EXPONENTIAL MODEL - not [0,1]
		// Note - could possible avoid filling half but
		// won't worry about it just now.

		Z[0][0] = 1;
		for (int l = 1; l < Z.length; l++) {
			Z[l][0] = 1;
			Z[l][1] = (1 - Math.exp(-theta * l)) / (1 - Math.exp(-theta));
		}
		for (int r = 1; r < Z[0].length; r++) {
			Z[0][r] = 1;
			Z[1][r] = (1 - Math.exp(-theta * (r + 1))) / (1 - Math.exp(-theta));
		}
		for (int l = 2; l < Z.length; l++) {
			for (int r = 1; r < Z[0].length; r++)
				Z[l][r] = Z[l][r - 1] * Math.exp(-theta * l) + Z[l - 1][r];
		}
		if (theta == 0)
			for (int l = 0; l < Z.length; l++)
				for (int r = 0; r < Z[0].length; r++) {
					Z[l][r] = 1;
					for (int rfact = 1; rfact <= r; rfact++)
						Z[l][r] = Z[l][r] * (l + rfact) / rfact;
				}
	}

	static void set_dLogZ(double[][] dZ, double theta) {
		// This is an EXPONENTIAL MODEL - not [0,1]
		for (int l = 0; l < dZ.length; l++)
			for (int r = 0; r < dZ[0].length; r++)
				dZ[l][r] = 0;

		if (Math.abs(theta) >= .00001)
			for (int l = 1; l < dZ.length; l++)
				for (int r = 1; r < dZ[0].length; r++) {
					dZ[l][r] = dZ[l - 1][r] - l * Math.exp(-theta * l) / (1 - Math.exp(-theta * l))
							+ (l + r) * Math.exp(-theta * (l + r)) / (1 - Math.exp(-theta * (l + r)));
				}
		else
			for (int l = 1; l < dZ.length; l++)
				for (int r = 1; r < dZ[0].length; r++)
					dZ[l][r] = -l * r / 2.0;
	}

	static double dLogLikelihood(double[][] dlZ, double[][] LRCounts, double pVbar, double theta, double denom_weight) {
		// This is an EXPONENTIAL MODEL - not [0,1]
		set_dLogZ(dlZ, theta);
		double retval = 0;
		for (int l = 1; l < LRCounts.length; l++)
			for (int r = 1; r < LRCounts[0].length; r++)
				retval += LRCounts[l][r] * dlZ[l][r];
		return retval - denom_weight * dlZ[LRCounts.length - 1][LRCounts[0].length - 1] - pVbar;
	}

	public void DPDatagramInit(AbstractDatagram[][][] datagrams, Consumer<AbstractDatagram> datagramSetter) {
		for (int i = 0; i < datagrams.length; i++)
			for (int j = 0; j < datagrams[i].length; j++)
				for (int k = 0; k < datagrams[i][j].length; k++)
					datagramSetter.accept(datagrams[i][j][k]);
	}

	static double ZLikelihood(double[][] LRCounts, double[][] Z, double denom_weight) {
		double retval = 0;
		for (int l = 1; l < LRCounts.length; l++)
			for (int r = 1; r < LRCounts[0].length; r++)
				retval += LRCounts[l][r] * Math.log(Z[l][r]);
		return retval - denom_weight * Math.log(Z[LRCounts.length - 1][LRCounts[0].length - 1]);
	}

	static double logLikelihood(double[][] Z, double[][] LRCounts, double pvbar, double theta, double denom_weight) {
		// use dummy for
		set_Z(Z, theta);
		double pzl = ZLikelihood(LRCounts, Z, denom_weight);
		double loglik = pzl - theta * pvbar;
		return (loglik);
	}

	static double[][] getQtilde(double[][] Z, double theta) {
		int L = Z.length - 1;
		int R = Z[0].length - 1;
		double[][] Q = new double[L][R];
		for (int l = 1; l <= L; l++) {
			Q[l - 1][1 - 1] = Z[L - l][R] / Z[L][R];
			if (R > 1)
				for (int r = 1; r < R; r++) // ADDED thet term
					Q[l - 1][r] = Q[l - 1][r - 1]
							+ Math.exp(-theta * r * (L - (l - 1))) * Z[l - 1][r] * Z[L - l][R - r] / Z[L][R];
		}
		return (Q);
	}

	static double[][] getQtilde(int L, int R, double theta) {
		double[][] Z=new double[L+1][R+1];
		set_Z(Z,theta);
		return(getQtilde(Z, theta));
	}
	
	static double[][] getPtilde(int L, int R, double theta) {
		double[][] Z=new double[L+1][R+1];
		set_Z(Z,theta);
		double[][] Q = getQtilde(Z,theta);
		double[][] Ptilde = new double[L + R][L + R];

		for (int l = 1; l <= L; l++) {
			Ptilde[l - 1][l - 1] = Q[l - 1][0];
			if (R > 1)
				for (int r = 1; r <= (R - 1); r++) {
					Ptilde[l - 1][l + r - 1] = Q[l - 1][r] - Q[l - 1][r - 1];
				}
			Ptilde[l - 1][l + R - 1] = 1.0 - Q[l - 1][R - 1];
		}
		for (int r = 1; r <= R; r++) {
			// l=1 case
			Ptilde[L + r - 1][r + 1 - 1 - 1] = 1.0 - Q[1 - 1][r - 1];
			for (int l = 2; l <= L; l++) {
				Ptilde[L + r - 1][r + l - 1 - 1] = Q[l - 1 - 1][r - 1] - Q[l - 1][r - 1];
			}
			Ptilde[L + r - 1][L + r - 1] = Q[L - 1][r - 1];
		}
		return (Ptilde);
	}
	
	public abstract class AbstractDatagram {
		int n, m, c;
		double logLikeTotal;// logLike of subtree
		double logLikeLocal;// logLike of node

		AbstractDatagram(int n0, int m0, int c0) {
			n = n0;
			m = m0;
			c = c0;
		}
	}

	public abstract class AbstractParameter {
		public String toString() {
			return ("AbstractParameter toString");
		}
	}

	public abstract class AbstractNode {
		/*
		 * Abstract node only contains key features of the node structure additional
		 * elements can be added (such as # categories) inside the param object
		 */
		AbstractNode left; // Children
		AbstractNode right; // Children
		boolean isleaf; // Only true on leaf nodes
		int item; // Only used on leaf nodes (-1 otherwise)
		AbstractParameter params; // Parameter at node - object allows various parameterizations
		int L, R, LR; // Number of items in left, right, and current node

		AbstractNode() {
			// System.out.println("AbstractNode Default Constructor");
		}

		AbstractNode(AbstractNode left, AbstractNode right, AbstractParameter param) {
			// System.out.println("AbstractNode internal initializer");
			this.left = left;
			this.L = this.left.LR;
			this.right = right;
			this.R = this.right.LR;
			this.LR = this.L + this.R;
			this.isleaf = false;
			this.item = -1;
			this.params = param;
		}

		AbstractNode(int item) {
			// System.out.println("AbstractNode leaf initializer");
			this.left = null;
			this.L = 0;
			this.right = null;
			this.R = 0;
			this.LR = 1;
			this.isleaf = true;
			this.item = item;
			this.params = null;
		}

		public String toString() {
			return "ERROR: Node-class toString method undefined\n";
		}

		public void applyFunction() {

		}
	}

	public static int[][] loadGroupIDs(String filename) throws FileNotFoundException {
		Scanner lineScanner = new Scanner(new File(filename));

		int n = 0;
		while (lineScanner.hasNextLine()) {
			lineScanner.nextLine();
			n++;
		}
		lineScanner.close();

		lineScanner = new Scanner(new File(filename));
		Scanner dataScanner = null;
		dataScanner = new Scanner(lineScanner.nextLine());
		dataScanner.useDelimiter(" ");
		int nitems = 0;
		while (dataScanner.hasNext()) {
			dataScanner.next();
			nitems++;
		}
		dataScanner.close();

		lineScanner = new Scanner(new File(filename));
		//dataScanner = new Scanner(lineScanner.nextLine());
		//dataScanner.useDelimiter(" ");
		int[][] groupIDs = new int[n][nitems];
		int nind = 0;
		int itemind = 0;
		
		//ANNE FIX ME, YOU ARE DROPPING THE FIRST OBS
		while (lineScanner.hasNext()) {
			dataScanner = new Scanner(lineScanner.nextLine());
			dataScanner.useDelimiter(" ");
			while (dataScanner.hasNext())
				groupIDs[nind][itemind++] = Integer.parseInt(dataScanner.next());
			dataScanner.close();
			itemind = 0;
			nind++;
		}

		return groupIDs;
	}
}
