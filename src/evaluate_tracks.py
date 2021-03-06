import cPickle as pickle
from modules.utils.parser import Parser
from modules.utils.munkres import Munkres
from modules.datastructures.detection import TrackDetection


def count_point_tracks(detections, point_tracks_history, frame_id):
  count = dict()
  for id in detections:
    count[id] = dict()
    (xmin, ymin, xmax, ymax) = detections[id].bounding_box
    for history_id in point_tracks_history:
      count[id][history_id] = 0
      point_tracks = point_tracks_history[history_id]
      for point_track in point_tracks:
        (x, y, z) = point_track.get_point(frame_id)
        if x > xmin and x < xmax and y > ymin and y < ymax:
          count[id][history_id] += 1
  
  return count


def match_detections(tubelets, detections, point_tracks_history, frame_id, global_id):
  ''' Evaluates all the incoming detections '''
  
  # Check if detections correspond to existing tubelets using Everingham evaluation and the Hungarian Algorithm.
  if tubelets:
    score = list()
    # Count how many point_tracks go through each detection.
    count = count_point_tracks(detections, point_tracks_history, frame_id)
    
    # Compute score for every combination of Detection and Tubelet.
    for id in detections:
      tubelet_scores = []
      for tubelet in tubelets:
        tubelet_scores.append(tubelet.evaluate_detection(detections[id], count[id], frame_id))
      score.append(tubelet_scores)
    # Find Tubelets that have a Detection that match both a certain threshold taken from Everingham et al. (Buffy paper).
    # Compute best decision with Hungarian Algorithm.
    
    munkres = Munkres()
    #print score
    try:
      indices = munkres.compute(score)
    except:
      print len(tubelets)
      print detections.keys()
      print len(point_tracks_history)
      print count
      print score
      print frame_id
    
    # Remove Detection that correspond to a Tubelet
    threshold = 0.5
    detection_ids = detections.keys()
    for detection_id, tubelet_id in indices:
      if score[detection_id][tubelet_id] < threshold:
        id = detection_ids[detection_id]
        tubelets[tubelet_id].update_detection(detections[id])
        del detections[id]
            
  # Create new tubelets for leftover detections
  for id in detections:
    detection = detections[id]
    tubelets.append(TrackDetection(global_id, detection.frame_id, detection.bounding_box))
    global_id += 1
    
  return [tubelets, global_id]

def find_point_tracks(tubelets, point_tracks, frame_nr, point_track_length):
  ''' Find tracks for tubelets that have bounding boxes in this frame '''  
  tubelets_new = list()
  tubelets_dead = list()
  for tubelet in tubelets:
    tubelet_frame = tubelet.get_last_frame()
    
    # Create point tracks for tubelets with new bounding boxes.
    if tubelet_frame == frame_nr:
      for point_track in point_tracks:
        tubelet.evaluate_point_track(point_track)
        
    # Remove all tubelets that do not have tracks in future frames.
    if (frame_nr >= tubelet_frame + point_track_length) or tubelet_frame not in tubelet.tracks:
      tubelets_dead.append(tubelet)
    else:
      tubelets_new.append(tubelet)
      
  return [tubelets_new, tubelets_dead]

def filter_detections(detections):
  ids = detections.keys()
  if len(ids) < 20:
    return detections
  ids.sort()
  ids.reverse()
  filtered = dict()
  for i in range(20):
    filtered[ids[i]] = detections[i]
  return filtered


def evaluate_tubelets(video_location, output_location, point_tracks_location, detections, frames, point_track_length, sample_rate):
  # Settings
  global_id = 0
    
  # Point tracks
  point_tracks = list()
  point_tracks_history = dict()
  
  # Tubelets
  tubelets_alive = list()
  tubelets_dead = list()
  
  for frame_id in range(0, frames, sample_rate):
    # Update TrackDetections with new detections.
    if frame_id in detections:
      filtered = filter_detections(detections[frame_id])
      [tubelets_alive, global_id] = match_detections(tubelets_alive, filtered, point_tracks_history, frame_id, global_id)
    
    # Find point tracks for Tubelets
    if tubelets_alive:
      point_tracks_file = "%s/tracks/%s/%d/%d_%.06d.txt" % (point_tracks_location, video_location, point_track_length, point_track_length, frame_id)
      point_tracks = parser.track_parser(point_tracks_file)
      [tubelets_alive, dead] = find_point_tracks(tubelets_alive, point_tracks, frame_id, point_track_length)
      tubelets_dead.extend(dead)
      
      # Keep track of history
      point_tracks_history[frame_id] = point_tracks

    # Check if history is still up to date
    for key in point_tracks_history.keys():
      if key < frame_id + sample_rate - point_track_length:
        del point_tracks_history[key]
        
    print "%s | %s | Frame %d/%d Count: %d" % (video_location, point_track_length, frame_id, frames, len(tubelets_alive) + len(tubelets_dead))
    #print point_tracks_history.keys()
  print "Alive: %d Dead: %d All: %d" % (len(tubelets_alive), len(tubelets_dead), len(tubelets_alive) + len(tubelets_dead))
  tubelets_alive.extend(tubelets_dead)
  pickle.dump(tubelets_alive, open("%s_%s_%d.p" % (output_location, video_location, point_track_length), "wb"))

if __name__ == '__main__':
  parameters = {1: ('COW810_1', 2694)}
  parser = Parser()
  '''
  sample_rate = 5

  annotation_location = "../dataset/annotations"
  for id in parameters:
    (video_location, frames) = parameters[id]
    for i in range(5, 21, 5):
      annotations_file = "%s/%s.txt" % (annotation_location, video_location)
      annotations = parser.vatic_parser(annotations_file, False)
      evaluate_tubelets(video_location, "annotations_wo", "/media/verschoor/Barracuda3TB", annotations, frames, i, sample_rate)
  '''
  sample_rate = 1
  detection_location = "../detections"
  detector = "COLOURDPM"

  for id in parameters:
    (video_location, frames) = parameters[id]
    detections_file = "%s/%s_%s.txt" % (detection_location, detector, video_location)
    for i in range(15, 21, 5):
      detections = parser.detection_parser(detections_file, -0.8)
      evaluate_tubelets(video_location, "%s_detections_-0.8" % (detector), "/media/verschoor/Barracuda3TB", detections, frames, i, sample_rate)