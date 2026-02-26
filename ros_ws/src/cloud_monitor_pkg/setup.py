from setuptools import setup
import os
from glob import glob

package_name = 'cloud_monitor_pkg'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='Cloud Robot Monitor',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'path_planner = cloud_monitor_pkg.path_planner_node:main',
        ],
    },
)
