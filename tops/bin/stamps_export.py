# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 16:38:04 2020

@author: Sonam
"""

import os
import sys
from pathlib import Path
import glob
import subprocess
# import shlex
import time
# from pprint import pprint 
inputfile = sys.argv[1]
#inputfile = 'asc_2017_multi.conf'
#inputfile = 'asc_2017_2019_multi.conf'
#inputfile = 'des_2017_multi_ms_snap.conf'

bar_message='\n###########################################################\n'
with open(inputfile) as file:
    for line in file.readlines():
        # print(line)
        if "PROJECTFOLDER" in line:
            PROJECT = line.split('=')[1].strip()
            print(type(PROJECT), PROJECT)
        if "IW" in line:
             IW = line.split('=')[1].strip(', ').rstrip()
             IW_list = IW.split(',')
             IW_str = ''.join(IW_list)
        if "POLARISATION" in line:
            POLARISATION = line.split('=')[1].strip()
            print(POLARISATION)
        if "GRAPHSFOLDER" in line:
            GRAPH = line.split('=')[1].strip()
            print(type(GRAPH), GRAPH)
        if "BottomBurstIndex" in line:
            BottomBurstIndex = line.split('=')[1].strip()
            print('BottomBurstIndex: {}'.format(BottomBurstIndex))
        if "TopBurstIndex" in line:
            TopBurstIndex = line.split('=')[1].strip()
            print('TopBurstIndex: {}'.format(TopBurstIndex))
        if "GPTBIN_PATH" in line:
            GPT = line.split('=')[1].strip()
            print(type(GPT), GPT)
        if "CPU" in line:
            CPU = line.split('=')[1].strip()
            # print(type(CPU), CPU)
        if "CACHE" in line:
            CACHE = line.split('=')[1].strip()
#############################################################################
##### StaMPS PSI export ##################
#############################################################################
def get_time():
    t = time.localtime()
    return 'Current Time: {}\n'.format(time.strftime("%H:%M:%S", t))

coregfolder = os.path.join(PROJECT, 'coreg')
ifgfolder = os.path.join(PROJECT, 'ifg')

for files in os.listdir(os.path.join(PROJECT, 'master')):
    outputexportfolder = os.path.join(PROJECT, 'INSAR_' + files)
    if not os.path.exists(outputexportfolder):
        os.makedirs(outputexportfolder)

logfolder = os.path.join(PROJECT, 'logs')
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
outlog = os.path.join(logfolder, 'export_proc_stdout.log')
out_file = open(outlog, 'a')
err_file = out_file
graphxml = os.path.join(GRAPH, 'export.xml')
graph2run = os.path.join(GRAPH, 'export2run.xml')
print(bar_message)
out_file.write(bar_message)
message = '## StaMPS PSI export started:\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)
k = 0
if len(IW_list)==1:
    total_file = len([file for file in os.listdir(coregfolder) if file.endswith('.dim')])
    print('Total File : {}\n'.format(total_file))
else:
    total_file = len([file for file in os.listdir(coregfolder) if file.endswith('.dim')])
    print('Total File : {}\n'.format(total_file))     

for dimfile in glob.iglob(coregfolder + './**/*.dim', recursive = True):
    head, tail = os.path.split(os.path.join(coregfolder, dimfile))
    k = k+1
    message = '[{}¦{}] Exporting pair: master-slave pair {}\n'.format(k, total_file, tail)
    ifgdim = Path(os.path.join(ifgfolder, tail))
    # print(type(ifgdim))
    if ifgdim.is_file():
        print(message)
        out_file.write(message)
        with open(graphxml, 'r') as file:
            filedata = file.read()
            # print(filedata)
            # Replace the target string
            filedata = filedata.replace('COREGFILE', dimfile)
            filedata = filedata.replace('IFGFILE', str(ifgdim))
            filedata = filedata.replace('OUTPUTFOLDER', outputexportfolder)
            # pprint(filedata)
            # Write the file out again
        with open(graph2run, 'w') as file:
            file.write(filedata)
        args = [GPT, graph2run, '-c', CACHE, '-q', CPU]
        print(args)
        # Launching process
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        print('Process started ^__^: {}\n'.format(get_time()))
        timeStarted = time.time()
        stdout = process.communicate()[0]
        print(get_time())
        print('SNAP STDOUT:{}'.format(stdout))
        timeDelta = time.time() - timeStarted  # Get execution time.
        # print('['+str(k)+'] Finished process in '+str(timeDelta)+' seconds.')
        print('[{}¦{}] Finished process in {} seconds\n'.format(k, total_file, timeDelta))
        out_file.write('[{}¦{}] Finished process in {} seconds\n'.format(k, total_file, timeDelta))
        if process.returncode != 0:
            message = 'Error exporting '+ str(tail)+'\n'
            err_file.write(message)
        else:
            message = 'Stamps export of '+ str(tail) + ' successfully completed.\n'
            print(message)
            out_file.write(message)
        print(bar_message)
        out_file.write(bar_message)
out_file.close()
err_file.close()
