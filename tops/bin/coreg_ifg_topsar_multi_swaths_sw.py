# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 16:38:04 2020

@author: Sonam
"""


### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Date: 21/06/2018
# Version: 1.0

# Step 1 : preparing slaves in folder structure
# Step 2 : TOPSAR Splitting (Assembling) and Apply Orbit
# Step 3 : Coregistration and Interferogram generation
# Step 4 : StaMPS export

# Added option for CACHE and CPU specification by user
# Planned support for DEM selection and ORBIT type selection 

import os
import sys
import glob
import subprocess
import time

inputfile = sys.argv[1]
#inputfile = 'asc_2017_multi.conf'
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

######################################################################################
## TOPSAR Coregistration and Interferogram formation ##
######################################################################################
master_splitfolder = os.path.join(PROJECT, 'split_master')
master_file = glob.glob(master_splitfolder + '/**/*.dim',  
                   recursive = True) # result is list
slavesplittedfolder = os.path.join(PROJECT, 'split_slave')
outputcoregfolder = os.path.join(PROJECT, 'coreg')
outputifgfolder = os.path.join(PROJECT, 'ifg')
logfolder = os.path.join(PROJECT, 'logs')
if not os.path.exists(outputcoregfolder):
    os.makedirs(outputcoregfolder)
if not os.path.exists(outputifgfolder):
    os.makedirs(outputifgfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
    
outlog = os.path.join(logfolder, 'coreg_ifg_proc_stdout.log')
graphxml = os.path.join(GRAPH, 'coreg_ifg_computation_subset_snap7.xml')
graph_ms_processor1 = os.path.join(GRAPH, 'coreg_ifg_deburst_snap7_sw.xml')
graph2run = os.path.join(GRAPH, 'coreg_ifg2run_ms.xml')
out_file = open(outlog, 'a')
err_file = out_file
print(bar_message)
out_file.write(bar_message)
message = '## Coregistration and Interferogram computation started:\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)
#total_file = (file for file in glob.iglob(slavesplittedfolder + '/*/*' + '.dim'))
#total_file = len(list(total_file))

if len(IW_list)==1:
    total_file = len([file for file in os.listdir(slavesplittedfolder)])
    print('Total File : {}\n'.format(total_file))
else:
    total_file = len([file for file in os.listdir(slavesplittedfolder)])*len(IW_list)
    print('Total File : {}\n'.format(total_file))

def grapg2process(graph_xml, dim_master, dim_slave):
    with open(graph_xml, 'r') as file:
       filedata = file.read()
       # Replace the target string
       filedata = filedata.replace('MASTER', dim_master)
       filedata = filedata.replace('SLAVE', dim_slave)
       filedata = filedata.replace('OUTPUTCOREGFOLDER', outputcoregfolder)
       filedata = filedata.replace('OUTPUTIFGFOLDER', outputifgfolder)
       filedata = filedata.replace('OUTPUTFILE', outputname)
       # filedata = filedata.replace('POLYGON', polygon)
    # Write the file out again
    with open(graph2run, 'w') as file:
       file.write(filedata)
k = 0
for dimfile_master in master_file:
    for dimfile in glob.iglob(slavesplittedfolder + '/**/*.dim', recursive = True):
        for iw in IW_list:
            if iw in dimfile and iw in dimfile_master:
                k = k+1
                head, tail = os.path.split(os.path.join(slavesplittedfolder, dimfile))
                #print('tail', tail)
                #print('head', head)
                message = '[{}¦{}]  Processing slave file: {}'.format(k, total_file, tail)
                print(message)
                out_file.write(message)
                outputname = tail
                print('Output file name : {}\n'.format(outputname))
                if len(IW_list)==1:
                     grapg2process(graphxml, dimfile_master, dimfile)
                elif len(IW_list)>1:
                    grapg2process(graph_ms_processor1, dimfile_master, dimfile)
                    
                args = [GPT, graph2run, '-c', CACHE, '-q', CPU]
                # Launch the processing
                process = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                           stderr=subprocess.STDOUT)
                timeStarted = time.time()
                stdout = process.communicate()[0]
                print('SNAP STDOUT:{}'.format(stdout))
                timeDelta = time.time() - timeStarted  # Get execution time.
                # print('[' + str(k) + '] Finished process in ' + str(timeDelta) + ' seconds.')
                print('[{}¦{}]  Finished process in : {} seconds\n'.format(k, total_file, timeDelta))
                out_file.write('[{}¦{}]  Finished process in : {} seconds\n'.format(k, total_file, timeDelta))
                if process.returncode != 0:
                    message = 'Error computing with coregistration and interferogram generation of splitted slave ' + str(dimfile)
                    err_file.write(message + '\n')
                else:
                    message = 'Coregistration and Interferogram computation for data '+str(tail)+' successfully completed.\n'
                    print(message)
                    out_file.write(message)
                print(bar_message)
                out_file.write(bar_message)
out_file.close()
