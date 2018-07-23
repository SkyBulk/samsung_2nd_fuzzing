#!/usr/bin/python

import re
import glob

uniq_crash = {}

def get_log(f):
	p = re.compile("(.*) from thread")
	with open(f, "r") as fh:
		data = fh.read()
	result = p.findall(data)[0]
	count = 0
	if len(uniq_crash) != 0:
		count = uniq_crash[result] + 1
	uniq_crash[result] = count 

if __name__ == '__main__':
	r = glob.glob("./crash/*.txt")

	for file in r:
		get_log(file)

	for k,v in uniq_crash.items():
		print "Crash Point :", k, "::: Count ==>", v