import maya.cmds as cmds
import numpy as np

"""
What code does:
selected object(curve) and its descendents will move based off movement of parent

Error handling:
- check if there is object selected, and if it has a parent

Functions:
- get_world_space_at_frame(which_obj, frame)
- get_loc_world_space_at_frame(which_loc, frame)
- compute_velocity(position1, position2, time_delta)
- distance_at_frame(position1, position2, frame)
- creat_loc_at_position(transform_values=[0, 0, 0], name="NameThis")

Create locators:
- create locator where the parent is and key it so it matches the parent’s positions 
- for loop to create locators where the selected object is and all of its children and store the initial positions in a list
- initialize the current positions in a list so they can be used and updated in loop
- create locators at current position and key it

Initializing values and setting default values
- get distance and displacement between the parent and object locator so this can be used for constraining later

LOOPING and actually moving the locators:
- update time
- get position of current parent locator
- get the displacement: displacement is the displacement from the original displacement(current frame object to parent) to the new displacement(next frame object to parent)
- acceleration from spring formula(using displacement above) inserted into the Verlet formula to get the next position of object locator
- constrain object locator so its at a fixed distance from parent
- move and key the object locator
- move and key the selected object 
- update positions so current becomes previous and next becomes current
	
"""

#############################################################################################
# ERROR HANDLING and selection ##############################################################
#############################################################################################
selected = cmds.ls(selection=True)
if not selected:
	cmds.warning("No object is selected")

obj = selected[0]
	
parent_obj = cmds.listRelatives(obj, parent=True)
if not parent_obj:
    cmds.error(f"{obj} has no parent.")

parent_obj = parent_obj[0]

obj_list = []
obj_list.append(obj) # Add the selected object itself

# Get all descendents
descendants = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
descendants.reverse() # Dunno why the order is from tip to root, so this is to correct that
# Filter for only the transform descendents and add to list
for node in descendants:
    if cmds.nodeType(node) == "transform":
        obj_list.append(node)

# print(obj_list)

#############################################################################################
# Define frame range because this should only work for a defined frame range
start_frame = 1
end_frame = 50

dt = 1
mass = 1
force= np.array([0, 0, 0]) # 300 was the number from https://editor.p5js.org/gustavocp/sketches/z-6Ap6xla
damping = 0.95


#############################################################################################
# FUNCTIONS #################################################################################
#############################################################################################
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
	world_pos = np.array(cmds.pointPosition(which_obj+".scalePivot", world=True))
	# print(f"World position of {obj} at frame {frame}: {world_pos}")
	return world_pos
# remove "#" to test:
# print(get_world_space_at_frame(parent_obj, 1))


# Separate function for getting world position for locator because translate actualyl works
# and pointPosition doesn't work
def get_loc_world_space_at_frame(which_loc, frame):
	cmds.currentTime(frame, edit=True)
	world_pos = np.array(cmds.xform(which_loc, query=True, worldSpace=True, translation=True))
	# print(f"World position of {obj} at frame {frame}: {world_pos}")
	return world_pos
# remove "#" to test:
# print(get_loc_world_space_at_frame("locator1", 1))


# Calculating velocity based on given values
def compute_velocity(position1, position2, time_delta):
	# Compute velocity (v = Δposition / Δtime).
	return (position2 - position1) / time_delta


# Calculating distance between given values and at given frame
def distance_at_frame(position1, position2, frame):
    cmds.currentTime(frame, edit=True)
    distance = np.linalg.norm(position2 - position1)
    return distance
# remove "#" to test:
# print(distance(np.array([0, 0, 0]), np.array([1, 1, 1]), 1))


# Create loc based on the given location
def creat_loc_at_position(transform_values=[0, 0, 0], name="NameThis"):
	loc = cmds.spaceLocator(name=name)
	cmds.move(transform_values[0], transform_values[1], transform_values[2], loc, relative=True)
	return loc
# remove "#" to test:
# creat_loc_at_position()


#############################################################################################
# CREATING LOCATORS #########################################################################
#############################################################################################

# set parent locator
# create a loc at the at the parent object's position
# and key it by following the parent obj according to the frame range
pos_current_parent_loc = get_world_space_at_frame(parent_obj, start_frame)
parent_loc = creat_loc_at_position(pos_current_parent_loc, "ParentLoc")


