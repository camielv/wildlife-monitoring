# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:51:31 2013

@author: wiggers
"""

import cv2
import csv

#def main(name = '../GOPRO/video/Flying/GOPR0809.MP4'):
def main(name = '../GOPRO/video/Flying/cutted/GOPR0809_start_0_27_end_1_55.mp4'):
  capture = cv2.VideoCapture(name)
  
  reader = csv.reader(open('annotations/cow_809_1.txt', 'rb'), delimiter=' ')
  annotations = dict()
  cow_ids = set()
  
  # Dictionary Per frame and per cow
  frame_nr = 0
  for row in reader:
    if int(row[5]) not in annotations:
      annotations[int(row[5])] = dict()

    annotations[int(row[5])][int(row[0])] = {
                  'xmin': int(row[1]),
                  'ymin': int(row[2]),
                  'xmax': int(row[3]),
                  'ymax': int(row[4]),
                  'lost': int(row[6]),
                  'occluded': int(row[7]),
                  'generated': int(row[8]),
                  'label': row[9],
    }
    cow_ids.add(int(row[0]))
  
  colours = dict()
  stepsize = int(round(255/(len(cow_ids))))
  step = 0
  for cow_id in cow_ids:
    colours[cow_id] = (255 - step * stepsize, step * stepsize, step * stepsize)
    step += 1

  # Read first frame
  ret, image = capture.read()
  frame_nr = 0
  
  while(ret):
    print "Frame number: %d" % (frame_nr)
    cows = annotations[frame_nr]
    for cow_id in cows:
      cow = cows[cow_id]
      if cow['lost'] != 1:
        cv2.rectangle(image, (cow['xmin'], cow['ymin']), (cow['xmax'], cow['ymax']), colours[cow_id], 2)
    
    cv2.imshow('Feed', image)
    cv2.waitKey(1)
    ret, image = capture.read()
    frame_nr += 1
    #break

  cv2.destroyWindow("Feed")

main()