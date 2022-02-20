import bpy
import random
import math

swPaths = [
  bpy.path.abspath('//../EasyStandard_ScuffedWalls.sw'),
  bpy.path.abspath('//../NormalStandard_ScuffedWalls.sw'),
  bpy.path.abspath('//../HardStandard_ScuffedWalls.sw'),
  bpy.path.abspath('//../ExpertStandard_ScuffedWalls.sw'),
  bpy.path.abspath('//../ExpertPlusStandard_ScuffedWalls.sw')
]

buff = []
counter = [0]

def toDeg(rad):
    return 57.2958*rad00

def toRad(deg):
    return deg/57.2958

def sin(deg):
    return math.sin(toRad(deg))

def cos(deg):
    return math.cos(toRad(deg))

def write(s):
    buff.append(s)

def writeSwFile():
    for swPath in swPaths:
        print('Writing to {}'.format(swPath))
        swFile = open(swPath, 'r')
        swContents = swFile.read()
        swFile.close()
        
        swContents = swContents.replace('\r\n', '\n')
        lines = swContents.split('\n')
        
        swFile = open(swPath, 'w')
        for line in lines:
            if '#AUTOGEN#' == line:
                break
            swFile.write(line)
            swFile.write('\n')
        
        swFile.write('#AUTOGEN#\n')
        
        swFile.write('\n'.join(buff))
        
        swFile.close()

EPS = 0.001
START_FRAME = 0
END_FRAME = 1106
FRAMES_PER_BEAT = 2.0
SAMPLE_RESOLUTION = 10
DURATION_FRAMES = END_FRAME - START_FRAME + 1
DURATION_BEATS = DURATION_FRAMES / FRAMES_PER_BEAT
MOVEMENT_METERS_PER_FRAME = 1

# EXPORT WALLS ===================================================

# A bucket is Dict<bucketNumber, Array<obj>>

