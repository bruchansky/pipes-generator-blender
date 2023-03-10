# Pipes Generator for Blender

A Python class to generate pipes that randomly fill a 3D space while avoiding obstacles. The procedural pipes are based on Blender primitives, so no need to import any mesh. 

![Pipes engine](https://github.com/bruchansky/pipes-generator-blender/blob/main/pipes-engine.jpg?raw=true)

Example ([Sauna part II](https://bruchansky.name/2023/02/24/sauna-pool-godlike/)):

![Pipes example](https://github.com/bruchansky/pipes-generator-blender/blob/main/god-pipes.jpeg?raw=true)



Instructions
1. Copy the code inside Blender (scripting workspace)
2. Add the following items onto your scene:
- A perimeter mesh to define the 3D space where pipes can grow (to set as invisible)
- A series of surfaces that define the origin of each pipe (location, angle and direction)
- Obstacles that pipes should avoid (optional)
3. Update parameters at the bottom of the script
4. Press play in the scripting workspace to generate the pipes
5. A random material is assigned to each pipe, and can be updated in materials

Current limitations
- Pipes don’t scale with their origin surfaces, but their radius and length are configurable.
- Pipes won’t be generated if other pipes are in front of their origin surfaces.
- The algorithm won’t always find a path for a pipe to reach the perimeter zone, and some pipes might be truncated.

Best is to play the script several times until a satisfactory composition is found.
