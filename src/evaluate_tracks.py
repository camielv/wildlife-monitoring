import cPickle as pickle
from modules.utils.parser import Parser
from modules.utils.munkres import Munkres
from modules.datastructures.detection import TrackDetection


def count_point_tracks(detections, point_tracks):
  if not point_tracks:
    return []
  
  count = dict()
  for id in detections:
    count[id] = 0
    (xmin, ymin, xmax, ymax) = detections[id].bounding_box
    
    for point_track in point_tracks:
      (x, y, z) = point_track.get_last_point()
      if x > xmin and x < xmax and y > ymin and y < ymax:
        count[id] += 1

  return count


def match_detections(tracks, detections, point_tracks, global_id):
  tracks_dead = list()
  tracks_new = list()
  if tracks:
    score = list()
    
    count = count_point_tracks(detections, point_tracks)
    
    # Compute score for every combination of Detection and TrackDetections.
    for id in detections:
      track_scores = []
      for track in tracks:
        track_scores.append(track.evaluate_detection(detections[id], count[id]))
      score.append(track_scores)
    # Find TrackDetections that have a Detection that match both a certain threshold taken from Everingham et al. (Buffy paper).
    # Compute best decision with Hungarian Algorithm.
    munkres = Munkres()
    indices = munkres.compute(score)
    
    # Remove Detection that correspond to a TrackDetection
    threshold = 0.5
    detection_ids = detections.keys()
    remove = list()
    for det_id, track_id in indices:
      if score[det_id][track_id] < threshold:
        id = detection_ids[det_id]
        tracks[track_id].update_detection(detections[id], id)
        tracks_new.append(tracks[track_id])
        del detections[id]
        remove.append(track_id)
    
    # Remove TrackDetections with a corresponding detection
    remove.sort()
    remove.reverse()
    for id in remove:
      del tracks[id]
    
    # Remove TrackDetections with no corresponding detection.
    for track in tracks:
      tracks_dead.append(track)
        
  # Create new TrackDetections for leftover detections  
  for id in detections:
    detection = detections[id]
    tracks_new.append(TrackDetection(global_id, detection.frame_id, detection.bounding_box, id))
    global_id += 1
    
  return [tracks_new, tracks_dead, global_id]

def find_tracks(tracks, point_tracks):
  # Check what point tracks belong to what TrackDetections
  for point_track in point_tracks:
    for track in tracks:
      track.evaluate_point_track(point_track)
  
  # Kill TrackDetections that do not have any tracks.
  tracks_new = list()
  tracks_dead = list()
  for track in tracks:
    if track.get_last_frame() in track.tracks:
      tracks_new.append(track)
    else:
      tracks_dead.append(track)
  return [tracks_new, tracks_dead]


def evaluate_tracks(video, frames, track_length):
  # Settings
  global_id = 0
  
  # Parse annotation file
  parser = Parser()
  annotations_file = "../dataset/annotations/%s.txt" % video
  annotations = parser.vatic_parser(annotations_file)
  
  # Tracks
  tracks_location = "/media/verschoor/Barracuda3TB/tracks2"
  tracks_alive = list()
  tracks_dead = list()
  point_tracks = list()
  
  for i in range(0, frames, track_length):
    # Update TrackDetections with new detections.
    if i in annotations:
      [tracks_alive, dead, global_id] = match_detections(tracks_alive, annotations[i], point_tracks, global_id)
      tracks_dead.extend(dead)
    
    # Find point tracks for TrackDetection.
    if tracks_alive:
      point_tracks_file = "%s/tracks/%s/%d/%d_%.06d.txt" % (tracks_location, video, track_length, track_length, i)
      point_tracks = parser.track_parser(point_tracks_file)
      [tracks_alive, dead] = find_tracks(tracks_alive, point_tracks)
      tracks_dead.extend(dead)
  
    print "Frame %d/%d" % (i, frames)
  print "Alive: %d Dead: %d All: %d" % (len(tracks_alive), len(tracks_dead), len(tracks_alive) + len(tracks_dead))
  tracks_alive.extend(tracks_dead)
  pickle.dump(tracks_alive, open("%s_%d.p" % (video, track_length), "wb"))

if __name__ == '__main__':
  parameters = {1: ('COW810_1', 2694), 2: ('COW810_2', 2989)}
  for id in parameters:
    (video, frames) = parameters[id]
    for i in range(40, 4, -5):
      evaluate_tracks(video, frames, i)
