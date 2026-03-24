#! /usr/bin/python3

import rclpy
from rclpy.node import Node

from std_srvs.srv import SetBool
from sensor_msgs.msg import Image

from cv_bridge import CvBridge
import cv2

from camera_control_msgs.srv import SetExposure
import time

class FlashTestNode(Node):
    def __init__(self):
        super().__init__("flash_test")

        self.bridge = CvBridge()

# todo? check if auto_flash is activated for camera

        self.declare_parameter("camera_name", "/pylon_camera_node")
        self.declare_parameter("exposure", 10000)

        self.img_topic = camera_name + '/image_raw'

# ensure current value (e.g. defaults) are visible on parameter server
        self.exposure = self.get_parameter("exposure").get_parameter_value().integer_value
        self.camera_name = self.get_parameter("camera_name").get_parameter_value().string_value


if self.exposure > 0:
    self.get_logger().info(f"Setting exposure to {self.exposure} ns")
    self.set_exposure_client = self.create_client(SetExposure, f"{self.camera_name}/set_exposure")
    try:
        if not self.set_exposure_client.wait_for_service(timeout_sec=3.0):
                    raise RuntimeError("SetExposure service not available")
        self.set_exposure_client.wait_for_service(3)
    except Exception as e:
        self.get_logger().error("%s, terminating" % str(e))
        exit(1)

        req = SetExposure.Request()
        req.target_exposure = self.exposure
        future = self.set_exposure_client .call_async(req)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(str(future.result()))

# establish service clients for outputs
self.clients = list()
for i in [0, 1]:
    client = self.create_client(SetBool, f"{self.camera_name}/activate_autoflash_output_{i}")
    try:
        if not client.wait_for_service(timeout_sec=3.0):
            raise RuntimeError(f"Autoflash service {i} not available")
    except Exception as e:
        self.get_logger().error("%s, terminating" % str(e))
        exit(1)
    self.clients.append(client)

assert len(clients) == 2


# Create different light situations and capture image (turn both off at end to stop the party)
self.lights = [(1, 1), (0, 1), (1, 0), (0, 0)]

self.img_prefix = "/tmp/flash_test_"

self.get_logger().info(f"Writing images to {img_prefix}_*.png")

for light in self.lights:
    self.get_logger().info(f"Setting lights to {light}")
    for i in [0, 1]:
                req = SetBool.Request()
                req.data = bool(light[i])
                future = self.clients[i].call_async(req)
                rclpy.spin_until_future_complete(self, future)
                self.get_logger().info(str(future.result()))
                time.sleep(0.02)
            time.sleep(0.5)     # needed??

    # continue
    try:
        img = rclpy.task.wait_for_message(self.img_topic, Image, timeout_sec=2)
    except Exception as e:
                self.get_logger().error(f"Did not receive image at {self.img_topic}")
                continue


    cv_img = self.bridge.imgmsg_to_cv2(img)
    self.get_logger().info(str(cv_img.shape))
    filename = img_prefix + "%i_%i.png" % (light[0], light[1])
    cv2.imwrite(filename, cv_img)
    # rospy.sleep(2)

self.get_logger().info("Test ended")

def main():
    rclpy.init()
    node = FlashTest()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()













