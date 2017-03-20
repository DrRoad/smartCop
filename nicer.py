#!/usr/bin/env python

import cv2
import numpy as np
from utils import get_four_points
from datetime import datetime
from optparse import OptionParser

#def reproject(img):

def open_stream(input_source):
  stream = cv2.VideoCapture(input_source)
  return stream


def show_frame(img,mirror=False):
  if mirror: 
      img = cv2.flip(img, 1)
  cv2.imshow('my webcam', img)


def main():
    # Parse Arguments
    parser = OptionParser()

    # If file_source is not specified, then camera will be used
    parser.add_option('--file_source', dest='file_source', default="None")

    # If no camera specified, then camera 0 will be used
    parser.add_option('--camera', dest='camera', default="0", type="int")

    # Warp is disable by default
    parser.add_option('--warp', dest='warp', action='store_true')
    parser.add_option('--no-warp', dest='warp', action='store_false')
    parser.set_defaults(warp=False)

    options, remainder = parser.parse_args()
    print(options.camera)
    print(options.warp)
    print(options.file_source)

    if options.file_source == "None":
       print("No input file source selected")
       stream = open_stream(options.camera)
    else:
       print("input desired from a file")
       stream = open_stream(options.file_source)

    if stream.isOpened() == False:
      print("failed to open input stream")
      return

    ret_val, img = stream.read()
    if ret_val == False:
      print("EOS input stream, exit")
      return


    #cv2.imshow('input image',img)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.bilateralFilter(gray, 11, 17, 17)
    #cv2.imshow('gray image',gray)
    #edged = cv2.Canny(gray, 30, 200)
    #cv2.imshow('Canny edges',edged)

    #(_,contours, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:40]
    #cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:40]
    #cv2.drawContours(img,cnts,-1,(0,255,0),2) #-1 fills it
    #cv2.imshow('final',img)

    #while(True):
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #       break

    #return

    if options.warp == True:
       print("warp was set to true");

       # Use the very first frame to get warp calibration
       # get the four points to apply reprojection
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
    # warp calibration done

    while True:
      
        #capture a new frame from camera
        ret_val, im_src = stream.read()
        if ret_val == False:
           print("EOS in input stream");
           if options.file_source != "None":
               print("Reopen the Input File");
               stream = open_stream(options.file_source)
               if stream.isOpened() == False:
                 print("Could not open input file")
                 return 
               ret_val, im_src = stream.read()
               if ret_val == False:
                 print("Could not read from File")
                 return

        #reproject_frame
        if options.warp == True:
           im_dst = cv2.warpPerspective(im_src, h,(size[1],size[0]))
           cv2.imshow('reprojected', im_dst)

        show_frame(im_src,mirror=False)

        # TODO: Pre-process the Input Image before conversion to gray?

        if options.warp == True:
            gray = cv2.cvtColor(im_dst, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(im_src, cv2.COLOR_BGR2GRAY)

        # TODO: Post-process the Input Image to sharpen it?

        # TODO: Get filter parameters from user
        #gray = cv2.bilateralFilter(gray, 11, 17, 17)
        cv2.imshow('gray image',gray)

        # TODO: Get Canny parameters from user
        edged = cv2.Canny(gray, 30, 200)
        cv2.imshow('Canny edges',edged)

        (_,contours, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key = cv2.contourArea, reverse = True)
        #cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:40]

        new_contour = cnts[:1]
        # TODO: Get a Threshold Parameter from User
        for c in cnts:
            # approximate the contour
            #peri = cv2.arcLength(c, True)
            # approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            #print(peri>100)
            area = cv2.contourArea(c)
            if area > 10:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if (len(approx) == 3 or 4 or 5):
                    new_contour.append(c)

        cnts = new_contour

        print("OVER TO NEXT Frame")

        # TODO: Get a parameter if only rectangle to be displayed
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        # if len(approx) == 4:
        # screenCnt = approx
        # break

        if options.warp == True:
            cv2.drawContours(im_dst,cnts,-1,(0,255,0),2) #-1 fills it
            cv2.imshow('final',im_dst)
        else:
            cv2.drawContours(im_src,cnts,-1,(0,255,0),2) #-1 fills it
            cv2.imshow('final',im_src)

        #print(str(datetime.now()))

        if cv2.waitKey(1) == 27: # Escape Character
            break # Esc to quit

if __name__ == '__main__':
    main()
