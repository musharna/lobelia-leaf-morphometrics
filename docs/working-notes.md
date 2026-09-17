# Working notes

_Verbatim from the original project notes, except where marked removed._

```
TO DO:
upload other sheets and finalize master
annotate small sets
create model
decide best model/experiment
CONVERT TXT TO DOCS

ginjinn2 -> detectron 2

possible fields:
family
genus
species name
fertile/non-fertile (presence of reproductive structures)
phenophase
flower absence/presence
flower bud/flowers/immature fruit/mature fruit
leaves-
	presence/absence
	area
	structure/form
	margin
	veination
	arrangement
	# of leaves
	broken leaves? (broken leaf area)

rescaled from
5100 x 3500 to
1200 x 800

cvat
[account name removed]
normalized via rescale to 256x256 no other preprocess

lobelia sect lobelia species:
appendiculata
floridana
flaccidifolia
feayana
homophylla
nuttallii
paludosa
kalmii
inflata
spicata
glandulosa
georgiana
gattingeri
cardinalis
apalachicolensis
anatina
laxiflora (NO)
dortmanna
siphilitica
puberula
canbyi
elongata
rogersii

batsonii
unknown/mixed?

Labeled (training) dataset should have
image directory (jpg images)
annotations json or file (coco or pascal voc)

also need validation dataset and final test dataset
datset is split in three 60:20:20

[credential removed]

used siphilitica2 folder

Tomaszewski et al. - leaf shape changes during drying
(shape analysis either dried or fresh only)

build dataset of quality heterogenous images from above
at least 500 specimens

no same species specimens in both training and testing
(avoid bias- will lower accuracy but more realistic)
(most specimens from our collection will need to be
put in the training and test composed of online
resources (some collectors are on test set))

ImageNet- standard for pre-training (use weights of a
trained model)
Herbarium1k pretraining?

image rights are seperate from occurence rights

filter for only recent entries to ensure quality?

anatina (74 images - ? downloaded)

work on fix inflata - then onto cardinalis
ensure cleanliness of data before cardinalis

make dataaquisitionnotes into excel master file for easier
readablity

2 images out of the 811 for cardinalis failed to upload?
which imageS??
3/723 failed for inflata... kms

inflata fixed via reupload!!

DONT FORGET TO record apalachicolensis

NOTE: cvat.org!! user is mjarnold1999 - not 98
-- cvat.org is limited but option for nonfunctional portions

relevant notes on getting cvat to work:!!!
if on WSL2 must have
-manual httptrigger port
-manual cvat-cvat network
-most up to date nuclio
^^^
https://github.com/openvinotoolkit/cvat/issues/4108

spec:
  ...
  triggers:
    myHttpTrigger:
      maxWorkers: 2
      kind: 'http'
      workerAvailabilityTimeoutMilliseconds: 10000
      attributes:
        port: 32768
        maxRequestBodySize: 33554432 # 32MB

  platform:
    attributes:
      restartPolicy:
        name: always
        maximumRetryCount: 3
      mountMode: volume
      network: cvat_cvat

serverless/deploy_cpu.sh

conda**** activate chungy to do ginjinn

redo inflata siphilitica ?

note: records purged cannot be simply counted by rows and must be counted by replciated removed

Batsonii couldn't be downloaded from gbif??

have to run many as python scripts

can bounding boxes be rotated? do they need annotated beyond the original mask?

tell ginjinnn to update link on example applications

creation of synthetic data, use of filters/flips/monochrom/etc?
pretrain on ginjinn leucanthemum?

remove hash (uncomment) to use augments

whole plant traits- leaf count, plant height

reproductive height or plant height? to highest point???

point of interest model for leaf counts?
many brevifolia leaves tend to fold in half on pressing - may not be helpful to add to model
homophylla very bushy lots of overlap

nuttallii thinnn
```
