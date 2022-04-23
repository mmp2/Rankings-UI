# Rankings-UI

This is a ranking UI that can visualize a CSV file that contains the reviews and rankings from multiple reviewers to multiple proposals.

Run the main.py file and then type in the CSV file name without any punctuation.(give an example here)

NOTE for Mac users. On my Mac book Pro, no combination works for "right clicking" on a reviewed item. I connect a _classic mouse_ and use the _middle button_. 

TO DO's

* also, add a "short name" field to Proposal, which should appear in the box. Currently the boxes are sized by the text size; they should have a size determined by Ranking, which in turn will get it from the higher level function such as main(), and the text should be trimmed to fit in.
* and now plot the proposals with x values slightly perturbed, so they don't appear exactly aligned. at the moment this doesn't mean anything, but we will want to allow for left-right movement of the boxes. 
* the rating bands must show (on the left) the rating value. How about a large, semitransparent digit (e.g. 5, 4, ..) left of the rankings?
* it will be nicer to have the bands not by separating them with lines, but as bands with different shades of gray (you can just alternate two shades, as long as on the left one can see the rating value. 

Tasks
======
* Displaying reviews on a canvas as boxes, with graphical attributes that depend on the reviews
* Simple GUI 
  -- right click on box, displays menu + info
  -- allows changing order of columns
  -- select a box--> highlight all boxes for the same proposal
* data input scripts (reading review files, reviewer files, proposal info...)
* menus for mapping properties to graph attributes, and legend


Associating rectangle properties to review and proposal attributes
--------------------------------------------------------------------
TBExpanded
tkinter rectangle attributes
* dash
* fill
* outline
* width
* Forget for now about: stipple and offset, all active and disabled state attributes
* tags -- this is a special one, to think how to use it
tkinter text attributes
 * t.b. listed
 Data representation
 ---------------------
 For each application, the user shall create some configuration files (can be done by hand) which specify
 * attributes for class Review (aka review questions)
 * attributes for class Proposal (aka area)
 * range of values/list of values for these attributes -- as numerical values 0:k_j (for property j)
 * for each rectangle/text attribute that we use, a dictionary that maps numerical values 0:k to a list of properties acceptable for the attribute
    - e.g. for fill, the numerical values will be mapped to colors
    - for width, they will be mapped to points, etc.
