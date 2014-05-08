# -*- coding: utf-8 -*-
"""
Some comments and so on here

"""

import csv

from ..datastructures.annotation import Annotation
from ..datastructures.detection import Detection

class Parser():
  def __init__(self):
    pass
  
  def vatic_parser(self, filepath):
    ''' This function parses a vatic dump txt file and converts it to a 
    dictionary sorted by frame id and annotation id '''
  
    annotations_file = csv.reader(open(filepath, 'rb'), delimiter=' ')
    annotations = dict()
    
    for row in annotations_file:
      annotation = Annotation(row[5], row[0], (row[1], row[2], row[3], row[4]), row[6], row[7], row[8], row[9])
      
      if annotation.frame_id not in annotations:
        annotations[annotation.frame_id] = dict()
  
      annotations[annotation.frame_id][annotation.id] = annotation
  
    return annotations
    
  def detection_parser(self, filepath):
    ''' This functions parses a dump created by the detector of Felzenswalb
    and converts it to a dictionary sort by frame id '''
  
    detections_file = csv.reader(open(filepath, 'rb'), delimiter=' ')
    detections = dict()
    
    for row in detections_file:
      detection = Detection(row[0], (row[1], row[2], row[3], row[4]), row[5])
      
      if int(row[0]) not in detections:
        detections[int(row[0])] = list()
      detections[int(row[0])].append(detection)
      
    return detections