from modules.utils.parser import Parser

video = 'COW810_1'
track_length = 6
parser = Parser()

annotations_file = "../dataset/annotations/%s.txt" % video
annotations = parser.vatic_parser(annotations_file)

frames = 2694
prev_detections =

for i in range(0, frames, 6):
  detections = annotations[i]
  tracks_file = "../tracks/%d/%d_%.06d.txt" % (track_length, track_length, i)
  if detections:
    