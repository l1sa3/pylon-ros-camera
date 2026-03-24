#!/usr/bin/python3

import rclpy
from rclpy.node import Node

from rclpy.action import ActionServer, ActionClient
from camera_control_msgs.msg import GrabImages

from sensor_msgs.msg import Image
from std_msgs.msg import Empty

class TriggeredImageTopic(Node):
    """
    This nodes provides allows to transform a trigger topic to an image topic using GrabImageAction.
    Whenever a signal is published on ~trigger a sensor_msg.msg.Image is published on the output topic.
    
    The interface is restricted to a rosparam for exposure with a low gain
    """
    def __init__(self):
            super().__init__("triggered_img_topic")

        self.declare_parameter('camera_name', '')
        self.declare_parameter('triggered_image_topic', 'triggered_images')
        self.declare_parameter('exposure_time', 20000.0)

        self.camera_name = self.get_parameter('camera_name').value
        self.output_topic_name = self.get_parameter('triggered_image_topic').value
        
        if not self.camera_name:
            self.get_logger().warn("No camera name given! Assuming 'pylon_camera_node' as"
                          " camera name")
            self.camera_name = '/pylon_camera_node'
        else:
            self.get_logger().info('Camera name is: ' + self.camera_name)

        self.pub = self.create_publisher(Image, self.output_topic_name, 10)
        self.subscriber = self.create_subscription(Empty, 'trigger', self.trigger_cb, 10)

        self._grab_imgs_rect_ac = ActionClient(self, GrabImages, f'{self.camera_name}/grab_images_rect')

        self.get_logger().info(f'Waiting for action server at {self.camera_name}/grab_images_rect...')
        if self._grab_imgs_rect_ac.wait_for_server(timeout_sec=10.0):
            self.get_logger().info(f'Found action server at {self.camera_name}/grab_images_rect')
        else:
            self.get_logger().error(f'Could not connect to action server at {self.camera_name}/grab_images_rect')
        
        


    def trigger_cb(self, msg):
        
        goal_msg = GrabImages.Goal()
        goal_msg.exposure_given = True
        goal_msg.exposure_times = [self.get_parameter('exposure_time').value]
        goal_msg.gain_given = True
        goal_msg.gain_values = [0.2]
        goal_msg.gain_auto = False

        send_goal_future = self._grab_imgs_rect_ac.send_goal_async(goal_msg)

        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return

        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future, timeout_sec=10.0)

        if not get_result_future.done():
            self.get_logger().error("Timeout waiting for result")
            return

        result = get_result_future.result().result
        self.get_logger().info("Got image")

        if len(result.images) > 0:
            self.get_logger().info('publish image')
            self.pub.publish(result.images[0])
        else:
            self.get_logger().warn('No images received')

        def spin(self):
        # spin() simply keeps python from exiting until this node is stopped
        rclpy.spin(self)

def main()
    rclpy.init()
    node = TriggeredImageTopic()
    node.spin()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
