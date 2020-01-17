from __future__ import print_function
import numpy as np
import cv2
from imutils.object_detection import non_max_suppression
from imutils import paths
import argparse
import imutils
import RPi.GPIO as GPIO
import time

global taygaloo_cat_en

imageWidth = 400
rangeX = ((imageWidth // 2) - 30, (imageWidth // 2) + 30)
desiredBoxHeight = 190
rangeY = (desiredBoxHeight - 20, desiredBoxHeight + 20)
cap = cv2.VideoCapture(0)
count = 0

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
# 12, 16, 18, 22, 24, 26, 32, 36

pins = {'flf': 8, 'flb': 7, 
		'frf': 12, 'frb': 16,
		'blf': 23, 'blb': 18,
		'brf': 25, 'brb': 24}

# GPIO.setup(pins['brf'], GPIO.OUT, initial=GPIO.HIGH)
# GPIO.setup(pins['blf'], GPIO.OUT, initial=GPIO.HIGH)
# GPIO.setup(pins['flf'], GPIO.OUT, initial=GPIO.HIGH)
# GPIO.setup(pins['frf'], GPIO.OUT, initial=GPIO.HIGH)

def trackImage(image):
	# initialize the HOG descriptor/person detector
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

	image = imutils.resize(image, width=min(imageWidth, image.shape[1]))
	# print(image.shape)
	orig = image.copy()

	# detect people in the image
	(rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
		padding=(8, 8), scale=1.05)

	# draw the original bounding boxes
	for (x, y, w, h) in rects:
		cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

	# draw the final bounding boxes
	maxBox = None
	maxSize = 0
	for (xA, yA, xB, yB) in pick:
		size = (xB - xA) * (yB - yA)
		if (size > maxSize):
			maxSize = size
			maxBox = [xA, yA, xB, yB]

	# if (maxBox is not None):
	# 	cv2.rectangle(image, (maxBox[0], maxBox[1]), (maxBox[2], maxBox[3]), (0, 255, 0), 2)
	# 	# print(maxBox)
	# cv2.imshow("After NMS", image)
	return maxBox



def stopTurning():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	for p in pins:
		GPIO.setup(pins[p], GPIO.OUT, initial=GPIO.LOW)



def turnLeft():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	stopTurning()
	# Turn right side forward
	GPIO.setup(pins['frf'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['brf'], GPIO.OUT, initial=GPIO.HIGH)

	# # Turn left side backward
	GPIO.setup(pins['flb'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['blb'], GPIO.OUT, initial=GPIO.HIGH)


def turnRight():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	stopTurning()
	# Turn left side forward
	GPIO.setup(pins['flf'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['blf'], GPIO.OUT, initial=GPIO.HIGH)

	# Turn right side backward
	GPIO.setup(pins['frb'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['brb'], GPIO.OUT, initial=GPIO.HIGH)


def moveForward():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	stopTurning()
	GPIO.setup(pins['flf'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['blf'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['frf'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['brf'], GPIO.OUT, initial=GPIO.HIGH)


def moveBackward():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pins['flb'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['blb'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['frb'], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(pins['brb'], GPIO.OUT, initial=GPIO.HIGH)


countStop = 0








while(True):
	if(True):
		ret, frame = cap.read()
		boxFound = trackImage(frame)
		if (boxFound is None):
			countStop += 1
			if (countStop > 5):
				stopTurning()
			else:
				moveForward()
			continue
		
		countStop = 0
		centerBoxX = boxFound[0] + ((boxFound[2] - boxFound[0]) // 2)

		# turn the car to the left
		if (centerBoxX < rangeX[0]):
			print("turning left")
			turnLeft()
		elif (centerBoxX > rangeX[1]):
			print("turning right")
			turnRight()
		else:
			print("moveForward")
			moveForward()

		# currBoxHeight = abs(boxFound[1] - boxFound[3])
		# print(boxFound, currBoxHeight, rangeY[0])
		# if (currBoxHeight < rangeY[0]):
		# 	print("move forward")
		# 	moveForward()

		# if (currBoxHeight > rangeY[1]):
		# 	print("move backward")
		# 	moveBackward()

	else:
		stopTurning()

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
stopTurning()
cap.release()
cv2.destroyAllWindows()
