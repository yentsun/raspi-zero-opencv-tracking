raspi-zero-opencv-tracking
==========================

OpenCV tracking experiment for RasPi Zero W.


Usage
-----
```
python main.py
```

Optional envars:

* `DEVICE` - video capture device index, default: `0`
* `MIN_AREA` - minimum area size, default: `500`
* `ACTION_URL` - url to POST action images to, default: `http://localhost/action`
* `STILL_URL` - url to POST still images to, default: `http://localhost/still`
* `THRESHOLD` - threshold value for `cv2.threshold`, default: `75`
