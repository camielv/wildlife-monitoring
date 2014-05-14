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

def draw_detections(video_name = '../videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_name = 'detections/comp4_cow_809_1.txt', output_name = 'video2.avi'):
  player = cv2.VideoCapture(video_name)
  recorder = cv2.VideoWriter(output_name, 1196444237, 1, (1920, 1080))
  reader = csv.reader(open(annotation_name, 'rb'), delimiter=' ')
  detections = dict()
  
  # Read in detections per frame
  for row in reader:
    if int(row[0]) not in detections:
        detections[int(row[0])] = []
    detections[int(row[0])].append({
                  'xmin': int(row[1]),
                  'ymin': int(row[2]),
                  'xmax': int(row[3]),
                  'ymax': int(row[4]),
                  'value': float(row[5])
    })
    
  # Read first frame
  ret, image = player.read()
  frame_nr = 0
  while(ret):
    print "Frame number: %d" % (frame_nr)
    if frame_nr in detections:
      cows = detections[frame_nr]
      for cow in cows:
        colour = (255, 255, 255)
        if cow['value'] < -0.9:
          colour = (255, 0, 0)
        elif cow['value'] < -0.8:
          colour = (0, 255, 0)
        elif cow['value'] < -0.7:
          colour = (0, 0, 255)
        elif cow['value'] < -0.6:
          colour = (255, 255, 0)
        cv2.rectangle(image, (cow['xmin'], cow['ymin']), (cow['xmax'], cow['ymax']), colour, 2)
        cv2.putText(image, "Value " + str(cow['value']), (cow['xmin'], cow['ymax'] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    recorder.write(image)
    cv2.imshow('Feed', image)
    cv2.waitKey(1)
    ret, image = player.read()
    frame_nr += 1
  recorder.release()
  cv2.destroyWindow("Feed")

if __name__ == '__main__':
  draw_detections()
  #draw_annotations(video_name = 'videos/GOPR0809_start_0_27_end_1_55.mp4', annotation_name = 'annotations/cow_809_1.txt', output_name = 'output/cow_809_1.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_2_09_end_2_27.mp4', annotation_name = 'annotations/cow_809_2.txt', output_name = 'output/cow_809_2.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_2_40_end_3_20.mp4', annotation_name = 'annotations/cow_809_3.txt', output_name = 'output/cow_809_3.avi')
  #draw_annotations(video_name = 'videos/GOPR0809_start_5_05_end_6_11.mp4', annotation_name = 'annotations/cow_809_4.txt', output_name = 'output/cow_809_4.avi')
  #draw_annotations(video_name = 'videos/GOPR0810_start_1_10_end_1_55.mp4', annotation_name = 'annotations/cow_810_1.txt', output_name = 'output/cow_810_1.avi')
  #draw_annotations(video_name = 'videos/GOPR0810_start_2_30_end_3_20.mp4', annotation_name = 'annotations/cow_810_2.txt', output_name = 'output/cow_810_2.avi')
