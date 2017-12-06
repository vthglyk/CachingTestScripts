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
  base_filename = "cache_hit_ratio"

  parser = argparse.ArgumentParser(description='Parse results')
  parser.add_argument('--input', '-i', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--window', '-w', default=60 ,type=int,
                      help='the window of processing the results in seconds (default: 60s)')
  parser.add_argument('--peering', '-p', required=True ,type=int,
                      help='was the peering active (1 for True and 0 for false')
  parser.add_argument('--stop', '-s', default=-1 ,type=int,
                      help='value to stop (Default: -1)')
  args = parser.parse_args()
  window = args.window

  if(os.path.isfile(args.input)  ==  False):
    print 'The input file "' + args.input +'" does not exist. Exiting'
    sys.exit()
  
  time = list()
  cache_hit_ratio_in_window = list()
  cpu_usage = list()
  cpu_usage_node_exporter = list()

  time.append(0)
  cache_hit_ratio_in_window.append(0)
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
      
    for i in range(0, len(data)):
      cpu_usage.append(data[i]['metrics']['cache_cpu_usage'])
      total_cpu_cycles = 0
      user_cpu_cycles = 0

      if 'cpu0' in data[i]['metrics']:
        for j in data[i]['metrics']['cpu0']:
          total_cpu_cycles += j['value']
          # print j
          if j['mode'] == 'user':
            user_cpu_cycles = j['value']
        cpu_usage_node_exporter.append(user_cpu_cycles/total_cpu_cycles*100)


    #   if 'cache_client_http_hits' in data[i]['metrics'].keys():
    #     print i, data[i]['metrics']['cache_client_http_hits'], (0 if args.peering == 0 else data[i]['metrics']['cache_client_icp_hits_peer']), data[i]['metrics']['cache_client_http_requests']
    #   else: 
    #     print i, "0 0 0"
    # for i in range(1410, len(data)):
    #   print i, data[i]['metrics']['cache_client_http_hits'], (0 if args.peering == 0 else data[i]['metrics']['cache_client_icp_hits_peer']), data[i]['metrics']['cache_client_http_requests']

    ########## REMOVE 0.75
    for i in range(calculation_step, len(data), calculation_step):
      time.append(i * step/60)  
      if i == calculation_step:
        cache_hit_ratio_in_window.append(data[i]['metrics']['cache_client_http_hits'] / \
                                         data[i]['metrics']['cache_client_http_requests'] * 100)
      else:
        if args.peering == 1:
          icp_hits_window = data[i]['metrics']['cache_client_icp_hits_peer'] - data[i-calculation_step]['metrics']['cache_client_icp_hits_peer']
        else:
          icp_hits_window = 0
        cache_hit_ratio_in_window.append((icp_hits_window + data[i]['metrics']['cache_client_http_hits'] - \
      	                                  data[i-calculation_step]['metrics']['cache_client_http_hits']) / \
                                         (data[i]['metrics']['cache_client_http_requests'] - \
      	                                  data[i-calculation_step]['metrics']['cache_client_http_requests']) * 100)
    ########## UNCOMMENT
    # Include remaining results if len(data) is not a multiple of calculation_step
    if len(data) % calculation_step != 1:
      print "debug", len(data), calculation_step, len(data) - len(data) % calculation_step,data[-1]['metrics']['cache_client_http_requests'], data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']
      if data[-1]['metrics']['cache_client_http_requests'] != data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']:

        cache_hit_ratio_in_window.append((data[-1]['metrics']['cache_client_http_hits'] - \
      	                                  data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_hits']) / \
                                         (data[-1]['metrics']['cache_client_http_requests'] - \
      	                                  data[len(data) - (len(data) % calculation_step)]['metrics']['cache_client_http_requests']) * 100)
        time.append(len(data) * step/60)

    print total_time, step, calculation_step, len(data)
    print cache_hit_ratio_in_window

    icp_hits = 0
    if args.peering == 1:
      print 1, args.peering
      icp_hits = data[args.stop]['metrics']['cache_client_icp_hits_peer']
    else:
      print 2, args.peering
      icp_hits = 0

    average_cache_hit_ratio = (data[args.stop]['metrics']['cache_client_http_hits'] + icp_hits)/\
                               data[args.stop]['metrics']['cache_client_http_requests']*100
    average_cpu_usage = np.average(cpu_usage)
    average_cpu_usage_node_exporter = np.average(cpu_usage_node_exporter)

    print "Average Cache Hit Ratio = ", str(average_cache_hit_ratio) + '%', data[args.stop]['metrics']['cache_client_http_requests'], icp_hits, data[args.stop]['metrics']['cache_client_http_hits'] 
    print "Average Cpu Usage = ", str(average_cpu_usage) + '%' 
    print "Average Cpu Usage Node Exporter = ", str(average_cpu_usage_node_exporter) + '%' 
    print len(cpu_usage_node_exporter), len(data)

  #print
  #print time 

  #print len(time), len(cache_hit_ratio_in_window)

  plt.plot(time, cache_hit_ratio_in_window, "-", lw=width, markersize=markersize)
  plt.plot(time, len(time) * [average_cache_hit_ratio], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("Cache Hit Ratio (\%)")

  ax = plt.gca()
  plt.xticks(np.arange(0,120+1,20))
  ax.set_xlim(0, math.ceil(120))
  ax.set_ylim(0, 100)

  plt.title("Window size = " + str(int(window/60)) + "min, " + ("with peering" if args.peering == 1 else "without peering"))
  

  fig = plt.gcf()
  text = "Average = %.2f"%(average_cache_hit_ratio)
  plt.text(0.17, average_cache_hit_ratio + 1, text + '\%', ha ='left', fontsize = 15, color = 'r')
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

  plt.savefig(output_folder + base_filename +"_" + str(int(window/60)) + "min" + \
            ("_with_peering" if args.peering == 1 else "_without_peering") + ".eps")
  # plt.show()



if __name__ == "__main__" :
  main()  