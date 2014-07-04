class TrackDetection():
  '''Class representing an tracked detection'''
  def __init__(self, id, frame_id, bounding_box):
    self.alive = True
    self.id = id
    self.frames = [frame_id]
    self.tracks = dict()
    self.bounding_box = {frame_id: bounding_box}
    self.virtual_bounding_box = dict()
    
  def get_bounding_box(self):
    frame_id = self.get_last_frame()
    if frame_id in self.bounding_box:
      return self.bounding_box[frame_id]
    else:
      return self.virtual_bounding_box[frame_id]

  def update_virtual_detection(self):
    frame_id = self.get_last_frame()
    (xmin, ymin, xmax, ymax) = self.get_bounding_box()
    
    tracks = self.tracks[frame_id]
    
    if not tracks:
      return False
    
    movement = [0, 0]
    for track in tracks:
      (x1, y1, frame_id) = track.get_first_point()
      (x2, y2, frame_id) = track.get_last_point()
      movement[0] += x2 - x1
      movement[1] += y2 - y1

    movement[0] = int(round(float(movement[0]) / len(tracks)))
    movement[1] = int(round(float(movement[0]) / len(tracks)))
    bounding_box = (xmin + movement[0], ymin + movement[1], xmax + movement[0], ymax + movement[1])

    self.virtual_bounding_box[frame_id] = bounding_box
    self.real_id[frame_id] = -1
    self.frames.append(frame_id)
    
    return True
    
  def update_detection(self, detection, real_id):
    self.frames.append(detection.frame_id)
    self.bounding_box[detection.frame_id] = detection.bounding_box
    self.real_id[detection.frame_id] = real_id
  
  def evaluate_point_track(self, track):
    (x, y, frame_id) = track.get_first_point()
    (xmin, ymin, xmax, ymax) = self.get_bounding_box()
    if  x > xmin and x < xmax and y > ymin and y < ymax:
      if frame_id in self.tracks:
        self.tracks[frame_id].append(track)
      else:
        self.tracks[frame_id] = [track]
  
  def evaluate_detection(self, detection, count, current_frame_id):
    score = 0
    (xmin, ymin, xmax, ymax) = detection.bounding_box
    track_frame_id = self.get_last_frame()
    point_tracks = self.tracks[track_frame_id]
    
    for point_track in point_tracks:
      (x, y, frame_id) = point_track.get_point(track_frame_id + (current_frame_id - track_frame_id))
      if x > xmin and x < xmax and y > ymin and y < ymax:
        score += 1
    return 1 - (float(score) / (len(point_tracks) + (count[track_frame_id] - score)))

  def get_last_frame(self):
    return self.frames[len(self.frames)-1]
  
  def __str__(self):
    # Todo finish
    return_string = "ID: %d\n" % self.id
    return_string += "Alive: %d\n" % (int(self.alive))
    return_string += "Frames:%s\n" % ("".join(" " + str(frame_id) for frame_id in self.frames))
    return_string += "Bounding box: %s" % str(self.bounding_box)
    return return_string

class Detection():
  '''Class representing an detection'''
  def __init__(self, frame_id, (xmin, ymin, xmax, ymax), confidence):
    self.frame_id = int(frame_id)
    self.bounding_box = (int(xmin), int(ymin), int(xmax), int(ymax))
    self.confidence = float(confidence)
    
  def __str__(self):
    return_string  = "Frame: %d\n" % self.frame_id
    return_string += "Bounding box: %s\n" % str(self.bounding_box)
    return_string += "Confidence: %f" % self.confidence
    return return_string