#!/usr/bin/env python

import cv2
import numpy as np
from utils import get_four_points
from datetime import datetime

#def reproject(img):

def open_stream():
  #stream = cv2.VideoCapture(0)
  stream = cv2.VideoCapture(1)
  #stream = cv2.VideoCapture("input.mp4")
  return stream


def get_frame(stream):
  ret_val, img = stream.read()
  return img


def show_frame(img,mirror=False):
  if mirror: 
      img = cv2.flip(img, 1)
  cv2.imshow('my webcam', img)


def main():

    # Parse Arguments

    stream = open_stream()
    # if Error, then quit

    img = get_frame(stream)
    # Use the first frame for reproject calibration 

    # get the four points to apply reporjection
    pts_src = get_four_points(img)

    # calculate width and height for the reprojected image
    W = int(pts_src[2][0] - pts_src[3][0])
    H = int(pts_src[3][1] - pts_src[0][1])

    pts_dst = np.array(
                       [
                        [0,0],
                        [W - 1, 0],
                        [W - 1, H -1],
                        [0, H - 1 ]
                        ], dtype=float
                       )
                       
    # Initialize Destination Frame
    im_dst = np.zeros((H,W,3),dtype="uint8")

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)
    size = im_dst.shape

    while True:
      
        #capture a new frame from camera
        im_src = get_frame(stream)

        #reproject_frame
        im_dst = cv2.warpPerspective(im_src, h,(size[1],size[0]))

        #show_frame(img,mirror=True)
        show_frame(im_src,mirror=False)

        cv2.imshow('reprojected', im_dst)

        #print(str(datetime.now()))

        if cv2.waitKey(1) == 27: # Escape Character
            break # Esc to quit

if __name__ == '__main__':
    main()
