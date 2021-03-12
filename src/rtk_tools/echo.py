from .topic import rtkTopic

import tkinter as tk
from tkinter import ttk
import subprocess
import roslib
import rospy

class rtkEcho(rtkTopic):
  def cb_sub(self,msg):
    sa=str(msg).split("\n")
    sd=""
    h=0
    width=self.Config["width"][1]
    f=""
    if "format" in self.prop: f="{:"+self.prop["format"]+"}"
    for s in sa:
      n=s.find(': ')
      if n<0: continue
      s=s[n+2:]
      if len(s)==0: continue
      fmt=f
      if (len(fmt)==0 and len(s)>width):
        fmt="{:."+str(width-6)+"e}"
      if len(fmt)>0:
        try:
          v=float(s)
          s=fmt.format(v)
        except Exception:
          s="-"*width
      sd=sd+s
      h=h+1
      if h<self.height: sd=sd+"\n"
      else: break
    self.disp=sd
    self.set_timeout(0)
  def __init__(self,page,prop):
    super(rtkEcho,self).__init__(page,prop)
    self.height=1+prop["label"].count("\n")
    self.io=tk.Text(page.frame,
      font=self.label["font"],
      width=self.Config["width"][1],
      height=self.height)
    self.io.grid(row=len(page.widgets),column=1,sticky="nswe")
    self.io.tag_configure("tag-right",justify="right")
    self.disp=""
  def on_connect(self,topic_type):
    rospy.Subscriber(self.prop["name"],topic_type,self.cb_sub)
  def on_timeout(self):
    if self.discon: super(rtkEcho,self).on_timeout()
    elif len(self.disp)>0:
      self.io.config(state='normal')
      self.io.config(foreground='#000000')
      self.io.delete("0.0","end")
      self.io.insert("0.0",self.disp,"tag-right")
      self.io.config(state='disabled')
      self.disp=""
      self.set_timeout(5)
    else:
      self.io.config(state='normal')
      self.io.config(foreground='#AAAAAA')
      self.io.config(state='disabled')

