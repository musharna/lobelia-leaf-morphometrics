# GinJinn2 workflow

_Verbatim from the original project notes, except where marked removed._

```
Ginjinn workflow

---Leucanthemum example---

wget download_link
unzip path

(if neccesary) flatten
get rid of main-vein using utils

ginjinn utils filter_cat \
	-a leucanthemum/annotations.json \
	-o leucanthemum_filtered \
	-f leaf

##note leaf here is keeping jsut leaf
##split into train validation and test 

ginjinn split -I leucanthemum_filtered -o leucanthemum_filtered_split -d instance-segmentation -t 0.2 -v 0.2

##sliding window splitting

ginjinn utils sw_split -I leucanthemum_split -o leucanthemum_split_sw -s 2048 -p 512 --remove_incomplete

###crop bounding boxes and start segmentation model

ginjinn utils crop -I leucanthemum_split -o leucanthemum_split_cropped -p 25 -t segmentation

ginjinn new leucanthemum_seg -t mask_rcnn_R_101_FPN_3x.yaml -d leucanthemum_split_cropped

##edit project config (if needed)
##train segmentation model

ginjinn train leucanthemum_seg

##evaluate

ginjinn evaluate leucanthemum_seg

##copy test images to predict on

cp -r leucanthemum_split/test/images new_images


##split into sliding windows

ginjinn utils sw_split -i new_images -o new_date_sw -s 2048 -p 512

##predict BB

ginjinn predict leucanthemum_bbox -i new_data_sw -o new_data_sw_pred -v

##merge duplicated sw predictions

ginjinn utils sw_merge -a new_data_sw_pred/annotation.json -i new_data_sw -o new_data_sw_pred_merged -t bbox-detection

##crop bounding boxes from reconstucted original images with padding

ginjinn utils crop -I new_data_sw_pred_merged -o new_data_sw_pred_merged/images_cropped -t bbox -p 25

##use cropped bboxes as input for seg mmodel

ginjinn predict leucanthemum_seg -i new_data_sw_pred_merged/images_cropped -o new_data_seg_pred -v -c -r

##not working???
```
