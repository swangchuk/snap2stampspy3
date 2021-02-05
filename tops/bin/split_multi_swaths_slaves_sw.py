# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 13:14:24 2020

@author: Sonam
"""

import os
import glob, sys
import subprocess
import shutil
import time
inputfile = sys.argv[1]
#inputfile = 'asc_2017_multi.conf'
#inputfile = 'asc_2017_multi_v0.conf'
#inputfile = 'asc_2017_2019_multi.conf'
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
            print(type(IW_list), IW_list)
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
            # print(type(CACHE), CACHE)
            
#############################################################################
### TOPSAR Splitting (Assembling) and Apply Orbit section ####
#############################################################################
            
slavefolder = os.path.join(PROJECT, 'slaves')
for filename in os.listdir(slavefolder):
    if filename.endswith(".zip") : 
       print(os.path.join(slavefolder, filename))
       head, tail = os.path.split(os.path.join(slavefolder, filename))
       print (tail[17:25])
       subdirectory = os.path.join(slavefolder, tail[17:25])
       if not os.path.exists(subdirectory):
           os.makedirs(subdirectory)
       #### Moving files
       source = os.path.join(slavefolder, filename)
       destination=os.path.join(subdirectory, tail)
       print('Moving {} to {}'.format(source, destination))
       shutil.move(source, destination)

splitfolder = os.path.join(PROJECT, 'split_slave')
logfolder = os.path.join(PROJECT, 'logs')
if not os.path.exists(splitfolder):
    os.makedirs(splitfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
graph2run = os.path.join(GRAPH, 'splitgraph2run_slave_ms.xml')
outlog = os.path.join(logfolder, 'split_proc_stdout.log')
out_file = open(outlog, 'a')
err_file = out_file
print(bar_message)
out_file.write(bar_message)
message = '## TOPSAR Splitting and Apply Orbit\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)

if len(IW_list)==1:
    total_file = len([file for file in os.listdir(slavefolder)])
    print('Total File : {}\n'.format(total_file))
else:
    total_file = len([file for file in os.listdir(slavefolder)])*len(IW_list)
    print('Total File : {}\n'.format(total_file))

    
#class ComputeMultiSwaths():
#    @staticmethod
def split_swaths_bursts():
    k = 0
    for files in glob.iglob(slavefolder + './**/*.zip', recursive = True):
        print(files)
        for iw in IW_list:
             k = k+1
             print('[{}¦{}] Folder: {}\n'.format(k, total_file, files))
             out_file.write('[{}] Folder: {}\n'.format(k, files))
             out_file.write(str(os.path.join(slavefolder, files)) + '\n')
             # files = glob.glob(os.path.join(slavefolder, acdatefolder) + '/*.zip')
             out_file.write(str(files) + '\n')
             head, tail = os.path.split(files)
             split_tail = tail.split('_')[-4][0:8]
             splitslavefolder = os.path.join(splitfolder, split_tail)
             print('splitslavefolder', splitslavefolder)
             outputname = split_tail + '_' + iw  + '.dim'
             print('out', outputname)
             
             graphxml = os.path.join(GRAPH, 'slave_split_applyorbit.xml')
             # Read in the file
             with open(graphxml, 'r') as file:
                filedata = file.read()
                # Replace the target string
                filedata = filedata.replace('INPUTFILE', files)
                filedata = filedata.replace('IWs', iw)
                filedata = filedata.replace('BottomBurstIndex', BottomBurstIndex)
                filedata = filedata.replace('TopBurstIndex', TopBurstIndex)
                filedata = filedata.replace('POLARISATION', POLARISATION)
                filedata = filedata.replace('OUTPUTFILE', os.path.join(splitslavefolder,
                                                             outputname))
             with open(graph2run, 'w') as file:
                 file.write(filedata)
             
             args = [GPT, graph2run, '-c', CACHE, '-q', CPU]
             print(args)
             out_file.write(str(args)+'\n')
             # launching the process --------------------------------------------------
             process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
             timeStarted = time.time()
             stdout = process.communicate()[0]
             print('SNAP STDOUT:{}'.format(stdout))
             timeDelta = time.time() - timeStarted # Get execution time
             print('{}¦{} Finished process in {} seconds\n'.format(k, total_file, timeDelta))
             out_file.write('{}¦{} Finished process in {} seconds\n'.format(k, total_file, timeDelta))
             if process.returncode != 0:
                 message = 'Error splitting slave '+str(files)
                 err_file.write(message)
             else:
                 message = 'Split slave' + str(files) + 'successfully completed.\n'
             print(message)
             out_file.write(message)
             print(bar_message)
             out_file.write(bar_message)
             
split_swaths_bursts()
            
