# Flocking Simulation (C++ & OpenGL)
This project implements a flocking simulation leveraging object-oriented programming principles, built using C++ and Bournemouth University's OpenGL libraries. The simulation demonstrates emergent flocking behavior through the interaction of individual "boid" agents.

## Project Overview
The core of this project is to simulate a flock of autonomous agents (boids) that exhibit natural-looking group behavior. This is achieved by defining a set of simple rules for each boid, such that their collective interactions result in complex and visually appealing patterns. Object-oriented programming was central to structuring the individual boid logic and the overall flocking system.

## Compiling and Runing The Code

Note: These are some general instructions of compiling and running the code. It is assumed you have the correct NGL environment build to leverage the BU OpenGL framework

- Compile the code using the provided makefile
```bash
make
```

- Run the simulation. Navigate to the root directory of the project and execute the compiled program:

``` bash
./FlockingGUI
```

## Key Componnets

`**Boid.cpp / Boid.h**`

This is the fundamental building block of the flocking system. The Boid class encapsulates all parameters and behaviors of an individual boid.

**Parameters**: Stores essential properties such as:

- position: The current 3D coordinates of the boid.
- rotation: The orientation of the boid.
- velocity: The current 3D velocity vector of the boid.
- direction: The current facing direction of the boid.
- seek, separate and align radiuses.
- shading parameters, colour, mesh information, etc

**Behaviors**: The core movements and interactions
- Move: Logic for updating the boid's position
- Rotate: Rotates the boid depending on the boid's direction
- Steer: assigns the new direction to the boid and calls the
rotate function

`**NGLScene.cpp / NGLScene.h**`

This class is responsible for orchestrating the entire flocking system.

- **Flock Construction:** Creates and manages an array (or other suitable data structure) of Boid objects.

- **Flock Behavior Implementation:** In its update loop, it iterates through all boids, applies the flocking rules, and updates their states based on their interactions with other boids in the flock.

- **Rendering:** Handles the rendering of all boids within the OpenGL context.