# AUTHOR - JAYNIL SHETH

import pybullet as p
import pybullet_data
import numpy as np
import time
import math

p.connect(p.GUI)  
p.setAdditionalSearchPath(pybullet_data.getDataPath())
plane = p.loadURDF("plane.urdf")
p.setGravity(0, 0, -10)

huskypos = [0, 0, 0]

# Load URDFs
husky = p.loadURDF("husky/husky.urdf", huskypos[0], huskypos[1], huskypos[2])

target= p.loadURDF("block0.urdf",5 , 5, 5)

for i in range(500):
    p.stepSimulation()

time.sleep(2)
maxForce = 50 #Newton.m
#camera should be facing in the direction of the car

def get_positions_and_headings():
    rear_bump= p.getLinkState(husky,9)
    front_bump= p.getLinkState(husky,8)
    target_pos= p.getBasePositionAndOrientation(target)
    v1= front_bump[0][0]-rear_bump[0][0]
    v2= front_bump[0][1]-rear_bump[0][1]
    v3= front_bump[0][2]-rear_bump[0][2]
    frontVec= np.array(list((v1, v2, v3)))
    
    return (frontVec, target_pos, rear_bump)

def pid(bot_heading_vector, target_pos, vehicle_pos):
    """
    Inputs:
    bot_heading_vector - front vector of bot
    target_pos - position of the target box
    vehicle_pos - position of the vehicle

    Returns:
    linear - Linear speed of the bot
    angular - Angular speed of the bot

    Note: speed of right side wheels will be (linear + angular) and speed of left side wheels will be (linear - angular), you can refer to the turn function for more details
    """
    # code here and edit the linear and angular velocity
    # P controller :-

    x_bot = vehicle_pos[0][0]
    y_bot = vehicle_pos[0][1]

    x_target = target_pos[0][0]
    y_target = target_pos[0][1]

    x_hv = bot_heading_vector[0]        # x-comp of heading vector
    y_hv = bot_heading_vector[1]        # y-comp of heading vector
    z_hv = bot_heading_vector[2]        # z-comp of heading vector

    x_uhv = (x_hv)/((x_hv)**2 + (y_hv)**2 + (z_hv)**2)**(0.5)      # x-comp of unit heading vector
    y_uhv = (y_hv)/((x_hv)**2 + (y_hv)**2 + (z_hv)**2)**(0.5)      # y-comp of unit heading vector

    d = ((x_target - x_bot)**2 + (y_target - y_bot)**2)**(0.5)      # distance between bot and target
    
    x_upv = (x_target - x_bot)/d         # x-comp of unit path vector (vector joining bot to target)
    y_upv = (y_target - y_bot)/d         # y-comp of unit path vector (vector joining bot to target)

    linear = 3.5 * (d)        # proportionality constant * distance between bot and target : error in linear displacement at any instant = (d - 0) = d

    angular = 20 * (math.asin((x_upv * y_uhv) - (x_uhv * y_upv)))        # proportionality constant * angle(theta) between unit heading vector and unit path vector : error in angular displacement at any instant = (theta - 0) = theta

    if (d <  2):        # Because we are using target block's centroid as our target location, so it will not completely stop before touching the block
        linear = 0
        angular = 0

    if (linear > 15):       # So that the car stays in the same plane
        linear = 15
    
    return linear, angular

def turn(linear, angular):
    targetVel_R = linear + angular
    targetVel_L = linear - angular
    for joint in range(1,3):
        p.setJointMotorControl2(husky,2* joint, p.VELOCITY_CONTROL, targetVelocity =targetVel_R,force = maxForce)
    for joint in range(1,3):
        p.setJointMotorControl2(husky,2* joint+1, p.VELOCITY_CONTROL,targetVelocity =targetVel_L,force = maxForce)
    p.stepSimulation()

while (1):
    	
    bot_heading_vector, target_pos, vehicle_pos = get_positions_and_headings()
    linear, angular = pid(bot_heading_vector, target_pos, vehicle_pos)
    turn(linear, angular)
    
    time.sleep(0.02)
            
p.disconnect()
