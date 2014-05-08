# -*- coding: utf-8 -*-
"""
Created on Thu May  8 17:15:21 2014

@author: camiel
"""
import random
import cv2

from .parser import Parser


class Visualizer():
  def __init__(self):
    pass
  
  def visualize_annotations(self, video_file_path, annotation_file_path, record=False, output_name="../output.avi"):
    '''This function visualizes the annotations from an annotation file on
    the corresponding video'''
    
    parser = Parser()
    annotations = parser.vatic_parser(annotation_file_path)
    
    # Find all annotation ids
    annotation_ids = set()
    for frame_id in annotations:
      annotation_ids = annotation_ids.union(annotations[frame_id].keys())
    
    # Create random colours
    colours = dict()
    for annotation_id in annotation_ids:
      colours[annotation_id] = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
    
    # Initialize player
    player = cv2.VideoCapture(video_file_path)
    ret, image = player.read()
    
    # Initialize recorder
    if record:
      recorder = cv2.VideoWriter(output_name, 1196444237, int(round(player.get(cv2.cv.CV_CAP_PROP_FPS))), (int(player.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(player.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))))

    # Display annotations    
    frame_id = 0
    while(ret):
      if frame_id in annotations:
        objects = annotations[frame_id]
        for object_id in objects:
          annotation = objects[object_id]
          if not annotation.lost:
            (xmin, ymin, xmax, ymax) = annotation.bounding_box
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), colours[object_id], 2)
      cv2.imshow("Video", image)
      
      if record:
        recorder.write(image)
        
      ret, image = player.read()
      frame_id += 1
      
      if cv2.waitKey(1) == ord('q'):
        break

    player.release()
    if record:
      recorder.release()
    
    cv2.destroyWindow("Video")
    
 
  def visualize_detections(self, video_file_path, detection_file_path):
    pass