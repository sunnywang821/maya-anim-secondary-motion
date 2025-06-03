 import maya.cmds as cmds
import numpy as np

"""
What code does:
selected object(curve) will move based off movement of parent

Error handling:
- check if there is object selected, and if it has a parent

Functions:
- getting world space of object at given frames
- getting velocity
- creating locator based off of given location

Base logic:
- Get position of selected object and its parent
- Create locators at the object position and the parent's position 
	The parent locator is going to have keys throughout so it matches parent location
	every frame with the given frame range
	
"""

#############################################################################################
# ERROR HANDLING ############################################################################
#############################################################################################
selected = cmds.ls(selection=True)
if not selected:
    cmds.warning("No object is selected")

obj = selected[0]
	
parent_obj = cmds.listRelatives(obj, parent=True)
if not parent_obj:
    cmds.error(f"{obj} has no parent.")

parent_obj = parent_obj[0]

#############################################################################################
# Define frame range because this should only work for a defined frame range
start_frame = 1
end_frame = 10

dt = 1
mass = 1
force_x = 0
force_y = 10 # 300 was the number from https://editor.p5js.org/gustavocp/sketches/z-6Ap6xla


# Getting worldspace values of a selected object at a certain frame
""" 
*NOTES:
- "scalePivot" is used because "translate" doesn't get the right value for some reason 
if transformation is frozen 
- "cmds.currentTime" is used to go to the current time because code doesn't work otherwise 
¯\_(ツ)_/¯
"""
def get_world_space_at_frame(which_obj, frame):
	cmds.currentTime(frame, edit=True)
	world_pos = np.array(cmds.pointPosition(which_obj+".scalePivot", world=1))
	# print(f"World position of {obj} at frame {frame}: {world_pos}")
	return world_pos
# remove "#" to test:
# print(get_world_space_at_frame(parent_obj, 1))


# Calculating velocity based on given values
def compute_velocity(position1, position2, time_delta):
    # Compute velocity (v = Δposition / Δtime).
    return (position2 - position1) / time_delta


# Create locator based on the given location
def creat_locator_at_position(transform_values=[0, 0, 0], name="NameThis"):
    locator = cmds.spaceLocator(name=name)
    cmds.move(transform_values[0], transform_values[1], transform_values[2], locator, relative=True)
    return locator
# remove "#" to test:
# creat_locator_at_position()

'''
# need to delete the locators after using them
if parent_locator: 
    cmds.delete(parent_locator)
if obj_locator:
    cmds.delete(obj_locator)
'''

# create a locator at the at the parent object's position
# and key it by following the parent obj according to the frame range
pos1_parent = get_world_space_at_frame(parent_obj, frame)
parent_locator = creat_locator_at_position(pos1_parent, "ParentLocator")

for frame in range(start_frame, end_frame + 1):
    pos1_parent = get_world_space_at_frame(parent_obj, frame)
    cmds.move(pos1_parent[0], pos1_parent[1], pos1_parent[2], parent_locator, worldSpace=True)
    cmds.setKeyframe(parent_locator, attribute="translate", t=frame)


# create a locator at the starting frame of the object's position and key it
pos1_obj = get_world_space_at_frame(obj, start_frame)
obj_locator = creat_locator_at_position(pos1_obj, "ObjLocator")
cmds.setKeyframe(obj_locator, attribute="translate", t=start_frame)


# move the object to where the locator(child) is for the frame range
for frame in range(start_frame, end_frame + 1):
    pos_obj_locator_list_tuple = cmds.getAttr(f"{obj_locator[0]}.translate", time=frame)
    pos_obj_locator = list(pos_obj_locator_list_tuple[0])
    # print(pos_obj_locator[2])
    cmds.xform(pos_obj_locator[0], pos_obj_locator[1], pos_obj_locator[2], obj, worldSpace=True)
    cmds.setKeyframe(obj, attribute="translate", t=frame)
    








for frame in range(start_frame, end_frame + 1):
    pos1_parent = get_world_space_at_frame(parent_obj, frame)
    pos2_parent = get_world_space_at_frame(parent_obj, frame + 1)
    velocity = compute_velocity(pos1_parent, pos2_parent, dt)
    # print(f"the position of the parent object at frame {frame} is {pos1_parent}, at {(frame + 1)} is {pos2_parent}")
    # print(f"the velocity of the parent object at frame {frame} is {velocity}")
    new_velocity = velocity * -0.5
    
    
    # cmds.xform(obj, translation=new_velocity, worldSpace=True)
    cmds.move(new_velocity[0], new_velocity[1], new_velocity[2], obj, relative=True)
    cmds.setKeyframe(obj, attribute="translate", t=frame)
    
