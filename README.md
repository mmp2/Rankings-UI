# rankingTool

This is a ranking UI that can visualize a series of ratings and rankings from multiple reviewers to multiple proposals. 

How to run it
======
Before download the package, please make sure you have installed all dependencies, e.g., toml, pandas, tkinter.

Download the package:
```
pip install git+https://github.com/lexilxu/Rankings-UI
```
-----
To initialize the GUI, the user needs a configuration file. 
An example of the configuration file is provided in config_rest.toml.
After installation and preparation of the configuration file, the GUI can be opened by running the \texttt{main.py} file with the following codes:
```
instance = GUI(``config_rest.toml'')
instance.show()
```

Tasks
======
* Fix the problem with AStar
* Better example to check the results.
* Pop the load data window up again? Now it is one-time upload.
* A bug with filtering --- cannot switch back to all items.
* Proposal details?
* Add a default directory in the configuration file.


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

Contributors (in alphabetical order)
====================================
* Lexi Liu rankings-UI V2 (visual display of consensus)
* Murray Haoqian Kang **original repository creator**, wrote rankings-UI V1 code (visual display of reviewing results) 
* Marina Meila Professor, UW, concept, scientific advisor

  Acknowledgements
  ================
  This project is funded by NSF award 2019901 _Improving Panel Decision Making: Understanding Methods for Aggregating Reviewer Opinions_