BUCKET_DURATION_FRAMES = 1
BUCKET_DURATION_BEATS = BUCKET_DURATION_FRAMES / FRAMES_PER_BEAT
DRAW_DISTANCE_FRAMES = 100
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
    
    # Expert frames 2, 3, 4 + 5 6....
    # 2 .. 3 .. 4 .. 5 .. 6 ..
    # duration = 3
    # start = 2
    # end = 5
    
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
        bucketDurationFrames = endFrame - startFrame + 1
        bucketDurationBeats = bucketDurationFrames / FRAMES_PER_BEAT
        bucketStartBeat = startFrame / FRAMES_PER_BEAT
        trackPositionAnimation = '[0,0,{},0],[0,0,{},1]'.format(
            -1.0 * startFrame * MOVEMENT_METERS_PER_FRAME,
            -1.0 * (endFrame + BUCKET_DURATION_FRAMES + PERSISTENCE_FRAMES + 5) * MOVEMENT_METERS_PER_FRAME
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

# ===== WALL EFFETS LIB ===================================================

def b2t(beat, startBeat, duration):
    return (beat - startBeat) / duration

class AnimationData():
    def __init__(self):
        self.pos = [] # position
        self.rot = [] # rotation
        self.col = [] # color
        self.dis = [] # dissolve
        self.thicc = None
    
    def addPos(self, x, y, z, t):
        self.pos.append('[{},{},{},{}]'.format(x, y, z, t))
    
    def addRot(self, x, y, z, t):
        self.rot.append('[{},{},{},{}]'.format(x, y, z, t))
    
    def addCol(self, r, g, b, a, t):
        self.col.append('[{},{},{},{},{}]'.format(r/255.0, g/255.0, b/255.0, a, t))
    
    def addDis(self, d, t):
        self.dis.append('[{},{}]'.format(d, t))
        
    def addStandardDis(self):
        self.addDis(0.0, 0.000)
        self.addDis(0.0, 0.499)
        self.addDis(1.0, 0.500)
        self.addDis(0.0, 1.000)
        
    def setThicc(self, v):
        self.thicc = v
    
    def writeAll(self):
        if len(self.pos) > 0:
            write('  AnimatePosition:{}'.format(','.join(self.pos)))
        if len(self.rot) > 0:
            write('  AnimateLocalRotation:{}'.format(','.join(self.rot)))
        if len(self.col) > 0:
            write('  AnimateColor:{}'.format(','.join(self.col)))
        if len(self.dis) > 0:
            write('  AnimateDissolve:{}'.format(','.join(self.dis)))
        if self.thicc is not None:
            write('  Thicc:{}'.format(self.thicc))

def writeWall(blendFileName, startBeat, duration, animationData):
    write('{}:ModelToWall'.format(startBeat))
    write('  Path:blend/{}.dae'.format(blendFileName))
    write('  Duration:{}'.format(duration))
    write('  Interactable:false')
    write('  Fake:true')
    animationData.writeAll()
    
# ===== TILTED BUILDING ANIMATIONS ===================================================

def addTiltedBuilding(beat):
    repeat = 6
    for r in range(repeat):
        anim = AnimationData()
        anim.addDis(0, 0.00)
        anim.addDis(0, 0.25)
        anim.addDis(1, 0.50)
        anim.addDis(1, 0.80)
        anim.addDis(0, 1.00)
        x = random.uniform(20.0, 30.0)
        if random.uniform(0.0, 100.0) < 50.0:
            x = -x
        z = random.uniform(20.0, 80.0)
        anim.addPos(x, 0.0, z, 0.0)
        duration = 8.0
        start = beat - 4.0
        writeWall('city1', start, duration, anim)

def addTiltedBuildings():
    print('addTiltedBuildings')
    sectionOffsets = [5.0, 333.0]
    for sectionOffset in sectionOffsets:
        beat = sectionOffset + (1.0/3.0)
        gap = 8.0
        end = 64.0 + sectionOffset
        
        while beat < end:
            addTiltedBuilding(beat)
            beat += 1.0
            addTiltedBuilding(beat)
            beat += 1.0
            addTiltedBuilding(beat)
            beat += 6.0
        
def addTiltedRay(beat):
    repeat = 8
    for r in range(repeat):
        anim = AnimationData()
        anim.setThicc(10.0)
        anim.addStandardDis()
        x = 10.0
        name = 'cityRayRight'
        if random.uniform(0.0, 100.0) < 50.0:
            x = -x
            name = 'cityRayLeft'
        y = 0.0
        z = random.uniform(20.0, 80.0)
        anim.addPos(x, y, z, 0.0)
        duration = 1.0
        start = beat - (duration / 2.0)
        writeWall(name, start, duration, anim)

def addTiltedRays():
    print('addTiltedRays')
    sectionOffsets = [0.000,328.000]
    for sectionOffset in sectionOffsets:
        beats = [37.333,38.333,39.333,40.333,42.333,43.333,44.333,45.333,46.333,47.333,48.333,50.333,51.333,52.333,53.333,54.333,55.333,56.333,58.333,59.333,60.333,61.333,62.333,63.333,64.333,66.333,67.333,68.333]
        for b in beats:
            addTiltedRay(b + sectionOffset)
        
def addCityRotatingPatterns():
    print('addCityRotatingPatterns')
    for sectionOffset in [0.000,328.000]:
        for x in [-5.0, 5.0]:
            anim = AnimationData()
            anim.setThicc(10.0)
            y = 6.0
            z = 40.0
            anim.addPos(x, y, z, 0.0)
            startBeat = 37.333 + sectionOffset
            endBeat = 69.0 + sectionOffset
            duration = endBeat - startBeat
            beat = 38.0 + sectionOffset
            while beat < (69.0 + sectionOffset - EPS):
                rotZ = random.uniform(-15.0, 15.0)
                anim.addRot(0.0, 0.0, rotZ, b2t(beat, startBeat, duration))
                beat += 1.0
            anim.addDis(0.0, 0.0)
            anim.addDis(1.0, b2t(38.0 + sectionOffset, startBeat, duration))
            anim.addDis(1.0, b2t(68.0 + sectionOffset, startBeat, duration))
            anim.addDis(0.0, 1.0)
            writeWall('cityRotatingPattern', startBeat, duration, anim)
        
# ===== STRING MAZE ANIMATION EFFECTS ========================================

def genCircularCoords(radius):
    theta = random.uniform(0.0, 360.0)
    return [
        radius * cos(theta),
        radius * sin(theta)
    ]

def addMazeGroup(beats, offset):
    values = [0.000,0.333,1.000,1.333,2.000,2.333,3.000,3.333]
    for v in values:
        beats.append(v+offset)
        
def getMazeGroupOffsets():
    offsets = []
    curr = 74.000
    while curr < 125.0:
        offsets.append(curr)
        curr += 8.0
    return offsets

def addMazeRacingLines():
    print('addMazeRacingLines')
    offsets = getMazeGroupOffsets()
    beats = []
    for offset in offsets:
        addMazeGroup(beats, offset)
    for sectionOffset in [0.000,328.000]:
        for beat in beats:
            beat = beat + sectionOffset
            for r in range(4):
                anim = AnimationData()
                anim.setThicc(10.0)
                circularCoords = genCircularCoords(9.0)
                x = circularCoords[0]
                y = circularCoords[1] + 2.0
                z = random.uniform(-10.0, 10.0)
                anim.addPos(x, y, z, 0.0)
                anim.addStandardDis()
                duration = 3.0
                startBeat = beat - (duration / 2.0)
                writeWall('mazeRacingLines', startBeat, duration, anim)
            
def addMazeRings():
    print('addMazeRings')
    for sectionOffset in [0.000,328.000]:
        group = [0.000,2.0/6.0,4.0/6.0,5.0/6.0,6.0/6.0,8.0/6.0]
        offsets = []
        offset = 71.0
        while offset < 120.0:
            offsets.append(offset)
            offset += 8.0
        for offset in offsets:
            z = 25.0
            for g in group:
                beat = offset + g + sectionOffset
                duration = 3.0
                start = beat - (duration / 2.0)
                anim = AnimationData()
                anim.setThicc(0.5)
                x = 0.0
                y = 1.5
                anim.addPos(x, y, z, 0.0)
                anim.addStandardDis()
                writeWall('mazeRings', start, duration, anim)
                z -= 3.0
                
def addMazeSideWalls():
    print('addMazeSideWalls')
    colors = [
        [227, 59, 146],
        [209, 61, 162]
    ]
    for sectionOffset in [0.000,328.000]:
        i = 101.333
        while i < 141.000:
            beat = i + sectionOffset
            for r in range(4):
                duration = 0.5
                start = beat - (duration / 2.0)
                anim = AnimationData()
                anim.setThicc(2.0)
                x = 20.0
                if random.uniform(0.0, 1.0) < 0.5:
                    x = -x
                y = random.uniform(0.0, 10.0)
                z = random.uniform(10.0, 60.0)
                anim.addPos(x, y, z, 0.0)
                anim.addStandardDis()
                cidx = random.randrange(0, len(colors))
                c = colors[cidx]
                anim.addCol(c[0], c[1], c[2], 1.0, 0.0)
                writeWall('mazeSideWalls', start, duration, anim)
            i += 1.0

def addMazeTiles():
    print('addMazeTiles')
    colorStart = [136, 181, 109]
    colorEnd = [255, 36, 109]
    for sectionOffset in [0.000,328.000]:
        i = 133.333
        while i <= (141.000 + EPS):
            beat = i + sectionOffset
            for r in range(1):
                duration = 1.0
                start = beat - (duration / 2.0)
                anim = AnimationData()
                anim.setThicc(2.0)
                x = random.uniform(-10.0, 10.0)
                y = 5.0
                z = random.uniform(2.0, 20.0)
                anim.addPos(x, y, z, 0.0)
                anim.addStandardDis()
                prog = (i - 133.333) / (141.000 - 133.333)
                progInv = 1.0 - prog
                color = [
                    progInv * colorStart[0] + prog * colorEnd[0],
                    progInv * colorStart[1] + prog * colorEnd[1],
                    progInv * colorStart[2] + prog * colorEnd[2]
                ]
                anim.addCol(color[0], color[1], color[2], 1.0, 0.0)
                writeWall('mazeTile', start, duration, anim)
            i += (1.0/3.0)
            
# ===== PARTY ANIMATION EFFECTS ===========================================

def addPartyCeilEffect(beat, state):
    colors = [
        [64, 126, 227],
        [71, 115, 186],
        [25, 95, 209]
    ]
    zIndex = state[0] % 4
    for r in range(5):
        duration = 3.0
        start = beat - (duration / 2.0)
        x = r * 5.0 - 10.0
        y = 10.0
        z = -1.0 * zIndex * 5.0 + 30.0
        c = colors[random.randrange(0, len(colors))]
        anim = AnimationData()
        anim.setThicc(2.0)
        anim.addStandardDis()
        anim.addPos(x, y, z, 0.0)
        anim.addCol(c[0], c[1], c[2], 1.0, 0.0)
        writeWall('partyCeil', start, duration, anim)
    state[0] += 1

def addPartyCeilEffects():
    print('addPartyCeilEffects')
    state = [0]
    for sectionOffset in [0.000,328.000]:
        i = 141.333
        while i <= (204.333 + EPS):
            beat = i + sectionOffset
            addPartyCeilEffect(beat, state)
            i += 1.0

def addPartyRayEffect(beat, state):
    side = state[0]
    duration = 1.0
    start = beat - (duration / 2.0)
    x = -10.0
    if side:
        x = -x
    y = 0.0
    z = 15.0
    anim = AnimationData()
    anim.addStandardDis()
    anim.setThicc(10.0)
    anim.addPos(x, y, z, 0.0)
    writeWall('partyRays', start, duration, anim)
    state[0] = not state[0]
            
def addPartyRayEffects():
    print('addPartyRayEffects')
    state = [True]
    for sectionOffset in [0.000,328.000]:
        group = [0.0, 1.0, 2.0]
        i = 145.0
        while i <= (204.0 + EPS):
            for groupOffset in group:
                beat = i + groupOffset + sectionOffset
                addPartyRayEffect(beat, state)
            i += 8.0
            
# ===== CAVERN EFFECTS ==========

def addCavernBarEffect(beat):
    startAngle = 90.0-30.0
    endAngle = 90.0+30.0
    repeat = 25
    step = (endAngle - startAngle) / repeat
    beatStep = 1.0 / repeat
    currentAngle = startAngle
    currentBeat = beat
    for r in range(repeat):
        x = cos(currentAngle) * 40.0
        y = 0.0
        z = sin(currentAngle) * 40.0
        duration = 3.0
        start = currentBeat - (duration / 2.0)
        anim = AnimationData()
        anim.addStandardDis()
        anim.addPos(x, y, z, 0.0)
        writeWall('cavernBar', start, duration, anim)
        currentAngle += step
        currentBeat += beatStep

def addCavernBarEffects():
    print('addCavernBarEffects')
    beats = [205.333,213.333,217.000,221.333,229.333,233.000,237.333,245.333,249.000,253.333,261.333,265.000]
    for beat in beats:
        addCavernBarEffect(beat)

def addCavernRay(beat, state):
    heightIndex = state[0] % 6
    x = 0.0
    y = 0.75 + (0.30 * heightIndex)
    z = 0.0
    anim = AnimationData()
    duration = 1.0
    start = beat - (duration / 2.0)
    anim.addStandardDis()
    anim.addPos(x, y, z, 0.0)
    writeWall('cavernRay', start, duration, anim)
    state[0] += 1

def addCavernRays():
    print('addCavernRays')
    beats = []
    i = 237.333
    while i <= (253.333 + EPS):
        beats.append(i)
        i += 2.0
    i = 254.333
    while i <= (261.333 + EPS):
        beats.append(i)
        i += 1.0
    i = 262.000
    while i <= (268.000 + EPS):
        beats.append(i)
        beats.append(i + 0.333)
        i += 1.0
    state = [0]
    for beat in beats:
        addCavernRay(beat, state)
        
# ===== PALM EFFECTS ======================================================

def addPalmFloor(beat):
    for r in range(2):
        duration = 1.0
        start = beat - (duration / 2.0)
        anim = AnimationData()
        x = random.uniform(-20.0, 20.0)
        y = -1.0
        anim.addStandardDis()
        anim.addPos(x, y, 0.0, 0.0)
        anim.addPos(x, y, 0.0, 0.5)
        anim.addPos(x, y, -10.0, 1.0)
        writeWall('palmFloor', start, duration, anim)

def addPalmFloors():
    print('addPalmFloors')
    beats = []
    i = 269.333
    while i <= (332.333 + EPS):
        beats.append(i)
        i += 1.0
    for beat in beats:
        addPalmFloor(beat)
        
def addPalmParticleEffects():
    print('addPalmParticleEffects')
    beats = []
    i = 270.0
    while i <= (332.0 + EPS):
        beats.append(i)
        i += 1.0
    start = 269.0
    end = 333.0
    duration = end - start
    anim = AnimationData()
    anim.addDis(0.0, 0.0)
    for beat in beats:
        anim.addDis(0.0, b2t(beat - 0.01, start, duration))
        anim.addDis(1.0, b2t(beat, start, duration))
    anim.addDis(0.0, b2t(332.5, start, duration))
    writeWall('palmParticles', start, duration, anim)

# ===== MAIN ==============================================================

exportWalls('walls')
addTiltedBuildings()
addTiltedRays()
# addCityRotatingPatterns()
addMazeRacingLines()
# addMazeRings()
addMazeSideWalls()
# addMazeTiles()
addPartyCeilEffects()
addPartyRayEffects()
addCavernBarEffects()
addCavernRays()
addPalmFloors()
addPalmParticleEffects()
writeSwFile()
bpy.data.scenes[0].frame_start = START_FRAME
bpy.data.scenes[0].frame_end = END_FRAME
print('Export completed.')