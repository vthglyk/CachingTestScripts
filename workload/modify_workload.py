import sys
import os
import argparse
from random import randint
from pprint import pprint
def main() :

  parser = argparse.ArgumentParser(description='Modify Workload')
  parser.add_argument('--input', '-i', required=True,
                      help='name of the file describing the workload (REQUIRED)')
  parser.add_argument('--output', '-o', required=True,
                      help='output file (REQUIRED)')
  parser.add_argument('--size', '-s', type=int, required=True,
                      help='the catalogue size')
  parser.add_argument('--no_requests', '-n', type=int, default=1000,
                      help='number of requests (Default: 1000)')


  args = parser.parse_args()
  
  lines = []
  with open(args.input, 'r') as f:
    for i in range(args.no_requests):
      try:
        lines.append(next(f).split('\t'))
      except StopIteration:
        print "The file had only " + str(i) + " requests, but --no_requests was set to " + str(args.no_requests)
        break


  with open(args.output, 'w') as f:
    for i in range(len(lines)):
      id = int(lines[i][1])

      if id  >= args.size:
        lines[i][1] = randint(0,args.size - 1)
       
      f.write(str(lines[i][0]) + '\t' + str(lines[i][1]) + '\t' + str(lines[i][2]))
      

if __name__ == "__main__" :
  main()
