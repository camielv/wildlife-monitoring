class Track():
  '''Class representing a point track'''
  def __init__(self, point = None, frame_nr = None, track = None):
    if point is None:
      [self.X, self.Y, self.Z] = track
    else:
      [[x, y]] = point
      self.X = [x]
      self.Y = [y]
      self.Z = [frame_nr]
    
  def add_point(self, point, frame_nr):
    [[x, y]] = point
    self.X.append(x)
    self.Y.append(y)
    self.Z.append(frame_nr)
    
  def get_point(self, frame_nr):
    index = self.Z.index(frame_nr)
    return (int(round(self.X[index])), int(round(self.Y[index])), int(round(self.Z[index])))

  def get_last_point(self):
    index = len(self.X) - 1
    return (int(round(self.X[index])), int(round(self.Y[index])), int(round(self.Z[index])))

  def get_first_point(self):
    return (int(round(self.X[0])), int(round(self.Y[0])), int(round(self.Z[0])))
  
  def __str__(self):
    return_string =  str(self.X) + "\n"
    return_string += str(self.Y) + "\n"
    return_string += str(self.Z) + "\n"
    return return_string