import cv2, time
import argparse
import numpy as np
import util_extr as utilE

def getParser():
    #initialize parser
    parser = argparse.ArgumentParser(
            prog = 'ScatterScanner',
            description = 'A scanner for overlapping scatter marks. This is an implemention in Python for the paper ScatterScanner by Yuming Qiu. If you would like to use this package, please cite the original paper.',
            epilog = 'ScatterScanner')
    parser.add_argument('input', metavar='input', type=str, help='specify the path of scatter image file to be handled.')
    parser.add_argument('-m', '--mode', default='less', type=str, help = 'the mode to find the peak. Options: less_equal or less')
    parser.add_argument('--is-auto-kernel', default=True, action=argparse.BooleanOptionalAction, help = 'whether detect the Gaussian kernel aumatically.')
    parser.add_argument('--kernel-side', default=11, type=int, help = 'the sepicified kernel side.')
    parser.add_argument('--kernel-std-fator', default=3, type=int, help = 'the standard factor of the kernel.')
    parser.add_argument('-o', '--output', default=None, type=str, help = 'specify the path of Json formatted output file.')
    parser.add_argument('--is-hsv-s-channel', default=False, action=argparse.BooleanOptionalAction, help = 'auto detect search space.')
    parser.add_argument('-O', '--visualize-outfile', default=None, type=str, help = 'specify the path of visualized image file.')
    parser.add_argument('--is-remove-text-and-axis', default=False, action=argparse.BooleanOptionalAction, help = 'is remove text and axis?')
    parser.add_argument('--remove-kernel-size', default=11, type=int, help = 'kernel size for removing text and axises.')
    parser.add_argument('--out-point-size', default=12, type=int, help = 'output data point size.')
    parser.add_argument('--out-point-color', default='k', type=str, help = 'output data point color.')
    parser.add_argument('--blur-kernel-size', default=7, type=int, help = 'kernel size for Gaussian blur.')
    parser.add_argument('--binarize-method', default='ostu', type=str, help = 'the method to binarize. ostu or threshold')
    parser.add_argument('--binarize-threshold', default=180, type=int, help = 'the threshold value for binarization.')
    args = parser.parse_args()
    assert(args != None)
    print(args)
    return args

def checkStatus(x,y,blurredImg,mode):
    pixels2 = blurredImg[y-1:y+2, x-1:x+2]
    pixels = pixels2.flatten()
    centerP = pixels[4]
    pixels_ = np.delete(pixels, 4)
    #isGreatest = True
    for p in pixels_:
        if mode == 'less_equal':
            if p > centerP:
                return False
        elif mode == 'less':
            if p >= centerP:
                return False
        else:
            print('wrong mode.')
            exit()
    return True

def getLocFromGausRslt(blurredImg, mode):
    h, w = blurredImg.shape
    pts = []
    for y in range(1, h-1):
        for x in range(1, w-1):
            cs = checkStatus(x,y,blurredImg,mode)
            if cs: pts.append({'x':x,'y':y,'m':-1})

    return pts

def getKernelSize(bImg):
    #img = (img<240).astype(np.uint8)
    _, kW, kH, _ = utilE.getConnCompAndSingleMarkSize(bImg)
    return kW, kH 

def scatterScan(bImg, args):
    if args.is_auto_kernel:
        kW, kH = getKernelSize(bImg)
        print('got kernel automatically: ', kW, kH)
        kS = max(kW, kH)
    else:
        kS = args.kernel_side
    if kS%2==0: kS += 1
    kStd = kS/args.kernel_std_fator
    kSt = (kS, kS)
    blurredImg = cv2.GaussianBlur(bImg, kSt, kStd)
    markLoctions = getLocFromGausRslt(blurredImg, args.mode)
    return markLoctions

if __name__=='__main__':
    args = getParser()

    #open the image file and convert to gray image
    print('Handling:', args.input)
    if args.is_hsv_s_channel:
        oriImg = cv2.imread(args.input, cv2.IMREAD_COLOR)
        if len(oriImg.shape)==2:
            img = oriImg
        else:
            hsv = cv2.cvtColor(oriImg, cv2.COLOR_BGR2HSV)
            img = 255-hsv[:,:,1]
    else:
        img = cv2.imread(args.input, cv2.IMREAD_GRAYSCALE)
        oriImg = img

    if img is None:
        print('failed to open image, maybe unsupportable file format.')
        exit()

    #remove text and axis in the input image
    if args.binarize_method=='ostu':
        bImg = utilE.binarizeOtsu(img, args.blur_kernel_size)
    elif args.binarize_method=='threshold':
        bImg = utilE.binarizeThreshold(img, args.binarize_threshold)
    if args.is_remove_text_and_axis:
        bImg = util.removeTextAndAxis(bImg, args.remove_kernel_size)

    #scan
    startT = time.time()
    markLoctions = scatterScan(bImg, args)
    endT = time.time()
    timeCons = endT - startT 
    print('Costed:%d seconds.'%timeCons)

    #save to json file
    if args.output is not None:
        utilE.saveMarks(markLoctions, args.output)

    #save to visulized output image.
    if args.visualize_outfile is not None:
        rgb = cv2.cvtColor(oriImg, cv2.COLOR_BGR2RGB)
        utilE.saveVisualization(markLoctions, rgb, args.visualize_outfile, args.out_point_color, args.out_point_size)
