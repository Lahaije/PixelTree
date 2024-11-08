import numpy as np
import cv2 as cv
import glob

"""
Code taken from https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
Adjusted the checkerboard to detect 7 x 7 grid.

How to use:
First run file 'snap_to_calibrate.py' . This file will use the laptop's webcam to crate 20 images in 2 seconds.
When the file is running, the user should sit in front of the webcam, holding a standard 8 x 8 fields chessboard.
The user should re-orient the chessboard after each picture is taken.

When the 20 pictures are complete, this file can run. The code automatically selects a subset of images and prints the
camera callibration matrix.
"""



# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = glob.glob('*.png')

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7, 7), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 7), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(mtx)