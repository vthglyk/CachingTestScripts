import sys
import os
import argparse
from pprint import pprint

def main() :

  parser = argparse.ArgumentParser(description='Modify Catalogue')
  parser.add_argument('--input', '-i', required=True,
                      help='name of the file describing the catalogue (REQUIRED)')
  parser.add_argument('--output', '-o', required=True,
                      help='output file (REQUIRED)')
  parser.add_argument('--size', '-s', type=int, required=True,
                      help='the catalogue size')


  args = parser.parse_args()
  
  lines = []
  with open(args.input, 'r') as f:
    for i in range(args.size):
      try:
        lines.append(next(f).split('\t'))
      except StopIteration:
        print "The file had only " + str(i) + " entries, but --size was set to " + str(args.size)
        break

  with open(args.output, 'w') as f:
    for i in range(len(lines)):
      f.write(lines[i][0] + '\t' + lines[i][1] + '\t' + lines[i][2] + '\t' + lines[i][3])
      
  

if __name__ == "__main__" :
  main()
