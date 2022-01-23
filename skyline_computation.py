import test_NN
import shortest_path
from learned_filters import learnedFilters as LRFS

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import scipy.io as sio
import json
import time
from tqdm import tqdm
from queue import PriorityQueue
from numpyencoder import NumpyEncoder

def compute_skyline(img_filename):

	img_name = img_filename
	img = cv2.imread(os.getcwd() + "/uploads/" + img_filename)
	print(img)
	## resizing the img
	resized = False
	height = int(img.shape[0])
	width = int(img.shape[1])
	while height*width > 10**6:
		height = int(height/2)
		width = int(width/2)
		resized = True
	new_dim = (width, height)
	img = cv2.resize(img, new_dim, interpolation = cv2.INTER_AREA)
	if resized:
		print('Image successfully resized')
	else:
		print('Image did not require resizing')

	## parameters
	srBins = 6
	coBins = 3
	orBins = 16
	filter_size = 7

	fileNameFilters = './filterBank/Web_filterSz_7_filters.npy'
	allFilters = np.load(fileNameFilters)

	half_filter_size = int(filter_size/2.0)
	image = cv2.copyMakeBorder(img, half_filter_size, half_filter_size, half_filter_size, half_filter_size, cv2.BORDER_REFLECT)
	image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	canny_mask = cv2.Canny(np.array(image_gray, dtype=np.uint8), 50.0, 220.0)
	lrfObj = LRFS(image, image_gray, canny_mask, coBins, srBins, orBins, filter_size)
	mask = lrfObj.generateOutput(allFilters)

	strImage = lrfObj.strength.copy()
	strImage = test_NN.normalize(strImage)

	mask[mask < 0.0] = 0.0
	mask[mask > 255.0] = 255.0

	edgeness = test_NN.generateDenseMap(mask, strImage)
	height, width, data = image.shape
	rows, cols = edgeness.shape
	m = 50
	L = [np.argpartition(edgeness[:, j], m)[:m] for j in range(cols)]
	L = np.array(L).transpose()
	print('Edgemap successfully computed')

	## finding skyline (shortest path)
	delta = 1
	default_weight = 5
	DX = [i for i in range(-delta, delta+1)]

	distances = np.full((rows, cols), np.inf, dtype = float)
	predecessor = [[(0, 0) for j in range(cols)] for i in range(rows)]
	visited = np.full((rows, cols), False)
	pq = PriorityQueue()

	for i in range(rows):
	    distances[i, 0] = default_weight
	    if i in L[:,0]:
	        distances[i, 0] = edgeness[i, 0]
	    pq.put((distances[i, 0], (i, 0)))

	while not pq.empty():
	    (distance, current) = pq.get()
	    if visited[current]: continue
	    visited[current] = True
	    for dx in DX:
	        next_node = (current[0] + dx, current[1] + 1)
	        if not shortest_path.isvalid(next_node, (rows, cols)): continue
	        previous_distance = distances[next_node]
	        weight = default_weight
	        if current[0] in L[:,current[1]]:
	            weight = edgeness[current]
	        new_distance = distance + weight
	        if(new_distance < previous_distance):
	            predecessor[next_node[0]][next_node[1]] = current
	            distances[next_node] = new_distance
	            pq.put((new_distance, next_node))

	skyline_right_row = np.argmin(distances[:, cols-1])
	current = (skyline_right_row, cols-1)
	skyline = [current[0]]

	while current[1] != 0:
	    skyline.append(current[0])
	    current = predecessor[current[0]][current[1]]

	for i in range(len(skyline)):
		skyline[i] =  height - skyline[i]
	print('Skyline successfully computed')

	## saving skyline
	skyline = skyline[::-1]
	#with open(os.getcwd() + '/skylines/' + img_name + ".json", 'w') as file:
	#    json.dump([height] + skyline, file, indent=4, cls=NumpyEncoder)
	#print('Skyline successfully saved')

	## drawing skyline
	skyline[0] =  height - skyline[0]
	image[skyline[0], 0] = [0, 0, 0]
	for i in range(1, len(skyline) - 1):
		skyline[i] =  height - skyline[i]
		image[skyline[i], i] = [0, 0, 0]
		image[skyline[i]-1, i] = [0, 0, 0]
		image[skyline[i]+1, i] = [0, 0, 0]
		image[skyline[i], i-1] = [0, 0, 0]
		image[skyline[i], i+1] = [0, 0, 0]
	skyline[len(skyline)-1] =  height - skyline[len(skyline)-1]
	image[skyline[len(skyline)-1], len(skyline)-1] = [0, 0, 0]
	print('Skyline successfully drawn')

	## saving skyline on img
	image_skyline_filename = img_name + "-skyline.png"
	cv2.imwrite(os.getcwd() + '/uploads/' + image_skyline_filename, image)
	print('Image with skyline successfully saved')

	return image_skyline_filename

#compute_skyline("/uploads/" + image_filename)