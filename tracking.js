const cv = require('opencv4nodejs');
const {grabFrames, drawRectAroundBlobs} = require('./utils');


const bgSubtractor = new cv.BackgroundSubtractorMOG2();
const delay = 50;
const cap = new cv.VideoCapture(0);
const size = new cv.Size(640, 480);
const out  = new cv.VideoWriter('test.avi', cv.VideoWriter.fourcc('MJPG'), 15, size, true);

grabFrames(cap, delay, (frame) => {
    console.log(frame)
    const foreGroundMask = bgSubtractor.apply(frame);

    const ITERATIONS = 2;
    const dilated = foreGroundMask.dilate(
        cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(4, 4)),
        new cv.Point(-1, -1),
        ITERATIONS
    );

    const blurred = dilated.blur(new cv.Size(10, 10));
    const thresholded = blurred.threshold(200, 255, cv.THRESH_BINARY);
    const minPxSize = 4000;
    drawRectAroundBlobs(thresholded, frame, minPxSize);

    cv.imshow('foreGroundMask', foreGroundMask);
    cv.imshow('thresholded', thresholded);
    cv.imshow('frame', frame);
    out.write(frame);
});
