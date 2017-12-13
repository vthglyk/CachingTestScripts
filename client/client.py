import requests
import grequests
from threading import Thread
import sys
import time
import os
import argparse
import json
from gevent.pool import Pool
import subprocess

results = dict()
prometheus = list()
start_time = time.time()
prometheus_stats_file = 'prometheus_stats'
grequests_stats_file = 'grequests_stats'
prometheus_query = '''{__name__=~"^cache.*"} or node_cpu or {__name__=~"^node_memory_Mem.*"} 
                      or {__name__=~"^node_disk.*"} or {__name__=~"^node_network.*"}'''
delimiter = '/'  # '/' for testing, '?' for debugging
finished = False
headers = {'Accept-Encoding' : 'bytes'}


def query_prometheus(prometheus_query_interval, prometheus_url, prometheus_job):
    global finished
    counter = 0

    while finished == False:
        # print finished, time.time(), prometheus_query_interval, prometheus_url
        stat = dict()
        counter += 1

        url = prometheus_url + "/api/v1/query?query=" + prometheus_query
        r = requests.get(url)
        content = json.loads(r.content)

        stat['time'] = time.time()
        stat['metrics'] = dict()

        for i in content['data']['result']:
            if i['metric']['job'] != prometheus_job and i['metric']['__name__'] != 'cache_client_icp_hits':
                continue

            metric_name = i['metric']['__name__']

            if i['metric']['__name__'] == 'node_cpu':
                cpu = i['metric']['cpu']
                if cpu not in stat['metrics']:
                    stat['metrics'][cpu] = list()

                cpu_stat = dict()
                cpu_stat['mode'] = i['metric']['mode']
                cpu_stat['value'] = float(i['value'][1])
                stat['metrics'][cpu].append(cpu_stat)

            elif 'node_network' in i['metric']['__name__']:
                device = i['metric']['device']
                if device == 'lo':
                    continue
                if device not in stat['metrics']:
                    stat['metrics'][device] = list()

                device_stat = dict()
                device_stat['__name__'] = i['metric']['__name__']
                device_stat['value'] = float(i['value'][1])
                stat['metrics'][device].append(device_stat)

            else:
                if metric_name == 'cache_client_icp_hits' and i['metric']['job'] != prometheus_job:
                    stat['metrics'][metric_name + '_peer'] = float(i['value'][1])
                else:
                    stat['metrics'][metric_name] = float(i['value'][1])

        prometheus.append(stat)
        time.sleep(prometheus_query_interval)
        # print len(r.content)


def hook_factory(*factory_args, **factory_kwargs):
    def response_hook(res, *request_args, **request_kwargs):
        # subtract always the start_time to get the time relative to the start of the program
        latency = time.time() - start_time
        size = len(res.content)
        dtime = time.time() - start_time
        id = factory_kwargs['request_id']
        session = factory_kwargs['session']
        file = res.url.split(delimiter)[-1].split('.')[0]
        print file, id, size

        results[id]['end'] = dtime
        results[id]['latency'] = latency
        results[id]['size'] = size
        results[id]['download_time'] = str((results[id]['end'] - results[id]['start']) * 1000) + ' ms'
        results[id]['status_code'] = res.status_code
        results[id]['X-Cache'] = res.headers['X-Cache']
        results[id]['X-Cache-Lookup'] = res.headers['X-Cache-Lookup']

        return None  # or the modified response

    return response_hook


