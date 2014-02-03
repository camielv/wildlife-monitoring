class Detection():
  '''Class representing an detection'''
  def __init__(self, id, frame_id, bounding_box, real_id):
    self.alive = True
    self.id = id
    self.frames = [frame_id]
    self.tracks = dict()
    self.bounding_box = {frame_id: bounding_box}
    self.real_id = {frame_id: real_id}
    
  def __str__(self):
    # Todo finish
    return_string = "Alive: %d\n" % (int(self.alive))
    return_string += "Frames: %s\n" % ("".join(" " + str(frame_id) for frame_id in self.frames))
    return return_string
