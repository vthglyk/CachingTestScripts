import json
import argparse
import os
import sys
import math
import matplotlib
import matplotlib.pyplot as plt 
import seaborn
import numpy as np
import subprocess


def main() :
  matplotlib.rcParams['text.usetex'] = True
  seaborn.set(font_scale=2.3)
  seaborn.set_style("whitegrid")
  width = 4
  markersize = 15
  base_filename = "icp_hit_ratio"

  parser = argparse.ArgumentParser(description='Plot icp hits')
  parser.add_argument('--input', '-i', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--window', '-w', default=60 ,type=int,
                      help='the window of processing the results in seconds (default: 60s)')

  args = parser.parse_args()
  window = args.window

  if(os.path.isfile(args.input)  ==  False):
    print 'The input file "' + args.input +'" does not exist. Exiting'
    sys.exit()
  
  time = list()
  icp_hit_ratio_in_window = list()

  time.append(0)
  icp_hit_ratio_in_window.append(0)
  start_time = 0
  total_time = 0

  with open(args.input, 'r') as f:
    data = json.load(f)
    start_time = data[0]['time']
    total_time = data[-1]['time'] - start_time
    step = data[1]['time'] -data[0]['time']

    if window < step:
      print 'The window (' + str(window) + 's) was smaller than the prometheus query step (' + str(step) + 's)'
      print 'Exiting'
      sys.exit()

    calculation_step = int(math.ceil(window/step))
      
    for i in range(0, 40):
      print i, data[i]['metrics']['cache_client_icp_hits_peer']

    for i in range(1410, len(data)):
      print i, data[i]['metrics']['cache_client_icp_hits_peer']

    for i in range(calculation_step, len(data), calculation_step):
      time.append(i * step/60)  
      if i == calculation_step:
        icp_hit_ratio_in_window.append(data[i]['metrics']['cache_client_icp_hits_peer'] / \
                                         data[i]['metrics']['cache_client_http_requests'] * 100)
      else:

        icp_hit_ratio_in_window.append((data[i]['metrics']['cache_client_icp_hits_peer'] - \
      	                                  data[i-calculation_step]['metrics']['cache_client_icp_hits_peer']) / \
                                         (data[i]['metrics']['cache_client_http_requests'] - \
      	                                  data[i-calculation_step]['metrics']['cache_client_http_requests']) * 100)

    # Include remaining results if len(data) is not a multiple of calculation_step
    if len(data) % calculation_step != 1:
      # print "debug", len(data), calculation_step, len(data) - len(data) % calculation_step,data[-1]['metrics']['cache_client_http_requests'], data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']
      icp_hit_ratio_in_window.append((data[-1]['metrics']['cache_client_icp_hits_peer'] - \
      	                                data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_icp_hits_peer']) / \
                                       (data[-1]['metrics']['cache_client_http_requests'] - \
      	                                data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']) * 100)
      time.append(len(data) * step/60)

    print total_time, step, calculation_step, len(data)
    print icp_hit_ratio_in_window
    print data[-1]['metrics']['cache_client_icp_hits_peer'], data[-1]['metrics']['cache_client_http_requests']

    average_icp_ratio = data[-1]['metrics']['cache_client_icp_hits_peer'] /\
                data[-1]['metrics']['cache_client_http_requests']*100
    print "Average ICP Hit Ratio = ", str(average_icp_ratio) + '%' 
     
  #print
  #print time 

  #print len(time), len(icp_hit_ratio_in_window)

  plt.plot(time, icp_hit_ratio_in_window, "-", lw=width, markersize=markersize)
  plt.plot(time, len(time) * [average_icp_ratio], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("ICP Hit Ratio (\%)")

  ax = plt.gca()
  plt.xticks(np.arange(0,120+1,20))
  ax.set_xlim(0, math.ceil(120))
  ax.set_ylim(0, 100)

  plt.title("Window size = " + str(int(window/60)) + "min")
  

  fig = plt.gcf()
  text = "Average = %.2f"%(average_icp_ratio)
  plt.text(0.17, average_icp_ratio + 1, text + '\%', ha ='left', fontsize = 15, color = 'r')
  fig.tight_layout()
  fig.set_size_inches(10,7)

  output_folder = args.input.replace('prometheus_stats', 'figures/')
  if(os.path.isdir(output_folder)  ==  False):
    print "The output folder " + output_folder + " does not exist. It will be automatically created."
    try:
      output=subprocess.check_output(["mkdir", "-p", output_folder])
      print "The output folder was created successfully!"
    except subprocess.CalledProcessError as grepexc:
      print "Error while creating the output folder", grepexc.returncode, grepexc.output

  plt.savefig(output_folder + base_filename +"_" + str(int(window/60)) + "min.eps")
  # plt.show()



if __name__ == "__main__" :
  main()  