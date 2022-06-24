from GUI import GUI
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rating_path", type=str, help="path of the rating file", required=True)
parser.add_argument("--ranking_path", type=str, help="path of the ranking file", required=True)
parser.add_argument("--num", "--num_str", type=int, help="number of string displayed in the papers' short name", default=15)
args = parser.parse_args()
RATINGS_PATH = "dummy_ICML.xls"
RANKING = "ReviewerSubmissionComparisons.txt"
'''
RATING_PATHS = {
    "overall": OP_RATINGS_PATH,
    "Investigator": FQ_RATINGS_PATH,
    "Approach": OP_RATINGS_PATH,
    "Innovation": OP_RATINGS_PATH,
    "Significance": FQ_RATINGS_PATH,

}
'''

rating_to_attr = {
    "Bands": "Overall Score",
    "Box_Background_Color": "Relevance and Significance",
    "Width": "Novelty",
    "Dash": "Technical Quality",
    "Outline" : "Experimental Evaluation"
}

def main():
    instance = GUI(args.ranking_path, args.rating_path, rating_to_attr, args.num)
    instance.show()

if __name__ == "__main__":
    main()