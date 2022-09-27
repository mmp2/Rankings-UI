# Rankings-UI

This is a ranking UI that can visualize a series of ratings and rankings from multiple reviewers to multiple proposals. 

How to run it
======
Before download the package, please make sure you have installed all dependencies, e.g., toml, pandas, tkinter.

Download the package:
```
pip install Rankings_UI
```
-----
Users might need to preprocess different input files into specific format and pass them into the classes of Rankings, Reviews, Reviewers, and Proposals, and then to pass the four classes and a configuration file into the GUI.

Specific Parameter Format for Each Class
------
Rankings(rating_df, ranking, ties, rating_names, reviewer_col_name="Reviewer Name", prop_col_name="Proposal Name", overall_col_name="Overall Score")
  - rating_df: A pandas dataframe without any index that has columns for every rating, reviewer name, proposal name, and overall merit, and each row contains ratings that a given reviewer gave for a given proposal. 
  - ranking: A dictionary that the keys are the reviewer names and the values are the list of proposals in the descending ranking order that the reviewer gave.
  - rating_names: A list of rating names.
  - reviewer_col_name: The column name of the reviewer names that the users gave in the dataframe of rating_df. The default is "Reviewer Name".
  - prop_col_name: The column name of the proposal names that the users gave in the dataframe of rating_df. The default is "Proposal Name".
  - reviewer_col_name: The column name of the overall merit that the users gave in the dataframe of rating_df. The default is "Overall Score".

Reviews(df, review_titles, prop_colname="Proposal Name", reviewer_colname="Reviewer Name", str_wrap_len=35)
  - df: A dataframe without any index that has columns for every review text, proposal names, reviewers names, and numerical ratings (optional), and each row contains review text of the proposal given by the reviewer.
  - review_titles: A list of column names of each review title in the df above.
  - prop_col_name: The column name of the proposal names that the users gave in the dataframe of rating_df. The default is "Proposal Name".
  - reviewer_col_name: The column name of the reviewer names that the users gave in the dataframe of rating_df. The default is "Reviewer Name".
  - str_wrap_len: A int that indicated the length of string wrapped in the window of review text. The default is 35.

Reviewers()

Proposals()

Tasks
======
* Displaying reviews on a canvas as boxes, with graphical attributes that depend on the reviews 
* Simple GUI  
  -- right click on box, displays menu + info
  -- allows changing order of columns
  -- select a box--> highlight all boxes for the same proposal
* data input scripts (reading review files, reviewer files, proposal info...)  (demo version)
* menus for mapping properties to graph attributes, and legend 
* filtering e.g proposals with OM >= 3


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

Notes to add in the user manual
================================
NOTE for Mac users. On my Mac book Pro, no combination works for "right clicking" on a reviewed item. I connect a _classic mouse_ and use the _middle button_. **(Murray: It should be working now, and it works on my MacBook. I used the double finger to touch the touchpad. But the window user should click the scroll of the mouse.)** excellent --> keeping it for user manual

## To run the GUI, simply type below in the terminal
```
python main.py --rating_path xxx --ranking_path xxx --num xxx
```

For example:
```
python main.py --rating_path "dummy_ICML.xls" --ranking_path "ReviewerSubmissionComparisons.txt" --num 15
```
