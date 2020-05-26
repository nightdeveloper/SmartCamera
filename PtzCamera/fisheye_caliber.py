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
REF_IMAGE = 'TestImages/ref.jpg'

object_point = np.zeros((1, CHESSBOARD_WIDTH*CHESSBOARD_HEIGHT, 3), np.float32)
object_point[0, :, :2] = np.mgrid[0:CHESSBOARD_WIDTH, 0:CHESSBOARD_HEIGHT].T.reshape(-1, 2)


# images with printed chessboard
filenames = [
    "TestImages/1.jpg",
    "TestImages/2.jpg",
    "TestImages/3.jpg",
    "TestImages/4.jpg",
    "TestImages/5.jpg"
]

image_size = []

object_points = []
image_points = []

for filename in filenames:

    logging.info("processing file " + filename)

    logging.info("reading image...")
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

ref_image = cv2.imread(REF_IMAGE)
(ref_image_shape_w, ref_image_shape_h) = ref_image.shape[:2]

# first method

logging.info(" --- first method")

result, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors \
    = cv2.calibrateCamera(object_points, image_points, (ref_image_shape_w, ref_image_shape_h), None, None)

logging.info("distortion coefficients = " + str(distortion_coefficients))

logging.info("writing test image...")
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients,
                                                       (ref_image_shape_w, ref_image_shape_h), 1,
                                                       (ref_image_shape_w, ref_image_shape_h))

result_image = cv2.undistort(ref_image, camera_matrix, distortion_coefficients, None, new_camera_matrix)

cv2.imwrite('TestImages/out_first.jpg', result_image)


# second method

logging.info(" --- second method")

calibration_flags = 0
calibration_flags |= cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC
calibration_flags |= cv2.fisheye.CALIB_FIX_SKEW

K = np.zeros((3, 3))
D = np.zeros((4, 1))

r_vectors = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(filenames))]
t_vectors = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(filenames))]

cv2.fisheye.calibrate(
    object_points,
    image_points,
    (ref_image_shape_w, ref_image_shape_h),
    K,
    D,
    r_vectors,
    t_vectors,
    calibration_flags,
    (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))

logging.info("distortion coefficients K = " + str(K) + ", D = " + str(D))

logging.info("writing test image...")
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, ref_image.shape[:2], cv2.CV_16SC2)
result_image = cv2.remap(ref_image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

cv2.imwrite('TestImages/out_second.jpg', result_image)

logging.info("finished")

