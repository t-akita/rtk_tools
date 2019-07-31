from .widget import rtkWidget

import Tkinter as tk
import ttk
import subprocess
import roslib
import rospy
import yaml

class rtkEcho(rtkWidget):
  width=16
  def cb_sub(self,msg):
    sa=str(msg).split("\n")
    sd=""
    h=0
    for s in sa:
      n=s.find(': ')
      if n<0: continue
      s=s[n+2:]
      if len(s)==0: continue
      sd=sd+" "*(self.width-len(s))+s
      h=h+1
      if h<self.height: sd=sd+"\n"
      else: break
    self.disp=sd
  def connect(self):
    cmd="rostopic type "+self.prop["name"]
    try:
      res=subprocess.check_output(cmd.split(" "))
      typ=res.split("/")
      exec("from "+typ[0].strip()+".msg import "+typ[1].strip()+" as topic_type")
      rospy.Subscriber(self.prop["name"],topic_type,self.cb_sub)
      self.discon=False
    except:
      print "No topic",self.prop["name"]
  def __init__(self,page,prop):
    super(rtkEcho,self).__init__(page,prop)
    self.height=1+prop["label"].count("\n")
    self.io=tk.Text(page.frame,width=self.width,height=self.height)
    self.io.grid(row=len(page.widgets),column=2,sticky="nsw")
    self.discon=True
    self.disp=""
    self.dimmer=0
  def reflesh(self):
    if self.discon: self.connect()
    elif len(self.disp)>0:
      self.io.config(state='normal')
      self.io.config(foreground='#000000')
      self.io.delete("0.0","end")
      self.io.insert("0.0",self.disp)
      self.io.config(state='disabled')
      self.disp=""
      self.dimmer=5
    elif self.dimmer>0:
      self.dimmer=self.dimmer-1
      if self.dimmer==0:
        self.io.config(state='normal')
        self.io.config(foreground='#AAAAAA')
        self.io.config(state='disabled')
