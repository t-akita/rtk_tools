#!/usr/bin/env python3

import collections

def merge(DCT,dct):
  for k,v in dct.items():
    if (k in DCT and isinstance(DCT[k], dict) and isinstance(dct[k], dict)):
      merge(DCT[k],dct[k])
    else:
      DCT[k]=dct[k]

def cross(DCT,dct):
  for k,v in DCT.items():
    if isinstance(DCT[k], dict) and (k in dct and isinstance(dct[k], dict)):
      cross(DCT[k],dct[k])
    elif k in dct:
      DCT[k]=dct[k]

Param={
  "car":{
    "toyota":{
      "crown":500,"corola":100
    },
    "used":50
  },
  "train":1000,
  "food":{
    "gust":3,"kfc":4
  }
}

param={
  "car":{
    "toyota":{
      "corola":200,"vitz":50
    },
    "used":10
  },
  "wear":{
    "gu":3,"workman":1
  },
  "week":[1,2,3,4,5,6]
}

cross(Param,param)

print(Param)
