from gpiozero import LED
from gpiozero import Button
from gpiozero import Motor
from time     import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2

#define parameters for speed and angle
#----------------- Speed ---------------
errS = 0
preErrS = 0
kPS = 0.65
kIS = 0.0
kDS = 0.4
outS = 0
pPartS = 0
iPartS = 0
dPartS = 0
#----------------- Angle ---------------
errA = 0
preErrA = 0
kPA = 5
kIA = 0
outA = 0
pPartA = 0
iPartA = 0
#---------------------------------------
width = 640
heigh = 480
Gradius = 0
car_pos = width/2
center_x = 0
center_y = 0
run_flag = 0

motorFrontLeft  = Motor(forward=11, backward=5)
motorFrontRight = Motor(forward=10, backward=9)
motorBackLeft   = Motor(forward= 6, backward=13)
motorBackRight  = Motor(forward=26, backward=19)
led1 = LED(2)
led2 = LED(3)
led3 = LED(4)
btn1 = Button(22)
btn2 = Button(27)

def nothing(x):
    pass
def setSpeedFront(speedA, speedB):
    # set giá trị động cơ (%)
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
     
 if (speedB >= 0):
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
def fix_position(pos):
    global errA,preErrA,kPA,kIA,outA,pPartA,iPartA
    errA = pos - car_pos
    if(errA > 60):
        setSpeed(15,-20,20,-15)
    elif(errA < -60):
        setSpeed(-20,15,-15,20)
    else:
        setSpeed(0,0,0,0)
    
def calculator(pos):
    # thông báo các biến dưới đây là các biến toàn cục đã dc khai báo ở trên
    global errA,preErrA,kPA,kIA,outA,pPartA,iPartA
    global errS,preErrS,kPS,kIS,kDS,outS,pPartS,iPartS, dPartS
    global Gradius
    errA = pos - car_pos
    if(errA >=-60 and errA <= 60):
        errA = 0
    pPartA = kPA * errA
    #setSpeed(pPartA, -pPartA, pPartA, -pPartA)
    if(Gradius >= 65 and Gradius <= 75):
        errS = 0
    if(Gradius > 75):
        errS = 80 - Gradius
    elif(Gradius < 65):
        errS = 60 - Gradius
    pPartS = kPS * errS
    dPartS = kDS * (preErrS - errS)
    iPartS += (kIS *errS)
    outS = pPartS + dPartS + iPartS
    ####################################################
    #preErrS = errS
    # giới hạn giá trị tốc độ động cơ
    if(outS > 100):
        outS = 100
    elif(outS < -100):
        outS = -100
    # nếu khoảng cách ok thì fix vị trí
    if(Gradius >= 45 and Gradius <= 75):
        fix_position(pos)
    # nếu bán kính > 75 thì chạy lui
    elif(Gradius > 75):
        setSpeed(-10, -10, -10, -10)
    # nếu bán kính < 65 thì chạy tơi
    elif(Gradius < 65):
        if(errA < -90): #60
            setSpeed(outS * 0, outS*5.5, outS * 0, outS*3.5)
        elif(errA > 90):
            setSpeed(outS * 5.5, outS * 0, outS * 3.5, outS* 0)
        else:
            setSpeed(outS, outS, outS, outS)

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
_, frame = cap.read()
def imageProcessing():
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
    
    # tao ma tran 5x5 
    kernel = np.ones((5,5),np.uint8)
    # khu nhieu
    # khu nhieu ngoai vung den
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    # khu nhieu ben trong vung trang
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # chon vat the lon nhat la trai banh
        c = max(cnts, key=cv2.contourArea)
        # ve hinh tron xung quanh vat the, lay duoc ban kinh'
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        # tim trong tam cua vat the
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        global Gradius
        Gradius = radius
        global center_x
        center_x =center[0]
        global center_y
        center_y =center[1]
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(frame, center, 3, (0, 0, 255), -1)
            cv2.putText(frame,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255, 255, 255),1)
            cv2.putText(frame,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255, 255, 255),1)
            cv2.putText(frame,"radius: "+str(radius), (center[0]+10,center[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255, 255, 255),1)
    # show the frame to our screen
    #cv2.rectangle(frame,(100,110),(540,370),(180,105,255),2)
    cv2.line(frame,(int(width/2), 0), (int(width/2), int(heigh-1)), (0, 255, 0), 2)
    cv2.line(frame,(int(width/2 -60), 0), (int(width/2-60), int(heigh-1)), (255, 255, 0), 2)
    cv2.line(frame,(int(width/2 +60), 0), (int(width/2+60), int(heigh-1)), (255, 255, 0), 2)
    cv2.imshow("Original", frame)
    #cv2.imshow("Thresh", thresh)
    cv2.imshow("Mask", mask)
    return (center_x, center_y)
while True:
    #setSpeed(30,10,20,10)
    #imageProcessing()
    #calculator(center_x)
    #fix_position(center_x)
    #print("center_x: ", Gradius)
    #print("center_y: ", center_y)
    # press "ESC" to exit
    if(btn1.is_pressed):
        run_flag = 1
        sleep(0.5)
    if(btn2.is_pressed):
        run_flag = 0
        sleep(0.5)
    if(run_flag == 1):
        led1.off()              # bật led 1
        led3.off()
        imageProcessing()       # xử lý ảnh
        calculator(center_x)    # tính toán đưa ra tốc độ chạy
    else:
        led1.on()               # tắt led 1
        led3.on()               # tắt led 3
        setSpeed(0,0,0,0)       # đừng động cơ
    key = cv2.waitKey(1) & 0xff
    if key == 27:
        break
    
setSpeed(0,0,0,0)   
cap.release()
cv2.destroyAllWindows()
