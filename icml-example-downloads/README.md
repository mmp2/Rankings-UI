ReviewRatings.txt
-----------------
Meta-reviewer evaluates each review.
tab separated

ReviewerSubmissionComparison.txt
---------------------------------
This is the rankings file. Tab separated
reviewer enters as many comparisons as they want about the papers assigned to them.
comparisons must agree with overall score.

Comparable means =
paperA PreferredTo paperB means A better than B.

paperA, paperB are paper id's, i.e. natural numbers.

For ICML, all comparison information should be displayed, not just top-t. 

Reviews.xls
------------
Excel file with all reviews for the selected papers. Ordered by paper id. 
Q1, Q2, Q9 are free text (the review summary and the full review, questions for authors).
The other Q's are multiple choice; the choices can be found in the review form.
I have deleted some fields and did not fill them with dummy data (e.g. reviewer names and emails). 

ReviewsSnapshot.xls
--------------------
Currently, this file is identical to Reviews.xls.

In ICML, a reviewer does not see all the papers. So, the conference chair can see all the reviews, but everyone else sees only a subset captured on ReviewsSnapshot. For our purposes, currently, both can be used as input files in the same way. Later, we may add a few more fields to Reviews.xls.
 

What reviewer questions Q1-15 to display
-----------------------------------------
* in the **UI**, these numerical values
    * 3 significance
    *  4 novelty
    *   5 technical
    *   6 experiments
    *   7 clarity
    *   8 reproducibility
    *   11 confidence
    *   **10 Overall is the Merit rating**

* in **Review Details**
    * 1 Summary
    * 2 Details
    * 9 Questions for Authors

* also in Review details
   * 13, 14, 15
