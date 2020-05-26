import cv2
import numpy as np
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("init calibration")

# Chessboard dimensions
CHESSBOARD_WIDTH = 8
CHESSBOARD_HEIGHT = 6

object_point = np.zeros((CHESSBOARD_WIDTH*CHESSBOARD_HEIGHT, 3), np.float32)
object_point[:, :2] = np.mgrid[0:CHESSBOARD_WIDTH, 0:CHESSBOARD_HEIGHT].T.reshape(-1, 2)

# images with printed chessboard
filenames = [
    "TestImages/1.jpg",
    #"TestImages/2.jpg",
    #"TestImages/3.jpg",
    #"TestImages/4.jpg",
    #"TestImages/5.jpg"
]

image_size = []

object_points = []
image_points = []

last_image_shape = []

for filename in filenames:

    logging.info("processing file " + filename)

    logging.info("reading image...")
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    last_image_shape = gray.shape[::-1]

    logging.info("finding chessboard corners...")

    flags = 0
    flags |= cv2.CALIB_CB_ADAPTIVE_THRESH
    flags |= cv2.CALIB_CB_FAST_CHECK
    flags |= cv2.CALIB_CB_NORMALIZE_IMAGE

    result, corners = cv2.findChessboardCorners(gray, (CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT), flags)

    if result is True:
        logging.info("find result = " + str(result) + ", corners = " + ",".join(map(str, corners)))

        object_points.append(object_point)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_subpix = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        image_points.append(corners_subpix)

    else:
        logging.info("can't find chessboard at the image " + filename)

result, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors \
    = cv2.calibrateCamera(object_points, image_points, last_image_shape, None, None)

logging.info("distortion coefficients = " + str(distortion_coefficients))

logging.info("writing test image...")
ref_image = cv2.imread('TestImages/ref.jpg')
h,  w = ref_image.shape[:2]
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w, h), 1, (w,h))

result_image = cv2.undistort(ref_image, camera_matrix, distortion_coefficients, None, new_camera_matrix)

cv2.imwrite('TestImages/reg_out.jpg', result_image)

logging.info("finished")

