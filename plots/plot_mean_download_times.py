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
  base_filename = "mean_download_times"

  parser = argparse.ArgumentParser(description='Plot mean download times in a time window')
  parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='name of the results file to be parsed (REQUIRED)')
  parser.add_argument('--labels', '-l', nargs='+', required=True,
                      help='labels of the plots (REQUIRED)')
  parser.add_argument('--window', '-w', default=60 ,type=int,
                      help='the window of processing the results in seconds (default: 60s)')
  parser.add_argument('--filename', '-f', 
                      help='filename')
  parser.add_argument('--ylim', '-y', default=1000, type=int,
                      help='y axis limit (Default: 1000)')
  parser.add_argument('--ytick', '-yt', default=100, type=int,
                      help='y axis tick (Default: 100)') 
  args = parser.parse_args()
  window = args.window

  time = list()
  download_times = list()
  local_hit_times = list()
  peer_hit_times = list()
  miss_times = list()
  
  start_time = 0
  total_time = 0


  for j in args.input:
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
      
      start_time = data['1']['start']
      total_time = data[str(len(data))]['end'] - start_time
      download_times_help = list()
      download_times_help.append(0)
      time_help = list()
      time_help.append(0)

      with open("hahaha", 'w') as haha:
        for i in range(1, len(data) + 1):
          text =  str(data[str(i)]['file']) + ' ' + str(data[str(i)]['start']) \
                  + ' ' + data[str(i)]['download_time'] + ' ' + data[str(i)]['X-Cache'] + '\n'
          haha.write(text)

      # for i in range(1410, 1436):
      #   print i, data[i]['metrics']['cache_http_hits'], data[i]['metrics']['cache_client_http_requests']
      
      next_window_end = window
      window_download_time = 0
      window_requests = 0
      total_download_time = 0
      local_hit_times_help = list()
      peer_hit_times_help = list()
      miss_times_help = list()

      for i in range(1, len(data) + 1):
        d_time = float(data[str(i)]['download_time'].replace(" ms", ''))
        if data[str(i)]['start'] <= next_window_end:
          window_download_time += d_time
          window_requests += 1
        else:
          # print i, window_download_time, window_requests, next_window_end
          time_help.append(int(next_window_end)/60)
          next_window_end += window
          download_times_help.append(window_download_time/window_requests)
          window_download_time = d_time
          window_requests = 1

        total_download_time += d_time
        cache_info = data[str(i)]['X-Cache'].split(' ')
        if len(cache_info) == 6:
          peer_hit_times_help.append(d_time)
        elif len(cache_info) == 3 and cache_info[0] == 'HIT':
          local_hit_times_help.append(d_time)
        elif len(cache_info) == 3 and cache_info[0] == 'MISS':
          miss_times_help.append(d_time)



      if window_requests != 0:
        download_times_help.append(window_download_time/window_requests)
        window_download_time = 0
        window_requests = 0
        time_help.append(int(next_window_end)/60)

      average_download_time = total_download_time/len(data)  
      average_local_hit_time = np.average(local_hit_times_help)
      average_peer_hit_time = np.average(peer_hit_times_help)
      average_miss_time = np.average(miss_times_help)
      print "Average Download Time = ", str(average_download_time) + ' ms',  total_download_time
      print "Average Local Hit Time = ", str(average_local_hit_time) + ' ms',  len(local_hit_times_help)
      print "Average Peer Hit Time = ", str(average_peer_hit_time) + ' ms',  len(peer_hit_times_help)
      print "Average Miss Time = ", str(average_miss_time) + ' ms',  len(miss_times_help)
      
      download_times.append(download_times_help)
      time.append(time_help)

  # print total_time
  # print time, len(time)
  # print download_times, len(download_times)

  #print len(time), len(cache_hit_ratio_in_window)
  for i in range(0, len(args.input)):
    plt.plot(time[i], download_times[i], "-", label=args.labels[i], lw=width, markersize=markersize)
  # plt.plot(time, len(time) * [average_download_time], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("Average Download Time (ms)")

  ax = plt.gca()
  plt.xticks(np.arange(0,60+1,10))
  ax.set_xlim(0, math.ceil(60))
  ax.set_ylim(0, args.ylim)
  plt.yticks(np.arange(0, args.ylim + 1, args.ytick))

  # plt.title("Window size = " + str(int(window/60)) + "min")
  plt.legend(loc='upper right', prop={'size':22})

  fig = plt.gcf()
  # plt.text(0.18, average_download_time + 30, "Average = %.2fms"%(average_download_time), ha ='left', fontsize = 15, color = 'r')
  fig.tight_layout()
  fig.set_size_inches(10,7)

  # output_folder = args.input.replace('grequests_stats', 'figures/')
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