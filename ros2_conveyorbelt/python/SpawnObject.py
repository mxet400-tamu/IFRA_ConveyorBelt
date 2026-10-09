#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import tempfile
import xacro
from ament_index_python.packages import get_package_share_directory

def main():
    parser = argparse.ArgumentParser(description='Spawn object into Gazebo Sim world.')
    parser.add_argument('--package', type=str, default='', help='Package where URDF/SDF file is located.')
    parser.add_argument('--urdf', type=str, default='', help='URDF of the object to spawn.')
    parser.add_argument('--sdf', type=str, default='', help='SDF of the object to spawn.')
    parser.add_argument('--name', type=str, default='box', help='Name of the object to spawn.')
    parser.add_argument('--world', type=str, default='default', help='Gazebo world name.')
    parser.add_argument('--x', type=float, default=0.0, help='Initial X position [m].')
    parser.add_argument('--y', type=float, default=0.0, help='Initial Y position [m].')
    parser.add_argument('--z', type=float, default=0.0, help='Initial Z position [m].')
    parser.add_argument('--roll', type=float, default=0.0, help='Initial roll [rad].')
    parser.add_argument('--pitch', type=float, default=0.0, help='Initial pitch [rad].')
    parser.add_argument('--yaw', type=float, default=0.0, help='Initial yaw [rad].')

    args, unknown = parser.parse_known_args()

    file_to_spawn = None

    if args.urdf:
        if args.package:
            candidates = [
                os.path.join(get_package_share_directory(args.package), 'urdf', args.urdf),
                os.path.join(get_package_share_directory(args.package), args.urdf),
            ]
            for c in candidates:
                if os.path.exists(c):
                    file_to_spawn = c
                    break
        else:
            file_to_spawn = args.urdf

    elif args.sdf:
        if args.package:
            candidates = [
                os.path.join(get_package_share_directory(args.package), 'sdf', args.sdf),
                os.path.join(get_package_share_directory(args.package), 'models', args.sdf),
                os.path.join(get_package_share_directory(args.package), 'urdf', args.sdf),
                os.path.join(get_package_share_directory(args.package), args.sdf),
            ]
            for c in candidates:
                if os.path.exists(c):
                    file_to_spawn = c
                    break
        else:
            file_to_spawn = args.sdf

    if not file_to_spawn or not os.path.exists(file_to_spawn):
        print(f"[SpawnObject] Error: Model file not found: {file_to_spawn or args.urdf or args.sdf}", file=sys.stderr)
        sys.exit(1)

    print(f"[SpawnObject] Found model file: {file_to_spawn}")

    # If it's a xacro/urdf, process with xacro
    if file_to_spawn.endswith('.xacro') or file_to_spawn.endswith('.urdf'):
        xacro_doc = xacro.process_file(file_to_spawn)
        xml_string = xacro_doc.toxml()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as f:
            f.write(xml_string)
            temp_path = f.name
        spawn_file = temp_path
    else:
        temp_path = None
        spawn_file = file_to_spawn

    cmd = [
        'ros2', 'run', 'ros_gz_sim', 'create',
        '-world', args.world,
        '-file', spawn_file,
        '-name', args.name,
        '-x', str(args.x),
        '-y', str(args.y),
        '-z', str(args.z),
        '-R', str(args.roll),
        '-P', str(args.pitch),
        '-Y', str(args.yaw),
        '-allow_renaming', 'true'
    ]

    print(f"[SpawnObject] Executing command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)

    if result.returncode != 0:
        print(f"[SpawnObject] Spawning exited with code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    else:
        print(f"[SpawnObject] Successfully spawned {args.name} into world {args.world}!")

if __name__ == '__main__':
    main()