#!/usr/bin/env python
from __future__ import print_function

import sys
import rospy

from std_msgs.msg import Float32


class Characterizator(object):
    def __init__(self, p_max=0.58, p_min=0.00, dp=0.005, chamber=1):
        p1_topic = 'control/p_chamber1'
        p2_topic = 'control/p_chamber2'
        p3_topic = 'control/p_chamber3'

        # Inizitialize Subscribers & Publishers
        self.p1_pub = rospy.Publisher(p1_topic, Float32, queue_size=1)
        self.p2_pub = rospy.Publisher(p2_topic, Float32, queue_size=1)
        self.p3_pub = rospy.Publisher(p3_topic, Float32, queue_size=1)

        self.p1 = Float32()
        self.p2 = Float32()
        self.p3 = Float32()

        self.p = p_min
        self.is_ascending = True

        self.__p_max = p_max
        self.__p_min = p_min
        self.__dp = dp
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


        if self.is_ascending:
            if self.p < self.__p_max:
                self.p = self.p + self.__dp
            elif self.p >= self.__p_max:
                self.is_ascending = False
            else:
                rospy.signal_shutdown('Out of scope?')
        elif self.is_ascending is False:
            if self.p > self.__p_min:
                self.p = self.p - self.__dp
            elif self.p <= self.__p_min:
                self.is_ascending = True
            else:
                rospy.signal_shutdown('Out of scope?')

    def release_pressure(self):
        p0 = Float32()
        p0.data = 0
        self.p1_pub.publish(p0)
        self.p2_pub.publish(p0)
        self.p3_pub.publish(p0)


def main(args):
    rospy.init_node('characterization_publisher', anonymous=True)
    rate = rospy.Rate(8)  # in Hz
    # Define max., min. pressure, pressure step, and chamber selection
    c = Characterizator(p_max=0.2, p_min=0.0, dp=0.1, chamber=2)
    rospy.on_shutdown(c.release_pressure)

    while not rospy.is_shutdown():
        rospy.loginfo('p = {0}'.format(c.p))
        c.run_characterization()
        rate.sleep()
    rospy.spin()


if __name__ == '__main__':
    try:
        main(sys.argv)
    except rospy.ROSInterruptException:
        pass
