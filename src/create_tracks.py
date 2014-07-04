import cv2
import threading
import csv
import os
import math
import numpy as np
from modules.utils.parser import Parser
from modules.datastructures.track import Track

feature_params = dict(maxCorners = 10000000, qualityLevel = 0.01, minDistance = 5, blockSize = 19)
lk_params = dict(winSize  = (19, 19), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))


def multi_tracks(name, output_folder, steps, num_threads):
  print "THIS FUNCTION IS BUGGED PLEASE FIX IT creates wrong tracks sometimes"
  if os.path.isdir(output_folder):
    print "Error: Output directory already exists"
  else:
    os.makedirs(output_folder)

  reader = csv.reader(open(name + '/info.txt', 'rb'), delimiter=' ')      
  total_frames = int(reader.next()[1])
  size = int(round(total_frames/num_threads))
  threads = []
  for i in range(num_threads - 1):
    threads.append(threading.Thread(target=get_point_tracks, args=[name, output_folder, steps, i*size, (i+1)*size]))
  threads.append(threading.Thread(target=get_point_tracks, args=[name, output_folder, steps, (num_threads-1)*size, total_frames]))

  for thread in threads:
    thread.start()
    
  for thread in threads:
    thread.join()

def get_point_tracks(name, output_folder, steps, start, end):
  if os.path.isdir(output_folder):
    print "Error: Output directory already exists"
  else:
    os.makedirs(output_folder)

  for i in range(start, end):
    print '###### Frame: %d ######' % i
    tracks = create_point_tracks(name, i, min(i + steps + 1, end), False)
    output_name = output_folder + '/%d_%.06d.txt' % (steps, i)
    write_tracks(output_name, tracks)
  

def write_tracks(output_name, tracks):
  writer = csv.writer(open(output_name, 'wb'), delimiter=' ')
  for track in tracks:
    writer.writerow(track.X)
    writer.writerow(track.Y)
    Z = track.Z
  writer.writerow(['###'])
  writer.writerow(Z)

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
  print "Start: %d Features: %d Active Tracks: %d Dead Tracks: %d" % (start_frame_nr, len(features), len(active_tracks), len(dead_tracks))
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


def repair_point_tracks():
  parser = Parser()

  parameters = {1: ('COW810_1', 2694), 2: ('COW810_2', 2989)}
  point_tracks_location = "/media/verschoor/Barracuda3TB"
  
  for id in parameters:
    (video, frames) = parameters[id]
    video_location = '../../videos/%s' % video
    for point_track_length in range(0, 41, 5):
      for frame_id in range(frames):
        point_tracks_file = "%s/tracks/%s/%d/%d_%.06d.txt" % (point_tracks_location, video, point_track_length, point_track_length, frame_id)
        point_tracks = parser.track_parser(point_tracks_file)
        if len(point_tracks[0].Z) != point_track_length + 1:
          print "GOT YOU EVIL %d | %d!" % (frame_id, len(point_tracks[0].Z))
          tracks = create_point_tracks(video_location, frame_id, min(frame_id + point_track_length + 1, frames), False)
          write_tracks(point_tracks_file, tracks)

        if frame_id % 10 == 0:
          print "%d/%d | %s | %d" % (frame_id, frames, video, point_track_length)

if __name__ == '__main__':
  '''
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/5', 5, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/10', 10, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/15', 15, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/20', 20, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/25', 25, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/30', 30, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/35', 35, 5)
  multi_tracks('../../videos/COW810_1', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_1/40', 40, 5)

  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/5', 5, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/10', 10, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/15', 15, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/20', 20, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/25', 25, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/30', 30, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/35', 35, 5)
  multi_tracks('../../videos/COW810_2', '/media/verschoor/Barracuda3TB/tracks3/tracks/COW810_2/40', 40, 5)
  '''
  repair_point_tracks()
