# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 18:16:02 2020

@author: Sonam
"""


import os
import sys
import glob
import subprocess
import time
import shutil

inputfile = sys.argv[1]
#inputfile = 'des_2017_multi.conf'
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
            print(type(IW_list), IW_list)
        if "MASTER" in line:
            MASTER = line.split('=')[1].strip()
            print(type(MASTER), MASTER)
        if "GRAPHSFOLDER" in line:
            GRAPH = line.split('=')[1].strip()
            print(type(GRAPH), GRAPH)
        if "North_Lat" in line:
            North_Lat = line.split('=')[1].strip()
        if "West_Lon" in line:
            West_Lon = line.split('=')[1].strip()
        if "South_Lat" in line:
            South_Lat = line.split('=')[1].strip()
        if "East_Lon" in line:
            East_Lon = line.split('=')[1].strip()
        if "GPTBIN_PATH" in line:
            GPT = line.split('=')[1].strip()
            print(type(GPT), GPT)
        if "CPU" in line:
            CPU = line.split('=')[1].strip()
            # print(type(CPU), CPU)
        if "CACHE" in line:
            CACHE = line.split('=')[1].strip()

AOI = 'POLYGON(({} {}, {} {}, {} {}, {} {}, {} {}))'.format(East_Lon,North_Lat,
                                                          West_Lon,North_Lat,
                                                          West_Lon,South_Lat,
                                                          East_Lon,South_Lat,
                                                          East_Lon,North_Lat)
print('Subset Bound: {}'.format(AOI))

##############################################################################
## TOPSAR Merging and Subseting Coregistered and Interferogram Files ##
##############################################################################
outputcoregfolder = os.path.join(PROJECT, 'coreg')
coreg_file = glob.glob(outputcoregfolder + '/**/*.dim', recursive = True)
ifgfolder = os.path.join(PROJECT, 'ifg')
ifg_file = glob.glob(ifgfolder + '/**/*.dim', recursive = True)
logfolder = os.path.join(PROJECT, 'logs')
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
outlog = os.path.join(logfolder, 'coreg_ifg_merge_subset_stdout.log')
graphxml_coreg = os.path.join(GRAPH, 'coreg_merge_subset_snap7.xml')
graph2_write_run_coreg = os.path.join(GRAPH, 'coreg_merge_subset2run_ms.xml')
graphxml_ifg = os.path.join(GRAPH, 'ifg_merge_subset_snap7.xml')
graph2_write_run_ifg = os.path.join(GRAPH, 'ifg_merge_subset2run_ms.xml')
out_file = open(outlog, 'a')
err_file = out_file
print(bar_message)
out_file.write(bar_message)
message = '## Merge and subset started:\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)

def grapg2process(graph_xml, file1, file2, outputfile_name, graph2write):
    with open(graph_xml, 'r') as file:
       filedata = file.read()
       # Replace the target string
       filedata = filedata.replace('FILE1', file1)
       filedata = filedata.replace('FILE2', file2)
       filedata = filedata.replace('COREGFOLDER', outputcoregfolder)
       filedata = filedata.replace('IFGFOLDER', ifgfolder)
       filedata = filedata.replace('OUTFILE', outputfile_name)
       filedata = filedata.replace('POLYGON', AOI)
    with open(graph2write, 'w') as file:
       file.write(filedata)
    
def merge_subset_ms(input_file, graph_xml, graph2write, gpt_graph2run):
    img_date_lst = [os.path.split(i)[1][:8] for i in input_file]
    unique_date = list(dict.fromkeys(img_date_lst))
    k = 0
    for mf in input_file:
        for ud in unique_date:
            if ud in mf and IW_list[0] in mf:
                file11 = mf
            if ud in mf and IW_list[1] in mf:
                file22 = mf
                k = k+1
                image_date = os.path.split(mf)[1][:8]
                folder_name = image_date + '_' + IW_str
                file_name = folder_name + '.dim'
                grapg2process(graph_xml, file11, file22, file_name, graph2write)
                message = '[{}¦{}]  Processing slave file: {}'.format(k, len(unique_date), file_name)
                print(message)
                args = [GPT, gpt_graph2run, '-c', CACHE, '-q', CPU]
                # Launch the processing
                process = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                           stderr=subprocess.STDOUT)
                timeStarted = time.time()
                stdout = process.communicate()[0]
                print('SNAP STDOUT:{}'.format(stdout))
                timeDelta = time.time() - timeStarted  # Get execution time.
                print('[{}¦{}]  Finished process in : {} seconds\n'.format(k, len(unique_date), timeDelta))
                out_file.write('[{}¦{}]  Finished process in : {} seconds\n'.format(k, len(unique_date), timeDelta))
                if process.returncode != 0:
                    message = 'Error merging and subsetting of {}'.format(file_name)
                    err_file.write(message + '\n')
                else:
                    message = 'Merging and subseting of {} successfully completed\n'.format(file_name)
                    print(message)
                    out_file.write(message)
                print(bar_message)
                # Remove files after processing
                data_path = os.path.splitext(file11)[0] + '.data'
                shutil.rmtree(data_path)
                os.remove(file11)
                data_path = os.path.splitext(file22)[0] + '.data'
                shutil.rmtree(data_path)
                os.remove(file22)
                out_file.write(bar_message)
    return unique_date

coreg = merge_subset_ms(coreg_file, graphxml_coreg, graph2_write_run_coreg, graph2_write_run_coreg)
ifg = merge_subset_ms(ifg_file, graphxml_ifg, graph2_write_run_ifg, graph2_write_run_ifg)
out_file.close()
