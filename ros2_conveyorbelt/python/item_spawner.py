#!/usr/bin/env python3

import os
import subprocess
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point, Quaternion
from ament_index_python.packages import get_package_share_directory
from gz.msgs.pose_v_pb2 import Pose_V
import gz.transport

#from _________ import __________ # Import the message type you will use for publishing the box color information (e.g., String, Int32, etc.)

class ItemSpawner(Node):

    def __init__(self):
        super().__init__('item_spawner')
        self.pkg = 'conveyorbelt_gazebo'  # Source package of the URDF files
        self.urdf_folder_path = os.path.join(get_package_share_directory(self.pkg), 'urdf')
        self.object_name = 'box' 
        self.ref_frame = 'world'
        
        # Loop through this URDF files list
        self.items = [
            os.path.join(self.urdf_folder_path, "red_box.urdf"),
            os.path.join(self.urdf_folder_path, "blue_box.urdf"),
            os.path.join(self.urdf_folder_path, "green_box.urdf") 
        ]

        self.col = 0    # Create column variable to increment

        # Gazebo Sim state tracking
        self.gz_node = gz.transport.Node()
        self.box_z = None
        self.model_present = False
        self.gz_node.subscribe(Pose_V, "/world/default/dynamic_pose/info", self._on_pose)

################## MODIFY HERE ################################################

        # ADD PUBLISHER INFORMATION HERE using the following template:
        #self.pub = self.create_publisher(message type, 'topic name', 10) # publish object type (e.g., String, Int32, etc.) to a topic (e.g., "box_color") with a queue size of 10

###############################################################################

    def _on_pose(self, msg):
        found = False
        for p in msg.pose:
            if p.name == self.object_name:
                self.box_z = p.position.z
                found = True
                break
        self.model_present = found
        if not found:
            self.box_z = None

    def checkModel(self):
        return self.model_present

    def getPosition(self):
        return self.box_z if self.box_z is not None else 1.0

    def spawn_object(self):
        try:
            urdf_file_path = self.items[self.col]

################## MODIFY HERE ################################################
            
            #1. Create a variable for the box color message and set it to the correct object type (e.g., String, Int32, etc.)
            #   Review the previous publishers and subscribers you made for reference.
            
            #2. The boxes are spawned in order of the list defined in self.items (line 28) starting with self.col = 0 for the red box.
            #   Based on the value of self.col, set the color message variable to the correct color (e.g., "red", "blue", "green") using if-elif statements.
            #   After setting the color message variable for each conditional statement, change the value of self.col to the next box color in the list.
            
            #3. Publish color message using the template:
            #self.pub.publish(color variable you made)

###############################################################################

            self.get_logger().info(f"Spawning {self.object_name}...")
            cmd = [
                'ros2', 'run', 'ros_gz_sim', 'create',
                '-world', 'default',
                '-file', urdf_file_path,
                '-name', self.object_name,
                '-x', '0.0',
                '-y', '-0.5',
                '-z', '0.76',
                '-allow_renaming', 'false'
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                self.get_logger().info(f"{self.object_name} spawned successfully.")
            else:
                self.get_logger().error(f"Failed to spawn {self.object_name}")

        except Exception as e:
            self.get_logger().error(f"An error occurred: {e}")

    def delete_object(self):
        try:
            self.get_logger().info(f"Deleting {self.object_name}...")
            cmd = [
                'ros2', 'run', 'ros_gz_sim', 'delete_entity',
                '--name', self.object_name
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                self.get_logger().info(f"{self.object_name} deleted successfully.")
            else:
                self.get_logger().error(f"Failed to delete {self.object_name}")

        except Exception as e:
            self.get_logger().error(f"An error occurred: {e}")

def main(args=None):
    rclpy.init(args=args)
    
    cs = ItemSpawner()
    print("Item Spawner node started")
    try:
        while rclpy.ok():
            rclpy.spin_once(cs, timeout_sec=0.1)
            if cs.checkModel() == False:
                print("Spawning object")
                cs.spawn_object()
                time.sleep(1.0)
            elif cs.getPosition() < 0.05:
                print("Deleting object")
                cs.delete_object()
                time.sleep(1.0)

    except KeyboardInterrupt:
        pass

    cs.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
