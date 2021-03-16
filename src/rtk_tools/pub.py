from .topic import rtkTopic
from . import dictlib
import subprocess

import tkinter as tk
from tkinter import messagebox
import roslib
import rospy
from std_msgs.msg import Bool

class rtkPub(rtkTopic):
  buttonicon=None
  def on_init(self):
    super(rtkPub,self).on_init()
    dictlib.merge(self.prop,{"message":"","confirm":False,"icon":"run.png"})
  def __init__(self,page,prop):
    super(rtkPub,self).__init__(page,prop)
    # 2021/03/16 hato ------------------------------ start ------------------------------
    # iconpath=commands.getoutput("rospack find rtk_tools")+"/icon/"
    iconpath=subprocess.getoutput("rospack find rtk_tools")+"/icon/"
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    if self.buttonicon is None:
      self.buttonicon=tk.PhotoImage(file=iconpath+self.prop["icon"])
    self.io=tk.Button(page.frame,image=self.buttonicon,command=self.cb_pub)
    self.io.grid(row=len(page.widgets),column=1,sticky="nswe")

  def cb_pub(self):
    x=self.io.winfo_rootx()
    y=self.io.winfo_rooty()
    msg=""
    if type(self.prop["confirm"]) is str:
      msg=self.prop["confirm"]
    elif self.prop["confirm"]:
      msg=self.prop["message"]
      if msg=="": msg=self.prop["label"]
    f=True
    if msg!="": f=tkMessageBox.askyesno("Confirm",msg)
    if f is False: return
    if self.discon:
      self.label.config(background='#FF0000')
    else:
      self.pub.publish(self.msg)
      self.label.config(background='#555555')
    self.set_timeout(0.1)

  def on_connect(self,topic_type):
    self.pub=rospy.Publisher(self.prop["name"],topic_type,queue_size=1)
    self.msg=topic_type()
    if "data" in self.prop:
      exec("self.msg"+self.prop["data"])

  def on_timeout(self):
    if self.discon: super(rtkPub,self).on_timeout()
    self.label.config(background=self.Config["color"]["label"][1])

