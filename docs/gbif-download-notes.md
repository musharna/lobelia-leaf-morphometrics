# GBIF download procedure

_Verbatim from the original project notes._

```
NOTES ON DOWNLOAD PROCESS
Download from gbif with parameters:
Gbif.org parameters:
Basis of record: Preserved specimen
Country or area: Mexico, USA, Canada
Has coordinate: true
Has geospatial issue: false
Media type: StillImage
Scientific name: ~
Extract download & open multimedia in excel through importing data as csv.
Sort gbifID smallest to largest and go down column looking for duplicate entries (reading last three digits) – highlight duplicate entry rows (separate entries with different highlight colors for ease of use) (highlight duplicates with conditional formatting?) 
Remove duplicate gbif entries by looking through entries with same ID and selecting most representative image (delete rows of superfluous entries and note in logs (unpreserved plants generally aren’t recorded as an off-target result)) – do not forget to unhighlight the final image if neccesary
Copy the links to clipboard and import into simplemassdownloader for bulk download. Bulk download in a local directory with naming procedure {counter}.jpg. Some links may be visualized at this point as broken and skipped or deleted later if producing the incorrect result (.html files, etc). Purge any images that are unable to be bulk downloaded and record in logs. Log down deleted entries/highlight problematic download links and move on to download.
After download use the multimedia file to create a simple text file for renaming the image collection. This text file is simply filename1|filename2. Do not forget the extensions (.jpg). Given there were no duplicate gbif entries, no errors should result (if so, fix and retry)
```
