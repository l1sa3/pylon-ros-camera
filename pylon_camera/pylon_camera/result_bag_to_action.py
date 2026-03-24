#! /usr/bin/python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

import camera_control_msgs.msg
import sensor_msgs.msg
from camera_control_msgs.action import GrabImages
from rclpy.qos import QoSProfile

import time

__author__ = 'klank'


class ImageReplicator(Node):
    def __init__(self):
            super().__init__('result_bag_to_action')

        self._action_name = action_name
        self.get_logger().info("open action server: " + str(action_name))
        
        self._as = ActionServer(
            self,
            camera_control_msgs.action.GrabImages,
            self._action_name,
            self.execute_cb)

        self.get_logger().info("subscribe to : /bag" + str(action_name) + "/result")

        qos = QoSProfile(depth=5)

        self._sub1 = self.create_subscription(
            camera_control_msgs.msg.GrabImagesActionResult,
            "/bag"+str(action_name)+"/result",
            self.image_callback,
            qos)

        self.get_logger().info("subscribe to : /bag/sol_camera/camera_info")

        self._sub2 = self.create_subscription(
            sensor_msgs.msg.CameraInfo,
            "/bag/sol_camera/camera_info",
            self.cam_info_callback,
            qos)
        
        self.get_logger().info("publish: /bag/sol_camera/camera_info")

        self._pub = self.create_publisher(
            sensor_msgs.msg.CameraInfo,
            "/sol_camera/camera_info",
            qos
        )

        self.image_list = []

    def cam_info_callback(self, msg):
        self._pub.publish(msg)

    def image_callback(self, msg):
        self.image_list.append(msg)

    def execute_cb(self, goal_handle):
        while len(self.image_list) == 0:
            time.sleep(0.5)

        msg = self.image_list[0]

        if len(self.image_list) > 1:
            self.image_list = self.image_list[1:]
        else:
            self.image_list = []

        goal_handle.succeed()
        return msg.result


def main():
    rclpy.init()
    node = ImageReplicator("/sol_camera/grab_images_raw")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
