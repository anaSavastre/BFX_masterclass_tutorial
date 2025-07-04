from maya.api import OpenMaya as om
from maya import cmds as mc

def get_closest_UV_on_Surface(nrbSurface, position):
    '''
    This function will return the closes UV parameter to a specified position

    Parameters
    ----------
    nrbSurface  : str : name of the nurbs surface
    position    : list or MPoint: provide the X, Y, Z coordinates of the position we are querying 

    Returns
    -------
    u, v : double : the closest U, V parameters on the surface
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
    This function will construct a rivet set-up, using a point on surface info node to extract surface normal and tangents, and a four by four matrix to construct our rivet transform matrix. 

    The 4X4 matrix will have the following structure:
        [
            [surfaceTangentU.X, surfaceTangentU.Y, surfaceTangentU.Z, 0],
            [surfaceNormal.X, surfaceNormal.Y, surfaceNormal.Z, 0],
            [biNormal.X, biNormal.Y, biNormal.Z, 0],
            [position.X, position.Y, position.Z, 1]
        ], 
    where the 
            biNormal = surfaceTangent ^ surfaceNormal 
            position = world space position at parameters u, v
    
    Parameters
    ----------
    nrbSurface  : str : name of the nurbs surface
    transform   : str : name of transform we want to rivet
    u, v        : double: parameter at which we are constructing the rivet 

    Returns
    -------
    None

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
    Returning the minimum between our attribute and a provided value
    -> min(attribute, value)

    Parameters
    ----------
    name        : str : name to assign to the condition node
    attribute   : str : name of attribute we want to construct the minimum for 
    value       : double: min value we compare against 

    Returns
    -------
    conditionNode: str 
    
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
    Returning the max between our attribute and a provided value
    -> max(attribute, value)

    Parameters
    ----------
    name        : str : name to assign to the condition node
    attribute   : str : name of attribute we want to construct the maximum for 
    value       : double: max value we compare against 

    Returns
    -------
    conditionNode: str 
    '''

    maxNode = mc.createNode('condition', name=name)
    mc.connectAttr(attribute, maxNode+'.firstTerm') 
    mc.connectAttr(attribute, maxNode+'.colorIfTrueR') 
    mc.setAttr(maxNode+'.operation', 2 )
    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(maxNode+'.colorIfFalseR', value)
        mc.setAttr(maxNode+'.secondTerm', value)
    else:
        mc.connectAttr(value, maxNode+'.colorIfFalseR')
        mc.connectAttr(value, maxNode+'.SecondTerm')
    
    
    return maxNode

def subtract(name, attribute, value):
    '''
    Returns attribute - value

    Parameters
    ----------
    name        : str : name to assign to the node
    attribute   : str : name of attribute we want to subtract from 
    value       : double: value to subtract 

    Returns
    -------
    subtractNode: str
    '''

    node = mc.createNode('subtract', name=name)
    mc.connectAttr(attribute, node+'.input1') 
    
    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(node+'.input2', value)
    else:
        mc.connectAttr(value, node+'.input2')

    return node

def multiply_Double(name, attribute, value):
    '''
    Returns attribute * value

    Parameters
    ----------
    name        : str : name to assign to the node
    attribute   : str : name of attribute we want to multiply from 
    value       : double: value to subtract 

    Returns
    -------
    subtractNode: str
    '''
    node = mc.createNode('multDoubleLinear', name=name)
    mc.connectAttr(attribute, node+'.input1') 

    if isinstance(value, float) or isinstance(value, int):
        mc.setAttr(node+'.input2', value)
    else:
        mc.connectAttr(value, node+'.input2')

    return node
    