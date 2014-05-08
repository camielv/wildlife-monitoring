class Annotation():
  '''Class representing an annotation'''
  def __init__(self, frame_id, id, (xmin, ymin, xmax, ymax), lost, occluded, generated, label):
    self.frame_id = int(frame_id)
    self.id = int(id)
    self.bounding_box = (int(xmin), int(ymin), int(xmax), int(ymax))
    self.lost = bool(int(lost))
    self.occluded = bool(int(occluded))
    self.generated = bool(int(generated))
    self.label = label
    
  def __str__(self):
    # Todo finish
    return_string =  "Frame ID: %d\n" % (self.frame_id)
    return_string += "Annotation ID: %d\n" % (self.annotation_id)
    return_string += "Bounding box: (%d, %d, %d, %d)" % self.bounding_box
    return return_string
