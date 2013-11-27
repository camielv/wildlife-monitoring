# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 11:23:02 2013

@author: wiggers
"""

import cv2
import math
import itertools
import numpy as np

feature_params = dict(maxCorners = 100, qualityLevel = 0.01, minDistance = 10, blockSize = 19)     
lk_params = dict(winSize  = (19, 19), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def main(name = '../GOPRO/video/Flying/GOPR0813.MP4'):
  capture = cv2.VideoCapture(name)

  # Initialize
  ret, prev_bgr_image = capture.read()
  #prev_bgr_image = prev_bgr_image[0:200, 0:200]
  
  if ret:
    prev_feature_pts = get_features(prev_bgr_image)
    prev_num_features = len(prev_feature_pts)
  else:
    return
    
  #draw_features(prev_bgr_image, prev_feature_pts)
  cv2.waitKey(1)
  
  while True:
    ret, bgr_image = capture.read()
    #bgr_image = bgr_image[0:200, 0:200]

    if ret:
      # Forward
      feature_pts, st, err = cv2.calcOpticalFlowPyrLK(prev_bgr_image, bgr_image, prev_feature_pts, None, **lk_params)
      # Backward
      prev_feature_pts_r, st, err = cv2.calcOpticalFlowPyrLK(bgr_image, prev_bgr_image, feature_pts, None, **lk_params)
      # Remove wrong matches
      d = abs(prev_feature_pts-prev_feature_pts_r).reshape(-1, 2).max(-1)
      good = d < 1
      new_features = []
      for feature, value in itertools.izip(feature_pts, good):
        if value:
          new_features.append([[feature[0][0], feature[0][1]]])
          
      new_feature_pts = np.array(new_features)
      num_features = len(new_features)
      
      # Generate new features if features are lost.
      if prev_num_features - num_features > 0:
        possible_feature_pts = get_features(bgr_image)
        iterator = 0
        while len(new_features) < feature_params['maxCorners']:
          if possible_feature_pts is not None and iterator < len(possible_feature_pts):
            pos_x, pos_y = possible_feature_pts[iterator, 0]
            iterator += 1
            for x, y in new_feature_pts[:, 0]:
              if math.sqrt((x - pos_x) ** 2 + (y - pos_y) ** 2) > feature_params['minDistance']:
                continue
            new_features.append([[pos_x, pos_y]])
          else:
            break
          

      prev_feature_pts = np.array(new_features)
      prev_num_features = len(new_features)
      prev_bgr_image = bgr_image.copy()
      
      draw_features(bgr_image.copy(), prev_feature_pts)
      cv2.waitKey(1)
    else:
      break
      
  cv2.destroyAllWindows()
  
def get_features(bgr_image):
  gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)  
  return cv2.goodFeaturesToTrack(gray_image, **feature_params)
  
  
def draw_features(bgr_image, feature_pts):
  if feature_pts is not None:
    for x, y in feature_pts[:, 0]:
      cv2.circle(bgr_image, (x,y), 2, (255, 0, 0), -1)
  text = "Features: %d" % (len(feature_pts))
  cv2.putText(bgr_image, text, (10, 10), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0))
  cv2.imshow('Features', bgr_image)
  
main()