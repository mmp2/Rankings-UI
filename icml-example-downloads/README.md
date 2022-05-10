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
PreferredTo means better

I don't know what the X means in this file. Normally there should be paper id's, i.e. natural numbers.

Reviews.xls
------------
Excel file with all reviews for the selected papers. Ordered by paper id. 
Q1, Q2, Q9 are free text (the review summary and the full review, questions for authors).
The other Q's are multiple choice; the choices can be found in the review form.
I have deleted some fields and did not fill them with dummy data (e.g. reviewer names and emails). 

ReviewsSnapshot.xls
--------------------
I saw no difference in this file from Reviews.xls.

In ICML, a reviewer does not see all the papers. So each ranking is over a subset of papers.
Also, a reviewer does not create a total order of the papers, because some papers are not comparable (e.g. different area). So, they can enter any number of comparisons, possibly none.
If Reviewer enters =, means that the papers are comparable and same quality. 
