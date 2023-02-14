import bpy 
import bmesh
import random
from math import radians # for angles
from mathutils.bvhtree import BVHTree

# Christophe Bruchansky, February 2023
# Class that generates pipes within a given perimeter while avoiding obstacles
class Pipes(object):
    
    __perimeterTree = None # perimeter (BVHTree)
    __toAvoidTrees = [] # all obstacles (BVHTrees)
    
    # Creates an instance 
    def __init__(self, perimeter):
        self.__perimeter_tree = self.__getTree(perimeter)
        
    # Add an obstacle that pipes should avoid
    def addObstacle(self,mesh):
        mesh_tree = self.__getTree(mesh)
        self.__toAvoidTrees.append(mesh_tree) 
        
    # Detects if a mesh collides
    # any obstacle (returns 1)
    # with the perimeter (returns 2) 
    def __detectCollision(self,mesh):
        mesh_tree = self.__getTree(mesh)
        for object_tree in self.__toAvoidTrees:
            intersections = mesh_tree.overlap(object_tree)
            if intersections:
                return 1
        intersections = mesh_tree.overlap(self.__perimeter_tree)
        if intersections:
                return 2
        return 0
    
    # Returns a BVHTree for a given mesh
    def __getTree(self,mesh):
        m_1 = mesh.matrix_world.copy()
        mesh_verts = [m_1 @ vertex.co for vertex in mesh.data.vertices]
        mesh_polys = [polygon.vertices for polygon in mesh.data.polygons]
        mesh_tree = BVHTree.FromPolygons(mesh_verts, mesh_polys)
        return mesh_tree
        
    # Generates a pipe from a given surface (location, angle and direction) 
    def createPipe(self,source,radius,min_length,max_length):
        inPerimeter = True
        iterations = 0 # number of iterations to create the pipe
        maxIterations = 20 # to avoid endless loops in some edge cases
        
        # Randomly generated pipe material
        mat_pipe = bpy.data.materials.new(name = "Pipe Material") 
        mat_pipe.use_nodes = True
        node_tree = mat_pipe.node_tree
        nodes = node_tree.nodes
        bsdf = nodes.get("Principled BSDF") 
        bsdf.inputs[0].default_value = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
        bsdf.inputs[6].default_value = 1
        bsdf.inputs[9].default_value = 0.2

        # Creates a temporary new pipe segment
        tempSegment = self.__createPipeSegment(source, radius,min_length,max_length, mat_pipe, None)
        tempAngle = None
        segment = None
        collision2 = None

        # And test if that new pipe segment collides with anything
        while inPerimeter:
            collision = self.__detectCollision(tempSegment) # collision with the pipe segment
            for child in tempSegment.children: # collision with the angle at the end of the pipe segment
                    if child.name == "angle":
                        tempAngle = child
                        collision2 = self.__detectCollision(tempAngle)
            if iterations > 20: 
                inPerimeter=False
                print ('Maximum pipe iterations reached')
                break
            elif collision == 2 or collision2 == 2:
                inPerimeter=False
                print ('Pipe is out of perimeter')
                break
            elif (collision == 1 or collision2 == 1) and segment:
                tempSegment.select_set(True)
                for child in tempSegment.children:
                    child.select_set(True)
                bpy.ops.object.delete() 
                segment.select_set(True)
                print('Collision is detected, abort pipe segment, try a new direction and length')
            elif collision == 1:
                tempSegment.select_set(True)
                for child in tempSegment.children:
                    child.select_set(True)
                bpy.ops.object.delete() 
                print('An obstacle is blocking the pipe source, pipe is aborted')
                break
            else: # if no obstacle, then the new segment is confirmed
                segment = tempSegment
                self.addObstacle(segment)
                if tempAngle:
                    self.addObstacle(tempAngle)
            iterations +=1
            tempSegment = self.__createPipeSegment(segment, radius, min_length, max_length , mat_pipe, True)
    
    # Generates a new pipe segment with a random length and direction
    def __createPipeSegment(self,parent, radius, min_length, max_length, mat_pipe, side):
        length = random.uniform(min_length,max_length)
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0, 0, 0), scale=(1, 1, 1),end_fill_type='NOTHING')
        segment = bpy.context.active_object
        segment.data.materials.append(mat_pipe)
        bpy.ops.object.shade_smooth(use_auto_smooth=True)
        bpy.ops.transform.rotate(value=radians(random.randint(0,3)*90), orient_axis='Z', orient_type='GLOBAL')
        segment.parent = parent
        bpy.ops.transform.resize(value=(1/parent.scale[0],1/parent.scale[1],1/parent.scale[2]), orient_type='GLOBAL')
        if side:
            # Turn pipe to make an angle
            bpy.ops.transform.translate(value=(0, 0.25*radius, parent.dimensions.z / 2 +radius+0.28*radius), orient_type='LOCAL')
            bpy.ops.transform.translate(value=(0, length/2+radius, 0), orient_type='LOCAL')
            bpy.ops.transform.rotate(value=radians(90), orient_axis='X', orient_type='LOCAL')
            # Create angle to connect it with previous pipe segment
            bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1),end_fill_type='NOTHING')
            angle = bpy.context.active_object  
            angle.parent=segment
            angle.name="angle"
            bpy.ops.transform.translate(value=(0, 0, -length/2-radius), orient_type='LOCAL')
            bpy.ops.transform.rotate(value=radians(-45), orient_axis='X', orient_type='LOCAL')
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform"].angle = radians(90)
            bpy.ops.object.shade_smooth(use_auto_smooth=True)
            bpy.ops.transform.resize(value=(radius, radius, radius),orient_type='LOCAL')
            bpy.ops.transform.translate(value=(0, 0.35*radius, -0.2*radius), orient_type='LOCAL')
            angle.data.materials.append(mat_pipe)
        else:
            bpy.ops.transform.translate(value=(0, 0, length/2), orient_type='LOCAL')

        # Adds details to the pipe segment
        maxr = int(length/min_length)
        for r in range(1,maxr):
            bpy.ops.mesh.primitive_cylinder_add(radius=radius*1.1, depth=min_length/5, location=(0, 0, 0), scale=(1, 1, 1))
            c = bpy.context.active_object
            c.parent=segment
            c.data.materials.append(mat_pipe)
            bpy.ops.transform.translate(value=(0, 0, length/2-(length/maxr*r)), orient_type='LOCAL')
        bpy.context.view_layer.objects.active = segment
        
        return segment
                

# TO BE CONFIGURED ##### 

print('')
print('Generating pipes...')

min_radius = 0.5 # minimum pipe radius
max_radius = 1 # maximum pipe radius
min_length = 1 # minimum pipe segment length
max_length = 10 # maximum pipe segment length

pipes = Pipes(bpy.data.objects["perimeter"])
pipes.addObstacle(bpy.data.objects['Suzanne']) # objects that pipe should avoid
pipes.createPipe(bpy.data.objects["source1"],random.uniform(min_radius, max_radius),min_length,max_length)
pipes.createPipe(bpy.data.objects["source2"],random.uniform(min_radius, max_radius),min_length,max_length)
pipes.createPipe(bpy.data.objects["source3"],random.uniform(min_radius, max_radius),min_length,max_length)
pipes.createPipe(bpy.data.objects["source4"],random.uniform(min_radius, max_radius),min_length,max_length)

print('All pipes generated')