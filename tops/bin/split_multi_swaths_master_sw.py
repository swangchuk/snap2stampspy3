# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 13:14:24 2020

@author: Sonam
"""

import os
import glob
import sys
import shutil
import subprocess
import time
inputfile = sys.argv[1]
#inputfile = 'des_2017_multi.conf'
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
        #if "MASTER" in line:
        #    MASTER = line.split('=')[1].strip()
        #    print(type(MASTER), MASTER)
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
############################################################################
            
directory = os.path.join(PROJECT, 'master')
for filename in os.listdir(directory):
    if filename.endswith(".zip") : 
       print(os.path.join(directory, filename))
       head, tail = os.path.split(os.path.join(directory, filename))
       print (tail[17:25])
       subdirectory = directory+'/'+tail[17:25]
       if not os.path.exists(subdirectory):
           os.makedirs(subdirectory)
       #### Moving files
       source=os.path.join(directory, filename)
       destination=os.path.join(subdirectory, tail)
       print('Moving '+source+' to '+destination)
       shutil.move(source,destination)
       
masterfolder = os.path.join(PROJECT, 'master') # PROJECT+'/slaves'
splitfolder = os.path.join(PROJECT, 'split_master')
logfolder = os.path.join(PROJECT, 'logs')
if not os.path.exists(splitfolder):
    os.makedirs(splitfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
graph2run = os.path.join(GRAPH, 'splitgraph2run_master_ms.xml')
outlog = os.path.join(logfolder, 'split_proc_stdout.log')
out_file = open(outlog, 'a')
err_file = out_file
print(bar_message)
out_file.write(bar_message)
message = '## Splitting TOPSARand Applying Orbit\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)
if len(IW_list)==1:
    total_file = len([file for file in os.listdir(masterfolder)])
else:
    total_file = len([file for file in os.listdir(masterfolder)])*len(IW_list)

    
#class ComputeMultiSwaths():
#    @staticmethod
def split_swaths_bursts():
    k = 0
    for files in glob.iglob(masterfolder + '/*/*' + '.zip', recursive=True):
        for iw in IW_list:
             k = k+1
             print('[{}¦{}] Folder: {}\n'.format(k, total_file, files))
             out_file.write('[{}] Folder: {}\n'.format(k, files))
             out_file.write(str(os.path.join(masterfolder, files)) + '\n')
             # files = glob.glob(os.path.join(masterfolder, acdatefolder) + '/*.zip')
             out_file.write(str(files) + '\n')
             head, tail = os.path.split(files)
             split_tail = tail.split('_')[-4][0:8]
             splitmasterfolder = os.path.join(splitfolder, split_tail)
             print('splitmasterfolder', splitmasterfolder)
             outputname = split_tail + '_' + iw  + '.dim'
             print('out', outputname)
             graphxml = os.path.join(GRAPH, 'master_split_applyorbit.xml')
             # Read in the file
             with open(graphxml, 'r') as file:
                filedata = file.read()
                # Replace the target string
                filedata = filedata.replace('INPUTFILE', files)
                filedata = filedata.replace('IWs', iw)
                filedata = filedata.replace('BottomBurstIndex', BottomBurstIndex)
                filedata = filedata.replace('TopBurstIndex', TopBurstIndex)
                filedata = filedata.replace('POLARISATION', POLARISATION)
                filedata = filedata.replace('OUTPUTFILE', os.path.join(splitmasterfolder,
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
            
