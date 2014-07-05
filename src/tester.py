# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:17:20 2014

@author: camiel
"""

import csv
import matplotlib.pyplot as plt
import numpy
from matplotlib.font_manager import FontProperties
#from modules.utils.parser import Parser
#from modules.utils.visualizer import Visualizer
plt.yticks(numpy.arange(0, 1.01, 0.1))
plt.xticks(numpy.arange(0, 1.01, 0.1))
names = [("DPM", "dpm-precision.txt", "dpm-recall.txt"), ("Exemplar SVM", "esvm-precision.txt", "esvm-recall.txt"), ("Color DPM", "hogdpm-precision.txt", "hogdpm-recall.txt")]
for name in names:
  (sort, precision_location, recall_location) = name
  precision_file = csv.reader(open("plots/%s" % precision_location, 'rb'))
  recall_file = csv.reader(open("plots/%s" % recall_location, 'rb'))
  recall = list()
  precision = list()
  for line in precision_file:
    precision.append(float(line[0]))
  for line in recall_file:
    recall.append(float(line[0]))
    
  plt.plot(recall, precision, label=sort)
  plt.ylabel('Precision')
  plt.xlabel('Recall')
  plt.xlim(0, 1.0)
  plt.ylim(0, 1.0)

fontP = FontProperties()
fontP.set_size("small")
plt.legend(prop=fontP)
plt.grid()
plt.savefig("%s.pdf" % ("PR-CURVE-DETECTIONS"))
plt.clf()

'''
#visualizer = Visualizer()
#visualizer.video_to_images("../dataset/videos/COW809_1.MP4", "../dataset/images/COW809_1")
#visualizer.visualize_annotations("../dataset/videos/COW809_1.MP4", "../dataset/annotations/COW809_1.txt", True)

parser = Parser()
#tracks = parser.track_parser("../tracks/5/5_000001.txt")
annotations = parser.vatic_parser("../dataset/annotations/COW810_1.txt")
test = set()
count = 0
frames = 2694
steps = 40

for id in range(0, frames, steps):
  if id in annotations:
    test = test.union(set(annotations[id].keys()))
    count += len(annotations[id])
  
print len(test)
print count
#detections = parser.detection_parser("../detections/COW809_1_2.txt")
#print len(detections)
#for key in detections:
#  print detections[key].pop()
#  break
'''