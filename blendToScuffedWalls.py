import bpy
import mathutils

templatePath = bpy.path.abspath('//../swtemplate')
swPath = bpy.path.abspath('//../ExpertPlusStandard_ScuffedWalls.sw')

buff = []
counter = [0]

def toDeg(rad):
    return 57.2958*rad

def toRad(deg):
    return deg/57.2958

def write(s):
    buff.append(s)

def writeSwFile():
    templateFile = open(templatePath, 'r')
    templateContent = templateFile.read()
    templateFile.close()
    
    content = templateContent.replace('#INCLUDE#', '\n'.join(buff))
    
    swFile = open(swPath, 'w')
    swFile.write(content)
    swFile.close()

START_FRAME = 0
END_FRAME = 991
FRAMES_PER_BEAT = 2.0
SAMPLE_RESOLUTION = 10
DURATION_FRAMES = END_FRAME - START_FRAME + 1
DURATION_BEATS = DURATION_FRAMES / FRAMES_PER_BEAT
MOVEMENT_METERS_PER_FRAME = 1

def getLocationArray(obj):
    loc = obj.location
    newPos = [
        loc[0], 
        loc[2] + 0.65, 
        loc[1] + 1.1
    ]
    return newPos

def getRotationArray(obj):
    rot = obj.rotation_euler.copy()
    otherRot = mathutils.Euler([toRad(0),toRad(15),toRad(45)],'XYZ')
    otherRot.rotate(rot)
    rot = otherRot
    newRot = [
        toDeg(rot[0]),
        toDeg(rot[2]),
        toDeg(rot[1])
    ]
    return newRot

def getScaleArray(obj):
    sc = obj.scale
    newScale = [
        sc[0] * 0.18 * 2, 
        sc[2] * 0.0048 * 2, 
        sc[1] * 0.16 * 2
    ]
    return newScale

# EXPORT BLOCKS =============================================

# start and end are both inclusive
# 3 4 5
# start = 3
# end = 5
# durationFrames = 2
# curr = 3, relframe = 0, normalizedTime = 0
# curr = 4, relFrame = 1, normalizedTime = 1/2 = 0.5
# curr = 5, relFrame = 2, normalizedTime = 2/2 = 1.0

def getObjPositionAnimation(locationAnimations, obj):
    keyframes = locationAnimations[obj.name]
    return ','.join(keyframes)

def makeBlockAnimations(objects, startFrame, endFrame):
    print('Computing block animations...')
    # Key: obj name, string
    # Value: Array<string>, each is a SW animation keyframe
    locationAnimations = {}
    
    durationFrames = endFrame - startFrame
    durationBeats = durationFrames / FRAMES_PER_BEAT
    currentFrame = startFrame
    while (currentFrame <= endFrame):
        print('Frame {}/{}'.format(currentFrame, endFrame))
        relFrame = currentFrame - startFrame
        normalizedTime = float(relFrame) / (durationFrames)
        bpy.context.scene.frame_set(currentFrame)
        zOffset = -1.0 * (currentFrame) * MOVEMENT_METERS_PER_FRAME
        for obj in objects:
            pos = getLocationArray(obj)
            newKeyframe = '[{},{},{},{}]'.format(
                pos[0],
                pos[1],
                pos[2] + zOffset,
                normalizedTime
            )
            objName = obj.name
            if not (objName in locationAnimations):
                locationAnimations[objName] = []
            objectKeyframes = locationAnimations[objName]
            objectKeyframes.append(newKeyframe)
        currentFrame += SAMPLE_RESOLUTION
    return locationAnimations
    

