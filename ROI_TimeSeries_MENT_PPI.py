#!/usr/bin/env python


import os,sys
import argparse
import numpy as np
import re
from datetime import datetime
from subprocess import call
from subprocess import check_output
import csv
import shutil



# parser = argparse.ArgumentParser()

# # parser.add_argument("--subjects",help="process listed subjects",nargs='+',action="store")
# parser.add_argument('-n','--network',help="Specificy which network to look at (dmn or aon).")
# args = parser.parse_args()

#set locations
datafolder = '/Volumes/AZLab/AON_tasks/fmri_data/'
# if not os.path.exists(datafolder):
# 	datafolder = '/Volumes/AZLab/AON_tasks/fmri_data/'
# if not os.path.exists(datafolder):
# 	datafolder = '/Volumes/AZLab/AON_tasks/fmri_data/'
# ROImask = "/Volumes/AZLab/AON_tasks/Analysis/ROI/functional_peaks/CB_RestingState_GroupSheres/RightInsula_37_12_-4_bin.nii.gz"
stand_image = "/usr/local/fsl/data/standard/MNI152_T1_2mm_brain" 

# Paths for different folders of masks/seeds depending on arguemnt given (aon or dmn) 
# if args.network: 
# 	network = args.network
	# if network == "aon":
seedir = '/Volumes/AZLab/AON_tasks/Analysis/' + "ROI/Mentalizing_Analysis/"
# 		seedlist = [elem for elem in os.listdir(seedir) if "_bin.nii.gz" in elem]
# 	elif network == "dmn":
# 		seedir = datafolder + "ROIs/%s_rois_fox" %(network)
seedlist = ['fwhy-how_dorsomedial_pfc.nii.gz']


#logging colors
sectionColor = "\033[94m"
sectionColor2 = "\033[96m"
groupColor = "\033[90m"
mainColor = "\033[92m"
pink = '\033[95m'
yellow = '\033[93m'
red = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


#subject list 
subjectList = [
# 'LA001_TD',
'LA002_TD',
'LA003_TD',
'LA005_TD',
'LA006_TD',
'LA019_TD',
'LA021_TD',
'LA022_TD',
# 'LA023_TD',
'LA024_TD',
'LA036_TD',
'LA038_TD',
'LA043_TD',
'LA046_TD',
# 'LA048_TD',
# 'LA051_TD',
'LA054_TD',
'LA055_TD',
'LA057_TD',
# 'LA059_TD',
'LA075_TD',
'LA076_TD',
'LA077_TD',
'LA079_TD',
'LA096_TD',
'LA100_TD',
'LA102_TD',
'LA109_TD',
'LA116_TD',
'LA120_TD',
'LA121_TD',
'LA124_TD',
'LA125_TD',
'LA126_TD',
'LA129_TD',
# 'LA004_ASD',
'LA008_ASD',
'LA009_ASD',
'LA016_ASD',
'LA018_ASD',
'LA026_ASD',
'LA027_ASD',
# 'LA029_ASD',
'LA033_ASD',
'LA037_ASD',
'LA039_ASD',
'LA041_ASD',
'LA049_ASD',
'LA056_ASD',
'LA061_ASD',
'LA064_ASD',
'LA065_ASD',
'LA068_ASD',
'LA069_ASD',
'LA070_ASD',
'LA071_ASD',
'LA072_ASD',
'LA081_ASD',
'LA084_ASD',
'LA088_ASD',
'LA091_ASD',
# 'LA099_ASD',
'LA106_ASD',
'LA117_ASD',
'LA118_ASD',
'LA101_ASD',
'LA104_ASD',
'LA032_DCD',
'LA035_DCD',
'LA044_DCD',
'LA045_DCD',
'LA047_DCD',
'LA050_DCD',
'LA053_DCD',
'LA062_DCD',
'LA063_DCD',
'LA073_DCD',
# 'LA078_DCD',
# 'LA089_DCD',
'LA092_DCD',
'LA093_DCD',
'LA094_DCD',
'LA095_DCD',
'LA097_DCD',
'LA098_DCD',
'LA105_DCD',
'LA122_DCD',
'LA123_DCD',
'LA128_DCD',
'LA132_DCD',
]

for subj in subjectList:
	subject = subj

	subjfolder = datafolder + subject + '/'

	regdir = subjfolder + "mentalizing/mentalizing_task.feat/reg"
	tffile = subjfolder + "mentalizing/mentalizing_task.feat/filtered_func_data.nii.gz"
	preprocess_featfolder = "/Volumes/AZLab/AON_tasks/fmri_data/%s/mentalizing/mentalizing_pre.feat" %(subject)

#----------------------------------------

# Regress out confounds (do not include scrubbing file): 

#----------------------------------------


	print sectionColor + "Extracting seed timeseries ---------------------------" + mainColor

	#Create new directory 
	#subjectseedir = subjfolder + "aon_seeds_hoa"
	# if network == 'aon':
	# 	subjectseedir = subjfolder + "/observation/aon_seeds_peaks"
	# elif network == 'dmn':
	subjectseedir = subjfolder + "mentalizing/ROI/"
		
	if not os.path.exists(subjectseedir):
		os.makedirs(subjectseedir)

	for s in seedlist:
		seed = s[:-7]
		seedout = subjectseedir + '/%s.nii.gz' %(seed)
		seedimage = subjectseedir + '/%s.png' %(seed)
		seedpath = seedir + "/" + s
		print seedpath,seedout

		if not os.path.exists(seedout):

			print sectionColor2	+ "Warping and extracting time series from %s for %s%s" %(seed,subject,mainColor)
			print sectionColor2 + "flirt -in %s -ref %s/example_func.nii.gz -applyxfm -init %s/standard2example_func.mat -o %s %s" % (seedpath,regdir,regdir,seedout,mainColor)
			command = "flirt -in %s -ref %s/example_func.nii.gz -applyxfm -init %s/standard2example_func.mat -o %s" % (seedpath,regdir,regdir,seedout)
			call(command, shell=True)
			print sectionColor2 + "fslmeants %s" %(mainColor)
			command = "fslmeants -i %s -m %s -o %s/%s_ts.txt" % (tffile,seedout,subjectseedir,seed)
			call(command, shell=True)
			command = "slicer %s/example_func.nii.gz %s/%s -z .7 %s/%s.png" % (preprocess_featfolder,subjectseedir,seed,subjectseedir,seed)
			call(command, shell=True)

		else: 
			print yellow + "Already completed seed extraction for %s. Moving on\n%s"  % (subject,mainColor) 

		# writeToLog("<h2>Masks</h2><br>SMA:<br><img src=sma.png><br><br>PreSMA:<br><img src=presma.png><br><br>LP:<br><img src=lp.png><br><br><hr>",reportfile)

