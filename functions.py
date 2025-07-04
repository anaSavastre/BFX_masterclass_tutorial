from maya.api import OpenMaya as om
from maya import cmds as mc

def get_closest_UV_on_Surface(nrbSurface, position):
    '''
    '''
    if isinstance(position, list):
        position = om.MPoint(position)
    # Get the MObject for the NURBS surface
    selection_list = om.MSelectionList()
    selection_list.add(nrbSurface)
    nrb_dag_path = selection_list.getDagPath(0)

    # Create an MFnNurbsSurface object from the surface
    nurbs_surface_fn = om.MFnNurbsSurface(nrb_dag_path)

    # Find the closest point on the NURBS surface
    closest_point, u, v = nurbs_surface_fn.closestPoint(position, space=om.MSpace.kWorld)

    return u, v

def rivet_to_surface(nrbSurface, transform, u, v):
    '''
    PointOnSurfaceInfo -> Matrix -> object.offsetParentMatrix
    '''

    pointOnSurface = mc.createNode('pointOnSurfaceInfo',  name=transform[:-3]+'PSI')
    mc.connectAttr(nrbSurface+'.worldSpace', pointOnSurface+'.inputSurface')

    matrix = mc.createNode('fourByFourMatrix', name=transform[:-3]+'MAT')
    biNormal = mc.createNode('vectorProduct', name=transform[:-3]+'VPR')
    mc.connectAttr(pointOnSurface+'.result.normal', biNormal+'.input1')
    mc.connectAttr(pointOnSurface+'.result.tangentU', biNormal+'.input2')
    mc.setAttr(biNormal+'.operation', 2)
    mc.setAttr(pointOnSurface+'.parameterU', u)
    mc.setAttr(pointOnSurface+'.parameterV', v)

    for i, axis in enumerate('XYZ'):
        mc.connectAttr(pointOnSurface+'.result.tangentU.tangentU'+axis.lower(), matrix+'.in0'+str(i))
        mc.connectAttr(pointOnSurface+'.result.normal.normal'+axis, matrix+'.in1'+str(i))
        mc.connectAttr(biNormal+'.output.output'+axis, matrix+'.in2'+str(i))
        mc.connectAttr(pointOnSurface+'.result.position.position'+axis, matrix+'.in3'+str(i))
    
    # Mult matrix * transform.parentInverseMatrix
    localMatrix = mc.createNode('multMatrix', name=transform[:-3]+'MMT')
    mc.connectAttr(matrix+'.output', localMatrix+'.matrixIn[0]')
    mc.connectAttr(transform+'.parentInverseMatrix', localMatrix+'.matrixIn[1]')
    decomposeMatrix = mc.createNode('decomposeMatrix', name=transform[:-3]+'DCM')

    mc.connectAttr(localMatrix+'.matrixSum', decomposeMatrix+'.inputMatrix')
    mc.connectAttr(decomposeMatrix+'.outputTranslate', transform+'.translate')
    mc.connectAttr(decomposeMatrix+'.outputRotate', transform+'.rotate')
    
def min(name, attribute, value):
    '''
    For simplicity we will take the min between an attr and a value
    '''

    minNode = mc.createNode('condition', name=name)
    mc.connectAttr(attribute, minNode+'.firstTerm') 
    mc.connectAttr(attribute, minNode+'.colorIfTrueR') 
    mc.setAttr(minNode+'.operation', 4 )
    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(minNode+'.colorIfFalseR', value)
        mc.setAttr(minNode+'.secondTerm', value)
    else:
        mc.connectAttr(value, minNode+'.colorIfFalseR')
        mc.connectAttr(value, minNode+'.secondTerm')
    
    
    return minNode


def max(name, attribute, value):
    '''
    For simplicity we will take the max between an attr and a value
    '''

    minNode = mc.createNode('condition', name=name)
    mc.connectAttr(attribute, minNode+'.firstTerm') 
    mc.connectAttr(attribute, minNode+'.colorIfTrueR') 
    mc.setAttr(minNode+'.operation', 2 )
    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(minNode+'.colorIfFalseR', value)
        mc.setAttr(minNode+'.secondTerm', value)
    else:
        mc.connectAttr(value, minNode+'.colorIfFalseR')
        mc.connectAttr(value, minNode+'.SecondTerm')
    
    
    return minNode

def subtract(name, attribute, value):
    '''
    
    '''

    node = mc.createNode('subtract', name=name)
    mc.connectAttr(attribute, node+'.input1') 
    
    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(node+'.input2', value)
    else:
        mc.connectAttr(value, node+'.input2')

    return node

def multiply_Double(name, attribute, value):
    node = mc.createNode('multDoubleLinear', name=name)
    mc.connectAttr(attribute, node+'.input1') 

    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(node+'.input2', value)
    else:
        mc.connectAttr(value, node+'.input2')

    return node
    