# Rankings-UI

This is a ranking UI that can visualize a CSV file that contains the reviews and rankings from multiple reviewers to multiple proposals.

Run the main.py file and then type in the CSV file name without any punctuation.(give an example here)

NOTE for Mac users. On my Mac book Pro, no combination works for "right clicking" on a reviewed item. I connect a _classic mouse_ and use the _middle button_. 

TO DO's

* edit the input csv file, and make sure that OP is consistent with the rankings. (i.e. if OP(Chipotle) > OP( Xi'an) then Chipotle is higher ranked than Xi'an. (DONE?)
* now we want the rankings to look less like a table, so control the box width to leave some space between columns.
* also, add a "short name" field to Proposal, which should appear in the box. Currently the boxes are sized by the text size; they should have a size determined by Ranking, which in turn will get it from the higher level function such as main(), and the text should be trimmed to fit in.
* and now plot the proposals with x values slightly perturbed, so they don't appear exactly aligned. at the moment this doesn't mean anything, but we will want to allow for left-right movement of the boxes. 
* the rating bands must show (on the left) the rating value. How about a large, semitransparent digit (e.g. 5, 4, ..) left of the rankings?
* it will be nicer to have the bands not by separating them with lines, but as bands with different shades of gray (you can just alternate two shades, as long as on the left one can see the rating value. 


