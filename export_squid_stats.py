import time
import re
import argparse
from subprocess import check_output
from prometheus_client import start_http_server, Gauge

peer_address = None
client_address = None

def extract_metric(output, metric):

  if metric == "cacheClientIcpHits":
    help = output.split('cacheClientHttpHits.' + str(peer_address))[-1].split(":")
  elif metric == "cacheClientIcpRequests":
    help = output.split(metric + '.' + str(peer_address))[-1].split(":")
  elif metric == "cacheClientHttpHits" or metric == "cacheClientHttpRequests":
    help = output.split(metric + '.' + str(client_address))[-1].split(":")
  else:
    help = output.split(metric)[-1].split(":")


  if help[1] == '':
    return 0
  else:
    return int(help[1].split("\n")[0])


def main():

  parser = argparse.ArgumentParser(description='Export cache metrics to prometheus')
  parser.add_argument('--peer_address', '-p', required=True,
                      help='the ip address of the cache peer (REQUIRED)')
  parser.add_argument('--client_address', '-c', required=True,
                      help='the ip address of the client (REQUIRED)')
  args = parser.parse_args()

  global peer_address
  global client_address

  peer_address = args.peer_address
  client_address = args.client_address

  start_http_server(9101)
  # Generate some requests.
  gCacheClientIcpHits = Gauge('cache_client_icp_hits', 'Advertises the value of the metric "cacheClientIcpHits" of squid')
  gCacheClientIcpRequests = Gauge('cache_client_icp_requests', 'Advertises the value of the metric "cacheClientIcpRequests" of squid')
  gCacheClientHttpHits = Gauge('cache_client_http_hits', 'Advertises the value of the metric "cacheClientHttpHits" of squid')
  gCacheClientHttpRequests = Gauge('cache_client_http_requests', 'Advertises the value of the metric "cacheClientHttpRequests" of squid')
  gCacheRequestHitRatio1 = Gauge('cache_request_hit_ratio_1', 'Advertises the value of the metric "cacheRequestHitRatio.1" of squid')
  gCacheRequestByteRatio1 = Gauge('cache_request_byte_ratio_1', 'Advertises the value of the metric "cacheRequestByteRatio.1" of squid')
  gCacheRequestHitRatio5 = Gauge('cache_request_hit_ratio_5', 'Advertises the value of the metric "cacheRequestHitRatio.5" of squid')
  gCacheRequestByteRatio5 = Gauge('cache_request_byte_ratio_5', 'Advertises the value of the metric "cacheRequestByteRatio.5" of squid')
  gCacheRequestHitRatio60 = Gauge('cache_request_hit_ratio_60', 'Advertises the value of the metric "cacheRequestHitRatio.60" of squid')
  gCacheRequestByteRatio60 = Gauge('cache_request_byte_ratio_60', 'Advertises the value of the metric "cacheRequestByteRatio.60" of squid')
  gCacheCpuUsage = Gauge('cache_cpu_usage', 'Advertises the value of the metric "cacheCpuUsage" of squid')
  gCacheNumObjCount = Gauge('cache_num_obj_count', 'Advertises the value of the metric "cacheNumObjCount" of squid')
  gCacheProtoClientHttpRequests = Gauge('cache_proto_client_http_requests', 'Advertises the value of the metric "cacheProtoClientHttpRequests" of squid')
  gCacheHttpHits = Gauge('cache_http_hits', 'Advertises the value of the metric "cacheHttpHits" of squid')

  gNodeCpu = Gauge('node_cpu', 'Advertises the cpu usage', ['cpu', 'mode'])

  while True:
    
    time.sleep(1);

    output = check_output(["snmpwalk", "-v", "1", "-c", "public", "-m", "SQUID-MIB", "-Cc", "localhost:3401", "squid"])
    
    gCacheClientIcpHits.set(extract_metric(output, "cacheClientIcpHits"))
    gCacheClientIcpRequests.set(extract_metric(output, "cacheClientIcpRequests"))
    gCacheClientHttpHits.set(extract_metric(output, "cacheClientHttpHits"))
    gCacheClientHttpRequests.set(extract_metric(output, "cacheClientHttpRequests"))
    gCacheRequestHitRatio1.set(extract_metric(output, "cacheRequestHitRatio.1"))
    gCacheRequestByteRatio1.set(extract_metric(output, "cacheRequestByteRatio.1"))
    gCacheRequestHitRatio5.set(extract_metric(output, "cacheRequestHitRatio.5"))
    gCacheRequestByteRatio5.set(extract_metric(output, "cacheRequestByteRatio.5"))
    gCacheRequestHitRatio60.set(extract_metric(output, "cacheRequestHitRatio.60"))
    gCacheRequestByteRatio60.set(extract_metric(output, "cacheRequestByteRatio.60"))
    gCacheCpuUsage.set(extract_metric(output, "cacheCpuUsage"))
    gCacheNumObjCount.set(extract_metric(output, "cacheNumObjCount"))
    gCacheProtoClientHttpRequests.set(extract_metric(output, "cacheProtoClientHttpRequests"))
    gCacheHttpHits.set(extract_metric(output, "cacheHttpHits"))
    
    output = check_output(["top", "-b", "-n1"])
    help = output.split('Cpu(s):')[-1].split('\n')[0].split(' ')
    help2 = [item for item in help if re.match('\d+\.\d+$', item)]
    gNodeCpu.labels(cpu='cpu0', mode='us').set(float(help2[0]))
    gNodeCpu.labels(cpu='cpu0', mode='sy').set(float(help2[1]))
    gNodeCpu.labels(cpu='cpu0', mode='ni').set(float(help2[2]))
    gNodeCpu.labels(cpu='cpu0', mode='id').set(float(help2[3]))
    gNodeCpu.labels(cpu='cpu0', mode='wa').set(float(help2[4]))
    gNodeCpu.labels(cpu='cpu0', mode='hi').set(float(help2[5]))
    gNodeCpu.labels(cpu='cpu0', mode='si').set(float(help2[6]))
    gNodeCpu.labels(cpu='cpu0', mode='st').set(float(help2[7]))


if __name__ == '__main__':
  # Start up the server to expose the metrics.
  main()
