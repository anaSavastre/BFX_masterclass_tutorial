# Maya C++ Plug-in Library

This repository contains the C++ source code for my personal library of Autodesk Maya plug-ins. These plug-ins were specifically compiled for **Maya 2018**.

## Plug-ins

Below is a list of the plug-ins included in this repository, along with a brief description of their functionality.

## asMatloft

The purpose of the matloft node is to generate and drive a nurbs surface from a series of transforms. Given a series of matrices and a vector we calculate the necessary points to compose a nurbs surface. 

- **as_inWorldMatrix**: Takes in a list of matrices. For example the world matrices of the transforms we want to generate the nurbs surface from

- **as_inRevolveVector**: The user can specify the x, y, z components of a vector that will be used to revolve the surface along. For example if we provide (1, 0, 0) we will be revolving along the X axis of all the transform matrices.

- **as_inWidthOffset**: This parameter will control the with of the surface.

- **as_outSurface**: This will correspond to the output of the node calculation, the output surface. Plug this attribute into the `create` attribute of a nurbs surface to draw your resulting surface.

## asRivet

Rivet nodes are used to attach transforms to nurbs surface. The advantage of this method is that the node gives users control over the parameter U, V at which we rivet the transform as well as the forwards and up vector to use, so that user can control the orientation of the resulting transform.

- **m_inSurfaceWS**: The surface we attach to
- **m_inU**, **m_inV**: The surface u, v parameters at which we attach our transform
- **m_tangent**: Specify which tangent to use in the calculation, choose between u or v. Depending on how the nurbs surface is used, providing a tangent can give us different results.
- **m_forward**: Forwards vector, this should specify the axis we want to point along the specified tangent
- **m_up**: Up vector, the axis/vector of the transform that will be in line with the surface normal.

## asSlidingSkinning

(Name is not great for this node)

This is a C++ skin sliding deformer using the Maya API. I wanted to create a deformer that could easily be incorporated into a character rig, creating a system that gives an immediate feedback of how the deformation looks.

There are two sides of this deformer. 

- A user defined sliding deformation.
- Sliding deformer that acts on top of the existing character deformation.

### User defined sliding

The inputs of the system are:

- **Vertex Handle**: representing the vertex ID from where the motion is driven
- **Radius**: defining the area of influence
- **Transformation Parameter**: this defines the deformation. To create an interface for controlling this parameter one can connect the translation of a controller object (a locator or any kind of transform node)

**Computing the deformation**

This section of the program deals with converting the input transformation parameter into a displacement vector in the plane that is tangent to the surface at the vertex handle point. The transformation would be done as follows:

1. Compute the transformation vector
2. Translate the vector to the vertex handle position
3. Get the projection of the transformation vector onto the plane, projecting the vector on to the tangent plane of the point we are deforming.
