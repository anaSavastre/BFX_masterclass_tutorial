from maya import cmds as mc
import json
from . import static

def add_control(guide, name, parent, shapeName, deleteGuide=True):

    # Storing guide info
    guide_world_matrix = mc.xform(guide, q=1, ws=1, matrix=1)
    if deleteGuide:
        mc.delete(guide)

    # Creating our control hierarchy 
    # GRP>OFS>CTL>JNT
    grp = mc.createNode('transform', name=name+'_GRP')

    ofs = mc.createNode('transform', name=name+'_OFS')
    mc.parent(ofs, grp)

    ctl = build_control_from_json(shapeName, name, ofs) 

    jnt = mc.createNode('joint', name=name+'_JNT')
    mc.parent(jnt, ctl)
    mc.setAttr(jnt+'.visibility', 0)

    # Setting the position of our control
    mc.xform(grp, ws=1, matrix=guide_world_matrix)
    mc.parent(grp, parent)


    class ctlStruct:
        def __init__(self):
            self.grp=grp
            self.ofs=ofs
            self.trn=ctl
            self.jnt=jnt

    return ctlStruct()

def build_control_from_json(shapeName, name, parent):
    def create_new_curve_shape(curveNode, cvGuideList, degree, name="curveShape"):
        curve = mc.curve(name=name+'_Shape' , point = cvGuideList, ws=True, degree=degree)
        shape = mc.listRelatives(curve)[0]
        mc.parent(shape, curveNode, shape=True, r=True)
        mc.delete(curve)
        return shape
    # Read the JSON file
    with open(static.controlShapeFile, 'r') as f:
        data = json.load(f)
    
    # Check if the key exists in the JSON data
    if shapeName not in data:
        mc.error(f'Key "{shapeName}" not found in the JSON file.')
        return
    
    # Extract the points from the JSON file
    shapes = data[shapeName]
    
    if not shapes:
        mc.error(f'No points available for key "{shapeName}".')
        return
    
    # Creating our curve transform
    ctl = mc.createNode('transform', name=name+'_CTL')
    mc.parent(ctl, parent)

    for shape in shapes:
        create_new_curve_shape(ctl, shape['points'], shape['degree'], name=name+'Shape')

    return ctl

def build_masterWalk_control(shapeName, name, parent):
    def create_new_curve_shape(curveNode, cvGuideList, degree, name="curveShape"):
        curve = mc.curve(name=name , point = cvGuideList, ws=True, degree=degree)
        shape = mc.listRelatives(curve)[0]
        mc.parent(shape, curveNode, shape=True, r=True)
        mc.delete(curve)
        return shape
    # Read the JSON file
    with open(static.controlShapeFile, 'r') as f:
        data = json.load(f)
    
    # Check if the key exists in the JSON data
    if shapeName not in data:
        mc.error(f'Key "{shapeName}" not found in the JSON file.')
        return
    
    # Extract the points from the JSON file
    shapes = data[shapeName]
    
    if not shapes:
        mc.error(f'No points available for key "{shapeName}".')
        return
    
    # Creating our curve transform
    ctl = mc.createNode('transform', name=name)
    mc.parent(ctl, parent)

    for i, shape in enumerate(shapes):
        create_new_curve_shape(ctl, shape['points'], shape['degree'], name=name+'Shape')
        if i==0:
            continue
        for j in range(3):
            shapeCrv = create_new_curve_shape(ctl, shape['points'], shape['degree'], name=name+'Shape')
            # For the other arrows we want to reposition them
            mc.xform(shapeCrv+".cv[*]", ro=[0, 90*(j+1), 0], ws=True)

    return ctl

def scale_control(name, scaleAmount):
    # Calculate Point Center
    mc.select(name)
    center = mc.objectCenter(name)
    for shape in mc.listRelatives(name, type='nurbsCurve'):
        # Scale
        mc.xform(shape+"*.cv[*]", s=[scaleAmount, scaleAmount, scaleAmount], piv=center, r=True)