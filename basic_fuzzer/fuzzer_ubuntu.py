#!/usr/bin/python

import glob
import os
import random
import subprocess
import shutil
from threading import Timer
from time import localtime, strftime

INPUT_DIR = r"./inputs/"
TESTCASE_DIR = r"./testcases/"
CRASHED_DIR = r"./crash/"
MUTATE_COUNT = 10

def mutator():
	r = random.choice(glob.glob(INPUT_DIR + "*"))
	if r == "":
		return None

	ext = os.path.splitext(r)[1]	
	with open(r, "r") as fh:
		data = list(fh.read())

	#mutated
	for i in range(MUTATE_COUNT):
		offset = random.randint(0, len(data)-1)
		data[offset] = chr(random.randint(0,255))
	data = "".join(data)

	outfile = TESTCASE_DIR + "testcase" + ".jp2"
	with open(outfile, "w") as fh:
		fh.write(data)

	return outfile

def RunAndMonitor(cmd):
	p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

	kill_proc = lambda x : x.kill()
	timer = Timer(10, kill_proc, [p])

	try:
		timer.start()
		for line in p.stderr.readlines():
			if "AddressSanitizer" in line:
				return [True, p.stderr]
		return [False,None]
	finally:
		timer.cancel()
		return [False,None]


if __name__ == '__main__':
	if os.path.exists(INPUT_DIR) == False:
		os.mkdir(INPUT_DIR)
	if os.path.exists(TESTCASE_DIR) == False:
		os.mkdir(TESTCASE_DIR)
	if os.path.exists(CRASHED_DIR) == False:
		os.mkdir(CRASHED_DIR)

	print "running...."

	while True:
		mutated_file = mutator()
		is_crashed = RunAndMonitor(['/home/samsung/openjpeg-2.3.0/build/bin/opj_dump', "-i", mutated_file])

		if is_crashed[0]:
			print "[+] Got Crashed!!!"
			crash_log_file = "crashlog"+strftime("%Y%m%d%H%M%S", localtime())
			ext = os.path.splitext(mutated_file)[1]
			try:
				shutil.copy(mutated_file, CRASHED_DIR + crashlog + ext)
				with open(CRASHED_DIR + crashlog + ".log", "w") as fh:
					for line in is_crashed[1]:
						fh.write(line)
			except:
				print "???"
				pass

