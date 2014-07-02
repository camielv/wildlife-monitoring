# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:17:20 2014

@author: camiel
"""

from modules.utils.parser import Parser
#from modules.utils.visualizer import Visualizer



#visualizer = Visualizer()
#visualizer.video_to_images("../dataset/videos/COW809_1.MP4", "../dataset/images/COW809_1")
#visualizer.visualize_annotations("../dataset/videos/COW809_1.MP4", "../dataset/annotations/COW809_1.txt", True)

parser = Parser()
#tracks = parser.track_parser("../tracks/5/5_000001.txt")
annotations = parser.vatic_parser("../dataset/annotations/COW810_1.txt")
test = set()
for id in annotations:
  test = test.union(set(annotations[id].keys()))
print len(test)
#detections = parser.detection_parser("../detections/COW809_1_2.txt")
#print len(detections)
#for key in detections:
#  print detections[key].pop()
#  break
