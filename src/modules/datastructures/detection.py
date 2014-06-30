class TrackDetection():
  '''Class representing an tracked detection'''
  def __init__(self, id, frame_id, bounding_box, real_id):
    self.alive = True
    self.id = id
    self.frames = [frame_id]
    self.tracks = dict()
    self.bounding_box = {frame_id: bounding_box}
    self.real_id = {frame_id: real_id}
    
  def add_detection(self, detection, real_id):
    self.frames.append(detection.frame_id)
    self.bounding_box[detection.frame_id] = detection.bounding_box
    self.real_id[detection.frame_id] = real_id
  
  def evaluate_point_track(self, track):
    (x, y, frame_id) = track.get_first_point()
    (xmin, ymin, xmax, ymax) = self.bounding_box[frame_id]
    if  x > xmin and x < xmax and y > ymin and y < ymax:
      if frame_id in self.tracks:
        self.tracks[frame_id].append(track)
      else:
        self.tracks[frame_id] = [track]
  
  def get_frame(self):
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