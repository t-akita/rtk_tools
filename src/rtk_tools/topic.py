from .widget import rtkWidget

import Tkinter as tk
import ttk
import subprocess
import roslib
import rospy

class rtkTopic(rtkWidget):
  def on_connect(self,topic_type):
    return
  def connect(self):
    cmd="rostopic type "+self.prop["name"]
    try:
      res=subprocess.check_output(cmd.split(" "))
      typ=res.split("/")
      exec("from "+typ[0].strip()+".msg import "+typ[1].strip()+" as topic_type")
      self.on_connect(topic_type)
      self.discon=False
    except:
      print "rtkTopic::["+self.prop["name"]+"] not registered"
  def __init__(self,page,prop):
    super(rtkTopic,self).__init__(page,prop)
    self.discon=True
    self.set_timeout(1)
  def on_timeout(self):
    if self.discon: self.connect()
    if self.discon: self.set_timeout(1)
