#!/usr/bin/python3

# This script creates a ros node that looks for nodes that publish Image msgs and advertises a to a camera_control_msgs/SetSleeping service. 
# If it does find any, it assumes it is a Pylon camera and sends it either to sleep or wakes it up, depending on argument.
# Will turn on/off all cameras at the same time. Best used as an alias in bashrc:
# alias pylonon='rosrun pylon_camera toggle_camera 0' # turns cameras off
# alias pylonoff='rosrun pylon_camera toggle_camera 1' # turns cameras on
#
# valid arguments: 1 wakes cameras, every other int sleeps cameras
  
import rclpy
import sys
from camera_control_msgs.srv import SetSleeping
from rclpy.utilities import remove_ros_args

def main():
    rclpy.init()
    node = rclpy.create_node('toggle_camera')

    argument = remove_ros_args(sys.argv)[1:]
    try:
        sleep_param = int(argument[0])==0
    except Exception:
        print('Usage: ./toggle_camera [0,1]')
        rclpy.shutdown()
        exit(1)
        
    service_suffix = "/set_sleeping"

    cameras = set()
    topics = node.get_topic_names_and_types()
     for topic_name, topic_types in topics:
       if 'sensor_msgs/msg/Image' in topic_types:
            node_name = topic_name.split('/')[1]
            # Service prüfen
            service_name = f"/{node_name}{service_suffix}"
            client = node.create_client(SetSleeping, service_name)
            if client.wait_for_service(timeout_sec=1.0):
                cameras.add(node_name)

    if not cameras:
        print('No cameras found!')
        rclpy.shutdown()
        exit(0)
        
    for camera in cameras:
        service_name = f"/{camera}{service_suffix}"
        try:
            client = node.create_client(SetSleeping, service_name)
            if not client.wait_for_service(timeout_sec=1.0):
            raise RuntimeError(f"Service {service_name} not available")

            req = SetSleeping.Request()
            req.sleep = sleep_param

            future = client.call_async(req)
            rclpy.spin_until_future_complete(node, future)
            res = future.result()
            print(f"Toggling camera '{camera}'")

        except Exception as e:
            print("Service call failed for %s: %s" % (camera, e))
        
        rclpy.shutdown()

if __name__ == '__main__':
    main()