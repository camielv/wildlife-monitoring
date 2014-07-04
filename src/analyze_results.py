# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 10:27:51 2014

@author: verschoor
"""
import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np

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
      unique_ids = set(tube.real_id.values())
      if len(unique_ids) > 1:
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
Dus, in je gesorteerde lijst van tublets die loopt van 1..N.
Dan, meet de precision hoeveel goeie je hebt op punt i in je lijst.
Als de i=1 goed is, dan komt op plek 1 een 1/1
Als de i=2 goed is, dan komt op plek 2 een 2/2
Als de i=3 fout is, dan komt op plek 3 een 2/3
Als de i=4 goed is, dan komt op plek 4 een 3/4
... etc

Dit geeft je een PR-curve.

Dan blijven er twee vragen over:

1- hoe sorteer je de lijst
2- wat betekend 'goed/fout'

voor 1, zou ik zeggen het aantal BBs in een tubelet, wat denk je?

voor 2, heb je een aantal mogelijkheden dat een tubelet fout is:
- er komt geen enkele ground-truth koe voor in de tubelet
- er komen verschillende ground-truth koeien voor in de tubelet
- je hebt de koe die bij deze tubelet hoort al een keer eerder in je gesorteerde lijst gezien
  '''

if __name__ == '__main__':
  parameters = {1: ('COW810_1', 2694), 2: ('COW810_2', 2989)}
  for id in parameters:
    (video, frames) = parameters[id]
    for i in range(5, 41, 5):
      name = "../count_results/%s_%d.p" % (video, i)
      tracks = pickle.load(open(name, "rb"))
      pr_curve(tracks, i)
      #doubles = count_doubles(tracks)
      #print '--- %d --- %s' % (i, video)
    plt.legend()
    plt.savefig("%s.pdf" % (video))
    plt.clf()