import maya.cmds as cmds
import numpy as np

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