for frame in range(start_frame, end_frame + 1):
	pos_current_parent_loc = get_world_space_at_frame(parent_obj, frame)
	cmds.move(pos_current_parent_loc[0], pos_current_parent_loc[1], pos_current_parent_loc[2], parent_loc, worldSpace=True)
	cmds.setKeyframe(parent_loc, attribute="translate", t=frame)


# set default pos for initial pos, and intialize position for current pos
# create a loc at the starting frame of the object's position and key it
pos_default_obj_list = []
pos_current_obj_list = []
obj_loc_list = []
number = 1

for obj in obj_list:
    pos_obj = get_world_space_at_frame(obj, start_frame)
    
    pos_default_obj_list.append(pos_obj)
    pos_current_obj_list.append(pos_obj)
    
    loc_name = (f"ObjLoc_{number}")
    obj_loc = creat_loc_at_position(pos_obj, loc_name)
    cmds.setKeyframe(obj_loc, attribute="translate", t=start_frame)
    obj_loc_list.append(obj_loc)
    
    number += 1

    

#############################################################################################
# INITIALIZING AND SETTING DEFAULT VALUES ###################################################
#############################################################################################

# Get positions of locator at starting frame because the loop below needs these initialized values
pos_current_obj_loc_list = []
pos_previous_obj_loc_list = []
for loc in obj_loc_list:
    current = get_loc_world_space_at_frame(loc, start_frame)
    previous = pos_previous_obj_loc = get_loc_world_space_at_frame(loc, (start_frame - 1))
    
    pos_current_obj_loc_list.append(current)
    pos_previous_obj_loc_list.append(previous)


# Get distance and displacement between the parent locator and child locator
# So later on this distance can be used as constraint
# distance is between each segment
# distance between parent and selected object is stored at 0
# distance between selected object and its first child is stored at 1, so on and so forth
pos_current_parent_loc = get_loc_world_space_at_frame(parent_loc, start_frame)

distance_default_list = []
displacement_default_list = []

distance_default_list.append(distance_at_frame(pos_current_parent_loc, pos_current_obj_loc_list[0], start_frame))
displacement_default_list.append(pos_current_obj_loc_list[0] - pos_current_parent_loc)


n = len(pos_current_obj_loc_list) - 1
for i in range(n):
    distance = distance_at_frame(pos_current_obj_loc_list[i + 1], pos_current_obj_loc_list[i], start_frame)
    displacement = pos_current_obj_loc_list[i + 1] - pos_current_obj_loc_list[i]
    
    distance_default_list.append(distance)
    displacement_default_list.append(displacement)
    print(i)
    i += 1
# print(f"the distance between each segment on {start_frame} is {distance_default_list}")
# print(f"the displacement between each segment on {start_frame} is {displacement_default_list}")

# Temporary override for ease of access DELETE LATER
dt = 1
mass = 1
force= np.array([0, 0, 0])

# move this up LATER
k = 0.1 # Higher the value, stiffer this becomes
damping = 0.8


#############################################################################################
# LOOP N MOVE ###################################################
#############################################################################################

