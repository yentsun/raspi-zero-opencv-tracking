raspi-zero-opencv-tracking
==========================

OpenCV tracking experiment for RasPi Zero W


Usage
-----
```
python main.py
```

Optional envars:

* `DEVICE` - video capture device index, default: `0`
* `MIN_AREA` - minimum area size, default: `500`
* `POST_URL` - url to POST images to, default: `http://localhost/action`
* `THRESHOLD` - threshold value for `cv2.threshold`, default: `75`
