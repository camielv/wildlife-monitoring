# -*- coding: utf-8 -*-
"""
Created on Thu May  8 17:15:21 2014

@author: camiel
"""
import os
import csv
import random
import cv2

from .parser import Parser


class Visualizer():
  """This class contains various methods to display data"""
  
  def __init__(self):
    pass
  
  def visualize_annotations(self, video_file_path, annotation_file_path, record=False, output_name="../output.avi"):
    """This function visualizes the annotations from an annotation file on
    the corresponding video"""
    
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
    
  def video_to_images(self, video_file_path, output_folder):
    """This function converts a video to images"""
    
    if os.path.isdir(output_folder):
      print "Error: Output directory already exists"
      return
      
    os.makedirs(output_folder)
    
    player = cv2.VideoCapture(video_file_path)
    ret, rgb_frame = player.read()

    frame_id = 0
    
    while(ret):
      filename = '%s/%.06d.png' % (output_folder, frame_id)
      cv2.imwrite(filename, rgb_frame)
            
      ret, rgb_frame = player.read()
      print "Frame: %.06d" % (frame_id)
      frame_id += 1
    
    player.release()
    writer = csv.writer(open(output_folder + '/info.txt', 'w'), delimiter =' ')
    writer.writerow(["Frames:", frame_id - 1])
    
  def cut_annotations(self, video_file_path, annotation_file_path, output_folder):
    """This functions converts a video of annotations to images of the
    annotations"""
    
    if os.path.isdir(output_folder):
      print "Error: Output directory already exists"
      return
      
    os.makedirs(output_folder)
    
    parser = Parser()
    annotations = parser.vatic_parser(annotation_file_path)

    player = cv2.VideoCapture(video_file_path)
    ret, rgb_frame = player.read()

    annotation_nr = 0
    frame_id = 0
    
    while(ret):
      if frame_id in annotations:
        frame_annotations = annotations[frame_id]
        for annotation_id in frame_annotations:
          annotation = frame_annotations[annotation_id]
          if not annotation.lost:
            (xmin, ymin, xmax, ymax) = annotation.bounding_box
            crop_frame = rgb_frame[ymin:ymax, xmin:xmax]
            filename = '%s/%.06d.png' % (output_folder, annotation_nr)
            cv2.imwrite(filename, crop_frame)
            annotation_nr += 1
            
      ret, rgb_frame = player.read()
      print "Frame: %.06d Annotations: %.06d" % (frame_id, annotation_nr)
      frame_id += 1

    player.release()

 
  def visualize_detections(self, video_file_path, detection_file_path):
    """This function visualizes the annotations from an detection file on
    the corresponding video"""
    
    pass