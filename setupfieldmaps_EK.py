#!/usr/bin/python

import sys,os
from subprocess import call, check_output
import argparse
import re

#command line options
parser = argparse.ArgumentParser()
parser.add_argument("--folder",help="subject folder",action="store")
args = parser.parse_args()

nifti_folder = os.path.join(args.folder,"NIFTI")

#determine which image is which
files = os.listdir(nifti_folder)
files = [elem for elem in files if "SpinEchoFieldMap2.5mm_AP" in elem]

numberlist = []
for apfile in files:
	
	pattern = "(\d+)-.*"
	result = re.match(pattern,apfile)
	sn = int(result.groups()[0])
	numberlist.append(sn)

numberlist.sort()
print numberlist

counter = 1

paramfile = "/Volumes/AZLab/AON_tasks/topup_settings/my_acq_param.txt"

#make output folder if doesn't exist
output_folder = os.path.join(args.folder,"topup_correction")
if not os.path.exists(output_folder):
	os.mkdir(output_folder)

for scannum in numberlist:

	apfile = str(scannum) + "-SpinEchoFieldMap2.5mm_AP.nii.gz"
	pan = scannum + 1
	pafile = str(pan) + "-SpinEchoFieldMap2.5mm_PA.nii.gz"

	if os.path.exists(os.path.join(nifti_folder,pafile)):
		print "\n\nFound pair of fieldmaps %d: %s %s" % (counter,apfile,pafile)

		#make output folder
		this_output_folder = "%s/Fieldmap_%d" % (output_folder,counter)
		if not os.path.exists(this_output_folder):
			os.mkdir(this_output_folder)

		command = "fslmerge -t %s/both_b0 %s %s" % (this_output_folder,os.path.join(nifti_folder,apfile),os.path.join(nifti_folder,pafile))
		print command
		call(command,shell=True)

		command = "topup --imain=%s/both_b0 --datain=%s --config=b02b0.cnf --out=%s/my_topup_results --fout=%s/my_field --iout=%s/my_unwarped_images" % (this_output_folder,paramfile,this_output_folder,this_output_folder,this_output_folder)
		print command
		call(command,shell=True)

		command = "fslroi %s/my_unwarped_images %s/my_fieldmap_mag 0 -1 0 -1 0 -1 0 1" % (this_output_folder,this_output_folder)
		print command
		call(command,shell=True)

		command = "fslmaths %s/my_field -mul 6.28 %s/my_fieldmap_rads" % (this_output_folder,this_output_folder)
		print command
		call(command,shell=True)

		command = "bet2 %s/my_fieldmap_mag %s/my_fieldmap_mag_brain" % (this_output_folder,this_output_folder)
		print command
		call(command,shell=True)

	else:

		print "---------------------WARNING: DID NOT FIND SECOND OF FIELD MAP PAIR: %s" % pafile

	counter = counter + 1