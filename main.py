from Ranking import Ranking
from GUI import GUI
from Review import Review


def main():
    #review_text = "This proposal is awesome."
    #example_review = Review(review=review_text)
    ranking_path = input("Please Enter The Name of the Ranking File: ")
    rankings = Ranking(ranking_path)
    instance = GUI(rankings)
    #instance.createWindow()
    instance.show()

if __name__ == "__main__":
    main()