from setuptools import setup
import os

# 获取当前文件所在目录
package_name = 'cloud_monitor_pkg'
# 显式构建资源文件路径
resource_file = os.path.join('resource', package_name)

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    # 关键修改：确保这里引用的文件路径是相对路径，且文件确实存在
    data_files=[
        # 第一个元素是安装目标路径
        # 第二个元素是【源文件列表】，必须包含确切存在的文件
        ('share/ament_index/resource_index/packages', [resource_file]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/system_launch.py']),
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
            'param_service = cloud_monitor_pkg.param_service_node:main',
        ],
    },
)