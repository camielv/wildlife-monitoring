# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:17:20 2014

@author: camiel
"""

from modules.utils.parser import Parser
from modules.utils.visualizer import Visualizer

visualizer = Visualizer()
visualizer.visualize_annotations("../dataset/videos/COW809_1.MP4", "../dataset/annotations/COW809_1.txt", True)


parser = Parser()
annotations = parser.vatic_parser("../dataset/annotations/COW809_1.txt")
print len(annotations)
detections = parser.detection_parser("../detections/COW809_1_2.txt")
print len(detections)
for key in detections:
  print detections[key].pop()
  break
