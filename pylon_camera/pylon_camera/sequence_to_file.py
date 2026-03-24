#! /usr/bin/python3

# __author__ = 'nikolas'

import os
import cv2

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge


from rclpy.action import ActionClient
from camera_control_msgs.action import GrabSequence


class SequenceToFile(Node):
    def __init__(self):
            super().__init__("image_sequence_to_file")
            self.client = ActionClient(self, GrabSequence, '/image_file_sequencer')


    def send_goal_blocking(self, goal):
      
        send_goal_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            raise RuntimeError("Goal rejected")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        return result_future.result().result
    

    def get_images(self, goal_folder):

        if not os.path.isdir(goal_folder):
            self.get_logger().error("'"+goal_folder+"' is no directory")
            return

        self.client.wait_for_server()
        self.get_logger().info("Got server")

        goal = GrabSequence.Goal()
        goal.desired_exposure_times = [40, 700, 7000]  # todo: select exposures as soon as supported

        self.get_logger().info("Waiting for result")
        result = self.send_goal_blocking(goal)

        if not result.success:
            self.get_logger().error("Action returned but failed")
            return

        bridge = CvBridge()

        for i in range(len(result.exposureTimes)):
            file_name = goal_folder+'/'+"img_"+str(int(result.exposureTimes[i]))+".png"
            print(file_name)
            mat = bridge.imgmsg_to_cv2(result.images[i], "mono8")
            cv2.imwrite(file_name, mat)

        self.get_logger().info("Wrote " + str(len(result.exposureTimes)) + " images to " + goal_folder)


def main()
    rclpy.init()
    node = SequenceToFile
    node.get_images("/tmp")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
