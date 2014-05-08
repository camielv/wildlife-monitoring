class TrackDetection():
  '''Class representing an tracked detection'''
  def __init__(self, id, frame_id, bounding_box, real_id):
    self.alive = True
    self.id = id
    self.frames = [frame_id]
    self.tracks = dict()
    self.bounding_box = {frame_id: bounding_box}
    self.real_id = {frame_id: real_id}
    
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