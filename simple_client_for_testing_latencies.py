import requests
import grequests
from threading import Thread
import sys
import time
import os
import argparse
import json
from pprint import pprint
from gevent.pool import Pool
import subprocess

results = dict()
start_time = time.time()

delimiter = '/' # '/' for testing, '?' for debugging
finished = False

def hook_factory(*factory_args, **factory_kwargs):
  def response_hook(res, *request_args, **request_kwargs):
    print res.headers
    dtime = time.time() - start_time
    print "response_hook1:", dtime
    #size = len(res.content)
    id = factory_kwargs['request_id']
    session = factory_kwargs['session']
    file = res.url.split(delimiter)[-1].split('.')[0]
    print "response_hook2:", file, id
    
    global results
    results[id]['end'] = dtime
    results[id]['download_time'] = str((results[id]['end'] - results[id]['start']) * 1000) + ' ms'
    results[id]['status_code'] = res.status_code
    results[id]['X-Cache'] = res.headers['X-Cache']
    results[id]['X-Cache-Lookup'] = res.headers['X-Cache-Lookup']
    return None # or the modified response
  return response_hook


def main() :

  parser = argparse.ArgumentParser(description='Simulate client behaviour')
  parser.add_argument('--workload', '-w', required=True,
                      help='name of the file describing the workload (REQUIRED)')
  parser.add_argument('--offset', '-o', default=100000, type=int,
                      help='offset  (default: 100000)')
  parser.add_argument('--pool', '-p', default=1, type=int,
                      help='size of the pool (default: 1)')
  parser.add_argument('--size', '-s', type=int,
                      help='the catalogue size')
  parser.add_argument('--catalogue', '-c', type=int,
                      help='the catalogue')
  parser.add_argument('--prometheus_query_interval', '-q', default=1,type=int,
                      help='the query interval of prometheus in seconds (default: 1s)')
  parser.add_argument('--content_server_base_url', default='http://192.168.2.200',
                      help='the base url of the content server (default: "http://192.168.2.200"')
  parser.add_argument('--prometheus_url', default='http://192.168.2.10:9090',
                      help='the base url of the prometheus server (default: "http://192.168.2.10:9090"')

  args = parser.parse_args()

  print args

  global finished

  print "My pid is: ", os.getpid()

  size = args.size

  pool = Pool(args.pool)

  offset = 0

  previous_file_start_time = 0
  request_id = 0

  if(os.path.isfile(args.workload)  ==  False):
    print 'The workload file "' + args.workload +'" does not exist. Exiting'
    sys.exit()

  with open(args.workload, 'r') as f:
    lines = (line.split('\t') for line in f)

    for line in lines:
      request_id += 1
      # print line
      file_id = line[1]

      # print file_id
      session = requests.Session()
      r = grequests.get(args.content_server_base_url + delimiter + file_id +'.html',
                        hooks={'response': [hook_factory(request_id=request_id, session=session)]}, session=session)
      results[request_id] = dict()
      results[request_id]['file'] = file_id
      sleep_time = float(line[0]) - previous_file_start_time
      print "sleep_time =", sleep_time, "request = ", request_id, "file_id = ", file_id
      time.sleep(sleep_time)
      grequests.send(r, pool)
      results[request_id]['start'] = time.time() - start_time
      previous_file_start_time = float(line[0])
  
  pool.join()
  print "Finishing...."
  time.sleep(2)
  finished = True

  pprint(results)

  all_requests_received = 1

  average = 0
  for k in results.keys():
    average += float(results[k]['download_time'].replace(" ms", ''))
    if results[k]['status_code'] != 200:
      print "Status code of request " + str(k) + " was " + str(results[k]['status_code'])
      all_requests_received = 0
  average /= len(results)

  print "The program ran for " + str(time.time() - start_time) + " s\n"
  if all_requests_received == 1:
    print "All the requests were served correctly"
    print "Average Download Time = " + str(average)  + " ms", len(results),

if __name__ == "__main__" :
  main()  
 
