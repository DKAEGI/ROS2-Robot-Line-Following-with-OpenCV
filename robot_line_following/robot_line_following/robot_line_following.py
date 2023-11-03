import cv2
import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node 
from cv_bridge import CvBridge 
from sensor_msgs.msg import Image 
from geometry_msgs.msg import Twist

class robot_line_following(Node):
    def __init__(self):
        super().__init__('robot_line_following')
        self.subscriber = self.create_subscription(Image,'/camera/image_raw',self.process_image_data,10)
        self.bridge = CvBridge() # Converting ROS images to opencv data
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 40) # Periodic publisher call
        timer_period = 0.1;self.timer = self.create_timer(timer_period, self.send_cmd_vel)
        self.velocity=Twist()
        self.error=0;
        self.action=""

    ## Publisher callback     
    def send_cmd_vel(self):
        # Constant linear velocity
        self.velocity.linear.x = 0.2
        
        # P-controller for angular velocity
        # Kp is the proportional gain, a tuning parameter
        Kp = 0.1  # You may need to tune this value to get the best performance
        
        # Calculate angular velocity
        self.velocity.angular.z = float(Kp * self.error)
        
        # Limit the angular velocity to some maximum value for safety
        max_angular_velocity = 0.3  
        self.velocity.angular.z = max(min(self.velocity.angular.z, max_angular_velocity), -max_angular_velocity)
        
        # Determine action based on sign of error
        if self.error > 0:
            self.action = "Go Left"
        elif self.error < 0:
            self.action = "Go Right"
        else:
            self.action = "Go Straight"
        
        # Publishing completed velocities
        self.publisher.publish(self.velocity)


    ## Subscriber callback
    def process_image_data(self, data): 
        image = self.bridge.imgmsg_to_cv2(data) # Performing conversion
        # Check if image correct
        if image is None:
            print("Failed to load the image.")
        
        # Convert to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret,binary_image = cv2.threshold(gray_image,127,255,cv2.THRESH_BINARY)

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
            # Get Image center 
            image_center_x = width // 2

            # Calculate the deviation error from the center, get x coordinate of middle_point
            self.error = image_center_x - middle_point[0] 

            # Draw the points and the middle point on the original image for visualization
            cv2.circle(image, left_point, radius=5, color=(0, 255, 0), thickness=-1)
            cv2.circle(image, right_point, radius=5, color=(0, 255, 0), thickness=-1)
            cv2.circle(image, middle_point, radius=5, color=(0, 255, 0), thickness=-1)
            cv2.circle(image, (image_center_x,middle_point[1]), radius=5, color=(0, 0, 255), thickness=-1)

            # Display the result
            cv2.imshow('Edges', edges)
            cv2.imshow('Result', image)
            cv2.waitKey(1)

        else:
            print("No edges were found in the ROI.")
            # Make robot stop


def main(args=None):
  rclpy.init(args=args)
  image_subscriber = robot_line_following()
  rclpy.spin(image_subscriber)
  rclpy.shutdown()
  
if __name__ == '__main__':
  main()