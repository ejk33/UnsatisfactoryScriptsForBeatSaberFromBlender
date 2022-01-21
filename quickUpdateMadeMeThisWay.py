import bpy
import random
import shutil

templatePath = bpy.path.abspath('//../swtemplate')
swPath = bpy.path.abspath('//../ExpertPlusStandard_ScuffedWalls.sw')
expertPath = bpy.path.abspath('//../ExpertStandard_ScuffedWalls.sw')
hardPath = bpy.path.abspath('//../HardStandard_ScuffedWalls.sw')
normalPath = bpy.path.abspath('//../NormalStandard_ScuffedWalls.sw')
easyPath = bpy.path.abspath('//../EasyStandard_ScuffedWalls.sw')
contentPath = bpy.path.abspath('//../swcontent.sw')

templateFile = open(templatePath, 'r')
templateContent = templateFile.read()
templateFile.close()

contentFile = open(contentPath, 'r')
contentContent = contentFile.read()
contentFile.close()

def wline(f, l):
    f.write(l)
    f.write('\n')

f = open(swPath, 'w')
f.write(templateContent.replace('#INCLUDE#', contentContent))

def write(l):
    wline(f, l)

# ===== Triplets =======================================================

TRIPLET_COLORS = [
  [122, 230, 212],
  [122, 230, 124],
  [214, 230, 122]
]

def addTriplet(f, beat):
    detailedLocs = [beat, beat + 0.5, beat + 1.0]
    for detailedLoc in detailedLocs:
        startBeat = beat - 1.0
        randX = random.uniform(-3.0,3.0)
        randY = random.uniform(-1.0,1.0)
        c = TRIPLET_COLORS[random.randrange(len(TRIPLET_COLORS))]
        wline(f, '{}:ModelToWall'.format(startBeat))
        wline(f, '  Path:blend/triplet.dae')
        wline(f, '  Duration:2')
        wline(f, '  Interactable:false')
        wline(f, '  Fake:true')
        wline(f, '  animateposition:[{},{},0,0]'.format(randX, randY))
        wline(f, '  animatedissolve:[0,0],[0,0.499],[1,0.500],[0,1.0]')
        write('  animateColor:[{},{},{},1,0]'.format(
            c[0] / 255.0,
            c[1] / 255.0,
            c[2] / 255.0
        ))
    #wline(f, '  animateRotation:[0,0,0,0.33],[0,0,100,0.50],[0,0,0,0.66]')

tripletLocations = [
    200,
    202,
    208,
    210,
    216,
    218,
    224,
    226,
    392,
    394,
    400,
    402,
    408,
    410,
    416,
    418,
    424,
    426,
    432,
    434,
    440,
    442,
    448,
    450,
    456,
    458,
    464,
    466,
    472,
    474,
    480,
    482,
]
for location in tripletLocations:
    addTriplet(f, location)
    
# ===== DOUBLETS =====

DOUBLET_COLORS = [
  [0, 119, 255],
  [255, 0, 225],
  [255, 183, 0]
]

def addDoubletDown(beat):
    for i in [0, 1, 2, 3]:
        x = random.uniform(-40.0, 40.0)
        y = random.uniform(-10.0, 10.0)
        start = beat - 1.0
        c = DOUBLET_COLORS[random.randrange(len(DOUBLET_COLORS))]
        write('{}:ModelToWall'.format(start))
        write('  Path:blend/doublets.dae')
        write('  Duration:2')
        write('  Interactable:false')
        write('  Fake:true')
        write('  animateDissolve:[0,0],[0,0.499],[1,0.500],[0,1.0]')
        write('  animatePosition:[{},{},0,0]'.format(x, y))
        write('  animateColor:[{},{},{},1,0]'.format(
            c[0] / 255.0,
            c[1] / 255.0,
            c[2] / 255.0
        ))

def addDoubletUp(beat):
    for i in [0, 1, 2, 3]:
        x = random.uniform(-40.0, 40.0)
        y = random.uniform(-10.0, 10.0)
        start = beat - 1.0
        c = DOUBLET_COLORS[random.randrange(len(DOUBLET_COLORS))]
        write('{}:ModelToWall'.format(start))
        write('  Path:blend/doubletsUp.dae')
        write('  Duration:2')
        write('  Interactable:false')
        write('  Fake:true')
        write('  animateDissolve:[0,0],[0,0.499],[1,0.500],[0,1.0]')
        write('  animatePosition:[{},{},0,0]'.format(x, y))
        write('  animateColor:[{},{},{},1,0]'.format(
            c[0] / 255.0,
            c[1] / 255.0,
            c[2] / 255.0
        ))
    
DOUBLET_UP_LOCATIONS = [
  136,
  137,
  144,
  145,
  152,
  153,
  160,
  161,
  184,
  185,
  192,
  193,
  328,
  329,
  336,
  337,
  344,
  345,
  352,
  353,
  376,
  377,
  384,
  385
]

DOUBLET_DOWN_LOCATIONS = [
  140,
  141,
  148,
  149,
  156,
  157,
  164,
  165,
  188,
  189,
  196,
  197,
  332,
  333,
  340,
  341,
  348,
  349,
  356,
  357,
  380,
  381,
  388,
  389
]

for l in DOUBLET_UP_LOCATIONS:
    addDoubletUp(l)
    
for l in DOUBLET_DOWN_LOCATIONS:
    addDoubletDown(l)
    
# ===== DOWNBEATS =====

