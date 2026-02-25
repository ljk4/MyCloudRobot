from setuptools import setup
import os
from glob import glob

package_name = 'cloud_monitor_pkg'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        # 现在这个相对路径能正确指向 root/resource/cloud_monitor_pkg
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='Cloud Robot Monitor',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator = cloud_monitor_pkg.simulator_node:main',
            # 左边 'param_service' 是你在终端输入的命令
            # 右边 'param_service_node' 是文件名 (不带 .py)
            # ':main' 是函数名
            'param_service = cloud_monitor_pkg.param_service_node:main', 
        ],
    },
)