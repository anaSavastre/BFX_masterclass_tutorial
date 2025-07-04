from maya import cmds as mc
from maya import OpenMaya as om
import os, json
import static
import controlFn as ctlFn



def build_rig_scene(assetName):
    '''
    In this function we are going to create our rig scene.
    Steps are:
        - Creating a new scene
        - Creating the basic hierarchy
        - Importing components file
        - Importing model

    Basic Hierarchy:        
            - AssetGroup
                - AssetGroup_CTL
                    -MasterWalk
                        -ctl
                        -rig
                        -jnt
                    -geometry

    '''
    # Creating new file
    mc.file(new=1, f=1)

    # Import model
    path = '/'.join([static.project, assetName, 'modeling'])
    modelFile = os.listdir(path)
    modelFile.sort()
    mc.file('/'.join([path, modelFile[-1]]), i= True, type= "mayaAscii", usingNamespaces= False, f=True)  

    # Create our hierarchy
    characterGroup = mc.createNode('transform', name=static.characterGroup)
    masterWalkCtl = ctlFn.build_masterWalk_control('masterWalk', name=static.      masterWalk, parent=characterGroup)
    ctlFn.scale_control(masterWalkCtl, 5)

    # Parent geometry group
    mc.parent(static.geometryGroup, characterGroup)

    # Creating the rig groups: ctl, rig, jnt
    for grpName in [static.ctlGroup, static.jntGroup, static.rigGroup]:
        grp = mc.createNode('transform', name=grpName)
        mc.parent(grp, masterWalkCtl)

    # Import components file
    path = '/'.join([static.project, assetName, 'rigging', 'components'])
    if not os.path.exists(path):
        os.makedirs(path)
        return
    componentsFile = os.listdir(path)
    if len(componentsFile)>0:
            
        componentsFile.sort()
        mc.file('/'.join([path, componentsFile[-1]]), i= True, type= "mayaAscii", usingNamespaces= False, f=True) 
    

def get_boundingBox(object):
    bbx = mc.exactWorldBoundingBox(object)

    boundingBox = om.MBoundingBox (om.MPoint(bbx[0], bbx[1], bbx[2]), om.MPoint(bbx[3], bbx[4], bbx[5]))
    return boundingBox
# def add_control(side='C', name='control', shape='globalMove'):

