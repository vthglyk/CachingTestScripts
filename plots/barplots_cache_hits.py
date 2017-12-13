import json
import argparse
import os
import sys
import matplotlib
import matplotlib.pyplot as plt 
import seaborn
import numpy as np
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
  width = 4
  markersize = 15
  base_filename = "_on_cache_hit_ratio"

  parser = argparse.ArgumentParser(description='Parse results')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--xlabel', '-xl',
                      help='x axis label') 
  parser.add_argument('--stop', '-s', default=-1 ,type=int,
                      help='value to stop (Default: -1)')
  parser.add_argument('--title', '-t',
                      help='value to stop')
  parser.add_argument('--filename', '-f', required=True,
                      help='filename')
  parser.add_argument('--ylim', '-y', type=int, default=100,
                      help='y axis limit (Default: 100)')
  parser.add_argument('--ytick', '-yt', default=10, type=int,
                      help='y axis tick (Default: 10)')
  args = parser.parse_args()

  if len(args.input) != len(args.labels):
    parser.error("len(input) != len(labels) (" + \
                  str(len(args.input)) + " != " + str(len(args.labels)) + ")")

  total_cache_hit_ratio = list()
  local_hit_ratio = list()

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
      data = json.load(f)

      icp_hits = data[args.stop]['metrics']['cache_client_icp_hits_peer']
      local_hits = data[args.stop]['metrics']['cache_client_http_hits']
      total_requests = data[args.stop]['metrics']['cache_client_http_requests']
      total_hits = local_hits + icp_hits
      total_cache_hit_ratio.append(total_hits/total_requests*100)
      local_hit_ratio.append(local_hits/total_requests*100)

      print "Total Cache Hit Ratio = ", str(total_cache_hit_ratio[-1]) + '%'
      print "Local Cache Hit Ratio = ", str(local_hit_ratio[-1]) + '%'
      print "Total ICP Hit Ratio = ", str(icp_hits/total_requests*100) + '%'


  x_positions = range(0, len(total_cache_hit_ratio))
  client1_positions = list()
  client2_positions = list()
  client1_tchr = list()
  client2_tchr = list()
  client1_lchr = list()
  client2_lchr = list()

  for i in range(0,len(x_positions), 2):
      if i >1:
        x_positions[i] += i/2*0.5
        x_positions[i+1] += i/2*0.5
      client1_positions.append(x_positions[i])
      client2_positions.append(x_positions[i+1])
      client1_tchr.append(total_cache_hit_ratio[i])
      client2_tchr.append(total_cache_hit_ratio[i+1])
      client1_lchr.append(local_hit_ratio[i])
      client2_lchr.append(local_hit_ratio[i+1])


  x_ticks = list()
  for i in range(1,len(x_positions), 2):
      x_ticks.append((x_positions[i] + x_positions[i-1]) / 2.0)

  print x_positions
  print client1_positions
  print client1_tchr
  print client1_lchr
  print client2_positions
  print client2_tchr
  print client2_lchr
  print x_ticks


  # x_positions = range(0, len(total_cache_hit_ratio))
  # for i in range(2,len(x_positions), 2):
  #     x_positions[i] += i/2*0.5
  #     x_positions[i+1] += i/2*0.5

  # x_ticks = list()
  # for i in range(1,len(x_positions), 2):
  #     x_ticks.append((x_positions[i] + x_positions[i-1]) / 2.0)

  # print x_positions
  # print x_ticks
  width = 0.75

  # seaborn.barplot(x = x_positions, y = total_cache_hit_ratio, color = "red")
  # bottom_plot = seaborn.barplot(x = x_positions, y = local_hit_ratio, color = "#0000A3")

  # p1 = plt.bar(x_positions, total_cache_hit_ratio, width, color="red")
  # p2 = plt.bar(x_positions, local_hit_ratio, width, color = "#0000A3")

  client1_tchr_color = "#ff0000"
  client1_lchr_color = "#0000ff"
  client2_tchr_color = "#ff0000"
  client2_lchr_color = "#0000ff"
  p1 = plt.bar(client1_positions, client1_tchr, width, color = client1_tchr_color)
  p2 = plt.bar(client1_positions, client1_lchr, width, color = client1_lchr_color)
  p3 = plt.bar(client2_positions, client2_tchr, width, color = client2_tchr_color, hatch='///')
  p4 = plt.bar(client2_positions, client2_lchr, width, color = client2_lchr_color, hatch='///')

  # p1 = seaborn.barplot(data =, color = client1_tchr_color, width = width)

  # p1 = seaborn.barplot(x = client1_positions, y = client1_tchr, color = client1_tchr_color, width = width)
  # p2 = seaborn.barplot(x = client1_positions, y = client1_lchr, color = client1_lchr_color, width = width)
  # p3 = seaborn.barplot(x = client2_positions, y = client2_tchr, color = client2_tchr_color, hatch='///', width = width)
  # p4 = seaborn.barplot(x = client2_positions, y = client2_lchr, color = client2_lchr_color, hatch='///', width = width)

  # p1 = plt.bar(x_positions, total_cache_hit_ratio, width, color="red")
  # p2 = plt.bar(x_positions, local_hit_ratio, width, color = "#0000A3")

  topbar_client1 = plt.Rectangle((0,0),1,1,fc=client1_tchr_color, edgecolor = 'none')
  bottombar_client1 = plt.Rectangle((0,0),1,1,fc=client1_lchr_color,  edgecolor = 'none')
  topbar_client2 = plt.Rectangle((0,0),1,1,fc=client2_tchr_color, edgecolor = 'none', hatch='///')
  bottombar_client2 = plt.Rectangle((0,0),1,1,fc=client2_lchr_color,  edgecolor = 'none', hatch='///')

  if (args.title != None):
    plt.title(args.title)
  l = plt.legend([topbar_client1, bottombar_client1, topbar_client2, bottombar_client2],
                 ['Peering Hit Ratio - VNO A', 'Local Hit Ratio - VNO A', 'Peering Hit Ratio - VNO B', 'Local Hit Ratio - VNO B' ], loc=1, ncol = 2, prop={'size':22})
  l.draw_frame(False)

  #Optional code - Make plot look nicer
  # seaborn.despine(left=True)
  # bottom_plot.set_ylabel("Cache Hit Ratio (\%)")
  # bottom_plot.set_xlabel("Scenarios")
  plt.xlabel("Scenarios" if args.xlabel == None else args.xlabel)
  plt.ylabel("Cache Hit Ratio (\%)")

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
  #plt.savefig("MECCOM_plots/" + args.filename + base_filename + ".eps")

  plt.show()


if __name__ == "__main__" :
  main()  