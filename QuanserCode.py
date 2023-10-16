ip_address = 'localhost' # Enter your IP Address here
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier,ip_address,QLabs,hardware)
potentiometer = potentiometer_interface()
#---------------------------------------------------------------------------------
import random

#this function will rotate the arm in accordance to the potentiometer input
#right = angle
#left: 0 = reset angle, 0 < x <= 0.5 = keep rotating, 0.5 < x < 1 = small box, 1 = big box
def rotate_arm_base(container_id, before):
    container_colour = container_id[0]
    correct_autoclave = False
    current_deg = 0
    before_left = 999
    while(correct_autoclave == False or potentiometer.left() < 0.5):
        #if the potentiometer value has changed, it rotates
        if(potentiometer.right() != before):
            #sets the degree to somewhere between -180 and 180 then -5 to keep it within -175 and 175
            degree = (potentiometer.right()-0.5) * 360
            if (degree > 175):
                degree = 175
            elif (degree < -175):
                degree = -175
            change_deg = degree - current_deg
            current_deg = current_deg + change_deg
            arm.rotate_base(change_deg)
            before = potentiometer.right()
            before_left = potentiometer.left()
        elif(potentiometer.left() == 0 and potentiometer.left() != before_left):  #Error handling
            #sends arm to home and sets the current degree to be 0
            arm.move_arm(0.406,0,0.483)
            current_deg = 0
            #so it doesn't reset continuously
            before_left = potentiometer.left()
        correct_autoclave = arm.check_autoclave(container_colour)
    return potentiometer.right()


def drop_off(container_id):
    #Activates all autoclaves
    arm.activate_autoclaves()
    #Sets the container colour as the first index of the parameter of the function which is a list of form ["colour", "size"]
    container_colour = container_id[0]
    #Sets the container size as the second index of the parameter of the function which is a list of form ["colour", "size"]
    container_size = container_id[1]
    #Defines a control variable called dropped_off as False
    dropped_off = False
    #A while loop that runs the nested code while the control variable is still False
    while (dropped_off == False):
        #An if conditional that runs the nested code if the potentiometer value is between 0.5 and 1.0 AND if the container_size is small
        if 0.5 < potentiometer.left() < 1.0 and container_size == "small":
            #Various motion commands for the arm that brings the held container to the top of the autoclave, drops it inside, and returns the arm home
            arm.rotate_elbow(-15)
            time.sleep(1)
            arm.rotate_shoulder(35)
            time.sleep(1)
            arm.control_gripper(-45)
            time.sleep(1)
            arm.home()
            #Sets the control variable to True, terminating the while loop
            dropped_off = True
        #An elif conditional that runs the nested code if the potentiometer value is 1.0 AND the container size is large
        elif potentiometer.left() == 1.0 and container_size == "large":
            #Various motion commands for the arm that opens autoclave, places the container inside, returns the arm home, and closes the autoclave
            time.sleep(1)
            #Operation that opens the autoclave which is the same colour as the held container
            arm.open_autoclave(container_colour)
            time.sleep(1)
            arm.rotate_elbow(30)
            time.sleep(1)
            arm.rotate_shoulder(20)
            time.sleep(1)
            arm.control_gripper(-45)
            time.sleep(1)
            arm.home()
            #Operation that closes the autoclave which is the same colour as the held container
            arm.open_autoclave(container_colour, False)
            #Sets the control variable to True, terminating the while loop
            dropped_off = True
    #Deactivates all autoclaves
    arm.deactivate_autoclaves()
        
#this function will pick up an object given its position [x,y,z]
def pick_up(pos):
    #moves arm to provided position
    arm.move_arm(pos[0],pos[1],pos[2])
    time.sleep(1)
    #grasps item
    arm.control_gripper(45)
    time.sleep(1)
    #moves arm back to home
    arm.move_arm(0.406,0,0.483)
    time.sleep(1)


def randomize_spawn(cages):  #Uses mapping for the cage perameters
    if not cages:
        return cages, ["", ""]

    cage_num = random.choice(cages)
    cages.remove(cage_num)
    arm.spawn_cage(cage_num)

    cage_id_mapping = {
        1: ["red", "small"],
        2: ["green", "small"],
        3: ["blue", "small"],
        4: ["red", "large"],
        5: ["green", "large"],
        6: ["blue", "large"]
    }

    cage_id = cage_id_mapping.get(cage_num, ["", ""])
    
    return cages, cage_id


def main():
    pos1 = [0.531, 0.056, 0.044]
    cage_nums = [1,2,3,4,5,6]
    cage_id = ["",""] #placeholder
    before = 0.5
    while (len(cage_nums) > 0):
        #Spawns in a random box and removes that from the boxes able to spawn
        cage_nums, cage_id = randomize_spawn(cage_nums)
        #Picks up the object
        pick_up(pos1)
        before = rotate_arm_base(cage_id, before)
        drop_off(cage_id)
main()
#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