def exportBlocks(collectionName):
    print('Exporting blocks...')
    currentIndex = 0
    totalObjects = len(bpy.data.collections[collectionName].objects)
    # Compute animations
    allLocationAnimationKeyframes = makeBlockAnimations(bpy.data.collections[collectionName].objects, START_FRAME, END_FRAME)
    # Write data
    for obj in bpy.data.collections[collectionName].objects:
        write('0:Environment')
        write('  Id:BTSEnvironment\\.\\[0\\]Environment\\.\\[16\\]PillarPair\\.\\[0\\]PillarL\\.\\[0\\]Pillar$')
        write('  duplicate:1')
        write('  LookUpMethod:Regex')
        write('  active:true')
        newPos = getLocationArray(obj)
        newScale = getScaleArray(obj)
        newRot = getRotationArray(obj)
        newTrackName = 'gentrack{}'.format(counter[0])
        counter[0] += 1
        write('  position:[{},{},{}]'.format(newPos[0], newPos[1], newPos[2]))
        write('  scale:[{},{},{}]'.format(newScale[0], newScale[1], newScale[2]))
        write('  localRotation:[{},{},{}]'.format(newRot[0], newRot[1], newRot[2]))
        write('  track:{}'.format(newTrackName))
        
        write('0:AnimateTrack')
        write('  track:{}'.format(newTrackName))
        write('  duration:{}'.format(DURATION_BEATS))
        write('  AnimatePosition:{}'.format(getObjPositionAnimation(allLocationAnimationKeyframes, obj)))
        print('Experted {}/{}'.format(currentIndex, totalObjects))
        currentIndex += 1

# EXPORT WALLS ===================================================

# A bucket is Dict<bucketNumber, Array<obj>>

BUCKET_DURATION_FRAMES = 1
BUCKET_DURATION_BEATS = BUCKET_DURATION_FRAMES / FRAMES_PER_BEAT
DRAW_DISTANCE_FRAMES = 35
PERSISTENCE_FRAMES = 3 # How many frames before despawn after passing by the player

def computeBucketNumber(positionOrFrame):
    return int(round(positionOrFrame / BUCKET_DURATION_FRAMES))

def getOrCreateBucket(buckets, bucketNumber):
    if not (bucketNumber in buckets):
        buckets[bucketNumber] = []
    return buckets[bucketNumber]

def deselectAll():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

def exportWalls(collectionName):
    print('Exporting walls...')
    bpy.context.scene.frame_set(START_FRAME)
    buckets = {}
    for obj in bpy.data.collections[collectionName].objects:
        depthLoc = obj.location[1] # Y
        bucketNumber = computeBucketNumber(depthLoc)
        bucket = getOrCreateBucket(buckets, bucketNumber)
        bucket.append(obj)
    
    for bucketNumber in buckets:
        bucket = buckets[bucketNumber]
        print('Bucket {} has {}'.format(bucketNumber, len(bucket)))
        centralFrame = bucketNumber * BUCKET_DURATION_FRAMES
        endFrame = centralFrame + BUCKET_DURATION_FRAMES + PERSISTENCE_FRAMES # ends when all objects in bucket go out of vision
        startFrame = centralFrame - DRAW_DISTANCE_FRAMES
        if (startFrame < START_FRAME):
            startFrame = START_FRAME
        if (endFrame > END_FRAME):
            endFrame = END_FRAME
        bucketDurationFrames = endFrame - startFrame
        bucketDurationBeats = bucketDurationFrames / FRAMES_PER_BEAT
        bucketStartBeat = startFrame / FRAMES_PER_BEAT
        trackPositionAnimation = '[0,0,{},0],[0,0,{},1]'.format(
            -1.0 * startFrame * MOVEMENT_METERS_PER_FRAME,
            -1.0 * endFrame * MOVEMENT_METERS_PER_FRAME
        )
        # Select objects
        deselectAll()
        for obj in bucket:
            obj.select_set(True)
        bpy.data.scenes[0].frame_start = startFrame
        bpy.data.scenes[0].frame_end = endFrame
        exportFileName = bpy.path.abspath('//bucket{}.dae'.format(bucketNumber))
        bpy.ops.wm.collada_export(
            filepath=exportFileName,
            selected=True,
            export_global_up_selection='Y',
            export_global_forward_selection='Z',
            apply_global_orientation=True,
            triangulate=False
        )
        # Write to SW file
        #0: ModelToWall
        #    Path:blend/main.dae
        #    Duration:495
        #    AnimatePosition:[0,0,0,0],[0,0,-991,1]
        #    Interactable: false
        #    Fake: true
        #    Thicc:0.1
        write('{}:ModelToWall'.format(bucketStartBeat))
        write('  Path:blend/bucket{}.dae'.format(bucketNumber))
        write('  Duration:{}'.format(bucketDurationBeats))
        write('  AnimatePosition:{}'.format(trackPositionAnimation))
        write('  Interactable:false')
        write('  Fake:true')
   
exportWalls('walls')
exportBlocks('blocks')
writeSwFile()
bpy.data.scenes[0].frame_start = START_FRAME
bpy.data.scenes[0].frame_end = END_FRAME
print('Export completed.')
