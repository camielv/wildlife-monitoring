# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 11:23:02 2013

@author: verschoor

- Creating point tracks.
  - A point track is created for every frame.
  - A point tracks starts in a certain frame.
  - A point tracks ends in a frame if no good match is found (Forward-Backward tracking).

"""

import os
import cv2
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from xml.dom.minidom import Document

feature_params = dict(maxCorners = 1000, qualityLevel = 0.01, minDistance = 10, blockSize = 19)
lk_params = dict(winSize  = (19, 19), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

class Detection():
  '''Class representing an detection'''
  def __init__(self, id, frame_id, bounding_box, real_id):
    self.alive = True
    self.id = id
    self.frames = [frame_id]
    self.tracks = dict()
    self.bounding_box = {frame_id: bounding_box}
    self.real_id = {frame_id: real_id}
    
  def __str__(self):
    # Todo finish
    return_string = "Alive: %d\n" % (int(self.alive))
    return_string += "Frames: %s\n" % ("".join(" " + str(frame_id) for frame_id in self.frames))
    return return_string

    
class Annotation():
  '''Class representing an annotation'''
  def __init__(self, frame_id, id, (xmin, ymin, xmax, ymax), lost, occluded, generated, label):
    self.frame_id = int(frame_id)
    self.id = int(id)
    self.bounding_box = (int(xmin), int(ymin), int(xmax), int(ymax))
    self.lost = bool(int(lost))
    self.occluded = bool(int(occluded))
    self.generated = bool(int(generated))
    self.label = label
    
  def __str__(self):
    # Todo finish
    return_string =  "Frame ID: %d\n" % (self.frame_id)
    return_string += "Annotation ID: %d\n" % (self.annotation_id)
    return_string += "Bounding box: (%d, %d, %d, %d)" % self.bounding_box
    return return_string

class Track():
  '''Class representing a point track'''
  def __init__(self, point, frame_nr):
    [[x, y]] = point
    self.X = [x]
    self.Y = [y]
    self.Z = [frame_nr]
    
  def add_point(self, point, frame_nr):
    [[x, y]] = point
    self.X.append(x)
    self.Y.append(y)
    self.Z.append(frame_nr)
    
  def get_point(self, frame_nr):
    index = self.Z.index(frame_nr)
    return self.X[index], self.Y[index]
    
  def __str__(self):
    return_string =  str(self.X) + "\n"
    return_string += str(self.Y) + "\n"
    return_string += str(self.Z) + "\n"
    return return_string


def get_annotations(annotation_name):
  '''Reads in the annotations given a file generated by the standard VATIC output'''
  annotations = dict()
  reader = csv.reader(open(annotation_name, 'rb'), delimiter=' ')
  
  # Sorts annotations per frame and id.
  for row in reader:
    annotation = Annotation(row[5], row[0], (row[1], row[2], row[3], row[4]), row[6], row[7], row[8], row[9])
    if annotation.frame_id not in annotations:
      # Add frame_id to dictionary if does not exist yet.
      annotations[annotation.frame_id] = dict()
    if annotation.occluded or annotation.lost:
      # Do not add if they are occluded (for now) and/or lost.
      continue
    # Add annotation
    annotations[annotation.frame_id][annotation.id] = annotation

  return annotations


def create_point_tracks(name, bounding_box, total, start_frame = 0, max_track_length = 20, draw = False):
  if start_frame > total - 1:
    return []
    
  # Initialize with first frame and second frame.
  image = cv2.imread(name + (("/image%.05d.jpg") % start_frame))
  
  # Select features within bounding box
  sub_image = image[bounding_box[0]:bounding_box[2], bounding_box[1]:bounding_box[3]]
  features = get_features(sub_image)
  
  if features == None:
    return []

  # Transform features to big image
  for i in xrange(len(features)):
    features[i][0][0] = features[i][0][0]+bounding_box[0]
    features[i][0][1] = features[i][0][1]+bounding_box[1]
  
  active_tracks = []
  dead_tracks = []
  for row in xrange(len(features)):
    active_tracks.append(Track(features[row], start_frame))
  
  for frame_nr in xrange(start_frame + 1, min(start_frame + max_track_length, total)):
    if len(features) == 0:
      # Break if no features anymore
      break
  
    #print "Features: %d Length: %d" % (len(features), track_length)
    if draw:
      draw_features(image, features)
    next_image = cv2.imread(name + (("/image%.05d.jpg") % frame_nr))

    ### Feature Selection method: Forward-Backward Tracking (Optical flow)
    # Forward in time
    forward_features, st, err = cv2.calcOpticalFlowPyrLK(image, next_image, features, None, **lk_params)
    # Backward in time
    backward_features, st, err = cv2.calcOpticalFlowPyrLK(next_image, image, forward_features, None, **lk_params)
    # Remove wrong matches
    distance = abs(features - backward_features).reshape(-1, 2).max(-1)
    matches = distance < 1
    matched_features = []
    new_active_tracks = []
    
    # Throw away all bad matches
    for i in range(len(matches)):
      if matches[i]:
        matched_features.append(forward_features[i])
        active_tracks[i].add_point(forward_features[i], frame_nr)
        new_active_tracks.append(active_tracks[i])
      else:
        dead_tracks.append(active_tracks[i])
        
    active_tracks = new_active_tracks
    features = np.array(matched_features)
    image = next_image.copy()

  return active_tracks
  
def create_tracks(annotation_location = 'annotations/cow_809_1.txt', video_location = 'videos/cow_809_1', stepsize = 10):
  '''Creates detection tracks hased on the stepsize'''
  annotations = get_annotations(annotation_location)
  detections = list()

  reader = csv.reader(open(video_location + '/info.txt', 'rb'), delimiter=' ')
  total_frames = int(reader.next()[1])
  
  for frame_nr in xrange(100, 100+5*stepsize, stepsize):
    for detection in detections:
      # Create point tracks within the detection box of stepsize
      if detection.alive and frame_nr-stepsize in detection.frames:
        # Get latest bounding_box and create tracks from there
        bounding_box = detection.bounding_box[frame_nr-stepsize]
        tracks = create_point_tracks(video_location, bounding_box, total_frames, frame_nr-stepsize, stepsize+1, True)
        if tracks:
          detections[detection.id].tracks[frame_nr] = tracks
        else:
          detections[detection.id].alive = False
      
    for annotation_id in annotations[frame_nr]:
      # For every annotation check whether the annotation fall inside the tracks of previous detections.
      annotation = annotations[frame_nr][annotation_id]
      bounding_box = annotation.bounding_box
      highest_freq = None
      highest_id = None
      # Todo fix that highest freq will get the annotation
      for detection in detections:
        if detection.alive and frame_nr in detection.tracks:
          # Check whether detection already is chosen
          tracks = detection.tracks[frame_nr]
          
          freq = 0
          for track in tracks:
            x, y = track.get_point(frame_nr)
            if x > bounding_box[0] and x < bounding_box[2] and y > bounding_box[1] and y < bounding_box[3]:
              freq += 1
          if freq > highest_freq:
            highest_freq = freq
            highest_id = detection.id

      if highest_id:
        # Found detection in tracks
        detections[highest_id].bounding_box[frame_nr] = bounding_box
        detections[highest_id].real_id[frame_nr] = annotation.id
        detections[highest_id].frames.append(frame_nr)
      else:
        # Create new record if no match is found
        detections.append(Detection(len(detections), frame_nr, bounding_box, annotation.id))
        
  # Plot the point tracks
  fig = plt.figure()
  ax = Axes3D(fig)
  ax.set_xlabel("x-axis")
  ax.set_ylabel("y-axis")
  ax.set_zlabel("time")
  colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
  for detection in detections:
    colour = colours.pop()
    colours.insert(0, colour)
    print detection.id, detection.real_id.values()
    for frame_nr in detection.tracks:
      for track in detection.tracks[frame_nr]:
        ax.plot(track.X, track.Y, zs=track.Z, color=colour)
  plt.show()  


def get_features(image):
  '''Creates features using goodFeaturesToTrack'''
  gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
  return cv2.goodFeaturesToTrack(gray_image, **feature_params)


def draw_features(image, features):
  '''Draws the features on the screen'''
  if features is not None:
    for x, y in features[:, 0]:
      cv2.circle(image, (x,y), 2, (255, 0, 0), -1)
  cv2.imshow('Features', image)
  cv2.waitKey(1)


def create_images(video_location = 'videos/GOPR0809_start_0_27_end_1_55.mp4', output_location = 'videos/cow_809_1'):
  '''Creates jpeg images of a video and a info file containing the amount of images'''
  capture = cv2.VideoCapture(video_location)
  try:
    print "Output directory created."
    os.mkdir(output_location)
  except:
    print "Ouput directory is already existing."
  
  frame_nr = 0
  while True:
    print frame_nr
    ret, image = capture.read()
    if not ret:
      break
    cv2.imwrite(output_location + ("/image%.05d.jpg" % frame_nr), image)
    frame_nr += 1

  capture.close()
  writer = csv.writer(open(output_location + '/info.txt', 'w'), delimiter =' ')
  writer.writerow(["Frames:", frame_nr])

def create_voc_pascal_annotations(video_location = 'videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_location = 'annotations/cow_809_1.txt', output_location = 'VOC_cow_809_1', database = 'The Verschoor 2013 Aerial Cow Database', annotator = 'Verschoor 2013'):
  try:
    print "Output directory created."
    os.mkdir(output_location)
  except:
    print "Ouput directory is already existing. Please check or change output name"
    #return

  capture = cv2.VideoCapture(video_location)
  VOC_image_location = output_location + '/JPEGimages'
  VOC_annotation_location = output_location + '/Annotations'
  #os.mkdir(VOC_image_location)
  #os.mkdir(VOC_annotation_location)
  
  annotations = get_annotations(annotation_location)
  
  frame_nr = 0
  while True:
    print frame_nr
    ret, image = capture.read()
    
    if not ret:
      break
    if len(annotations[frame_nr]) == 0:
      frame_nr += 1
      continue

    height, width, depth = image.shape
    
    doc = Document()
    annotation_xml = doc.createElement('annotation')
    doc.appendChild(annotation_xml)
    
    annotation_folder = doc.createElement('folder')
    folder_text = doc.createTextNode(output_location)
    annotation_folder.appendChild(folder_text)
    annotation_xml.appendChild(annotation_folder)
    
    annotation_filename = doc.createElement('filename')
    filename_text = doc.createTextNode('%.06d.jpg' % frame_nr)
    annotation_filename.appendChild(filename_text)
    annotation_xml.appendChild(annotation_filename)
    
    annotation_source = doc.createElement('source')
    annotation_xml.appendChild(annotation_source)    
    
    annotation_database = doc.createElement('database')
    database_text = doc.createTextNode(database)
    annotation_database.appendChild(database_text)
    annotation_source.appendChild(annotation_database)
    
    annotation_annotation = doc.createElement('annotation')
    annotation_text = doc.createTextNode(annotator)
    annotation_annotation.appendChild(annotation_text)
    annotation_source.appendChild(annotation_annotation)

    annotation_owner = doc.createElement('owner')
    annotation_xml.appendChild(annotation_owner)
    
    annotation_size = doc.createElement('size')
    annotation_xml.appendChild(annotation_size)
    
    annotation_segmented = doc.createElement('segmented')
    annotation_xml.appendChild(annotation_segmented)
    
    for id in annotations[frame_nr]:
      # Create annotation
      annotation = annotations[frame_nr][id]
      annotation_object = doc.createElement('object')
      annotation_xml.appendChild(annotation_object)
      
      annotation_object_name = doc.createElement('name')
      object_text = doc.createTextNode(annotation.label)
      annotation_object_name.appendChild(object_text)
      annotation_object.appendChild(annotation_object_name)


    print doc.toprettyxml()
    return
    
    # Write image
    #cv2.imwrite(VOC_image_location + ("/%.06d.jpg" % frame_nr), image)
    
    frame_nr += 1
    
    
  
if __name__ == '__main__':
  #create_images()
  #create_tracks()
  create_voc_pascal_annotations()