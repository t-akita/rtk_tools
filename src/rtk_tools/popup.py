from .topic import rtkTopic

import tkinter as tk
from tkinter import messagebox
import subprocess
import roslib
import rospy

class rtkPopup(rtkTopic):
  def cb_sub(self,msg):
    sa=str(msg).split("\n")
    sd=""
    for s in sa:
      n=s.find(': ')
      if n<0: continue
      s=s[n+2:]
      if len(s)==0: continue
      sd=sd+s
    self.disp=sd
    self.set_timeout(0)
  def __init__(self,page,prop):
    page.widgets.append(self)
    self.on_init()
    try:
      dictlib.merge(self.prop,prop)
    except:
      self.prop=prop
    self.discon=True
    self.set_timeout(1)
    self.disp=""
  def on_connect(self,topic_type):
    rospy.Subscriber(self.prop["name"],topic_type,self.cb_sub)
  def on_timeout(self):
    if self.discon: super(rtkPopup,self).on_timeout()
    elif len(self.disp)>0:
      f=tkMessageBox.showinfo("Notification",self.prop["label"]+"\n"+self.disp)

