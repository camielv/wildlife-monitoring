# -*- coding: utf-8 -*-
"""
Some comments and so on here

"""

import csv

from ..datastructures.annotation import Annotation
from ..datastructures.detection import Detection
from ..datastructures.track import Track

class Parser():
  """This class contains various function to parse data"""
  
  def __init__(self):
    pass
  
  def vatic_parser(self, file_path, occluded=True):
    """This function parses a vatic dump txt file and converts it to a 
    dictionary sorted by frame id and annotation id"""
  
    annotations_file = csv.reader(open(file_path, 'rb'), delimiter=' ')
    annotations = dict()
    
    for row in annotations_file:
      annotation = Annotation(row[5], row[0], (row[1], row[2], row[3], row[4]), row[6], row[7], row[8], row[9])

      if (occluded and annotation.occluded) or annotation.lost:
        continue
      elif annotation.frame_id not in annotations:
        annotations[annotation.frame_id] = dict()    
      annotations[annotation.frame_id][annotation.id] = annotation
  
    return annotations
    

  def detection_parser(self, file_path, threshold = -1):
    """This functions parses a dump created by the detector of Felzenswalb
    and converts it to a dictionary sort by frame id"""
    id = 0  
    detections_file = csv.reader(open(file_path, 'rb'), delimiter=' ')
    detections = dict()
    
    for row in detections_file:
      detection = Detection(row[0], (row[1], row[2], row[3], row[4]), row[5])
      
      if float(row[5]) < threshold:
        continue
      elif int(row[0]) not in detections:
        detections[int(row[0])] = dict()

      detections[int(row[0])][id] = detection
      id += 1
      
    return detections


  def track_parser(self, file_path):
    """This functions parses a dump txt file and converts it to a list of
    tracks"""
  
    tracks_file = csv.reader(open(file_path, 'rb'), delimiter=' ')
    tracks_list = list(tracks_file)
    tracks = list()
    
    Z = map(float, tracks_list[len(tracks_list) - 1])
    for i in range(0, len(tracks_list) - 2, 2):
      X = map(float, tracks_list[i])
      Y = map(float, tracks_list[i+1])
      tracks.append(Track(track=[X,Y,Z]))

    return tracks
