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
  base_filename = "median_download_times"

  parser = argparse.ArgumentParser(description='Plot median download times in a time window')
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
  all_times = list()

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
      time_help = list()
      time_help.append(0)
      download_times_help = list()
      download_times_help.append(0)
      # for i in range(1, len(data) + 1):
      #   print i, data[str(i)]['start'], data[str(i)]['download_time']

      # for i in range(1410, 1436):
      #   print i, data[i]['metrics']['cache_http_hits'], data[i]['metrics']['cache_client_http_requests']
      
      next_window_end = window
      download_times_current_window = list()

      for i in range(1, len(data) + 1):
        d_time = float(data[str(i)]['download_time'].replace(" ms", ''))
        all_times.append(d_time)
        if data[str(i)]['start'] <= next_window_end:
          download_times_current_window.append(d_time)
        else:
          # print i, next_window_end, download_times_current_window
          time_help.append(int(next_window_end)/60)
          next_window_end += window
          download_times_help.append(np.median(np.array(download_times_current_window)))
          download_times_current_window = list()
          download_times_current_window.append(d_time)


      if len(download_times_current_window) != 0:
        download_times_help.append(np.median(np.array(download_times_current_window)))
        download_times_current_window = list()
        time_help.append(int(next_window_end)/60)
      
    median = np.median(np.array(all_times))
    # print total_time
    # print time, len(time)
    # print download_times, len(download_times)
    print "Median Download Time = ", str(median) + ' ms'
    time.append(time_help)
    download_times.append(download_times_help)

    #print len(time), len(cache_hit_ratio_in_window)

  for i in range(0, len(args.input)):
    plt.plot(time[i], download_times[i], "-", label=args.labels[i], lw=width, markersize=markersize)
  # plt.plot(time, len(time) * [median], "r-", lw=width -2, markersize=markersize)

  font = {'family' : 'normal',
	        'weight' : 'normal',
	        'size'   : 22}
  plt.rc('font', **font)

  plt.xlabel("Time (min)")
  plt.ylabel("Median Download Time (ms)")

  ax = plt.gca()
  plt.xticks(np.arange(0,60+1,10))
  ax.set_xlim(0, math.ceil(60))
  ax.set_ylim(0, args.ylim)
  plt.yticks(np.arange(0, args.ylim + 1, args.ytick))
  plt.legend(loc='upper right', prop={'size':22})

  # plt.title("Window size = " + str(int(window/60)) + "min")
  

  fig = plt.gcf()
  # plt.text(0.18, median + 30, "Median = %.2fms"%(median), ha ='left', fontsize = 15, color = 'r')
  fig.tight_layout()
  fig.set_size_inches(10,7)

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