#!/usr/bin/python

# MASTER ANALYSIS SCRIPT FOR AON fMRI STUDY
# JAN 2018

import sys,os
from subprocess import call, check_output
import argparse
from datetime import datetime
import re
import csv
from subject import task
from subject import subject

starttime = datetime.now()

#This is from an earlier version. We may not use
analysislist = ["generic"]
suffixlist = {"generic" : "" , "generic-bytrial" : "_bytrial"}

#Here define which tasks you want to analyze
#tasklist = ["observation","execution","imitation","mentalizing"]
tasklist = ["mentalizing"]
# tasklist = ["observation","execution","mentalizing"]
ROI_folder="n81_Conjunction_ROI"

#command line options
parser = argparse.ArgumentParser()

parser.add_argument("--subjects",help="process listed subjects",nargs='+',action="store")
parser.add_argument("--all",help="process all subjects", action="store_true")
parser.add_argument("--nopre",help="skip all preprocessing steps", action="store_true")
parser.add_argument("--onlydcm",help="only do dicom conversion", action="store_true")
parser.add_argument("--nodcm",help="skip dicom conversion", action="store_true")
parser.add_argument("--nocheckfiles",help="skip dicom conversion", action="store_true")
parser.add_argument("--nofieldmap",help="skip fieldmap prep", action="store_true")
parser.add_argument("--noskullstrip",help="skip skullstripping", action="store_true")
parser.add_argument("--nologfiles",help="skip logfile processing", action="store_true")
parser.add_argument("--noinitialpre",help="skip initial preprocessing feat", action="store_true")
parser.add_argument("--noaroma",help="skip ICA AROMA", action="store_true")
parser.add_argument("--nofeat",help="skip feat analysis", action="store_true")
parser.add_argument("--noreg",help="skip registration copying", action="store_true")
parser.add_argument("--ROI",help="roi for phys",nargs='+',action="store")
parser.add_argument("--onlyfeat",help="only do feat", action="store_true")
args = parser.parse_args()


ROI = args.ROI
#set paths
pathbase = "/Volumes/AZLab/AON_tasks/"
designpath = "/Volumes/AZLab/AON_tasks/fmri_data/Design_Files"
datapath = pathbase + "fmri_data"	
logfilename = pathbase + "/logs/analysis_log.txt"
ROI_path = pathbase + "mentalizing/n81_Conjunction_ROI/%s"%(ROI)

#develop list of subjects

subjects = args.subjects

if args.onlydcm:
	args.noskullstrip = True
	args.nofieldmap = True
	args.nologfiles = True
	args.noaroma = True
	args.nofeat = True
	args.noinitialpre = True

if args.onlyfeat:
	args.noskullstrip = True
	args.nofieldmap = True
	args.nologfiles = True
	args.noaroma = True
	args.noinitialpre = True
	args.nopre = True
	args.nodcm = True
	args.noreg = True


if args.all:
	#Get list of subjects
	subjects = os.listdir(datapath)
	subjects = [elem for elem in subjects if elem.startswith("LA")]
	subjects.sort()

	#check if they've been done already
	candidate_subjects = subjects
	subjects = []

	firstdesign = analysislist[-1]
	suffix = suffixlist[firstdesign]

	for candidate in candidate_subjects:
		testfolder1 = "%s/%s/mentalizing/mentalizing%s.feat" % (datapath,candidate,suffix)	
		if not os.path.exists(testfolder1):
			subjects.append(candidate)

if subjects:
	print subjects
else:
	print "Subjects must be specified. Use --all for all subjects or --subjects to list specific subjects."
	sys.exit()

if ROI:
	print ROI
else:
	print "ROI must be specified. Use --ROI NAME  to use ROI."
	sys.exit()

