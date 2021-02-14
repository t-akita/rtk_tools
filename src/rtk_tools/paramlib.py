#!/usr/bin/env python3

import roslib
import rospy
import re

re1=None
re2=None

def __init__():
  global re1,re2
  re1=re.compile('/(.*)\[')
  re2=re.compile('/(.*)')

def get_param(tag):
  if not re1: __init__()
  tags=tag.split('[',1)
  if len(tags)==1:
    return rospy.get_param(tag)
  prm=rospy.get_param(tags[0])
  pass1=re1.sub(r'["\1"][',tags[1])
  pass2=re2.sub(r'["\1"]',pass1)
  return eval('prm['+pass2)

def set_param(tag,sval):
  tags=tag.split('[',1)
  if len(tags)==1:
    return rospy.set_param(tag,sval)
  prm=rospy.get_param(tags[0])
  pass1=re1.sub(r'["\1"][',tags[1])
  pass2=re2.sub(r'["\1"]',pass1)
  exec('prm['+pass2+'=sval')
  return rospy.set_param(tags[0],prm)

if __name__ == '__main__':
  rospy.init_node("array",anonymous=True)
  conf=get_param("/solver/Rejection")
  print("return=",conf)
  conf=get_param("/left/detector/ROIEdge[1]/Type")
  print("return=",conf)
  conf=get_param("/left/detector/Binary/ThBinary[3]")
  print("return=",conf)
  conf=get_param("/left/detector/ROIEdge[1]/Data[2]")
  print("return=",conf)
  conf=set_param("/solver/Rejection",1)
  conf=set_param("/left/detector/ROIEdge[1]/Type",2)
  conf=set_param("/left/detector/Binary/ThBinary[3]",3)
  conf=set_param("/left/detector/ROIEdge[1]/Data[2]",4)

