import os
import requests
import datetime
import imutils
import time
import cv2


DEVICE = int(os.getenv('DEVICE', 0))
MIN_AREA = int(os.getenv('MIN_AREA', 500))
ACTION_URL = os.getenv('ACTION_URL', 'http://localhost/action')
STILL_URL = os.getenv('STILL_URL', 'http://localhost/still')
THRESHOLD = int(os.getenv('THRESHOLD', 75))

camera = cv2.VideoCapture(DEVICE)
time.sleep(0.25)
firstFrame = None
action_saved = False
action_count = 0

while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    text = "still"

    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY_INV)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < MIN_AREA:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "car #%d" % action_count

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Scene Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p ") + "T: %d" % THRESHOLD,
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # cv2.imshow("Tracking Feed", frame)
    if text != 'still' and not action_saved:
        cv2.imwrite("action%d.png" % action_count, frame)
        try:
            headers = {'content-type': 'image/png'}
            _, img_encoded = cv2.imencode('.png', frame)
            requests.post(ACTION_URL, data=img_encoded.tostring(), headers=headers)
        except requests.exceptions.ConnectionError as error:
            print(error)
        action_saved = True
    if text == 'still':
        try:
            headers = {'content-type': 'image/png'}
            _, img_encoded = cv2.imencode('.png', frame)
            requests.post(STILL_URL, data=img_encoded.tostring(), headers=headers)
        except requests.exceptions.ConnectionError as error:
            print(error)
        if action_saved:
            print('object %d tracked' % action_count)
            action_count += 1
            action_saved = False

camera.release()
