#from matplotlib import pyplot as plt
#import cv2 as cv

import numpy as np

def MRI_Area(img, threshold_var = (-20, 20) , shape = None):
    if img.shape == (0,): 
        return np.zeros(img.shape), ((),())
    if type(shape)==type(None): 
        shape = img.shape
        
    
    img_t = img.copy().astype(float)
    down_th, up_th = threshold_var
    img_m = img.copy().astype(float)
    img2 = img.copy().astype(float)
    
    # Computes gradient
    gradx, grady = np.gradient(img)

    length=np.zeros(gradx.shape)
    for i in range(gradx.shape[0]):
        for j in range(gradx.shape[1]):
            length[i,j] = np.linalg.norm([gradx[i,j],grady[i,j]])
    # plt.imshow(length)
   
    # Detects the pixel value of the borders and thresholds.
    mean=length.mean()
    length[length>mean] = 255; length[length<mean]=0
    img_m[length==0] = np.NaN
    threshold = np.nanmean(img_m)
    img_t[img_t<threshold + up_th] = int(0); img_t[img_t>threshold + up_th] = int(1)
    img2[img2<threshold + down_th] = int(0); img2[img2>threshold + down_th] = int(1)
    
    dif = np.bitwise_xor(img_t.astype("uint8"), img2.astype("uint8"))
    
    Areas = (np.sum(img_t)/shape[0]/shape[1]*100, 
             np.abs(np.sum(dif)/shape[0]/shape[1]*100),
             np.abs(np.sum(dif)/img.shape[0]/img.shape[1]*100))
    return dif * 255 , Areas
