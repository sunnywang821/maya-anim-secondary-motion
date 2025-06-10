import maya.cmds as cmds
import numpy as np

"""
What code does:
selected object(curve) and its descendents will move based off movement of parent
(only works for single chain)

Error handling:
- check if there is object selected, and if it has a parent

Functions:
- getting world space of object at given frames
- getting velocity
- creating loc based off of given location

Base logic:
- Get position of selected object and its parent
- Create locs at the object position and the parent's position 
	The parent loc is going to have keys throughout so it matches parent location
	every frame with the given frame range
	
"""

#############################################################################################
# ERROR HANDLING ############################################################################
#############################################################################################
selected = cmds.ls(selection=True)
if not selected:
	cmds.warning("No object is selected")

obj = selected[0]
	
parent = cmds.listRelatives(obj, parent=True)
if not parent:
    cmds.error(f"{obj} has no parent.")

parent = parent[0]

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


'''
# need to delete the locs after using them
if parent_loc: 
	cmds.delete(parent_loc)
if obj_loc:
	cmds.delete(obj_loc)
'''

# set parent locator
# create a loc at the at the parent object's position
# and key it by following the parent obj according to the frame range
pos_current_parent_loc = get_world_space_at_frame(parent_obj, start_frame)
parent_loc = creat_loc_at_position(pos_current_parent_loc, "Parentloc")

for frame in range(start_frame, end_frame + 1):
	pos_current_parent_loc = get_world_space_at_frame(parent_obj, frame)
	cmds.move(pos_current_parent_loc[0], pos_current_parent_loc[1], pos_current_parent_loc[2], parent_loc, worldSpace=True)
	cmds.setKeyframe(parent_loc, attribute="translate", t=frame)


# create a loc at the starting frame of the object's position and key it
pos_current_obj = get_world_space_at_frame(obj, start_frame)
obj_loc = creat_loc_at_position(pos_current_obj, "ObjLoc")
cmds.setKeyframe(obj_loc, attribute="translate", t=start_frame)

# Get position of locator at starting frame because the loop below needs these initialized values
pos_current_obj_loc = get_loc_world_space_at_frame(obj_loc, start_frame)
pos_previous_obj_loc = get_loc_world_space_at_frame(obj_loc, (start_frame - 1))
# print(pos_current_obj_loc)

# Get distance and displacement between the parent locator and child locator
# So later on this distance can be used as constraint
pos_current_parent_loc = get_loc_world_space_at_frame(parent_loc, start_frame)
distance_default = distance_at_frame(pos_current_parent_loc, pos_current_obj_loc, start_frame)
displacement_default = pos_current_obj_loc - pos_current_parent_loc
# print(distance)


# Temporary override for ease of access DELETE LATER
dt = 1
mass = 1
force= np.array([0, 0, 0])

# move this up LATER
k = 0.1 # Higher the value, stiffer this becomes
damping = 0.8
#############################################################################################
# move the object to where the loc(child) is for the frame range
# this doesn't move still idk
for frame in range(start_frame, end_frame + 1):
    cmds.currentTime(frame)
    
    # current parent locator's position
    pos_current_parent_loc = get_loc_world_space_at_frame(parent_loc, frame)
    # distance between current parent locator's position and current object locator's position
    displacement_new = pos_current_obj_loc - pos_current_parent_loc
    displacement = displacement_new - displacement_default
    
    # acc = F / m
    # Fs = -kx
    acc = (-k * displacement) / mass
    # acceleration override for when code breaks _(: 」∠)_
    # acc = force / mass
    
    # Verlet Integration
    pos_next_obj_loc = pos_current_obj_loc + damping * (pos_current_obj_loc - pos_previous_obj_loc) + acc * dt * dt
    # print(f"The next position of object is {pos_next_obj_loc}")
    
    # constraint
    # update the next positon of the object locator with constraints applied
    # constaint: have a set distance between object locator and parent locator
    # Get ratio of distance_default / distance_new
    # This is because you can multiply the ratio with the vector from parent to child locator, to a new vector, that would
    # have default distance between the locators
    # Then you add the new vector to the current position so the distance is always default length
    # """
    distance_new = distance_at_frame(pos_current_parent_loc, pos_next_obj_loc, frame)
    # print(f"The distance between the locators is {distance_new}")
    
    distance_ratio =  distance_default / distance_new
    pos_next_obj_loc = (pos_next_obj_loc - pos_current_parent_loc) * distance_ratio + pos_current_parent_loc
    
    # """
    # move and key the object locator
    cmds.xform(obj_loc, ws=True, t=pos_next_obj_loc)
    cmds.setKeyframe(obj_loc, attribute="translate", t=frame)
    
    # update positions so current becomes previous and next becomes current
    pos_previous_obj_loc = pos_current_obj_loc
    pos_current_obj_loc = pos_next_obj_loc 







"""
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

"""
