#!/usr/bin/python

import sys
import os
import copy
import yaml
from rtk_tools import dictlib

dir="recipe.d"
files=["param.yaml"]

def merge(f):
  entry=os.listdir(dir)
  rc=entry[0]
  yf=open(dir+"/"+rc+"/"+f, "r")
  # 2021/03/16 hato ------------------------------ start ------------------------------
  # master=yaml.load(yf)
  master = yaml.safe_load(file)
  # 2021/03/16 hato ------------------------------  end  ------------------------------

  for rc in entry[1:]:
    yf=open(dir+"/"+rc+"/"+f,"r")
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # dictlib.merge(master,yaml.load(yf))
    dictlib.merge(master,yaml.safe_load(yf))
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    yf.close()

  for rc in entry:
    yf=open(dir+"/"+rc+"/"+f,"r")
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # dictlib.merge(master,yaml.load(yf))
    dictlib.merge(master,yaml.safe_load(yf))
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    yf.close()
    yf=open(dir+"/"+rc+"/"+f,"w")
    yaml.dump(master,yf,default_flow_style=False)
    yf.close()

def trim(f):
  entry=os.listdir(dir)
  rc=entry[0]
  yf=open(dir+"/"+rc+"/"+f, "r")
  # 2021/03/16 hato ------------------------------ start ------------------------------
  # master=yaml.load(yf)
  master=yaml.safe_load(yf)
  # 2021/03/16 hato ------------------------------  end  ------------------------------

  for rc in entry[1:]:
    yf=open(dir+"/"+rc+"/"+f,"r")
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # dictlib.intersect(master,yaml.load(yf))
    dictlib.intersect(master,yaml.safe_load(yf))
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    yf.close()

  for rc in entry:
    dm=copy.deepcopy(master)
    yf=open(dir+"/"+rc+"/"+f,"r")
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # dictlib.intersect(dm,yaml.load(yf))
    dictlib.intersect(dm,yaml.safe_load(yf))
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    yf.close()
    yf=open(dir+"/"+rc+"/"+f,"w")
    yaml.dump(dm,yf,default_flow_style=False)
    yf.close()

if len(sys.argv)>1:
  if sys.argv[1]=='trim':
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # print 'run as trim mode'
    print('run as trim mode')
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    map(trim,files)
  else:
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # print 'run as merge mode'
    print('run as merge mode')
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    map(merge,files)
else:
  # 2021/03/16 hato ------------------------------ start ------------------------------
  #print 'run as merge mode'
  print('run as merge mode')
  # 2021/03/16 hato ------------------------------ start ------------------------------
  map(merge,files)
