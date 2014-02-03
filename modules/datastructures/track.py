class Track():
  '''Class representing a point track'''
  def __init__(self, point, frame_nr):
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
    return int(self.X[index]), int(self.Y[index])
    
  def __str__(self):
    return_string =  str(self.X) + "\n"
    return_string += str(self.Y) + "\n"
    return_string += str(self.Z) + "\n"
    return return_string
