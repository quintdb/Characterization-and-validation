This project is based on the pneumatic_endoscope_controller_master package by Yoeko Mak.
Small modifications have been made to adapt it to my use case.

This package makes use of three different launch files and their corresponding source files. Before using each of these, the ros-igtl-bridge Plusserver needs to be launched first.

Characterization.launch launches the characterization script where the input pressure is ramped up and back down with resolution dp.

Step_input.launch and ramp_input.launch make use of 6th degree polynomials derived specifically for the bending in one direction of the origami-based actuator I used. Adjust these polynomials to your needs inside the source files before using the script.

For every launch file, the data can be stored by uncommenting the rosbag lines in the launch files.
