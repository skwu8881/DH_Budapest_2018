import subprocess
import time
import os, sys
from datetime import datetime

def main():
	flag = 1
	while True:
		sys.stdout.write('[JOB#%03d] -> '%(flag))

		ret = subprocess.call(('python',sys.path[0]+'/crawl.py'))
		
		if int(ret) != 0:
			sys.stdout.write('<error occurs!!>\n---------\n')
			
		flag += 1


if __name__=="__main__":
	main()