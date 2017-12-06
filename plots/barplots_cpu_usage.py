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
import scipy as sp
import math
from scipy import stats

def mean_confidence_interval(data, confidence=0.95):
  a = 1.0*np.array(data)
  n, min_max, mean, var, skew, kurt = stats.describe(data)
  std=math.sqrt(var) 
  h = stats.norm.interval(0.95,loc=mean,scale=std/math.sqrt(n)) 
  return [mean, h[0], h[1]]

def main() :
  matplotlib.rcParams['text.usetex'] = True
  seaborn.set(font_scale=2.3)
  seaborn.set_style("whitegrid")
  my_palette = seaborn.color_palette("deep")
  width = 4
  markersize = 15
  base_filename = "_on_cpu_usage"

  parser = argparse.ArgumentParser(description='Parse results')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--xlabel', '-xl',
                      help='x axis label')  
  parser.add_argument('--mode', '-m', type=int, default=1,
                      help='1 for squid, 2 for node exporter (Default: 1)')
  parser.add_argument('--title', '-t',
                      help='value to stop')
  parser.add_argument('--filename', '-f', required=True,
                      help='filename')
  parser.add_argument('--ylim', '-y', default=100, type=int,
                      help='y axis limit (Default: 100)')
  parser.add_argument('--ytick', '-yt', default=10, type=int,
                      help='y axis tick (Default: 10)')
  parser.add_argument('--confidence_interval', '-ci', default=0.95, type=float,
                      help='confidence interval (Default: 0.95)')

  args = parser.parse_args()

  if len(args.input) != len(args.labels):
    parser.error("len(input) != len(labels) (" + \
                  str(len(args.input)) + " != " + str(len(args.labels)) + ")")

  cpu_usage = list()
  confidence_intervals = list()
  input_files = list()
  for i in args.input:
    input_files.append(i)
    input_files.append(i.replace('_A', '_B'))

  print input_files
  for j in input_files:
    filename = 'newresults/' + j + '/prometheus_stats'
    if(os.path.isfile(filename)  ==  False):
      print 'The input file "' + filename +'" does not exist. Exiting'
      sys.exit()

    with open(filename, 'r') as f:
      print "\nWorking on ", filename

      cpu_usage_squid = list()
      cpu_usage_node_exporter = list()

      data = json.load(f)

     
      # Save squid data to cpu_usage_squid and node exporter data to cpu_usage_node_exporter
      for i in range(0, len(data)):
        cpu_usage_squid.append(data[i]['metrics']['cache_cpu_usage'])
        total_cpu = 100

        if 'cpu0' in data[i]['metrics']:
          for j in data[i]['metrics']['cpu0']:
            if j['mode'] == 'id' or j['mode'] == 'st':
              total_cpu -= j['value']
          cpu_usage_node_exporter.append(total_cpu)


      average_cpu_usage_squid = np.average(cpu_usage_squid)
      average_cpu_usage_node_exporter = np.average(cpu_usage_node_exporter)

      print "Average Cpu Usage = ", str(average_cpu_usage_squid) + '%'
      print "Average Cpu Usage Node Exporter = ", str(average_cpu_usage_node_exporter) + '%'

      if args.mode == 1:
        cpu_usage.append(average_cpu_usage_squid)
        confidence_intervals.append(mean_confidence_interval(cpu_usage_squid, args.confidence_interval))
      elif args.mode ==2:
        cpu_usage.append(average_cpu_usage_node_exporter)
        confidence_intervals.append(mean_confidence_interval(cpu_usage_squid, args.confidence_interval))

      print "(mean, low, high)", args.confidence_interval, confidence_intervals[-1]


  x_positions = range(0, len(cpu_usage))
  client1_positions = list()
  client2_positions = list()
  client1_cpu = list()
  client2_cpu = list()

  for i in range(0,len(x_positions), 2):
      if i >1:
        x_positions[i] += i/2*0.5
        x_positions[i+1] += i/2*0.5
      client1_positions.append(x_positions[i])
      client2_positions.append(x_positions[i+1])
      client1_cpu.append(cpu_usage[i])
      client2_cpu.append(cpu_usage[i+1])

  x_ticks = list()
  for i in range(1,len(x_positions), 2):
      x_ticks.append((x_positions[i] + x_positions[i-1]) / 2.0)

  print x_positions
  print client1_positions
  print client1_cpu
  print client2_positions
  print client2_cpu
  print x_ticks
  print confidence_intervals
  width = 0.75

  # seaborn.barplot(x = x_positions, y = total_cache_hit_ratio, color = "red")
  # bottom_plot = seaborn.barplot(x = x_positions, y = local_hit_ratio, color = "#0000A3")
  linewidth = 1
  ci_width = 0.07
  for i in range(0, len(confidence_intervals)):
    if i % 2 == 0:
      plt.plot((client1_positions[i/2], client1_positions[i/2]),
               (confidence_intervals[i][1],confidence_intervals[i][2]), "-", color = "#2E2E2E", linewidth = linewidth)
      plt.plot((client1_positions[i/2] - ci_width, client1_positions[i/2] + ci_width),
               (confidence_intervals[i][1],confidence_intervals[i][1]), "-", color = "#2E2E2E", linewidth = linewidth)
      plt.plot((client1_positions[i/2] - ci_width, client1_positions[i/2] + ci_width),
               (confidence_intervals[i][2],confidence_intervals[i][2]), "-", color = "#2E2E2E", linewidth = linewidth)

    else:
      plt.plot((client2_positions[i/2], client2_positions[i/2]),
               (confidence_intervals[i][1],confidence_intervals[i][2]), "-", color = "#2E2E2E", linewidth = linewidth)
      plt.plot((client2_positions[i/2] - ci_width, client2_positions[i/2] + ci_width),
               (confidence_intervals[i][1],confidence_intervals[i][1]), "-", color = "#2E2E2E", linewidth = linewidth)
      plt.plot((client2_positions[i/2] - ci_width, client2_positions[i/2] + ci_width),
               (confidence_intervals[i][2],confidence_intervals[i][2]), "-", color = "#2E2E2E", linewidth = linewidth)

  p1 = plt.bar(client1_positions, client1_cpu, width, color=my_palette[0])
  p2 = plt.bar(client2_positions, client2_cpu, width, color=my_palette[2])

  topbar = plt.Rectangle((0,0),1,1,fc=my_palette[2], edgecolor = 'none')
  bottombar = plt.Rectangle((0,0),1,1,fc=my_palette[0],  edgecolor = 'none')

  if (args.title != None):
    plt.title(args.title)
  l = plt.legend([bottombar, topbar], ['VNO A', 'VNO B'], loc=1, ncol = 2, prop={'size':22})
  l.draw_frame(False)

  #Optional code - Make plot look nicer
  # seaborn.despine(left=True)
  # bottom_plot.set_ylabel("Cache Hit Ratio (\%)")
  # bottom_plot.set_xlabel("Scenarios")
  plt.xlabel("Scenarios" if args.xlabel == None else args.xlabel)
  plt.ylabel("CPU Utilization (\%)")

  font = {'family' : 'normal',
          'weight' : 'normal',
          'size'   : 22}
  plt.rc('font', **font)

  ax = plt.gca()
  ax.set_ylim(0, args.ylim)
  ax.xaxis.grid(False)
  plt.xticks(x_ticks, args.labels)
  plt.yticks(np.arange(0, args.ylim + 1, args.ytick))

  fig = plt.gcf()
  fig.tight_layout()
  fig.set_size_inches(10,7)
  plt.savefig("MECCOM_plots/" + args.filename + base_filename + ".eps")

  plt.show()

if __name__ == "__main__" :
  main()  