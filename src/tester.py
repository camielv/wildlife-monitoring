# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:17:20 2014

@author: camiel
"""

from modules.parsers.parsers import Parser

parser = Parser()

annotations = parser.vatic_parser("../dataset/annotations/COW809_1.txt")
print len(annotations)
detections = parser.detection_parser("../detections/COW809_1_2.txt")
print len(detections)
for key in detections:
  print detections[key].pop()
  break