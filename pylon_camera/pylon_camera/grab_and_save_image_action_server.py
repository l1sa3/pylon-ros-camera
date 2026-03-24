#!/usr/bin/python3

import rclpy
from rclpy.node import Node
import cv2

from rclpy.action import ActionClient, ActionServer

from cv_bridge import CvBridge, CvBridgeError
from camera_control_msgs.action import GrabImages, GrabAndSaveImage


class GrabAndSaveImageActionServers(Node):
    """
    This nodes provides action server that extend the 'grab_images_raw' and
    'grab_images_rect' action servers from the pylon_camera_node.
    The new action servers are named 'grab_and_save_imgage_raw' and
    'grab_and_save_imgage_rect'. They have basically the same action goal as
    the 'GrabImagesAction' in case of grabbing only one image, but they extend
    above goal with a sting describing the full storage path and name of the
    image to be saved
    """

    def __init__(self):
        super().__init__('grab_and_save_image_action_servers')
        self.declare_parameter('camera_name', '')
        camera_name = self.get_parameter('camera_name').value
        if not camera_name:
            self.get_logger().warn(
                        "No camera name given! Assuming 'pylon_camera_node' as"
                        " camera name")
            camera_name = '/pylon_camera_node'
        else:
            self.get_logger().info('Camera name is: ' + camera_name)

        self._grab_imgs_raw_ac = ActionClient(
            self, 
            GrabImages, 
            '{}/grab_images_raw'.format(camera_name))

        self._grab_imgs_rect_ac = ActionClient(
            self,
            GrabImages,
            '{}/grab_images_rect'.format(camera_name))

        self._grab_and_save_img_raw_as = ActionServer(
            self,
            GrabAndSaveImage,
            'grab_and_save_image_raw',
            execute_cb=self.grab_and_save_img_raw_execute_cb
        )
        self.get_logger().info(f"Grab and save raw ActionServer started for {camera_name}")

        self._grab_and_save_img_rect_as = ActionServer(
            self,
            GrabAndSaveImage,
            'grab_and_save_image_rect',
            execute_cb=self.grab_and_save_img_rect_execute_cb
        )
        self.get_logger().info(f"Grab and save rect ActionServer started for {camera_name}")


    def convert_goals(self, grab_and_save_img_goal, grab_imgs_goal):
        grab_imgs_goal.exposure_given = grab_and_save_img_goal.exposure_given
        if grab_and_save_img_goal.exposure_time:
            grab_imgs_goal.exposure_times.append(grab_and_save_img_goal.exposure_time)
        grab_imgs_goal.gain_given = grab_and_save_img_goal.gain_given
        if grab_and_save_img_goal.gain_value:
            grab_imgs_goal.gain_values.append(grab_and_save_img_goal.gain_value)
        grab_imgs_goal.gamma_given = grab_and_save_img_goal.gamma_given
        if grab_and_save_img_goal.gamma_value:
            grab_imgs_goal.gamma_values.append(grab_and_save_img_goal.gamma_value)
        grab_imgs_goal.brightness_given = grab_and_save_img_goal.brightness_given
        if grab_and_save_img_goal.brightness_value:
            grab_imgs_goal.brightness_values.append(grab_and_save_img_goal.brightness_value)
        grab_imgs_goal.exposure_auto = grab_and_save_img_goal.exposure_auto
        grab_imgs_goal.gain_auto = grab_and_save_img_goal.gain_auto

    async def grab_and_save_img_raw_execute_cb(self, goal_handle):
        return await self.handle_goal(goal_handle, self._grab_imgs_raw_ac)

    async def grab_and_save_img_rect_execute_cb(self, goal_handle):
        return await self.handle_goal(goal_handle, self._grab_imgs_rect_ac)

    async def grab_and_save_img_execute_cb(self, goal_handle, action_client):
        grab_imgs_goal = GrabImages.Goal()
        self.convert_goals(goal_handle.request, grab_imgs_goal)

        await action_client.wait_for_server()
        future = action_client.send_goal_async(grab_imgs_goal)
        goal = await future
        result_future = goal.get_result_async()
        result = await result_future

        grab_and_save_result = GrabAndSaveImage.Result()

        if result is not None and result.result.success:
            filename = goal_handle.request.img_storage_path_and_name
            try:
                cv_img = CvBridge().imgmsg_to_cv2(result.result.images[0],
                                                  desired_encoding='passthrough')
            except CvBridgeError as exception:
                self.get_logger().error('Error converting img_msg_to_cv_img: ' +
                             str(exception))
                grab_and_save_img_result.success = False
                goal_handle.abort()
                return grab_and_save_result

            self.get_logger().info('Writing image to ' + filename)
            cv2.imwrite(filename, cv_img)
            grab_and_save_img_result.success = True
            goal_handle.succeed
        else:
            grab_and_save_img_result.success = False
            goal_handle.abort()

        return grab_and_save_result


def main():
    rclpy.init()

    node = GrabAndSaveImageActionServers()
    rclpy.spin(node)    # spin() simply keeps python from exiting until this node is stopped

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
