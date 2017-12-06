import matplotlib
matplotlib.rcParams['text.usetex'] = True
import matplotlib.pyplot as plt 
import seaborn
seaborn.set(font_scale=2.3)
seaborn.set_style("whitegrid")
import csv

base_filename = "bitcoin_block_generation"
width = 4 

with open("bitcoin_block_generation_distribution.csv", 'rb') as csvfile:
	data = csv.reader(csvfile, delimiter=',')
	rows = []
	for row in data:
		rows.append(row)

x = rows[0][1:]
print x
y0 = rows[1][1:]
print y0
y0 = [float(i)/100 for i in y0]
y0_label = "Measured distribution"
y1 = rows[2][1:]
print y1
y1 = [float(i)/100 for i in y1]
y1_label = "Karame et al."

plt.plot(x, y0, label=y0_label, linewidth=width)
plt.plot(x, y1, label=y1_label, linewidth=width)

font = {'family' : 'normal',
	'weight' : 'normal',
	'size'   : 22}
plt.rc('font', **font)

plt.xlabel("Block size (kb)")
plt.ylabel("Fraction")
#plt.title("From block height 360000 (June 2015)")
#plt.ylim(ymin=0)
#plt.legend(['True Positive Ratio'], loc='lower right')
plt.legend(loc='upper right', prop={'size':20})
#plt.grid(axis='y')
#plt.grid(axis='x')
fig = plt.gcf()
fig.tight_layout()
fig.set_size_inches(10,7)
plt.savefig(base_filename+".eps")

