import bpy

# Select particle first, then the emitter

# Set these to False if you don't want to key that property.
KEYFRAME_LOCATION = True
KEYFRAME_ROTATION = False
KEYFRAME_SCALE = False

def create_objects_for_particles(ps, obj):
    # Duplicate the given object for every particle and return the duplicates.
    # Use instances instead of full copies.
    obj_list = []
    mesh = obj.data
    particles_coll = bpy.data.collections.new(name="particles")
    bpy.context.scene.collection.children.link(particles_coll)

    for i, _ in enumerate(ps.particles):
        dupli = bpy.data.objects.new(
                    name="particle.{:03d}".format(i),
                    object_data=mesh)
        particles_coll.objects.link(dupli)
        obj_list.append(dupli)
    return obj_list

def match_and_keyframe_objects(ps, obj_list, start_frame, end_frame):
    # Match and keyframe the objects to the particles for every frame in the
    # given range.
    for frame in range(start_frame, end_frame + 1):
        print("frame {} processed".format(frame))
        bpy.context.scene.frame_set(frame)
        for p, obj in zip(ps.particles, obj_list):
            match_object_to_particle(p, obj)
            keyframe_obj(obj)

def match_object_to_particle(p, obj):
    # Match the location, rotation, scale and visibility of the object to
    # the particle.
    loc = p.location
    rot = p.rotation
    size = p.size
#    if p.alive_state == 'ALIVE':
#        size = p.size
#    else:
#        size = 0.0001
    obj.location = loc
    # Set rotation mode to quaternion to match particle rotation.
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot
    obj.scale = (size, size, size)

def keyframe_obj(obj):
    # Keyframe location, rotation, scale and visibility if specified.
    if KEYFRAME_LOCATION:
        obj.keyframe_insert("location")
    if KEYFRAME_ROTATION:
        obj.keyframe_insert("rotation_quaternion")
    if KEYFRAME_SCALE:
        obj.keyframe_insert("scale")

def main():
    #in 2.8 you need to evaluate the Dependency graph in order to get data from animation, modifiers, etc
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Assume only 2 objects are selected.
    # The active object should be the one with the particle system.
    ps_obj = bpy.context.object
    ps_obj_evaluated = depsgraph.objects[ ps_obj.name ]
    obj = [obj for obj in bpy.context.selected_objects if obj != ps_obj][0]
    ps = ps_obj_evaluated.particle_systems[0]  # Assume only 1 particle system is present.
    start_frame = bpy.context.scene.frame_start
    end_frame = bpy.context.scene.frame_end
    obj_list = create_objects_for_particles(ps, obj)
    match_and_keyframe_objects(ps, obj_list, start_frame, end_frame)

if __name__ == '__main__':
    main()