# Object-following-car
(the main file name is "Object-following-car.py")

Automatic car using raspberry pi 3 B+, Opencv and Python to develop.
The car following a tennis ball.

simple explain:

- Read image from camera
- Change the color space to HSV color space
- Filter color to black and white
- Detect object:
  + find contour function to detect white area.
  + draw a circle around it to calculate the diameter
  + using formula (M["m10"] / M["m00"]), int(M["m01"] / M["m00"]) to find center of the object
- Using PID algorithm to follow object
