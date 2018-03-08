import os
import requests
import datetime
import imutils
import time
import cv2


DEVICE = int(os.getenv('DEVICE', 0))
MIN_AREA = int(os.getenv('MIN_AREA', 500))
THRESHOLD = int(os.getenv('THRESHOLD', 75))
ACTION_URL = os.getenv('ACTION_URL', 'http://localhost/action')
STILL_URL = os.getenv('STILL_URL', 'http://localhost/still')

camera = cv2.VideoCapture(DEVICE)  # open video capture stream from the camera
time.sleep(0.25)
firstFrame = None
action_saved = False
action_count = 1

while True:  # start endless loop

    (grabbed, frame) = camera.read()  # grab a frame from the stream
    text = "still"

    if not grabbed:
        break

    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # create a grayscale frame
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if firstFrame is None:  # initialize the first frame
        firstFrame = gray
        continue

    frameDelta = cv2.absdiff(firstFrame, gray)  # compute difference between the first frame and current one
    thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]  # create thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)  # dilate thresholded image to fill in the gaps
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,  # find contours
                                 cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < MIN_AREA:
            continue

        # draw bounding box over the contours on the original frame
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "car #%d" % action_count

    # stamp datetime and other info onto the original frame
    cv2.putText(frame, "Scene Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p ") + "T: %d" % THRESHOLD,
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # if current frame contains boxed out contours (i.e.there is some
    # action), print the number, POST it to an 'action' HTTP endpoint and save
    # the image to filesystem
    if text != 'still' and not action_saved:
        print('action frame', action_count)
        cv2.imwrite("action%d.png" % action_count, frame)
        try:
            headers = {'content-type': 'image/png'}
            _, img_encoded = cv2.imencode('.png', frame)
            requests.post(ACTION_URL, data=img_encoded.tostring(), headers=headers)
        except requests.exceptions.ConnectionError as error:
            print(error)
        action_saved = True

    # otherwise POST it to a 'still' (no action) HTTP endpoint, for the live feed
    if text == 'still':
        try:
            headers = {'content-type': 'image/png'}
            _, img_encoded = cv2.imencode('.png', frame)
            requests.post(STILL_URL, data=img_encoded.tostring(), headers=headers)
        except requests.exceptions.ConnectionError as error:
            print(error)
        if action_saved:  # if a still frame follows an action frame - increment the counter
            print('object %d tracked' % action_count)
            action_count += 1
            action_saved = False

camera.release()
