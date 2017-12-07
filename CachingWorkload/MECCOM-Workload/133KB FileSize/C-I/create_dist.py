import random
import numpy as np
import threading



p = 0.5;
q = 0;

doc_file = "docs"
workload_file = "workload"

# reads docs.all file
docs = [];
f = open(doc_file + ".all", "r")
for index, line in enumerate(f):
	arguments = line.strip().split("\t");
	if (len(arguments) != 4):
		break;
	docs.append(arguments);
f.close()

popularities = [];
popularities[:] = [float(doc[1]) for doc in docs];
sortedpopularities = np.sort(popularities);
prob = 1. * np.arange(len(popularities))/(len(popularities) - 1);
#print prob
#print sortedpopularities
#plt.plot( sortedpopularities, prob);
#plt.show()

newdocs = [];
mapping = {};

# creates new identifiers for second file
for doc in docs:
	pi = random.random();
	if (pi >= p):
		new_id = doc[0] + "_0";
	else:
		while True:
			qi = random.random();
			if (qi >= q):
				new_id = doc[0];
			else:
				new_id = str(np.argmin(np.abs(prob - qi)))
			if mapping.get(new_id, -1) == -1:
				break
	mapping[new_id] = doc[0];
	doc[0] = new_id;
	newdocs.append(doc);

# creates second docs.all file
f = open(doc_file + str(p) + "-" + str(q) + "_b.all", "w")
for index, line in enumerate(newdocs):
	f.write(str(line[0]) + '\t' + str(line[1]) + '\t' + str(line[2]) + '\t' + str(line[3]) + '\n');
f.close();

# reads second workload.all file
workload_data = []
f = open(workload_file + ".all2", "r")
for index, line in enumerate(f):
	arguments = line.strip().split("\t");
	print index
	if (len(arguments) != 3):
		continue;
	arguments[1] = mapping.keys()[mapping.values().index(str(arguments[1]))];
	workload_data.append(arguments);
f.close();

# rewrites second workload.all file
f = open(workload_file + str(p) + "-" + str(q) +"_b.all", "w")
for index, line in enumerate(workload_data):
	f.write(str(line[0]) + '\t' + str(line[1]) + '\t' + str(line[2]) + '\n');
f.close();
