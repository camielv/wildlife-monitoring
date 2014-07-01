from modules.utils.parser import Parser
from modules.utils.munkres import Munkres
from modules.datastructures.detection import TrackDetection


def match_detections(tracks, detections, global_id):
  tracks_dead = list()
  tracks_new = list()
  if tracks:
    score = list()
    
    # Compute score for every combination of Detection and TrackDetections.
    for id in detections:
      track_scores = []     
      for track in tracks:
        track_scores.append(track.evaluate_detection(detections[id]))     
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
    
    # Update TrackDetections without a corresponding detection by taking the average movement of optical flow.
    for track in tracks:
      success = track.update_virtual_detection()
      if success:
        tracks_new.append(track)
      else:
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


# Settings
global_id = 0
video = 'COW810_1'
track_length = 5
frames = 2694

# Parse annotation file
parser = Parser()
annotations_file = "../dataset/annotations/%s.txt" % video
annotations = parser.vatic_parser(annotations_file)

# Tracks
tracks_alive = list()
tracks_dead = list()

for i in range(0, frames, track_length):
  # Update TrackDetections with new detections.
  if i in annotations:
    [tracks_alive, dead, global_id] = match_detections(tracks_alive, annotations[i], global_id)
    tracks_dead.extend(dead)
  
  # Find point tracks for TrackDetection.
  if tracks_alive:
    point_tracks_file = "../tracks/%s/%d/%d_%.06d.txt" % (video, track_length, track_length, i)
    point_tracks = parser.track_parser(point_tracks_file)
    [tracks_alive, dead] = find_tracks(tracks_alive, point_tracks)
    tracks_dead.extend(dead)
  
  print "Frame %d/%d" % (i, frames)
print "Dead: %d Alive: %d All: %d" % (len(tracks_alive), len(tracks_dead), len(tracks_alive) + len(tracks_dead))