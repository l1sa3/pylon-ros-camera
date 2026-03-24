#!/usr/bin/env python3
from setuptools import setup
package_name = 'pylon_camera'

setup(
    name=package_name,
    version='0.17.1',
    packages=['pylon_camera'],
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Marcel Debout',
    maintainer_email='pablo.quilez@dragandbot.com',
    description='Proprietary Package for Basler Cameras using the the Pylon API. - Supports DART, USB3 and GigE cameras. - Setting Gain, Gamma, Exposure, Binning and Brightness using Services.',
    license='BSD',

    data_files=[
    ('share/ament_index/resource_index/packages', ['resource/pylon_camera']),
    ('share/pylon_camera', ['package.xml']),
    ],
    entry_points={
        'console_scripts': [
            'pylon_camera_node = pylon_camera.file_sequencer:main',
            'pylon_camera_node = pylon_camera.grab_and_save_image_action_server:main',
            'pylon_camera_node = pylon_camera.result_bag_to_action:main',
            'pylon_camera_node = pylon_camera.sequence_to_file:main',
            'pylon_camera_node = pylon_camera.toggle_camera:main',
            'pylon_camera_node = pylon_camera.triggered_image_topic:main',
        ],
    },
)