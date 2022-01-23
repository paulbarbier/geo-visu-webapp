import numpy as np
import matplotlib.pyplot as plt
import cv2
from os import listdir
import os
import scipy.io as sio
from learned_filters import learnedFilters as LRFS
import time
from tqdm import tqdm

def listdirs(folder):
    if os.path.exists(folder):
         return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    else:
         return []

def normalize(image):
    minVal = np.min(image)
    
    if minVal < 0.0:
        image += np.abs(minVal)
    
    maxVal = np.max(image)
    image /= maxVal
    
    return image


def processSingleImage(imgName, fileName, allFilters, dirForImageOutput, dirForMatFiles, srBins, coBins, orBins, filter_size):
    half_filter_size = int(filter_size/2.0)
    image_org = cv2.imread(fileName)
    image = cv2.copyMakeBorder(image_org, half_filter_size, half_filter_size, half_filter_size, half_filter_size, cv2.BORDER_REFLECT)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    canny_mask = cv2.Canny(np.array(image_gray, dtype=np.uint8), 50.0, 220.0)
    print('ok')
    lrfObj = LRFS(image, image_gray, canny_mask, coBins, srBins, orBins, filter_size)
    mask = lrfObj.generateOutput(allFilters)
        
    # gradient strength -- computed as part of ST
    strImage = lrfObj.strength.copy()
    strImage = normalize(strImage)
    
    mask[mask < 0.0] = 0.0
    mask[mask > 255.0] = 255.0
    
    # saving the original size DCSI on which need to run shortest path
    maskDCSI = generateDenseMap(mask, strImage)
    height, width = maskDCSI.shape
    maskDCSI_orgSz = maskDCSI[half_filter_size:width - half_filter_size, half_filter_size:height - half_filter_size].copy()
    maskDCSI_orgSz = maskDCSI.copy()
    sio.savemat(dirForMatFiles, {'maskDCSI_orgSz':maskDCSI_orgSz})
    

def runInference(allFilters, dirForImageInput, dirForImageOutput, dirForMatFiles, srBins, coBins, orBins, filter_size, nbr_img):
    totalTime = 0.0
    numImages = nbr_img  
    dir_names = listdirs(dirForImageInput)
    for imgIndex in tqdm(range(1,numImages+1)):
        print(imgIndex)
        print(dir_names[imgIndex])   
        if os.path.isfile(dirForImageInput + dir_names[imgIndex] + '/resized_photo.jpg'):
            fileName = dirForImageInput + dir_names[imgIndex] + '/resized_photo.jpg'
        else:
            fileName = dirForImageInput + dir_names[imgIndex] + '/resized_photo.jpeg'
        print(fileName)   
        ##if imgIndex < 10:
        ##    fileName = './data/mopsi/images/R_GImag000' + str(imgIndex) + '.bmp'
        ##else:
        ##    fileName = './data/mopsi/images/R_GImag00' + str(imgIndex) + '.bmp'
        start = time.time()
        processSingleImage(imgIndex, fileName, allFilters, dirForImageOutput, dirForMatFiles, srBins, coBins, orBins, filter_size)
        end = time.time()
        totalTime += (end - start)
            
    print('Total Time: ', totalTime)
    print('Average Time: ', totalTime/numImages)


def generateDenseMap(image, srImage):
    height, width = image.shape
    hMap = 255.0 * np.zeros(shape=(height, width), dtype=np.float32)
    
    for i in range(height):
        for j in range(width):
            tempVal = 0.5 * (1.0 - image[i, j] / 255.0) + 0.5 * (1.0 - srImage[i, j])
            hMap[i, j] = tempVal
                    
    return hMap


def generateHeatMap(image):
    height, width = image.shape
    hMap = 255.0 * np.zeros(shape=(height, width, 3), dtype=np.float32)
    
    for i in range(height):
        for j in range(width):
            if image[i, j] > 0.0:
                tempVal = image[i, j] / 255.0 - 0.5
                if tempVal <= 0.0:
                    hMap[i, j, 0] = np.abs(tempVal + 0.5) * 510.0
                    hMap[i, j, 1] = 0.0
                    hMap[i, j, 2] = 0.0                    
                else:
                    hMap[i, j, 0] = 0.0
                    hMap[i, j, 1] = 0.0
                    hMap[i, j, 2] = np.abs(tempVal) * 510.0
    
    return hMap


def main():
    srBins = 6
    coBins = 3
    orBins = 16
    filter_size = 7
    nbr_img = 9

    fileNameFilters = './filterBank/Web_filterSz_' + str(filter_size) + '_filters.npy'
    allFilters = np.load(fileNameFilters)
    
    dirForImageInput = '/Users/alexandre/Documents/Travail/Ecole/2A/Projets/MOPSI:TDLOG/geoPose3K_final_publish/'
    dirForImageOutput = './output/database/'
    dirForMatFiles = './output/database_mat/'
    
    if not os.path.exists(dirForImageInput):
        os.makedirs(dirForImageInput)
    if not os.path.exists(dirForImageOutput):
        os.makedirs(dirForImageOutput)
    if not os.path.exists(dirForMatFiles):
        os.makedirs(dirForMatFiles)
    
    runInference(allFilters, dirForImageInput, dirForImageOutput, dirForMatFiles, srBins, coBins, orBins, filter_size, nbr_img)


if __name__ == '__main__':
    main()