def main():
    parser = argparse.ArgumentParser(description='Simulate client behaviour')
    parser.add_argument('--mode', '-m', default='normal', choices=['normal', 'disjoint', 'reverse'],
                        help='mode of client (default: normal)')
    parser.add_argument('--workload', '-w', required=True,
                        help='name of the file describing the workload (REQUIRED)')
    parser.add_argument('--output_folder', default='results/',
                        help='name of output folder (default: "results/{workload}"). It will be created automatically if non-existent. ' +
                             'The prometheus stats will be saved in the file "' + prometheus_stats_file + '" and the ' +
                             'grequests stats in the file "' + grequests_stats_file + '"')
    parser.add_argument('--offset', '-o', default=100000, type=int,
                        help='offset  (default: 100000)')
    parser.add_argument('--pool', '-p', default=1, type=int,
                        help='size of the pool (default: 1)')
    parser.add_argument('--size', '-s', type=int,
                        help='the catalogue size')
    parser.add_argument('--catalogue', '-c', type=int,
                        help='the catalogue')
    parser.add_argument('--prometheus_query_interval', '-q', default=1, type=int,
                        help='the query interval of prometheus in seconds (default: 1s)')
    parser.add_argument('--content_server_base_url', default='http://192.168.2.200',
                        help='the base url of the content server (default: "http://192.168.2.200"')
    parser.add_argument('--prometheus_url', default='http://192.168.2.10:9090',
                        help='the base url of the prometheus server (default: "http://192.168.2.10:9090"')
    parser.add_argument('--prometheus_job', required=True,
                        help='the prometheus job exporting the metrics of the cache')

    args = parser.parse_args()

    print args.output_folder
    if args.output_folder == 'results/':
        args.output_folder += args.workload
    print args.output_folder
    print args

    global finished

    print "My pid is: ", os.getpid()

    if args.mode == 'reverse':
        if args.size is None and args.catalogue is None:
            parser.error("reverse mode requires --size or catalogue")
        if args.catalogue is not None:
            with open(args.catalogue) as f:
                size = 0
                for line in f:
                    size += 1;
        else:
            size = args.size

    # print "args.pool", args.pool
    # print "args.offset", args.offset
    # print "args.size", args.size, size
    pool = Pool(args.pool)

    if args.mode == 'disjoint':
        offset = args.offset
    else:
        offset = 0

    previous_file_start_time = 0
    request_id = 0

    # t = Timer(args.prometheus_query_interval, query_prometheus, args=[args.prometheus_query_interval, args.prometheus_url])
    # t.start()
    # t = Timer(1, hello, args=[args.prometheus_query_interval, args.prometheus_url])
    # t.start()
    if (os.path.isfile(args.workload) == False):
        print 'The workload file "' + args.workload + '" does not exist. Exiting'
        sys.exit()
    thread = Thread(target=query_prometheus,
                    args=[args.prometheus_query_interval, args.prometheus_url, args.prometheus_job])

    try:
        thread.start()

        with open(args.workload, 'r') as f:
            lines = (line.split('\t') for line in f)

            for line in lines:
                request_id += 1
                # print line
                if args.mode == 'reverse':
                    file_id = str(size - int(line[1]) - 1)
                elif args.mode == 'disjoint':
                    file_id = str(int(line[1]) + offset)
                elif args.mode == 'normal':
                    file_id = line[1]

                # print file_id
                session = requests.Session()
                r = grequests.get(args.content_server_base_url + delimiter + file_id + '.html',
                                  hooks={'response': [hook_factory(request_id=request_id, session=session)]},
                                  session=session,
                                  headers=headers)
                results[request_id] = dict()
                results[request_id]['file'] = file_id
                sleep_time = float(line[0]) - previous_file_start_time
                print "sleep_time =", sleep_time, "request = ", request_id, "file_id = ", file_id
                time.sleep(sleep_time)
                grequests.send(r, pool)
                results[request_id]['start'] = time.time() - start_time
                previous_file_start_time = float(line[0])

    except (KeyboardInterrupt, SystemExit):
        print "Terminating due to Interrupt"
        finished = True
        sys.exit()

    pool.join()
    print "Finishing...."
    time.sleep(2 * args.prometheus_query_interval)
    finished = True

    # pprint(results)
    # pprint(prometheus)

    all_requests_received = 1

    # Print original times and test times
    with open(args.workload, 'r') as f:
        generator_lines = (line.split('\t') for line in f)
        lines = list(generator_lines)

        for k in results.keys():
            print k, results[k]['start'], lines[k - 1][0], results[k]['start'] - float(lines[k - 1][0])
            if results[k]['status_code'] != 200:
                print "Status code of request " + str(k) + " was " + str(results[k]['status_code'])
                all_requests_received = 0

    print "The program ran for " + str(time.time() - start_time) + " s\n"
    if all_requests_received == 1:
        print "All the requests were served correctly"

    if (os.path.isdir(args.output_folder) == False):
        print "The output folder " + args.output_folder + " does not exist. It will be automatically created."

        try:
            output = subprocess.check_output(["mkdir", "-p", args.output_folder])
            print "The output folder was created successfully!"
        except subprocess.CalledProcessError as grepexc:
            print "Error while creating the output folder", grepexc.returncode, grepexc.output

    with open(args.output_folder + '/' + prometheus_stats_file, 'w') as f:
        json.dump(prometheus, f)

    with open(args.output_folder + '/' + grequests_stats_file, 'w') as f:
        f.write("The program ran for " + str(time.time() - start_time) + " s\n")
        if all_requests_received == 1:
            f.write("All the requests were served correctly")
        json.dump(results, f)


if __name__ == "__main__":
    main()