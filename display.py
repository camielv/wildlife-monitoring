# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:51:31 2013

@author: verschoor
"""
import cv2
import random
import csv

def fix_annotations(annotation_name = 'annotations/cow_809_1', fix = 0):
  reader = csv.reader(open(annotation_name, 'rb'), delimiter=' ')
  writer = csv.writer(open(annotation_name + 'fix', 'wb'), delimiter =' ')
  
  # Read in annotations per frame per cow.
  for row in reader:
    if(int(row[5]) < fix):
      continue
    writer.writerow([int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5])-fix, int(row[6]), int(row[7]), int(row[8]), row[9]])

def draw_annotations(video_name = 'videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_name = 'annotations/cow_809_1', output_name = 'output/video.avi'):
  player = cv2.VideoCapture(video_name)
  recorder = cv2.VideoWriter(output_name, 1196444237, 60, (1920, 1080))
   
  reader = csv.reader(open(annotation_name, 'rb'), delimiter=' ')
  annotations = dict()
  cow_ids = set()
  
  # Read in annotations per frame per cow.
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
  
  # Generate random colours for the boxes
  colours = dict()
  for cow_id in cow_ids:
    colours[cow_id] = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))

  # Read first frame
  ret, image = player.read()
  frame_nr = 0
  while(ret):
    print "Frame number: %d" % (frame_nr)
    cv2.putText(image, "Copyright 2013 Verschoor, do not use without permission!", (950, 1060), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if frame_nr in annotations:
      cows = annotations[frame_nr]
      for cow_id in cows:
        cow = cows[cow_id]
        if cow['lost'] != 1:
          cv2.rectangle(image, (cow['xmin'], cow['ymin']), (cow['xmax'], cow['ymax']), colours[cow_id], 2)
          cv2.putText(image, "Bertha " + str(cow_id), (cow['xmin'], cow['ymax'] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    recorder.write(image)
    cv2.imshow('Feed', image)
    cv2.waitKey(1)
    ret, image = player.read()
    frame_nr += 1

  recorder.release()
  cv2.destroyWindow("Feed")

if __name__ == '__main__':
  #draw_annotations(video_name = 'videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_name = 'annotations/cow_809_1.txt', output_name = 'output/cow_809_1.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_2_09_end_2_27.mp4', annotation_name = 'annotations/cow_809_2.txt', output_name = 'output/cow_809_2.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_2_40_end_3_20.mp4', annotation_name = 'annotations/cow_809_3.txt', output_name = 'output/cow_809_3.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_5_05_end_6_11.mp4', annotation_name = 'annotations/cow_809_4.txt', output_name = 'output/cow_809_4.avi')
  #draw_annotations(video_name = 'videos/GOPR0810_start_1_10_end_1_55.mp4', annotation_name = 'annotations/cow_810_1.txt', output_name = 'output/cow_810_1.avi')
  #draw_annotations(video_name = 'videos/GOPR0810_start_2_30_end_3_20.mp4', annotation_name = 'annotations/cow_810_2.txt', output_name = 'output/cow_810_2.avi')