def getmetadata(subjectnum):
	#This function reads the Excel file to get all the information for each subject
	metafile = "/Volumes/AZLab/AON_tasks/metadata/Fieldmaps_Master_Key.csv"

	this_subj = subject(subjectnum)

	with open(metafile,'rbU') as csvfile:
		metareader = csv.reader(csvfile)
		for row in metareader:
			if row[0]==subjectnum:
				this_subj.resting.scan = row[4]
				this_subj.resting.t1 = row[5]
				this_subj.resting.fieldmap = row[6]

				this_subj.observation.scan = row[7]
				this_subj.observation.t1 = row[8]
				this_subj.observation.fieldmap = row[9]
				this_subj.observation.logfile = row[10]

				this_subj.execution.scan = row[11]
				this_subj.execution.t1 = row[12]
				this_subj.execution.fieldmap = row[13]
				this_subj.execution.logfile = row[14]

				this_subj.imitation.scan = row[15]
				this_subj.imitation.t1 = row[16]
				this_subj.imitation.fieldmap = row[17]
				this_subj.imitation.logfile = row[18]

				this_subj.mentalizing.scan = row[19]
				this_subj.mentalizing.t1 = row[20]
				this_subj.mentalizing.fieldmap = row[21]
				this_subj.mentalizing.logfile = row[22]

	return this_subj


#function to check for success of feat analysis
def checkfeat(featfolder):
	#This checks to see if analysis has completed
	testfile = featfolder + "/filtered_func_data.nii.gz" 
	print "testfile: %s" % testfile
	if not os.path.exists(testfile):
		print "WARNING: ANALYSIS DID NOT COMPLETE FOR %s" % (featfolder)
		logfile.write("%s: WARNING: ANALYSIS DID NOT COMPLETE FOR %s\n" % (datetime.now().strftime('%I:%M:%S%p'),featfolder))

def dopreprocess(task):

	outputfolder = "%s/%s/%s" % (datapath,this_subject,task)
	if not os.path.exists(outputfolder):
		os.mkdir(outputfolder)

	#Run the initial preprocessing steps
	print "Running preprocess for %s" % task
	genericfile = pathbase + "Design_Files/PPI_all_conditions_n81.fsf"

	outputfile = "%s/%s/%s/%s_%s_pre.fsf" % (datapath,this_subject,task,this_subject,task)
	print "inputfile: %s" % genericfile
	print "outputfile: %s" % outputfile

	subj = getmetadata(this_subject)
	this_task = getattr(subj,task)

	inputdata = "/Volumes/AZLab/AON_tasks/fmri_data/%s/NIFTI/%s" % (this_subject,subj.get_scanfile(task))
	numvolumes = checkImageLength(inputdata)

	command = "sed -e 's/DEFINESUBJECT/%s/g' -e 's/DEFINETASK/%s/g' -e 's/DEFINEINPUT/%s/g' -e 's/DEFINEANATOMICAL/%s/g' -e 's/DEFINEFIELDMAP/%s/g' -e 's/DEFINEVOLUMES/%s/g' %s > %s" % (this_subject,task,subj.get_scanfile(task),subj.get_t1file(task),this_task.fieldmap,numvolumes,genericfile,outputfile)
	call(command,shell=True)

	command = "feat %s" % outputfile
	print command
	call(command,shell=True)

# 


