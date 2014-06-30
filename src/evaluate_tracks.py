from modules.utils.parser import Parser
from modules.utils.munkres import Munkres
from modules.datastructures.detection import TrackDetection


def match_detections(tracks, detections, global_id):
  tracks_dead = list()
  if tracks:
    score = list()
    for id in detections:
      track_scores = []
      
      detection = detections[id]
      (xmin, ymin, xmax, ymax) = detection.bounding_box
      for track in tracks:
        track_score = 0
        for point_track in track.tracks[track.get_frame()]:
          (x, y, frame_id) = point_track.get_last_point()
          if x > xmin and x < xmax and y > ymin and y < ymax:
            track_score += 1
        track_scores.append(1 - (float(track_score) / len(track.tracks[track.get_frame()])))
      score.append(track_scores)

    munkres = Munkres()
    indices = munkres.compute(score)
    
    # Continue tracks if the error is low enough
    threshold = 0.5
    detection_ids = detections.keys()
    for det_id, track_id in indices:
      if score[det_id][track_id] < threshold:
        id = detection_ids[det_id]
        tracks[track_id].add_detection(detections[id], id)
        del detections[id]
  else:
    for id in detections:
      detection = detections[id]
      tracks.append(TrackDetection(global_id, detection.frame_id, detection.bounding_box, id))
      global_id += 1
  return [tracks, tracks_dead, global_id]

def find_tracks(tracks, point_tracks):
  for point_track in point_tracks:
    for track in tracks:
      track.evaluate_point_track(point_track)
  return tracks

global_id = 0
video = 'COW810_1'
track_length = 5
parser = Parser()

annotations_file = "../dataset/annotations/%s.txt" % video
annotations = parser.vatic_parser(annotations_file)

frames = 2694
tracks_alive = list()
tracks_dead = list()
for i in range(0, frames, track_length):
  if i in annotations:
    [tracks_alive, dead, global_id] = match_detections(tracks_alive, annotations[i], global_id)
    tracks_dead.extend(dead)
  
  # Update the point_tracks
  if tracks_alive:
    point_tracks_file = "../tracks/%s/%d/%d_%.06d.txt" % (video, track_length, track_length, i)
    point_tracks = parser.track_parser(point_tracks_file)
    tracks_alive = find_tracks(tracks_alive, point_tracks)
    for track in tracks_alive:
      if i in track.tracks:
        print len(track.tracks[i])
    
  if i > 100:
    break
  
'''      
  print len(annotations)
  tracks = parser.track_parser("../tracks/%s/%d/%d_%.06d.txt" % (video, track_length-1, track_length-1, 0))

  curr_detections = annotations[i]
  
  detections = annotations[i]
  tracks_file = "../tracks/%d/%d_%.06d.txt" % (track_length, track_length, i)
  if detections:
'''