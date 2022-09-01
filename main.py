from GUI import GUI
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rating_path", type=str, help="path of the rating file", required=True)
parser.add_argument("--ranking_path", type=str, help="path of the ranking file", required=True)
parser.add_argument("--num", "--num_str", type=int, help="number of string displayed in the papers' short name", default=15)
args = parser.parse_args()
RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"


def main():
    instance = GUI(args.ranking_path, args.rating_path)
    instance.show()

if __name__ == "__main__":
    main()