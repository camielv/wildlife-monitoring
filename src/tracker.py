# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 11:23:02 2013

@author: verschoor

- Creating point tracks.
  - A point track is created for every frame.
  - A point tracks starts in a certain frame.
  - A point tracks ends in a frame if no good match is found (Forward-Backward tracking).

"""
import time
import os
import cv2
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from xml.dom.minidom import Document

from modules.datastructures.annotation import Annotation
from modules.datastructures.detection import Detection
from modules.datastructures.track import Track

# Settings
feature_params = dict(maxCorners = 10000, qualityLevel = 0.01, minDistance = 5, blockSize = 19)
lk_params = dict(winSize  = (19, 19), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
ID = 0


def create_point_tracks(name, bounding_box, total, start_frame = 0, max_track_length = 20, draw = False):
  if start_frame > total - 1:
    return []
    
  # Initialize with first frame and second frame.
  image = cv2.imread(name + (("/image%.05d.jpg") % start_frame))
  
  # Select features within bounding box if given
  sub_image = image[bounding_box[0]:bounding_box[2], bounding_box[1]:bounding_box[3]]
  features = get_features(sub_image)

  if features == None:
    return []

  # Transform features to big image if bounding box
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

  return active_tracks, dead_tracks
  

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
        active_tracks, dead_tracks = create_point_tracks(video_location, bounding_box, total_frames, frame_nr-stepsize, stepsize+1, True)
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


def track(annotation_location = 'annotations/cow_809_1.txt', video_location = 'videos/cow_809_1', stepsize = 100):
  detections = get_annotations(annotation_location) # Detections of detector
  active_detections = list() # Tracked detections
  dead_detections = list() # Previously tracked detections
  
  reader = csv.reader(open(video_location + '/info.txt', 'rb'), delimiter=' ')
  total_frames = int(reader.next()[1])
  
  for frame_nr in xrange(500, 500+1*stepsize, stepsize):
    # Update detections to track based on the information provided by detector.
    active_detections = update_detections(detections, active_detections, frame_nr)
    
    # Create tracks for detections_t
    active_detections = new_create_point_tracks(video_location, active_detections, frame_nr, frame_nr + stepsize)
    
    break
    
def new_create_point_tracks(name, detections, start_frame_nr, next_frame_nr):
  '''Creates point tracks for every detection_t'''  
  # TODO tracking
  # Features on whole screen homography doesnt work
  # Homography per cow doesnt work (too noisy and few features)
  # Using all the BBox features seems to work but will get unreliable in time.
  # - Point tracks per bounding box versus global point tracking.
  # - Homography gets unprecise when only using BB points. (Use more tracked points)
  
  # Initialize with first frame and second frame.
  image = cv2.imread(name + (("/image%.05d.jpg") % start_frame_nr))
  
  if not detections:
    return []
  
  # Select features within bounding box for all detections
  features = None
  first_features = True
  num_features = []
  active_tracks = dict()
  dead_tracks = dict()
  bb_pred = dict()
  
  for i in xrange(len(detections)):
    bounding_box = detections[i].bounding_box[start_frame_nr]
    bb_pred[detections[i].id] = [bounding_box]
    
    sub_image = image[bounding_box[0]:bounding_box[2], bounding_box[1]:bounding_box[3]]
    fts = get_features(sub_image)
    
    # Transform feature from bounding box to image
    for row in xrange(len(fts)):
      fts[row][0][0] = fts[row][0][0]+bounding_box[0]
      fts[row][0][1] = fts[row][0][1]+bounding_box[1]
      
    # Keep track of different point tracks
    active_tracks[detections[i].id] = list()
    dead_tracks[detections[i].id] = list()
    for row in xrange(len(fts)):
      active_tracks[detections[i].id].append(Track(fts[row], start_frame_nr))
        
    if first_features:
      features = fts
      first_features = False
    else:
      features = np.vstack([features, fts])
    num_features.append(len(fts))
    
  fts = get_features(image)
  features = np.vstack([features, fts])
  

  # TODO EPIPOLAR MAGIC
  if features == None:
    return []
  
  draw = True  
  for frame_nr in xrange(start_frame_nr + 1, next_frame_nr):
    if len(features) == 0:
      # Break if no features anymore
      break
  
    #print "Features: %d Length: %d" % (len(features), track_length)
    if draw:
      drawimage = image.copy()
      for i in bb_pred:
        bbs = bb_pred[i]
        bb = bbs[len(bbs)-1]
        cv2.rectangle(drawimage, (bb[0], bb[1]), (bb[2], bb[3]), (255, 0, 0))
        
      draw_features(drawimage, features)
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
    prev_features = []
    
    # Throw away all bad matches
    iterator = 0
    for detection_id in active_tracks:
      tracks = active_tracks[detection_id]
      new_tracks = []
      
      for track in tracks:
        if matches[iterator]:
          prev_features.append(features[iterator])
          matched_features.append(forward_features[iterator])
          track.add_point(forward_features[iterator], frame_nr)
          new_tracks.append(track)
        else:
          dead_tracks[detection_id].append(track)
        iterator += 1

      active_tracks[detection_id] = new_tracks

    # Extra features for homography doesnt work.
    for i in xrange(iterator, len(matches)):
      if matches[i]:
        prev_features.append(features[i])
        matched_features.append(forward_features[i])
        

    # Find homography
    # Vier punten
    features = np.array(matched_features)
    prev_features = np.array(prev_features)
    P, mask = cv2.findHomography(prev_features, features, cv2.RANSAC, 1)
    
    for detection in detections:
      bbs = bb_pred[detection.id]
      bb = bbs[len(bbs)-1]
      
      # 4 points of bounding box
      pt1 = np.dot(P, np.array([bb[0], bb[1], 1]))
      pt2 = np.dot(P, np.array([bb[0], bb[3], 1]))
      pt3 = np.dot(P, np.array([bb[2], bb[1], 1]))
      pt4 = np.dot(P, np.array([bb[2], bb[3], 1]))
      # Find minima and maxima
      min_x = int(round(min(pt1[0], pt2[0], pt3[0], pt4[0])))
      max_x = int(round(max(pt1[0], pt2[0], pt3[0], pt4[0])))
      min_y = int(round(min(pt1[1], pt2[1], pt3[1], pt4[1])))
      max_y = int(round(max(pt1[1], pt2[1], pt3[1], pt4[1])))
      bb_pred[detection.id].append((min_x, min_y, max_x, max_y))
    
    image = next_image.copy()

  '''
  # Homography
  prev_features = []
  for detection_id in active_tracks:
    for track in active_tracks[detection_id]:
      prev_features.append([list(track.get_point(start_frame_nr))])
  prev_features = np.double(np.array(prev_features))
  features = np.double(features)
  P, mask = cv2.findHomography(prev_features, features, cv2.RANSAC)
  
  # Test
  cv2.destroyAllWindows()
  image = cv2.imread(name + (("/image%.05d.jpg") % start_frame_nr))
  for detection in detections:
    BB = detection.bounding_box[start_frame_nr]
    minimum = np.dot(P, np.array([BB[0],BB[1], 1]))
    maximum = np.dot(P, np.array([BB[2],BB[3], 1]))
    cv2.rectangle(image, (BB[0], BB[1]), (BB[2], BB[3]), (255, 0, 0))
    cv2.rectangle(next_image, (int(minimum[0]), int(minimum[1])), (int(maximum[0]), int(maximum[1])), (255, 0, 0))
  cv2.imshow('BB', image)
  cv2.imshow('Next BB', next_image)
  cv2.waitKey(100)
  time.sleep(100)
  '''
  return detections
  
def compute_scores(detections, detections_t, frame_nr):
  return False

def update_detections(detections, active_detections, frame_nr):
  if len(detections[frame_nr]) > 0:
    if len(active_detections) > 0:
      pass
      # Compute scores of active_detection for every detection.
      #scores = compute_scores(detections, active_detections, frame_nr)
      # Assign detection to active_detection or create new one and move all non corresponding detections to dead detections.
      # Munkres?
    else:
      global ID
      for detection_id in detections[frame_nr]:
        detection = detections[frame_nr][detection_id]
        active_detections.append(Detection(ID, frame_nr, detection.bounding_box, detection.id))
        ID += 1
  return active_detections

def create_all_point_tracks(database, name, total, start_frame = 0, max_track_length = 20, draw = False):
  if start_frame > total - 1:
    return []
    
  # Initialize with first frame and second frame.
  image = cv2.imread(name + (("image%.05d.jpg") % start_frame))
  
  # Select features within bounding box if given
  features = get_features(image)

  if features == None:
    return []
  
  active_tracks = []
  dead_tracks = []
  correct_features = []
  for row in xrange(len(features)):
    point_track = Track(features[row], start_frame)
    point = point_track.get_point(start_frame)
    if point in database[start_frame]:
      continue
    
    database[start_frame].append(point)
    correct_features.append(features[row])
    active_tracks.append(Track(features[row], start_frame))
  
  features = np.array(correct_features)  
  
  for frame_nr in xrange(start_frame + 1, min(start_frame + max_track_length, total)):
    if len(features) == 0:
      # Break if no features anymore
      break
  
    #print "Features: %d Length: %d" % (len(features), track_length)
    if draw:
      draw_features(image, features)
    next_image = cv2.imread(name + (("image%.05d.jpg") % frame_nr))

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
        database[frame_nr].append(active_tracks[i].get_point(frame_nr))
        new_active_tracks.append(active_tracks[i])
      else:
        dead_tracks.append(active_tracks[i])
        
    active_tracks = new_active_tracks
    features = np.array(matched_features)
    image = next_image.copy()
    active_tracks.extend(dead_tracks)
  return database, active_tracks
  
def create_all_tracks(video_location = 'videos/809_1/', track_length = 10):
  reader = csv.reader(open(video_location + 'info.txt', 'rb'), delimiter=' ')
  total_frames = int(reader.next()[1])
  database = dict()
  all_tracks = list()
  
  for frame_nr in xrange(total_frames):
    database[frame_nr] = list()

  for frame_nr in xrange(total_frames):
    print "Frame %d" % frame_nr
    database, tracks = create_all_point_tracks(database, video_location, total_frames, frame_nr, track_length)
    all_tracks.extend(tracks)

  '''
  # Plot the point tracks
  fig = plt.figure()
  ax = Axes3D(fig)
  ax.set_xlabel("x-axis")
  ax.set_ylabel("y-axis")
  ax.set_zlabel("time")
  colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
  for track in all_tracks:
    colour = colours.pop()
    colours.insert(0, colour)
    if len(track.X) > 9:
      ax.plot(track.X, track.Y, zs=track.Z, color=colour)
  plt.show()
  '''
  
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

def create_voc_pascal_annotations(video_location = 'videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_location = 'annotations/cow_809_1.txt', output_location = 'VOC2007', database = 'The VOC2007 Database', annotator = 'PASCAL VOC2007'):
  try:
    print "Output directory created."
    os.mkdir(output_location)
  except:
    print "Ouput directory is already existing. Please check or change output name"

  capture = cv2.VideoCapture(video_location)
  VOC_image_location = output_location + '/JPEGimages'
  VOC_annotation_location = output_location + '/Annotations'
  
  try:
    print "Image directory created."
    os.mkdir(VOC_image_location)
  except:
    print "Image directory is already existing. Please check or change output name"

  try:
    print "Annotation directory created."
    os.mkdir(VOC_annotation_location)
  except:
    print "Annotation directory is already existing. Please check or change output name"
  
  annotations = get_annotations(annotation_location)
  
  
  image_numbers = [13, 25, 211, 232, 273, 297, 306, 345, 360, 386, 408, 417, 432, 462, 464, 491, 504, 622, 725, 728, 767, 770, 786, 808, 827, 834, 880, 904, 986, 1073, 1100, 1103, 1120, 1130, 1143, 1182, 1299, 1312, 1442, 1468, 1471, 1508, 1589, 1614, 1641, 1697, 1713, 1716, 1741, 1764, 1806, 1917, 1974, 1987, 2005, 2021, 2088, 2092, 2115, 2126, 2152, 2173, 2237, 2299, 2300, 2313, 2314, 2323, 2326, 2369, 2387, 2494, 2505, 2576, 2623, 2634, 2669, 2676, 2695, 2749, 2763, 2770, 2789, 2794, 2818, 2868, 2903, 2940, 2978, 2991, 3030, 3068, 3105, 3201, 3215, 3288, 3354, 3394, 3410, 3411, 3439, 3633, 3640, 3750, 3840, 3841, 3887, 3982, 3994, 4022, 4023, 4081, 4141, 4181, 4200, 4233, 4332, 4368, 4375, 4399, 4441, 4445, 4474, 4500, 4537, 4571, 4585, 4608, 4635, 4686, 4741, 4772, 4775, 4826, 4901, 4980, 5017, 5036, 5063, 5080, 5114, 5124, 5141, 5326, 5335, 5339, 5404, 5418, 5514, 5547, 5617, 5653, 5711, 5728, 5797, 5841, 5843, 5876, 5981, 6021, 6060, 6073, 6085, 6095, 6111, 6148, 6170, 6173, 6177, 6202, 6291, 6316, 6378, 6404, 6414, 6562, 6573, 6579, 6589, 6591, 6612, 6708, 6711, 6761, 6770, 6841, 6881, 6935, 6973, 7008, 7044, 7045, 7069, 7072, 7075, 7118, 7153, 7158, 7215, 7380, 7389, 7452, 7516, 7528, 7554, 7599, 7602, 7772, 7786, 7851, 7939, 7979, 8000, 8005, 8078, 8081, 8090, 8111, 8189, 8202, 8208, 8299, 8304, 8342, 8345, 8358, 8418, 8475, 8527, 8605, 8607, 8615, 8636, 8706, 8722, 8758, 8763, 8853, 8863, 8927, 8973, 9082, 9113, 9133, 9170, 9189, 9223, 9245, 9264, 9301, 9308, 9400, 9429, 9450, 9463, 9545, 9586, 9650, 9710, 9717, 9760, 9768, 9771, 9865, 9897, 9908, 9909, 9912]  
  
  frame_nr = 0
  steps = 10
  while True:
    print frame_nr
    for i in range(steps):
      ret, image = capture.read()
    
    if not ret:
      break
    elif not image_numbers:
      break
    elif len(annotations[frame_nr]) == 0:
      frame_nr += steps
      continue
    image_number = image_numbers.pop()    
    
    height, width, depth = image.shape
    
    doc = Document()
    annotation_xml = createElement('annotation')
    doc.appendChild(annotation_xml)
    
    annotation_folder = createElement('folder', output_location)
    annotation_xml.appendChild(annotation_folder)
    
    annotation_filename = createElement('filename', '%.06d.jpg' % image_number)
    annotation_xml.appendChild(annotation_filename)
    
    annotation_source = createElement('source')
    annotation_xml.appendChild(annotation_source)
    
    source_database = createElement('database', database)
    annotation_source.appendChild(source_database)
    
    source_annotation = createElement('annotation', annotator)
    annotation_source.appendChild(source_annotation)

    annotation_owner = createElement('owner')
    annotation_xml.appendChild(annotation_owner)
    
    owner_name = createElement('name', 'Camiel Verschoor')
    annotation_owner.appendChild(owner_name)

    annotation_size = createElement('size')
    annotation_xml.appendChild(annotation_size)
    
    size_width = createElement('width', str(width))
    annotation_size.appendChild(size_width)
    
    size_height = createElement('height', str(height))
    annotation_size.appendChild(size_height)
    
    size_depth = createElement('depth', str(depth))
    annotation_size.appendChild(size_depth)
    
    annotation_segmented = createElement('segmented', '0')
    annotation_xml.appendChild(annotation_segmented)
    
    for id in annotations[frame_nr]:
      # Create annotation
      annotation = annotations[frame_nr][id]
      annotation_object = createElement('object')
      annotation_xml.appendChild(annotation_object)
      
      annotation_object_name = createElement('name', annotation.label.lower())
      annotation_object.appendChild(annotation_object_name)

      annotation_object_pose = createElement('pose', 'Unspecified')
      annotation_object.appendChild(annotation_object_pose)
      
      annotation_object_truncated = createElement('truncated', str(int(annotation.occluded)))
      annotation_object.appendChild(annotation_object_truncated)
      
      annotation_object_difficult = createElement('difficult', '0')
      annotation_object.appendChild(annotation_object_difficult)
      
      annotation_object_bndbox = createElement('bndbox')
      annotation_object.appendChild(annotation_object_bndbox)
      
      annotation_object_xmin = createElement('xmin', str(annotation.bounding_box[0]))
      annotation_object_bndbox.appendChild(annotation_object_xmin)

      annotation_object_ymin = createElement('ymin', str(annotation.bounding_box[1]))
      annotation_object_bndbox.appendChild(annotation_object_ymin)

      annotation_object_xmax = createElement('xmax', str(annotation.bounding_box[2]))
      annotation_object_bndbox.appendChild(annotation_object_xmax)

      annotation_object_ymax = createElement('ymax', str(annotation.bounding_box[3]))
      annotation_object_bndbox.appendChild(annotation_object_ymax)

    xml_string = doc.toprettyxml()[23:]
    f = open(VOC_annotation_location + '/%06d.xml' % image_number, 'w')
    f.write(xml_string)
    f.close()
        
    # Write image
    cv2.imwrite(VOC_image_location + ("/%.06d.jpg" % image_number), image)
    frame_nr += steps
    
def createElement(label, value=None):
  doc = Document()
  element = doc.createElement(label)
  if value:
    element.appendChild(doc.createTextNode(value))
  return element


if __name__ == '__main__':
  #create_images()
  #create_all_tracks()
  #create_all_tracks()
  #track()
  #create_voc_pascal_annotations()
