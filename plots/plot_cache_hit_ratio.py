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
  base_filename = "effect_of_peering_on_cache_hit_ratio"

  parser = argparse.ArgumentParser(description='Parse results')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--window', '-w', default=60 ,type=int,
                      help='the window of processing the results in seconds (default: 60s)')
  parser.add_argument('--stop', '-s', default=-1 ,type=int,
                      help='value to stop (Default: -1)')
  parser.add_argument('--peering', '-p', required=True ,type=int,
                      help='was the peering active (1 for True and 0 for false')
  parser.add_argument('--filename', '-f', 
                      help='filename')
  parser.add_argument('--ylim', '-y', default=1000, type=int,
                      help='y axis limit (Default: 1000)')
  parser.add_argument('--ytick', '-yt', default=100, type=int,
                      help='y axis tick (Default: 100)')  
  args = parser.parse_args()

  if len(args.input) != len(args.labels):
    parser.error("The input and label arguments have different sizes (" + \
                  str(len(args.input)) + " != " + str(len(args.labels)) + ")")
  window = args.window

  time = list()
  cache_hit_ratio_in_window = list()

  start_time = 0
  total_time = 0

  print args.input
  for j in args.input:
    filename = 'newresults/' + j + '/prometheus_stats'
    if(os.path.isfile(filename)  ==  False):
      print 'The input file "' + filename +'" does not exist. Exiting'
      sys.exit()

    with open(filename, 'r') as f:
      print "\nWorking on ", filename
      cache_hit_ratio_in_window_help = list()
      time_help = list()
      cache_hit_ratio_in_window_help.append(0)
      time_help.append(0)

      data = json.load(f)
      start_time = data[0]['time']
      total_time = data[-1]['time'] - start_time
      step = data[1]['time'] -data[0]['time']

      if window < step:
        print 'The window (' + str(window) + 's) was smaller than the prometheus query step (' + str(step) + 's)'
        print 'Exiting'
        sys.exit()

      calculation_step = int(math.ceil(window/step))
        
      for i in range(calculation_step, len(data), calculation_step):
        time_help.append(i * step/60)  
        # if i == calculation_step:
        #   cache_hit_ratio_in_window_help.append(data[i]['metrics']['cache_client_http_hits'] / \
        #                                    data[i]['metrics']['cache_client_http_requests'] * 100)
        # else:
        if args.peering == 1:
          icp_hits_window = data[i]['metrics']['cache_client_icp_hits_peer'] - data[i-calculation_step]['metrics']['cache_client_icp_hits_peer']
        else:
          icp_hits_window = 0
        cache_hit_ratio_in_window_help.append((icp_hits_window + data[i]['metrics']['cache_client_http_hits'] - \
        	                                     data[i-calculation_step]['metrics']['cache_client_http_hits']) / \
                                              (data[i]['metrics']['cache_client_http_requests'] - \
        	                                     data[i-calculation_step]['metrics']['cache_client_http_requests']) * 100)
      # Include remaining results if len(data) is not a multiple of calculation_step
      if len(data) % calculation_step != 1:
        if args.peering == 1:
          icp_hits_window = data[i]['metrics']['cache_client_icp_hits_peer'] - data[i-calculation_step]['metrics']['cache_client_icp_hits_peer']
        else:
          icp_hits_window = 0

        if data[-1]['metrics']['cache_client_http_requests'] != data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']:

          cache_hit_ratio_in_window_help.append((icp_hits_window + data[-1]['metrics']['cache_client_http_hits'] - \
        	                                  data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_hits']) / \
                                           (data[-1]['metrics']['cache_client_http_requests'] - \
        	                                  data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']) * 100)
          time_help.append(len(data) * step/60)

      # print total_time, step, calculation_step, len(data)
      # print cache_hit_ratio_in_window_help

      icp_hits = 0
      if args.peering == 1:
        # print 1, args.peering
        icp_hits = data[args.stop]['metrics']['cache_client_icp_hits_peer']
      else:
        # print 2, args.peering
        icp_hits = 0

      average_cache_hit_ratio = (data[args.stop]['metrics']['cache_client_http_hits'] + icp_hits)/\
                                 data[args.stop]['metrics']['cache_client_http_requests']*100
      local_cache_hit_ratio = data[args.stop]['metrics']['cache_client_http_hits']/data[args.stop]['metrics']['cache_client_http_requests']*100
      local_icp_hit_ratio = icp_hits/data[args.stop]['metrics']['cache_client_http_requests']*100

      print "Total Cache Hit Ratio = ", str(average_cache_hit_ratio) + '%', data[args.stop]['metrics']['cache_client_http_requests'], icp_hits, data[args.stop]['metrics']['cache_client_http_hits'] 
      print "Local Hit Ratio = ", str(local_cache_hit_ratio) + '%'
      print "ICP Hit Ratio = ", str(local_icp_hit_ratio) + '%'

      cache_hit_ratio_in_window.append(cache_hit_ratio_in_window_help)
      time.append(time_help)

  #print
  #print time 

  #print len(time), len(cache_hit_ratio_in_window)
  # print len(args.input), len(cache_hit_ratio_in_window)
  # print time
  # print cache_hit_ratio_in_window

  for i in range(0, len(args.input)):
    plt.plot(time[i], cache_hit_ratio_in_window[i], "-", label=args.labels[i], lw=width, markersize=markersize)
  # plt.plot(time, len(time) * [average_cache_hit_ratio], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("Cache Hit Ratio (\%)")

  ax = plt.gca()
  plt.xticks(np.arange(0,60+1,10))
  ax.set_xlim(0, math.ceil(60))
  ax.set_ylim(0, args.ylim)
  plt.yticks(np.arange(0,args.ylim+1,args.ytick))

  # plt.title("Window size = " + str(int(window/60)) + "min, " + ("with peering" if args.peering == 1 else "without peering"))
  plt.legend(loc='upper right', prop={'size':22})


  fig = plt.gcf()
  # text = "Average = %.2f"%(average_cache_hit_ratio)
  # plt.text(0.17, average_cache_hit_ratio + 1, text + '\%', ha ='left', fontsize = 15, color = 'r')
  fig.tight_layout()
  fig.set_size_inches(10,7)

  # output_folder = args.input.replace('prometheus_stats', 'figures/')
  output_folder = "MECCOM_plots/"
  if(os.path.isdir(output_folder)  ==  False):
    print "The output folder " + output_folder + " does not exist. It will be automatically created."
    try:
      output=subprocess.check_output(["mkdir", "-p", output_folder])
      print "The output folder was created successfully!"
    except subprocess.CalledProcessError as grepexc:
      print "Error while creating the output folder", grepexc.returncode, grepexc.output

  plt.savefig(output_folder + (args.filename if args.filename != None else "") + base_filename + ".eps")

  plt.show()



if __name__ == "__main__" :
  main()  