# move the object to where the loc(child) is for the frame range
# this doesn't move still idk
for frame in range(start_frame, end_frame + 1):
    cmds.currentTime(frame)
    
    # current parent locator's position
    pos_current_parent_loc = get_loc_world_space_at_frame(parent_loc, frame)
    # diplacement from parent locator to current object
    displacement_new = pos_current_obj_loc_list[0] - pos_current_parent_loc
    # diplacement of the diplacement from parent locator to current object on current frame to previous frame
    displacement = displacement_new - displacement_default_list[0]
    
    # distance segments between the descendents
    displacement_new_list = []
    displacement_list = []
    
    displacement_new_list.append(displacement_new)
    displacement_list.append(displacement)
    
    for i in range(n):
        disp_new = pos_current_obj_loc_list[i] - pos_current_obj_loc_list[i + 1]
        disp = disp_new - displacement_default_list[i]
        
        displacement_new_list.append(disp_new)
        displacement_list.append(disp)
        i += 1
    # I dunno what this gave me but it's scary
    # print(displacement_list)
    
    # acc = F / m
    # Fs = -kx
    acc = (-k * displacement) / mass
    
    acc_list = []
    acc_list.append(acc)
    
    for i in range(n):
        acc = (-k * displacement_list[i]) / mass
        acc_list.append(acc)
        i += 1
    
    # acceleration override for when code breaks _(: 」∠)_
    # acc = force / mass
    
    # Verlet Integration
    pos_next_obj_loc = pos_current_obj_loc_list[0] + damping * (pos_current_obj_loc_list[0] - pos_previous_obj_loc) + acc * dt * dt
    # print(f"The next position of object is {pos_next_obj_loc}")
    
    pos_next_obj_loc_list = []
    pos_next_obj_loc_list.append(pos_next_obj_loc)
    
    for i in range(n):
        next = pos_current_obj_loc_list[i] + damping * (pos_current_obj_loc_list[i] -  pos_previous_obj_loc_list[i]) + acc_list[i] * dt * dt
        pos_next_obj_loc_list.append(next)
        i += 1
    
    # constraint
    # update the next positon of the object locator with constraints applied
    # constaint: have a set distance between object locator and parent locator
    # Get ratio of distance_default / distance_new
    # This is because you can multiply the ratio with the vector from parent to child locator, to a new vector, that would
    # have default distance between the locators
    # Then you add the new vector to the current position so the distance is always default length
    """
    distance_new = distance_at_frame(pos_current_parent_loc, pos_next_obj_loc, frame)
    # print(f"The distance between the locators is {distance_new}")
    
    distance_ratio =  distance_default / distance_new
    pos_next_obj_loc = (pos_next_obj_loc - pos_current_parent_loc) * distance_ratio + pos_current_parent_loc
    
    pos_next_obj_loc_list = []
    pos_next_obj_loc_list.append(pos_next_obj_loc)
    
    for i in range(n):
        distance_new = distance_at_frame(pos_current_obj_loc_list[i], pos_next_obj_loc_list[i], frame)
        
        distance_ratio = distance_default / distance_new
        pos_next = (pos_next_obj_loc_list[i] - pos_current_obj_loc_list[i])
        
        distance_new_list.append(pos_next)
        
        i += 1
    """
    # move and key the object locator
    cmds.xform(obj_loc_list[0], ws=True, t=pos_next_obj_loc_list[0])
    cmds.setKeyframe(obj_loc_list[0], attribute="translate", t=frame)
    
    
    for i in range(n):
        cmds.xform(obj_loc_list[i + 1], ws=True, t=pos_next_obj_loc)
        cmds.setKeyframe(obj_loc_list[i + 1], attribute="translate", t=frame)
        
        i += 1
    # """
    # move and key the selected object
    # cannot move directly with the values of the world matrix, because of frozen transformation
    # have to take into account of the displacement from world matrix, just have to minus the displacement
    pos_next_obj_list= [] 
    pos_next_obj_list.append(pos_next_obj_loc_list[0] - pos_default_obj_list[0])

    cmds.xform(obj_list[0], ws=True, t=pos_next_obj_list[0])
    cmds.setKeyframe(obj_list[0], attribute="translate", t=frame)
    
    for i in range(n):
        pos_next_obj = pos_next_obj_loc_list[i + 1] - pos_default_obj_list[i + 1]
        
        cmds.xform(obj_list[i], ws=True, t=pos_next_obj)
        cmds.setKeyframe(obj_list[i], attribute="translate", t=frame)
        i += 1
    # """
    # update positions so current becomes previous and next becomes current
    pos_previous_obj_loc_list[0] = pos_current_obj_loc_list[0]
    pos_current_obj_loc_list[0] = pos_next_obj_loc_list[0]
    
    for i in range(n):
        pos_previous_obj_loc_list[i + 1] = pos_current_obj_loc_list[i + 1]
        pos_current_obj_loc_list[i + 1] = pos_next_obj_loc_list[i + 1] 




'''
# need to delete the locs after using them
if parent_loc: 
	cmds.delete(parent_loc)
if obj_loc:
	cmds.delete(obj_loc)
'''
