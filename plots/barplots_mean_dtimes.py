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
  base_filename = "_on_mean_download_time"

  parser = argparse.ArgumentParser(description='Plot mean download times in a time window')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--xlabel', '-xl',
                      help='x axis label')  
  parser.add_argument('--title', '-t', 
                      help='value to stop')
  parser.add_argument('--filename', '-f', required=True,
                      help='filename')
  parser.add_argument('--ylim', '-y', default=1000, type=int,
                      help='y axis limit (Default: 1000)')
  parser.add_argument('--ytick', '-yt', default=100, type=int,
                      help='y axis tick (Default: 100)')  
  parser.add_argument('--confidence_interval', '-ci', default=0.95, type=float,
                      help='confidence interval (Default: 0.95)')

  args = parser.parse_args()

  download_times = list()
  confidence_intervals = list()

  input_files = list()
  for i in args.input:
    input_files.append(i)
    input_files.append(i.replace('_A', '_B'))
  print input_files

  for j in input_files:
    filename = 'newresults/' + j + '/grequests_stats'
    if(os.path.isfile(filename)  ==  False):
      print 'The input file "' + filename +'" does not exist. Exiting'
      sys.exit()

    with open(filename, 'r') as f:
      print "\nWorking on ", filename
      json_string = ''

      lines = f.readlines()
      if "All the requests were served correctly" not in lines[1]:
        print "Not all the requests were served correctly"
      else:
        json_string = lines[1].replace("All the requests were served correctly", '')

      data = json.loads(json_string)
      

      # for i in range(1410, 1436):
      #   print i, data[i]['metrics']['cache_http_hits'], data[i]['metrics']['cache_client_http_requests']
      
      total_download_time = list()
      local_hit_times = list()
      peer_hit_times = list()
      miss_times = list()

      for i in range(1, len(data) + 1):
        d_time = float(data[str(i)]['download_time'].replace(" ms", ''))

        total_download_time.append(d_time)
        cache_info = data[str(i)]['X-Cache'].split(' ')
        if len(cache_info) == 6:
          peer_hit_times.append(d_time)
        elif len(cache_info) == 3 and cache_info[0] == 'HIT':
          local_hit_times.append(d_time)
        elif len(cache_info) == 3 and cache_info[0] == 'MISS':
          miss_times.append(d_time)

      average_download_time = np.average(total_download_time)
      average_local_hit_time = np.average(local_hit_times)
      average_peer_hit_time = np.average(peer_hit_times)
      average_miss_time = np.average(miss_times)

      print "Average Download Time = ", str(average_download_time) + ' ms'
      print "Average Local Hit Time = ", str(average_local_hit_time) + ' ms',  len(local_hit_times), str(100.0 * len(local_hit_times)/len(data)) + '%'
      print "Average Peer Hit Time = ", str(average_peer_hit_time) + ' ms',  len(peer_hit_times), str(100.0 * len(peer_hit_times)/len(data)) + '%'
      print "Average Miss Time = ", str(average_miss_time) + ' ms',  len(miss_times), str(100.0 * len(miss_times)/len(data)) + '%'
      print "Total Cache Hit Ratio = ", len(miss_times), str(100.0 * (len(data) - len(miss_times))/len(data)) + '%'
      download_times.append(average_download_time)
      confidence_intervals.append(mean_confidence_interval(total_download_time, args.confidence_interval))
      print confidence_intervals[-1]

  x_positions = range(0, len(download_times))
  client1_positions = list()
  client2_positions = list()
  client1_dtimes = list()
  client2_dtimes = list()

  for i in range(0,len(x_positions), 2):
      if i >1:
        x_positions[i] += i/2*0.5
        x_positions[i+1] += i/2*0.5
      client1_positions.append(x_positions[i])
      client2_positions.append(x_positions[i+1])
      client1_dtimes.append(download_times[i])
      client2_dtimes.append(download_times[i+1])

  x_ticks = list()
  for i in range(1,len(x_positions), 2):
      x_ticks.append((x_positions[i] + x_positions[i-1]) / 2.0)

  print x_positions
  print client1_positions
  print client1_dtimes
  print client2_positions
  print client2_dtimes
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

  p1 = plt.bar(client1_positions, client1_dtimes, width, color=my_palette[0])
  p2 = plt.bar(client2_positions, client2_dtimes, width, color=my_palette[2])

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
  plt.ylabel("Average Download Time (ms)")

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