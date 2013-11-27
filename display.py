# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:51:31 2013

@author: verschoor
"""

import cv2
import random
import csv

#def main(name = '../GOPRO/video/Flying/GOPR0809.MP4'):
def main(name = 'videos/GOPR0809_start_0_27_end_1_55.mp4'):
  capture = cv2.VideoCapture(name)
  video = cv2.VideoWriter('video.avi', 1196444237, 60, (1920, 1080))
  
  reader = csv.reader(open('annotations/cow_809_1.txt', 'rb'), delimiter=' ')
  annotations = dict()
  cow_ids = set()
  
  # Dictionary Per frame and per cow
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
  for cow_id in cow_ids:
    colours[cow_id] = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))

  # Read first frame
  ret, image = capture.read()
  frame_nr = 0
  
  while(ret):
    print "Frame number: %d" % (frame_nr)
    cv2.putText(image, "Copyright 2013 Verschoor, do not use without permission!", (950, 1060), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cows = annotations[frame_nr]
    for cow_id in cows:
      cow = cows[cow_id]
      if cow['lost'] != 1:
        cv2.rectangle(image, (cow['xmin'], cow['ymin']), (cow['xmax'], cow['ymax']), colours[cow_id], 2)
        cv2.putText(image, "Bertha " + str(cow_id), (cow['xmin'], cow['ymax'] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    video.write(image)
    #cv2.imshow('Feed', image)
    #cv2.waitKey(1)
    ret, image = capture.read()
    frame_nr += 1
    #break
  video.release()
  #cv2.destroyWindow("Feed")

main()