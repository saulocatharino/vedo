#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 15:23:35 2017

@author: mmusy
"""
from __future__ import division, print_function
import os
from glob import glob
import vtkutils as ut


###################################################################### 
def screenshot(obj=None, filename='screenshot.png'):
    try:
        import gtk.gdk
        w = gtk.gdk.get_default_root_window().get_screen().get_active_window()
        sz = w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
        pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0, sz[0], sz[1])
        if pb is not None:
            pb.save(filename, "png")
        else: ut.printc("Unable to save the screenshot. Skip.", 'red')
    except:
        import vtk
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(obj.renderWin)
        w2if.SetMagnification(1) #set the resolution of the output image
        w2if.SetInputBufferTypeToRGBA() #also record the alpha (transparency) channel
        w2if.ReadFrontBufferOff() # read from the back buffer
        w2if.Update()
         
        pngwriter = vtk.vtkPNGWriter()
        pngwriter.SetFileName(filename)
        pngwriter.SetInputConnection(w2if.GetOutputPort())
        pngwriter.Write()
        obj.interactor.Render()


def openVideo(obj=None, name='movie.avi', fps=12, duration=None, format="XVID"):
    try:
        import cv2 #just check existence
        cv2.__version__
    except:
        ut.printc("openVideo: cv2 not installed? Skip.",1)
        return
    obj._videoname = name
    obj._videoformat = format
    obj._videoduration = duration
    obj._fps = float(fps) # if duration is given, will be recalculated
    obj._frames = []
    if not os.path.exists('/tmp/v'): os.mkdir('/tmp/v')
    for fl in glob("/tmp/v/*.png"): os.remove(fl)
    ut.printc(("Video", name, "is open. Press q to continue.", 'magenta'))
    
    
def addFrameVideo(obj=None):
    if not obj._videoname: return
    fr = '/tmp/v/'+str(len(obj._frames))+'.png'
    screenshot(obj, fr)
    obj._frames.append(fr)


def pauseVideo(obj=None, pause=0):
    '''insert a pause, in seconds'''
    if not obj._videoname: return
    fr = obj._frames[-1]
    n = int(obj._fps*pause)
    for i in range(n): 
        fr2='/tmp/v/'+str(len(obj._frames))+'.png'
        obj._frames.append(fr2)
        os.system("cp -f %s %s" % (fr, fr2))
       

def releaseVideo(obj=None):      
    if not obj._videoname: return
    import cv2
    if obj._videoduration:
        obj._fps = len(obj._frames)/float(obj._videoduration)
        ut.printc(("Recalculated video FPS to", round(obj._fps,3)), 'yellow')
    else: obj._fps = int(obj._fps)
    fourcc = cv2.cv.CV_FOURCC(*obj._videoformat)
    vid = None
    size = None
    for image in obj._frames:
        if not os.path.exists(image):
            ut.printc(('Image not found:', image), 1)
            continue
        img = cv2.imread(image)
        if vid is None:
            if size is None:
                size = img.shape[1], img.shape[0]
            vid = cv2.VideoWriter(obj._videoname, fourcc, obj._fps, size, True)
        if size[0] != img.shape[1] and size[1] != img.shape[0]:
            img = cv2.resize(img, size)
        vid.write(img)
    if vid:
        vid.release()
        ut.printc(('Video saved as', obj._videoname), 'green')
    obj._videoname = False


# experimental
#    def openVideo2(self, name='movie.avi', fps=12, quality=1):
#        w2if = vtk.vtkWindowToImageFilter()
#        w2if.SetInput(self.renderWin)
#        self.writer = vtk.vtkAVIWriter()
#        self.writer.SetInputConnection(w2if.GetOutputPort())
#        self.writer.SetFileName(name)
#        self.writer.SetRate(fps)
#        self.SetQuality(quality)
#        self.writer.Start()
#        return     
#    def addFrameVideo2(self):     
#        self.writer.Write()
#        return         
#    def releaseVideo2(self):   
#        self.writer.End()
#        return 
