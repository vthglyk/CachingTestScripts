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
  base_filename = "effect_of_peering_on_cpu_usage"

  parser = argparse.ArgumentParser(description='Parse results')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--window', '-w', default=60 ,type=int,
                      help='the window of processing the results in seconds (default: 60s)')
  parser.add_argument('--stop', '-s', default=-1 ,type=int,
                      help='value to stop (Default: -1)')
  parser.add_argument('--mode', '-m', type=int, default=1,
                      help='1 for squid, 2 for node exporter (Default: 1)')
  parser.add_argument('--filename', '-f', 
                      help='filename')
  parser.add_argument('--ylim', '-y', default=100, type=int,
                      help='y axis limit (Default: 100)')
  parser.add_argument('--ytick', '-yt', default=100, type=int,
                      help='y axis tick (Default: 100)') 

  args = parser.parse_args()

  if len(args.input) != len(args.labels):
    parser.error("The input and label arguments have different sizes (" + \
                  str(len(args.input)) + " != " + str(len(args.labels)) + ")")
  window = args.window

  time = list()
  cpu_squid_in_window = list()


  start_time = 0
  total_time = 0

  print args.input
  for j in args.input:
    filename = 'newresults/' + j + '/prometheus_stats'
    if(os.path.isfile(filename)  ==  False):
      print 'The input file "' + filename +'" does not exist. Exiting'
      sys.exit()

    with open(filename, 'r') as f:
      print "Working on ", filename
      cpu_squid_in_window_help = list()
      time_help = list()
      cpu_usage = list()
      cpu_usage_node_exporter = list()
      time_help.append(0)
      cpu_squid_in_window_help.append(0)

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
        total_cpu = 100

        if 'cpu0' in data[i]['metrics']:
          for j in data[i]['metrics']['cpu0']:
            if j['mode'] == 'id' or j['mode'] == 'st':
              total_cpu -= j['value']
          cpu_usage_node_exporter.append(total_cpu)

      help = 0
      count = 0
      for i in range(1, len(cpu_usage)):
        if args.mode == 1:
          help += cpu_usage[i]
        else:
          help += cpu_usage_node_exporter[i]
        count += 1
        print i, help, calculation_step
        if i % calculation_step == 0:
          print i
          cpu_squid_in_window_help.append(help/count)
          time_help.append(int((time_help[-1]*60 + window)/60))
          help = 0
          count = 0

      if help != 0:
        cpu_squid_in_window_help.append(help/count)
        time_help.append(math.ceil(len(data) * step/60))
      


      average_cpu_usage = np.average(cpu_usage)
      average_cpu_usage_node_exporter = np.average(cpu_usage_node_exporter)

      print "Average Cpu Usage = ", str(average_cpu_usage) + '%', str(np.average(cpu_squid_in_window_help)) 
      print "Average Cpu Usage Node Exporter = ", str(average_cpu_usage_node_exporter) + '%', str(np.average(cpu_squid_in_window_help)) 
      print len(cpu_usage), len(data)
      print time_help
      # print cpu_usage
      # print cpu_squid_in_window_help
      cpu_squid_in_window.append(cpu_squid_in_window_help)
      time.append(time_help)

  #print
  #print time 

  #print len(time), len(cpu_squid_in_window)
  print len(args.input), len(cpu_squid_in_window)
  print time
  print cpu_squid_in_window

  for i in range(0, len(args.input)):
    plt.plot(time[i], cpu_squid_in_window[i], "-", label=args.labels[i], lw=width, markersize=markersize)
  # plt.plot(time, len(time) * [average_cache_hit_ratio], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("CPU Utilization (\%)")

  ax = plt.gca()
  plt.xticks(np.arange(0,60+1,10))
  plt.yticks(np.arange(0, args.ylim + 1, args.ytick))
  ax.set_xlim(0, math.ceil(60))
  ax.set_ylim(0, args.ylim)


  # plt.title("Window size = " + str(int(window/60)) + "min")
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