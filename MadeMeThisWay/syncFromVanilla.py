import bpy
import random
import shutil

difficulties = [
    'EasyStandard',
    'NormalStandard',
    'HardStandard',
    'ExpertStandard',
    'ExpertPlusStandard'
]

for difficulty in difficulties:
    sourceName = difficulty + '.dat'
    sourcePath = bpy.path.abspath('//../../Made me this way/' + sourceName)

    destName = difficulty + '_Old.dat'
    destPath = bpy.path.abspath('//../' + destName)
    
    shutil.copyfile(sourcePath, destPath)
    
print('Done SyncFromVanilla')
