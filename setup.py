from setuptools import find_packages, setup
from glob import glob

package_name = "robotics_final_project"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.*")),
        ("lib/" + package_name, [package_name + "/camera.py"]),
        ("lib/" + package_name, [package_name + "/patch_ftp.py"]),
        ("lib/" + package_name, [package_name + "/pathing.py"]),
        ("lib/" + package_name, [package_name + "/icp.py"]),
        ("lib/" + package_name, [package_name + "/mapping.py"]),
        ("lib/" + package_name, [package_name + "/move.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="robotics",
    maintainer_email="mg.marco@hotmail.ch",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "final_node = robotics_final_project.final_node:main",
        ],
    },
)