DOUBLET_COLORS = [
  [207, 180, 165],
  [176, 165, 207],
  [207, 165, 197]
]

DOWNBEAT_LOCATIONS = [
  166,
  171,
  174,
  187.5,
  179,
  182,
  187,
  190,
  194,
  195,
  358,
  363,
  366,
  370.5,
  371,
  374,
  379,
  382,
  386,
  387
]

def addDownbeat(beat):
    for i in [0,1]:
        x = random.uniform(-20.0, 20.0)
        y = random.uniform(-10.0, 10.0)
        start = beat - 2.0
        c = DOUBLET_COLORS[random.randrange(len(DOUBLET_COLORS))]
        write('{}:ModelToWall'.format(start))
        write('  Path:blend/downbeat.dae')
        write('  Duration:4')
        write('  Interactable:false')
        write('  Fake:true')
        write('  animateDissolve:[0,0],[0,0.499],[1,0.500],[0,1.0]')
        write('  animatePosition:[{},{},0,0]'.format(x, y))
        write('  animateColor:[{},{},{},1,0]'.format(
            c[0] / 255.0,
            c[1] / 255.0,
            c[2] / 255.0
        ))
    
for loc in DOWNBEAT_LOCATIONS:
    addDownbeat(loc)
    
# ===== LIGHTING ==========================================================

LIGHTING_INTERPOLATION_STEPS = 64.0

def appendLight(beat, color):
    write('{}:Event'.format(beat))
    write('  type:0')
    write('  value:1')
    write('{}:Event'.format(beat))
    write('  type:1')
    write('  value:1')
    write('{}:Event'.format(beat))
    write('  type:2')
    write('  value:1')
    write('{}:Event'.format(beat))
    write('  type:3')
    write('  value:1')
    write('{}:Event'.format(beat))
    write('  type:4')
    write('  value:1')
    write('{}:AppendToAllEventsBetween'.format(beat))
    write('  appendTechnique:1')
    write('  toBeat:{}'.format(beat + 0.01))
    write('  color:[{},{},{},{}]'.format(color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0))

def interpolateColors(interpolationValue, colorA, colorB):
    opposite = 1.0 - interpolationValue
    return [
        opposite * colorA[0] + interpolationValue * colorB[0],
        opposite * colorA[1] + interpolationValue * colorB[1],
        opposite * colorA[2] + interpolationValue * colorB[2],
        opposite * colorA[3] + interpolationValue * colorB[3],
    ]

def generateLighting(lightingInformation):
    lastBeat = 0.0
    lastColor = [0.0, 0.0, 0.0, 1.0]
    for lightingItem in lightingInformation:
        currentBeat = lightingItem[0]
        color = lightingItem[1]
        
        if currentBeat - lastBeat < 2.0:
            # Too close to interpolate
            appendLight(currentBeat, color)
        else:
            interpolationRange = (currentBeat - lastBeat)
            interpolationStep = interpolationRange / LIGHTING_INTERPOLATION_STEPS
            beat = lastBeat + interpolationStep
            while (beat < currentBeat):
                interpolationValue = (beat - lastBeat) / interpolationRange
                appendLight(beat, interpolateColors(interpolationValue, lastColor, color))
                beat += interpolationStep
            appendLight(currentBeat, color)
        
        lastBeat = currentBeat
        lastColor = color
        
lightingInformation = [
    [0, [26, 36, 54, 255]], # dark blue - intro
    [39, [179, 129, 199, 255]], # pale pink - bamboo forest
    [102, [255, 253, 227, 255]], # bright yellow - city
    [136, [129, 184, 136, 255]], # emerald - mountains
    [198, [161, 84, 255, 255]], # lightshow
    [231, [179, 129, 199, 255]], # pale pink - bamboo forest
    [293, [255, 253, 227, 255]], # bright yellow - city
    [328, [129, 184, 136, 255]], # emerald - mountains
    [390, [161, 84, 255, 255]], # lightshow
    [422, [70, 169, 212, 255]], # cyan - river
    [485, [0, 0, 0, 255]], # black - outro
]

for tripletLocation in tripletLocations:
    locA = tripletLocation         # ON
    locB = tripletLocation + 0.5 # OFF
    locC = tripletLocation + 1.0 # ON
    lightingInformation.append([locA, [176, 0, 224, 255]])
    lightingInformation.append([locB, [255, 255, 255, 255]])
    lightingInformation.append([locC, [0, 0, 0, 255]])

lightingInformation = sorted(lightingInformation, key=lambda x: x[0], reverse=False)

generateLighting(lightingInformation)

# ===== outro text

write('484:ModelToWall')
write('  Path:blend/text.dae')
write('  Duration:50')
write('  Interactable:false')
write('  Fake:true')
write('485:ModelToWall')
write('  Path:blend/text2.dae')
write('  Duration:50')
write('  Interactable:false')
write('  Fake:true')

f.close()

# ===== sync =====

def writeOtherDiffFile(path, difficultyNameSource):
    f = open(swPath, 'r')
    contents = f.read()
    f.close()
    
    contents = contents.replace('ExpertPlusStandard_Old.dat', difficultyNameSource)
    
    o = open(path, 'w')
    o.write(contents)
    o.close()
    
writeOtherDiffFile(expertPath, 'ExpertStandard_Old.dat')
writeOtherDiffFile(hardPath, 'HardStandard_Old.dat')
writeOtherDiffFile(normalPath, 'NormalStandard_Old.dat')
writeOtherDiffFile(easyPath, 'EasyStandard_Old.dat')

print('Done.')
