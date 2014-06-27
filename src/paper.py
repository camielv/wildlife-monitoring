import cv2
import csv
import numpy as np
import cPickle as pickle
from modules.datastructures.track import Track

feature_params = dict(maxCorners = 10000000, qualityLevel = 0.01, minDistance = 5, blockSize = 19)
lk_params = dict(winSize  = (19, 19), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def get_point_tracks(name, steps):
  reader = csv.reader(open(name + '/info.txt', 'rb'), delimiter=' ')
  writer = csv.writer(open('TRACKS_COW810_1.txt', 'wb'), delimiter=' ')
  total_frames = int(reader.next()[1])
  
  for i in range(total_frames):
    print '###### Frame: %d ######' % i
    tracks = create_point_tracks(name, i, min(i + steps, total_frames), False)
    write_tracks(writer, tracks)
  

def write_tracks(writer, tracks):
  for track in tracks:
    writer.writerow(track.X)
    writer.writerow(track.Y)
    Z = track.Z
  writer.writerow(['###'])
  writer.writerow(Z)
  writer.writerow(['###'])

def create_point_tracks(name, start_frame_nr, next_frame_nr, draw = True):
  image = cv2.imread(name + (("/%.06d.jpg") % start_frame_nr))
  features = get_features(image)  

  if features == None:
    return []
  
  active_tracks = []
  dead_tracks = []
  for row in xrange(len(features)):
    active_tracks.append(Track(features[row], start_frame_nr))
  
  for frame_nr in xrange(start_frame_nr + 1, next_frame_nr):
    if len(features) == 0:
      # Break if no features anymore
      break
  
    print "Features: %d Active Tracks: %d Dead Tracks: %d" % (len(features), len(active_tracks), len(dead_tracks))
    if draw:
      draw_image = image.copy()
      draw_features(draw_image, features)
    next_image = cv2.imread(name + (("/%.06d.jpg") % frame_nr))

    ### Feature Selection method: Forward-Backward Tracking (Optical flow)
    # Forward in time
    forward_features, st, err = cv2.calcOpticalFlowPyrLK(image, next_image, features, None, **lk_params)
    # Backward in time
    backward_features, st, err = cv2.calcOpticalFlowPyrLK(next_image, image, forward_features, None, **lk_params)
    # Remove wrong matches
    distance = abs(features - backward_features).reshape(-1, 2).max(-1)
    matches = distance < 1
    matched_features = []
    
    # Throw away all bad matches
    new_tracks = []
    for i in range(len(features)):
      track = active_tracks[i]

      if matches[i]:
        matched_features.append(forward_features[i])
        track.add_point(forward_features[i], frame_nr)
        new_tracks.append(track)
      else:
        dead_tracks.append(track)

    active_tracks = new_tracks
    features = np.array(matched_features)
    image = next_image.copy()

  return active_tracks

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

if __name__ == '__main__':
  get_point_tracks('../dataset/images/COW810_1', 15)
