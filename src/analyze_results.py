# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 10:27:51 2014

@author: verschoor
"""
import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np
from modules.utils.parser import Parser


def count(tracks):
  counts = dict()
  for track in tracks:
    length = len(track.real_id)
    if length in counts:
      counts[length] += 1
    else:
      counts[length] = 1
  return count

def count_doubles(tracks):
  doubles = dict()
  tubelets = list()
  unique_ids = set()
  for track in tracks:
    keys = track.real_id.keys()
    keys.sort()
    tubelet = list()
    for key in keys:
      tubelet.append(track.real_id[key])
    unique_ids = unique_ids.union(set(tubelet))
    tubelets.append(tubelet)    

  for id in unique_ids:
    doubles[id] = 0
    for tubelet in tubelets:
      if id in tubelet:
        doubles[id] += 1

  wrong_merges = 0
  for tubelet in tubelets:
    old = tubelet.pop()
    while tubelet:
      new = tubelet.pop()
      if old != new:
        wrong_merges += 1
      old = new
  print wrong_merges
  
  return doubles



def pr_curve(tracks, track_length):
  tubelets = dict()
  for track in tracks:
    length = len(track.real_id)
    if length in tubelets:
      tubelets[length].append(track)
    else:
      tubelets[length] = [track]

  lengths = tubelets.keys()
  lengths.sort()
  lengths.reverse()
  
  pr = list()
  seen = list()
  total = 0
  count = 0
  for length in lengths:
    tubes = tubelets[length]
    
    for tube in tubes:
      total += 1
      unique_ids = set(tube.ground_truth.values())
      if len(unique_ids) > 1 or len(unique_ids) == 0:
        pr.append(float(count)/total)
        continue
      id = unique_ids.pop()
      if id in seen:
        pr.append(float(count)/total)
        continue
      count += 1
      pr.append(float(count)/total)
      seen.append(id)
  rc = list()
  for i in range(total):
    rc.append(float(i)/total)
  print "AP: %f (%d)" % (np.mean(pr), track_length)
  plt.plot(rc, pr, label="Length = %d" % track_length)
  plt.ylabel('Precision')
  plt.xlabel('Recall')
  plt.xlim(0, 1.0)
  plt.ylim(0, 1.0)


  '''
1- hoe sorteer je de lijst
2- wat betekend 'goed/fout'

voor 1, zou ik zeggen het aantal BBs in een tubelet, wat denk je?

voor 2, heb je een aantal mogelijkheden dat een tubelet fout is:
- er komt geen enkele ground-truth koe voor in de tubelet
- er komen verschillende ground-truth koeien voor in de tubelet
- je hebt de koe die bij deze tubelet hoort al een keer eerder in je gesorteerde lijst gezien
  '''

def check_ground_truth(tubelets, annotation_location, video_location):
  parser = Parser()
  annotations_file = "%s/%s.txt" % (annotation_location, video_location)
  annotations = parser.vatic_parser(annotations_file)
  threshold = 0.5
  for tubelet in tubelets:
    ground_truth = dict()
    bounding_boxes = tubelet.bounding_box
    
    for id in bounding_boxes:
      (xminB, yminB, xmaxB, ymaxB) = bounding_boxes[id]
      best_match = None
      best_id = None
      if id in annotations:
        for annotation_id in annotations[id]:
          (xminA, yminA, xmaxA, ymaxA) = annotations[id][annotation_id].bounding_box
          intersection = max(0, min(xmaxA, xmaxB) - max(xminA, xminB)) * max(0, min(ymaxA, ymaxB) - max(yminA, yminB))
          surface_A = (xmaxA - xminA) * (ymaxA - yminA)
          surface_B = (xmaxB - xminB) * (ymaxB - yminB)
          
          union = surface_A + surface_B - intersection          
          ratio = intersection / union
                    
          if ratio > threshold and ratio > best_match:
            best_match = ratio
            best_id = annotation_id
            
      if best_id != None:
        ground_truth[id] = best_id
    tubelet.ground_truth = ground_truth
    
  return tubelets
  
if __name__ == '__main__':
  parameters = {1: ('COW810_1', 2694), 2: ('COW810_2', 2989)}
  for id in parameters:
    (video, frames) = parameters[id]
    for i in range(5, 41, 5):
      name = "../count_results/%s_%d.p" % (video, i)
      tubelets = pickle.load(open(name, "rb"))
      tubelets = check_ground_truth(tubelets, "../dataset/annotations", video)
      pr_curve(tubelets, i)
      #doubles = count_doubles(tracks)
      #print '--- %d --- %s' % (i, video)
    plt.legend()
    plt.savefig("%s.pdf" % (video))
    plt.clf()