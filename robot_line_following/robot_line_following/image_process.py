import cv2
import matplotlib.pyplot as plt
import numpy as np

# import os
# print("Current Working Directory:", os.getcwd())

def display_img(img, cmap=None):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111)
    ax.imshow(img, cmap)
    plt.show()

# Load image
path_file = '/home/dkae/Workspaces/ros2_py_ws/src/robot_line_following/robot_line_following/red_line.png'
image = cv2.imread(path_file, 0) # Load image as a grayscale, add 0 to it!!
if image is None:
    print("Failed to load the image. Please check the file path.")
else:
    display_img(image, cmap='gray')

ret,binary_image = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
display_img(binary_image,cmap='gray')

# Cut a region of interest (ROI), here we want the bottom quarter
height, width = binary_image.shape
roi_start = int(height * 0.75)  # Start at 75% of the height to get the bottom quarter
roi = binary_image[roi_start:height, 0:width]

# Detect edges within the ROI
edges = cv2.Canny(roi, 50, 150)

# Find the points that define the left and right edges of the red line
# Assuming that the line is vertical, we look for the first and last non-zero columns
non_zero_columns = np.nonzero(edges)[1]
if non_zero_columns.size:
    left_edge = np.min(non_zero_columns)
    right_edge = np.max(non_zero_columns)

    # Create two points for the left and right edge at the middle Y-coordinate of the ROI
    middle_y = roi_start + (roi.shape[0] // 2)
    left_point = (left_edge, middle_y)
    right_point = (right_edge, middle_y)

    # Calculate the middle point between the left and right edges
    middle_point = ((left_point[0] + right_point[0]) // 2, middle_y)

    # Draw the points and the middle point on the original image for visualization
    cv2.circle(image, left_point, radius=5, color=(0, 255, 0), thickness=-1)
    cv2.circle(image, right_point, radius=5, color=(0, 255, 0), thickness=-1)
    cv2.circle(image, middle_point, radius=5, color=(0, 0, 255), thickness=-1)

    # Display the result
    cv2.imshow('Edges', edges)
    cv2.imshow('Result', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("No edges were found in the ROI.")

