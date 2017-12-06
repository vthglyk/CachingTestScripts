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
  base_filename = "_on_median_download_time"

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
  args = parser.parse_args()

  download_times = list()

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

      median_download_time = np.median(total_download_time)  
      median_local_hit_time = np.median(local_hit_times)
      median_peer_hit_time = np.median(peer_hit_times)
      median_miss_time = np.median(miss_times)

      print "Median Download Time = ", str(median_download_time) + ' ms'
      print "Median Local Hit Time = ", str(median_local_hit_time) + ' ms',  len(local_hit_times)
      print "Median Peer Hit Time = ", str(median_peer_hit_time) + ' ms',  len(peer_hit_times)
      print "Median Miss Time = ", str(median_miss_time) + ' ms',  len(miss_times)
      download_times.append(median_download_time)


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
  width = 0.75

  # seaborn.barplot(x = x_positions, y = total_cache_hit_ratio, color = "red")
  # bottom_plot = seaborn.barplot(x = x_positions, y = local_hit_ratio, color = "#0000A3")

  p1 = plt.bar(client1_positions, client1_dtimes, width, color="blue")
  p2 = plt.bar(client2_positions, client2_dtimes, width, color="red")

  topbar = plt.Rectangle((0,0),1,1,fc="red", edgecolor = 'none')
  bottombar = plt.Rectangle((0,0),1,1,fc='blue',  edgecolor = 'none')

  if (args.title != None):
    plt.title(args.title)
  l = plt.legend([bottombar, topbar], ['VNO A', 'VNO B'], loc=1, ncol = 2, prop={'size':22})
  l.draw_frame(False)

  #Optional code - Make plot look nicer
  # seaborn.despine(left=True)
  # bottom_plot.set_ylabel("Cache Hit Ratio (\%)")
  # bottom_plot.set_xlabel("Scenarios")
  plt.xlabel("Scenarios" if args.xlabel == None else args.xlabel)
  plt.ylabel("Median Download Time (ms)")

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