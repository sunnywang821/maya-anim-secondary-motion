import maya.cmds as cmds

cmds.file(new=True, force=True)

def create_vertical_nurbs_hierarchy():
    normal_value = [0, 1, 0]
    # Create the root circle (PARENT)
    parent_circle = cmds.circle(name="PARENT", radius=2, normal=normal_value)[0]
    cmds.move(0, 0, 0, parent_circle)
    
    # Create SELECT_THIS as child of PARENT
    select_this = cmds.circle(name="SELECT_THIS", radius=1.5, normal=normal_value)[0]
    cmds.parent(select_this, parent_circle)
    cmds.move(0, 2, 0, select_this)
    cmds.makeIdentity(select_this, apply=True, t=1, r=1, s=1, n=0)
    
    # Create test01 as child of SELECT_THIS
    test01 = cmds.circle(name="test01", radius=1, normal=normal_value)[0]
    cmds.parent(test01, select_this)
    cmds.move(0, 4, 0, test01)
    cmds.makeIdentity(test01, apply=True, t=1, r=1, s=1, n=0)
    
    # Create test02 as child of test01
    test02 = cmds.circle(name="test02", radius=0.75, normal=normal_value)[0]
    cmds.parent(test02, test01)
    cmds.move(0, 6, 0, test02)
    cmds.makeIdentity(test02, apply=True, t=1, r=1, s=1, n=0)
    
    # Create test03 as child of test02
    test03 = cmds.circle(name="test03", radius=0.5, normal=normal_value)[0]
    cmds.parent(test03, test02)
    cmds.move(0, 8, 0, test03)
    cmds.makeIdentity(test03, apply=True, t=1, r=1, s=1, n=0)
    
    # Center the pivots for all circles
    '''
    for circle in [parent_circle, select_this, test01, test02, test03]:
        cmds.xform(circle, centerPivots=True)
    '''
    # Select the SELECT_THIS circle
    cmds.select(select_this)
    
    print("Successfully created vertical NURBS circle hierarchy: PARENT > SELECT_THIS > test01 > test02 > test03")

# Execute the function
create_vertical_nurbs_hierarchy()
