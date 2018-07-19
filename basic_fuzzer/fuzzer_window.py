#!/usr/bin/python

import random
import time
import threading
import os
import utils
import shutil
import glob
import struct
import md5
from time import localtime, strftime
from pydbg.defines import *
from pydbg import *

INPUT_DIR = r"./inputs/"
TESTCASE_DIR = r"./testcases/"
CRASHED_DIR = r"./crash/"
MUTATE_COUNT = 10

running = False
in_handler = False
dbg = None
pid = None

def mutator():
	r = random.choice(glob.glob(INPUT_DIR + "*"))
	if r == "":
		return None

	ext = os.path.splitext(r)[1]	
	with open(r, "r") as fh:
		data = list(fh.read())

	#mutated
	try:
		for i in range(MUTATE_COUNT):
			offset = random.randint(0, len(data)-1)
			data[offset] = chr(random.randint(0,255))
		data = "".join(data)
	except:
		return r

	outfile = TESTCASE_DIR + "testcase" + ext
	with open(outfile, "w") as fh:
		fh.write(data)

	return outfile

def Timeout():
	global running, dbg, pid, in_handler

	time_cnt = 0

	while time_cnt < 3 or pid != None:
		time.sleep(1)
		time_cnt+= 1

	if in_handler != True:
		try:
			dbg.terminate_process()
		except:
			pass
		running = False
	else:
		while running:
			time.sleep(1)

def Run2Monitor(fileName):
	global running,dbg,pid
	dbg = pydbg()
	running = True

	dbg.set_callback(EXCEPTION_ACCESS_VIOLATION, checkav)
	dbg.set_callback(0xC000001D, checkav)
	pid = dbg.load(r"C:\Program Files (x86)\Hantools\HanSee\HanSee.exe",fileName)
	dbg.run()

def checkav(dbg):
	global in_handler, running,mutated_file
	in_handler = True
	print "[+] Crash!!!!"
	crash_log_file = "crashlog"+strftime("%Y%m%d%H%M%S", localtime())
	ext = os.path.splitext(mutated_file)[1]
	crash_bin = utils.crash_binning.crash_binning()
	crash_bin.record_crash(dbg)
	try:		
		shutil.copy(mutated_file, CRASHED_DIR + crash_log_file + ext)
		with open(CRASHED_DIR + crash_log_file + ".txt", "w") as fh:
			fh.write(crash_bin.crash_synopsis())
	except:
		pass

	dbg.terminate_process()
	in_handler = False
	running = False
	return DBG_EXCEPTION_NOT_HANDLED

if __name__ == '__main__':
	global mutated_file
	if os.path.exists(INPUT_DIR) == False:
		os.mkdir(INPUT_DIR)
	if os.path.exists(TESTCASE_DIR) == False:
		os.mkdir(TESTCASE_DIR)
	if os.path.exists(CRASHED_DIR) == False:
		os.mkdir(CRASHED_DIR)

	while True:
		mutated_file = os.getcwd() + mutator()

		run_thread = threading.Thread(target=Run2Monitor,args=[mutated_file])
		run_thread.setDaemon(0)
		run_thread.start()

		timeout_thread = threading.Thread(target=Timeout)
		timeout_thread.setDaemon(0)
		timeout_thread.start()

		run_thread.join()
		timeout_thread.join()

