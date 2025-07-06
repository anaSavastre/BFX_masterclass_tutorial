from maya import cmds as mc
import json
from BFX_masterclass import static


class ctlStruct:
    def __init__(self, grp, ofs, trn, jnt):
        self.grp=grp
        self.ofs=ofs
        self.trn=trn
        self.jnt=jnt

    def scale_shape(self, scaleAmount, relative=True):
        '''
        Applying scaleAmount to the controls shapes. 
        
        Returns
        -------
        None
        '''
        center = mc.objectCenter(self.trn)

        for shape in mc.listRelatives(self.trn, type='nurbsCurve'):
            # Scale
            mc.xform(shape+"*.cv[*]", s=[scaleAmount, scaleAmount, scaleAmount], piv=center, r=relative)

def add(guide, name, parent, shapeName, deleteGuide=True):
    '''
    This function builds a control structure, from a given guide. The control struct contain a hierarchy of transforms:
        Parent Grout > Offset Transform > Control Transform > Joint

    Parameters
    ----------
    guide       : str : name of the guide used as pivot point for the control
    name        : str : name of the control
    parent      : str : name of control parent
    shapeName   : str : the shape type we will be loading from the      controlShapes.json file
    deleteGuide : bool : choose to delete the provided guide. There might be instance where we want to use the same guide for multiple controls

    Returns
    -------

    Struct
        grp - control parent
        ofs - offset parent
        trn - the control
        jnt - the joint parented under the control

    The struct will contain a 
    '''
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

    return ctlStruct(grp, ofs, ctl, jnt)

def build_control_from_json(shapeName, name, parent):
    '''
    This function is used to load the saved control shape from the library. It is not the best way to construct a control library, but it was a quick solution for this demo. I am only using a few shapes so no need to create a big library

    Parameters
    ----------
    shapeName   : str : the key we will be searching for in the shape library
    name        : str : name to assign to the shape nodes
    parent      : str : control under which to parent he shape

    Returns
    -------
    Str : the name of the control transform, which will contain the shape nodes
    '''
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
    
    # Extract the points from the JSON file
    shapes = data[shapeName]
    
    if not shapes:
        mc.error(f'No points available for key "{shapeName}".')
    
    # Creating our curve transform
    ctl = mc.createNode('transform', name=name+'_CTL')
    mc.parent(ctl, parent)

    for shape in shapes:
        create_new_curve_shape(ctl, shape['points'], shape['degree'], name=name+'Shape')

    return ctl

def build_masterWalk_control(shapeName, name, parent):
    '''
    Similar to the build_control_from_json() function, but we handle a particular case for the masterWalk control

    Parameters
    ----------
    shapeName   : str : the key we will be searching for in the shape library
    name        : str : name to assign to the shape nodes
    parent      : str : control under which to parent he shape

    Returns
    -------
    Str : the name of the control transform, which will contain the shape nodes

    '''
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
    '''
    This function is used to scale-up the control shape, so we can easily shape the controls in the build since we don't have an implementation for saving control shapes.

    The scale will be relative to the existing size of the shape

    Parameters
    ----------
    name        : str : the name of the control we will be scaling up
    scaleAmount :double: the amount we scale the control shape by

    Returns
    -------
    None
    '''
    # Calculate Point Center
    mc.select(name)
    center = mc.objectCenter(name)
    for shape in mc.listRelatives(name, type='nurbsCurve'):
        # Scale
        mc.xform(shape+"*.cv[*]", s=[scaleAmount, scaleAmount, scaleAmount], piv=center, r=True)
