#!/usr/bin/env python
from __future__ import print_function

import sys
import rospy
import time

from std_msgs.msg import Float32, Float64


class Characterizator(object):
    def __init__(self, a_max=0.58, a_min=0.00, da=0.005, chamber=1, p_min=0.0):
        p1_topic = 'control/p_chamber1'
        p2_topic = 'control/p_chamber2'
        p3_topic = 'control/p_chamber3'
	#setpoint_topic = '/setpoint'

        # Inizitialize Subscribers & Publishers
        self.p1_pub = rospy.Publisher(p1_topic, Float32, queue_size=1)
        self.p2_pub = rospy.Publisher(p2_topic, Float32, queue_size=1)
        self.p3_pub = rospy.Publisher(p3_topic, Float32, queue_size=1)
	#self.setpoint_pub = rospy.Publisher(setpoint_topic, Float64, queue_size=10)

        


        self.p1 = Float32()
        self.p2 = Float32()
        self.p3 = Float32()
	self.p = p_min
	self.__p_min = p_min
	#self.setpoint = 0

        self.a = a_min
        self.is_ascending = True

        self.__a_max = a_max
        self.__a_min = a_min
        self.__da = da
        self.__chamber = chamber


    def run_characterization(self):
        if self.__chamber == 1:
            self.p1.data = self.p
            self.p2.data = self.__p_min
            self.p3.data = self.__p_min
        elif self.__chamber == 2:
            self.p1.data = self.__p_min
            self.p2.data = self.p
            self.p3.data = self.__p_min
        elif self.__chamber == 3:
            self.p1.data = self.__p_min
            self.p2.data = self.__p_min
            self.p3.data = self.p
        elif self.__chamber == 12:
            self.p1.data = self.p
            self.p2.data = self.p
            self.p3.data = self.__p_min
        elif self.__chamber == 13:
            self.p1.data = self.p
            self.p2.data = self.__p_min
            self.p3.data = self.p
        elif self.__chamber == 23:
            self.p1.data = self.__p_min
            self.p2.data = self.p 
            self.p3.data = self.p
        elif self.__chamber == 123:
            self.p1.data = self.p
            self.p2.data = self.p
            self.p3.data = self.p
        else:
            rospy.signal_shutdown(
                "Select chamber either 1, 2, 3, 12, 23, 13, or 123")

        self.p1_pub.publish(self.p1)
        self.p2_pub.publish(self.p2)
        self.p3_pub.publish(self.p3)
	#self.setpoint_pub.publish(self.setpoint)

	


	if self.a < self.__a_max:
		self.p = (
	-9.277659174670159e-11 * self.a**6
	+ 2.490351106359760e-08 * abs(self.a**5)
	- 2.621782720318396e-06 * self.a**4
	+ 1.382696731540563e-04 * abs(self.a**3)
	- 0.003912423073244 * self.a**2
	+ 0.062468405150407 * abs(self.a)
	+ 0.003724871350122	
	)
	#		self.p = (
	#   -6.182828728433996e-11 * self.a**6
	#   + 1.760100704070713e-08 * abs(self.a**5)
	#   - 1.948712480267485e-06 * self.a**4
	#   + 1.066331280353382e-04 * abs(self.a**3)
	#   - 0.003060165907763 * self.a**2
	#   + 0.047412133923232 * abs(self.a)
	#   + 0.012411980088755
	#)
		self.a = self.a + self.__da
		#self.setpoint = self.a
	elif self.a >= self.__a_max:
		self.p = (
		    -9.277659174670159e-11 * self.a**6
		    + 2.490351106359760e-08 * abs(self.a**5)
		    - 2.621782720318396e-06 * self.a**4
		    + 1.382696731540563e-04 * abs(self.a**3)
		    - 0.003912423073244 * self.a**2
		    + 0.062468405150407 * abs(self.a)
		    + 0.003724871350122)
		#self.p = (
		#	   -6.182828728433996e-11 * self.a**6
		#	   + 1.760100704070713e-08 * abs(self.a**5)
		#	   - 1.948712480267485e-06 * self.a**4
		#	   + 1.066331280353382e-04 * abs(self.a**3)
		#	   - 0.003060165907763 * self.a**2
		#	   + 0.047412133923232 * abs(self.a)
		#	   + 0.012411980088755
		#	)
		self.a = self.__a_max
		#self.setpoint = self.a


    def release_pressure(self):
        p0 = Float32()
        p0.data = 0
        self.p1_pub.publish(p0)
        self.p2_pub.publish(p0)
        self.p3_pub.publish(p0)


def main(args):
    rospy.init_node('characterization_publisher', anonymous=True)

    rate = rospy.Rate(8)  # in Hz

    # Pre-step phase: wait 2 seconds at baseline before applying step
    pre_step_duration = rospy.Duration(2.0)
    pre_step_start_time = rospy.Time.now()
    
    c = Characterizator(a_max=30, a_min=0.0, da=30, chamber=2, p_min=0.0)
    rospy.on_shutdown(c.release_pressure)

    # Baseline publishing (e.g., angle = 0, pressure = 0)
    while not rospy.is_shutdown() and rospy.Time.now() - pre_step_start_time < pre_step_duration:
        #c.setpoint_pub.publish(Float64(0))
        c.release_pressure()
        rate.sleep()
    
    # Now begin normal test
    rospy.loginfo("Starting step input...")
    start_time = rospy.Time.now()
    duration = rospy.Duration(100)

    while not rospy.is_shutdown() and rospy.Time.now() - start_time < duration:
        rospy.loginfo('angle = {0}'.format(c.a))
        c.run_characterization()
        rate.sleep()


    else:
        rospy.signal_shutdown()
    rospy.spin()


if __name__ == '__main__':
    try:
        main(sys.argv)
    except rospy.ROSInterruptException:
        pass
