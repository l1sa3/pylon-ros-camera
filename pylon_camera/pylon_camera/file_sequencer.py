#! /usr/bin/python3
#pylint: disable=E0611
import os
import cv2

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge

from rclpy.action import ActionServer
from camera_control_msgs.action import GrabSequence
#from camera_control_msgs.msg import GrabSequenceAction, GrabSequenceResult

__author__ = 'nikolas'

server = None

class ImageFileSequencer(Node):

    def __init__(self):
        super().__init__('image_file_sequencer')

        self.bridge = CvBridge()

        # ActionServer erstellen
        self._action_server = ActionServer(
            self,
            GrabSequence,
            '/image_file_sequencer',
            self.execute_callback
        )

    def load_folder(self, folder):
        file_list = os.listdir(folder)
        print(file_list)
        file_map_ = dict()
        for f in file_list:
            try:
                s = int(f.split("_")[-1].split('.')[0])  # ???_number.??? -> number
            except ValueError as e:
                self.get_logger().error(f"Invalid filename {f}: {e}")
                continue
            file_map_[s] = folder+"/"+f
        return file_map_


    def select_images(self, file_map_, req_list):
        # select each image seperately (could lead to double images in result)
        res = GrabSequenceResult()

        res.exposureTimes = []

        res.images = []  #

        for t in sorted(file_map_.keys()):
            self.get_logger().info(f"File key: {t}")
            self.get_logger().info("")
            #print(t)
            #print("")

        for t in req_list:
            #print(t)
            best_exp = min(list(file_map_.keys()), key=lambda x: abs(x-t))
            res.exposureTimes.append(best_exp)
            best_file = file_map_[best_exp]

            # create sensor_msgs/Image from files
            #print(best_file)
            img = cv2.imread(best_file, 0)
            as_sensor_msg = self.bridge.cv2_to_imgmsg(img, "mono8")
            res.images.append(as_sensor_msg)
        res.success = True
        return res


    def grab_sequence_callback(self, goal_handle):
        folder = "/home/nikolas/Documents/sequence_test"
        if not os.path.isdir(folder):
            self.get_logger().error(f"'{folder}' is no directory")
            result = GrabSequence.Result()
            result.success = False
            goal_handle.succeed()
            return result

        file_map = self.load_folder(folder)
        print(file_map)

        result = self.select_images(file_map, goal_handle.request.desiredExposureTimes)

        goal_handle.succeed()
        return result

def main():
    rclpy.init()
    node = ImageFileSequencer()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()