def dolowerlevels(task):
	for this_ROI in ROI:

		#Run final task analysis
		print "Doing final task analysis feat for %s" %(this_ROI)

		#Run the initial preprocessing steps
		print "Running task analysis for %s" % task
		genericfile = pathbase + "Design_Files/Corrected_PPI_OBS_AI.fsf"

		outputfile = "%s/%s/%s/%s_%s_%s_PPI_all_conditions.fsf" % (datapath,this_subject,task,this_subject,task,this_ROI)
		print "inputfile: %s" % genericfile
		print "outputfile: %s" % outputfile

		subj = getmetadata(this_subject)
		this_task = getattr(subj,task)


		inputdata = "/Volumes/AZLab/AON_tasks/fmri_data/%s/%s/denoised_func_data_nonaggr.nii.gz" % (this_subject,task)
		numvolumes = checkImageLength(inputdata)

		# command = "sed -e 's/DEFINESUBJECT/%s/g' -e 's/DEFINETASK/%s/g' -e 's/DEFINESHORTNAME/%s/g' -e 's/DEFINELOGFILERUN/%s/g' -e 's/DEFINEVOLUMES/%s/g'  %s > %s" % (this_subject,task,this_task.shortname,this_task.logfile,numvolumes,genericfile,outputfile)
		# call(command,shell=True)

		command = "sed -e 's/DEFINESUBJECT/%s/g' -e 's/DEFINETASK/%s/g' -e 's/DEFINESHORTNAME/%s/g' -e 's/DEFINELOGFILERUN/%s/g' -e 's/DEFINEVOLUMES/%s/g' -e 's/DEFINEROIFOLDER/%s/g' -e 's/DEFINEROI/%s/g' %s > %s" % (this_subject,task,this_task.shortname,this_task.logfile,numvolumes, ROI_folder, this_ROI, genericfile,outputfile)
		call(command,shell=True)

		command = "feat %s" % outputfile
		print command
		call(command,shell=True)

def checkImageLength(imagename):
	#This function checks how many volumes a nifti image has
	command = 'fslinfo %s' % imagename
	results = check_output(command,shell=True)
	TR = results.split()[9]
	return int(TR)


#Loop through each subject in the list
for this_subject in subjects:


	#Let's keep track of what we are doing in a log file
	logfile = open(logfilename,'a')
	logfile.write("\n-----Analysis of subject %s started at %s\n" % (this_subject,starttime.strftime('%b %d %G %I:%M%p')))

	if not args.nopre:

		# #rename export folder to DICOM
		# subjectfolder = "%s/%s"  %(datapath,this_subject)
		# dicomfolder = "%s/%s/raw" % (datapath,this_subject)
		# niftifolder = "%s/%s/NIFTI" % (datapath,this_subject)
		# if not os.path.exists(niftifolder):
		# 	os.mkdir(niftifolder)

		# #DICOM conversion
		# if not args.nodcm:
		# 	command = 'dcm2niix -b n -o %s -f %%s-%%p -z y %s' % (niftifolder,dicomfolder)  
		# 	print command
		# 	call(command,shell=True)
		
		# #Skull stripping
		# if not args.noskullstrip:
		# 	command = '/Volumes/AZLab/Scripts/skullstrip_EK.py %s/%s/NIFTI' % (datapath,this_subject)
		# 	print command
		# 	call(command,shell=True)
		
		# #Preparing the field maps
		# if not args.nofieldmap:	
		# 	command = '/Volumes/AZLab/Scripts/setupfieldmaps_EK.py --folder %s/%s' % (datapath,this_subject)
		# 	call(command,shell=True)

		# #Convert raw MATLAB logfiles to FSL 3-column files
		# if not args.nologfiles:
		# 	command = "/Volumes/AZLab/Scripts/convertlogfiles_EK.py %s" % (this_subject)
		# 	call(command,shell=True)

		#Run initial preprocessing
		if not args.noinitialpre:
			print "Running initial preprocessing"
			for task in tasklist:
				dopreprocess(task)

		# #Run ICA AROMA denoising
		# if not args.noaroma:
		# 	for task in tasklist:
		# 		doaroma(task)

	else:
		print "Skipping preprocessing steps..."

	#Run final feat task analysis
	if not args.nofeat:	
		
		for task in tasklist:
			dolowerlevels(task)

	else:
		print "Skipping feats..."

	#We're done!
	endtime = datetime.now()
	delta = endtime - starttime
	logfile.write("-----Analysis of subject %s finished at %s, duration %s\n" % (subject,endtime.strftime('%b %d %G %I:%M%p'),str(delta)))
	logfile.close()
