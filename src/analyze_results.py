# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 10:27:51 2014

@author: verschoor
"""

import cPickle as pickle

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



def pr_curve(tracks):
  pass

if __name__ == '__main__':
  parameters = {1: ('COW810_1', 2694), 2: ('COW810_2', 2989)}
  for id in parameters:
    (video, frames) = parameters[id]
    for i in range(5, 41, 5):
      name = "../count_results/%s_%d.p" % (video, i)
      tracks = pickle.load(open(name, "rb"))
      doubles = count_doubles(tracks)
      print '--- %d --- %s' % (i, video)