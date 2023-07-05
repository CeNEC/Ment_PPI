

class task:
	
	t1 = 1
	fieldmap = 1
	scan = 1
	shortname = ""
	logfile = 1
	
	def __init__(self,name):
		self.name = name

class subject:
	
	observation = task("observation")
	observation.shortname = "OBS"

	imitation = task("imitation")
	imitation.shortname = "IMI"

	execution = task("execution")
	execution.shortname = "EXC"

	mentalizing = task("mentalizing")
	mentalizing.shortname = "MENT"

	resting = task("resting")

	def __init__(self,code):
		self.code = code

	def get_scanfile(self,task):

		if task == "observation":
			taskname = "%s-Observation_Task_MB_1.nii.gz" % self.observation.scan
		elif task == "imitation":
			taskname = "%s-Imitation_Task_MB_2.nii.gz" % self.imitation.scan
		elif task == "execution":
			taskname = "%s-Func_Execution_Task_MB.nii.gz" % self.execution.scan
		elif task == "mentalizing":
			taskname = "%s-Mentalizing_Task_MB_3.nii.gz" % self.mentalizing.scan
		elif task == "resting":
			taskname = "%s-Resting_State_MB.nii.gz" % self.resting.scan

		return taskname

	# def get_scanfile_new(self,task):

	# 	if task == "observation":
	# 		taskname = "%s-Observation_Task_MB_1.nii.gz" % self.observation.scan
	# 	elif task == "imitation":
	# 		taskname = "%s-Imitation_Task_MB_2.nii.gz" % self.imitation.scan
	# 	elif task == "execution":
	# 		taskname = "%s-Func_Execution_Task_MB.nii.gz" % self.execution.scan
	# 	elif task == "mentalizing":
	# 		taskname = "%s-Mentalizing_Task_MB_3.nii.gz" % self.mentalizing.scan
	# 	elif task == "resting":
	# 		taskname = "%s-Resting_State_7min.nii.gz" % self.resting.scan

	# 	return taskname

	def get_t1file(self,task):

		if task == "observation":
			t1name = "%s-t1_mprage_short_brain.nii.gz" % self.observation.t1
		elif task == "imitation":
			t1name = "%s-t1_mprage_short_brain.nii.gz" % self.imitation.t1
		elif task == "execution":
			t1name = "%s-t1_mprage_short_brain.nii.gz" % self.execution.t1
		elif task == "mentalizing":
			t1name = "%s-t1_mprage_short_brain.nii.gz" % self.mentalizing.t1
		elif task == "resting":
			t1name = "%s-t1_mprage_short_brain.nii.gz" % self.resting.t1
		
		return t1name
