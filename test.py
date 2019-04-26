from gpiozero import LED
from gpiozero import Button
from gpiozero import Motor
from time     import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2

motorFrontLeft  = Motor(forward=12, backward=16)
motorFrontRight = Motor(forward=20, backward=21)
motorBackLeft   = Motor(forward= 6, backward=13)
motorBackRight  = Motor(forward=19, backward=26)

def nothing(x):
    pass

def setSpeedFront(speedA, speedB):
 if (speedA >= 0):
     if (speedA > 100):
         speedA = 100;
     speedA /= 100
     motorFrontLeft.forward(speedA)
 else:
     if (speedA < -100):
         speedA = -100
     speedA = -speedA
     speedA /= 100
     motorFrontLeft.backward(speedA)
     
 if (speedB > 100):
     if (speedB > 100):
         speedB = 100
     speedB /= 100
     motorFrontRight.forward(speedB)
 else:
     if (speedB < -100):
         speedB = -100
     speedB = -speedB
     speedB /= 100
     motorFrontRight.backward(speedB)
 return;


def setSpeedBack(speedA, speedB):
 if (speedA >= 0):
     if (speedA > 100):
         speedA = 100;
     speedA /= 100
     motorBackLeft.forward(speedA)
 else:
     if (speedA < -100):
         speedA = -100
     speedA = -speedA
     speedA /= 100
     motorBackLeft.backward(speedA)
     
 if (speedB >= 0):
     if (speedB > 100):
         speedB = 100
     speedB /= 100
     motorBackRight.forward(speedB)
 else:
     if (speedB < -100):
         speedB = -100
     speedB = -speedB
     speedB /= 100
     motorBackRight.backward(speedB)
 return;

def setSpeed(frLeft, frRight, backLeft, backRight):
    setSpeedFront(frLeft, frRight)
    setSpeedBack(backLeft, backRight)
    
# Create trackbar and init value
cv2.namedWindow('UpperHSV')
cv2.namedWindow('LowerHSV')
cv2.createTrackbar('UH', 'UpperHSV', 0, 179, nothing)
cv2.createTrackbar('US', 'UpperHSV', 0, 255, nothing)
cv2.createTrackbar('UV', 'UpperHSV', 0, 255, nothing)
cv2.createTrackbar('LH', 'LowerHSV', 0, 179, nothing)
cv2.createTrackbar('LS', 'LowerHSV', 0, 255, nothing)
cv2.createTrackbar('LV', 'LowerHSV', 0, 255, nothing)
# init value
cv2.setTrackbarPos('UH', 'UpperHSV', 60)
cv2.setTrackbarPos('US', 'UpperHSV', 255)
cv2.setTrackbarPos('UV', 'UpperHSV', 255)
cv2.setTrackbarPos('LH', 'LowerHSV', 30)
cv2.setTrackbarPos('LS', 'LowerHSV', 130)
cv2.setTrackbarPos('LV', 'LowerHSV', 80) 

# turn on camera for video
cap = cv2.VideoCapture(0)

while True:
    setSpeed(0,0,0,0)
    
    # adjust trackbar
    UH = cv2.getTrackbarPos('UH','UpperHSV')
    US = cv2.getTrackbarPos('US','UpperHSV')
    UV = cv2.getTrackbarPos('UV','UpperHSV')
    LH = cv2.getTrackbarPos('LH','LowerHSV')
    LS = cv2.getTrackbarPos('LS','LowerHSV')
    LV = cv2.getTrackbarPos('LV','LowerHSV')
    
    _, frame = cap.read()
    
    #cv2.imshow('frame', frame)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
     # define range of color in HSV
    lower_HSV = np.array([LH,LS,LV])
    upper_HSV = np.array([UH,US,UV])
    
    thresh = cv2.inRange(hsv, lower_HSV, upper_HSV)
        
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(frame, center, 3, (0, 0, 255), -1)
            cv2.putText(frame,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
            cv2.putText(frame,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
 
    # show the frame to our screen
    cv2.imshow("Original", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Mask", mask)
 
    if cv2.waitKey(1) & 0xFF is ord('q'):
        break
        
    key = cv2.waitKey(10) & 0xff
    if key == 27:
        break
    
setSpeed(0,0,0,0)   
cap.release()
cv2.destroyAllWindows()
