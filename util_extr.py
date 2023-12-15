import os,cv2
import numpy as np
import util_extr as utile
import pandas.io.json as pjson
from matplotlib import pyplot as plt

def binarizeThreshold(img, val=250, isShow=False):
    threshold = img<val
    threshold = threshold.astype(np.uint8)*255
    return threshold

def binarizeOtsu(img, bk=7, isShow=False):
    blurred = cv2.GaussianBlur(img, (bk, bk), 0)
    threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    return threshold


def mkDirIfNotExist(path):
    path = path.replace('\\','/')
    cPath = path[0:path.rfind('/')]
    if not os.path.exists(cPath):
        print('mkdir or remkdir: %s' % cPath)
        os.makedirs(cPath)

#save to json file
def saveMarks(locs, fp):
    mkDirIfNotExist(fp)
    if fp is None: return
    data = {'locations':locs}
    with open(fp, "w" ) as writer:
        dumpS = pjson.dumps(data, indent=4, double_precision=3)
        writer.write(dumpS)
        print('saved:', fp)

#save to visulized output image.
def saveVisualization(pts, img, savePath, color, size, dpi=160, alpha=0.9):
    sm = ['o','o_','s','s_','D','D_','^','^_','v','v_','6','7','+','*']
    Xs = []
    Ys = []
    mks = {}
    for p in pts:
        if 'm' not in p.keys():
            k = 'o'
        else:
            k = sm[p['m']]
        if k not in mks.keys():
            mks[k] = {'Xs':[], 'Ys':[]}
        mks[k]['Xs'].append(p['x'])
        mks[k]['Ys'].append(p['y'])

    figSize = (img.shape[0]/72, img.shape[1]/72)
    fig = plt.figure(figsize=figSize)
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.imshow(img, cmap='gray')
    for k,v in mks.items():
        ax.scatter(v['Xs'], v['Ys'], s=size, c=color, marker='o', alpha=alpha)
    fig.savefig(savePath, pad_inches=0, bbox_inches='tight', dpi=dpi)
    print('Located marks are saved in: ', savePath)
    plt.close()

def getConnCompAndSingleMarkSize(img, zoom=3):
    assert(img is not None)
    num, labels = cv2.connectedComponents(img)
    labelsDict = {}
    sizeD = {}
    h, w = img.shape
    for y in range(h):
        for x in range(w):
            if not img[y,x]: continue
            k = labels[y][x]
            if k in labelsDict.keys():
                labelsDict[k].append([x, y])
                sizeD[k] += 1
            else:
                labelsDict[k] = [[x, y]]
                sizeD[k] = 1
    lD = {}
    sD = {}
    for k,v in labelsDict.items():
        if len(v) > 20:
            lD[k] = v
            sD[k] = sizeD[k]

    if len(lD)==0 or len(sD)==0:
        return None

    kW, kH, kS= getMeanSizeOfSinglePoints(lD, sD)  #mean

    return lD, kW, kH, kS

def getMeanSizeOfSinglePoints(labelsDict, sizeD, ratioThsld=0.5):
    sortedSizes = dict(sorted(sizeD.items(), key=lambda item: item[1]))
    sS = sortedSizes
    vS = list(sS.values())
    vSpost = vS[1:]
    vSpost.append(vS[-1]*2)
    vS = np.array(vS)
    vSpost = np.array(vSpost)

    diff = vSpost - vS
    diffRatios =  diff/np.sqrt(vSpost)
    
    candKeys = []
    ssKeys = list(sS.keys())
    isBreak = False
    for idx in range(len(diffRatios)): 
        if diffRatios[idx]<ratioThsld:
            k = ssKeys[idx]
            candKeys.append(k)
            isBreak = True
        elif isBreak:
            break
        else:
            continue
    if len(candKeys)==0:
        k = ssKeys[idx]
        candKeys.append(k)

    assert(len(candKeys)>0)
    kWHs = []
    Ss = []
    assert(len(candKeys)>0)
    for k in candKeys: 
        kW, kH = getSizeOfCompnt(labelsDict[k])
        cKey = 'n%d'%len(labelsDict[k])
        kWHs.append([kW, kH])
        Ss.append(len(labelsDict[k]))
    kWHs = np.array(kWHs)
    kW, kH = np.round(kWHs.mean(axis=0)).astype(np.uint16)
    kS = np.array(Ss).mean()

    return kW, kH, kS

def getSizeOfCompnt(v):
    v = np.array(v)
    if len(v.shape)<=1: return None
    t = min(v[:,1])
    b = max(v[:,1])
    l = min(v[:,0])
    r = max(v[:,0])
    w = r-l+1
    h = b-t+1
    return w,h
