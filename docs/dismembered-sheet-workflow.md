# Dismembered-sheet workflow

_Verbatim from the original project notes._

```
Dismembered Sheet workflow
Last updated: 5/2/22

##needs to include .nef change, rotation standardization (by tag? Tag in bottom right, saving??) and workflow optimization for segment/individ line, increased specificity
Preprocessing: Combine the images into an appropriate file structure and ensure all images are rotated the same with no erroneous entries (Images and directories stored on OneDrive)
Note site code and plant id #
Open Image in ImageJ and rotate images to standardize leaf orientation (leaf tip always facing upward)
Note # of total leaves
Measure scale length (standard of 1cm), base to first leaf (look for green or green yellow arrows), base to first flower (magenta arrow), stem thickness at base, stem thickness at first flower
Select leaves which would be appropriate for leaf analysis (Does leaf still look like a leaf? Is it excessively folded?) 
Crop original image into smaller images of only selected leaves (Stored in OneDrive)
Use leaf crops in R and other morphometric programs
In R:
#Load package
library(LeafArea)
#Measure 
run.ij(set.directory = "C:/Users/<user>/Desktop/4",
       distance.pixel = 85, 
       known.distance = 1, 
       trim.pixel = 0)
#General use format:
#set.directory = "C:/ location (USE SHORT PATH)
#distance.pixel = # pixels pr one cm
#known.distance = 1 (cm)
#trim.pixel = 0 (remove 0 px)
```
