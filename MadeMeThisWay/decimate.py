import bpy
import random

DELETION_PROBABILITY = 0.5;

toBeDeleted = []

for obj in bpy.context.selected_objects:
    r = random.uniform(0.0, 1.0)
    if r < DELETION_PROBABILITY:
        toBeDeleted.append(obj)
        
for obj in bpy.context.selected_objects:
    obj.select_set(False)

print('Deleting {} objects'.format(len(toBeDeleted)))

for obj in toBeDeleted:
    obj.select_set(True)
    
bpy.ops.object.delete()
 
print('Done.') 
