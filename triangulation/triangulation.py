import sys
from mpmath import *

beacon_1 = [10, 12]
beacon_2 = [14, 28]
beacon_3 = [8, 14]

angle_1 = 40
angle_2 = 120
angle_3 = 90

x1_prime = 0 
x3_prime = 0
y1_prime = 0 
y3_prime = 0
t_12 = 0
t_23 = 0
t_31 = 0
x12_prime = 0
x23_prime = 0
y12_prime = 0
y23_prime = 0
x31_prime = 0 
y31_prime = 0 
k31_prime = 0
d = 0
x_r = 0
y_r = 0

def calc_modified_beacon():
	global x1_prime, x3_prime, y1_prime, y3_prime
	x1_prime = beacon_1[0] - beacon_2[0]
	x3_prime = beacon_3[0] - beacon_2[0]
	y1_prime = beacon_1[1] - beacon_2[1]
	y3_prime = beacon_3[1] - beacon_2[1]
	print("Modified beacons computed")
	
def calc_three_cot():
	global t_12, t_23, t_31
	t_12 = cot(angle_2 - angle_1)
	t_23 = cot(angle_3 - angle_2)
	t_31 = (1 - t_12*t_23)/(t_12 + t_23)
	print("Cotangents computed   ")
	
def calc_modified_center():
	global x12_prime, x23_prime, y12_prime, y23_prime, x31_prime, y31_prime
	x12_prime = x1_prime + t_12*y1_prime
	x23_prime = x3_prime - t_23*y3_prime
	y12_prime = y1_prime - t_12*x1_prime
	y23_prime = y3_prime + t_23*x3_prime
	x31_prime = (x3_prime + x1_prime) + t_31*(y3_prime - y1_prime)
	y31_prime = (y3_prime + y1_prime) - t_31*(x3_prime - x1_prime)
	print("Modified center computed")
	
def calc_k31_prime(): 
	global k31_prime
	k31_prime = x1_prime*x3_prime + y1_prime*y3_prime + t_31*(x1_prime*y3_prime - x3_prime*y1_prime)
	print("k31 computed   ")
	
def calc_d():
	global d
	d = (x12_prime - x23_prime)*(y23_prime - y31_prime) - (y12_prime - y23_prime)*(x23_prime - x31_prime)
	print("D computed   ")
	
def calc_robot_position():
	global x_r, y_r 
	x_r = beacon_2[0] + ((k31_prime*(y12_prime - y23_prime))/d)
	y_r = beacon_2[1] + ((k31_prime*(x23_prime - x12_prime))/d)
	print("Robot position computed")
	
calc_modified_beacon()
calc_three_cot()
calc_modified_center()
calc_k31_prime()
calc_d()
calc_robot_position()

print("(" + repr(x_r) + ", " + repr(y_r) + ")")