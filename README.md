# Welcome to the BFX rigging masterclass

This repository contains a few scripts that are intended to streamline the process during the session.

Use these sparingly because they have not been build with the purpose of being used outside this context. 

## Set-up

To start playing with the code and the build file, please copy the shared folder to the following path `C:/Users/{YOUR_USER_NAME}/Documents/maya/projects/`

## Running the code

To run the code you can open the `build/Ellie.py` file in your maya script editor.

Let's go over the content of this file

1. First function we run in here is `flush_python_cache()`. The reason why we need to run this before anything else is because Maya creates a python cash of all the modules that we load, so if we make any changes to functions/modules that live outside the main scope of the file we are running. So we wouldn't really be able to see our changes and updates.

2. Second stage, we are running the `pipeline.build_rig_scene('CHR_Ellie')`. This function is a very simple method that will **create a new working scene**, bringing together our latest model file, latest rig components and creating the main hierarchy of the rig, driven by the master move control.

3. Third stage is where we start constructing the main components of our rig. 
In the case of this master class we will be focusing on building a leg, therefore we will add a COG (Center of Gravity control), which will act as out **hips** and then the leg module.

## Master Class Over View: Building an IK Leg

During the masterclass I will go over how to create an IK leg rig. 
I will cover the following topics:

- **Building Leg Components:**
To achieve appealing and realistic deformations we want to choose appropriate pivot point from where to deform our leg and character in general. Also I will present the advantages of using a scripted pipeline when building your rigs.

- **Building the IK Leg:**
Presenting the IK mechanics and how to create a stretchy IK.

- **Constructing Pole Vector:**
I will present a solution for how to procedurally construct your pole vector based on the leg guides we have already provided to the module. Be ready to use some of the vector maths you have been learning in your uni course work.

- **Leg Surface:**
This is where things will be getting a bit more complicated. We will create a nurbs surface that will be driven by the IK leg. Along the surface we will rivet a few joints which will be our **bind joints**. 

- **Foot Roll:**

- **Skinning**
Finally, having completed the building of the leg we will look at some skinning practices. I will share my workflow and a few tips and tricks that I use.

I hope you enjoyed the session! 

