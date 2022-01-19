import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import json
import cv2
import os

from queue import PriorityQueue
from numpyencoder import NumpyEncoder
from tqdm import tqdm

def isvalid(p, shape):
    if p[0] < 0 or p[0] >= shape[0]:
        return False
    if p[1] < 0 or p[1] >= shape[1]:
        return False
    return True

def listdirs(folder):
    if os.path.exists(folder):
         return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    else:
         return []


def main():
	dir_names = listdirs('/Users/alexandre/Documents/Travail/Ecole/2A/Projets/MOPSI:TDLOG/geoPose3K_final_publish')

	for n in tqdm(range(1, 10)):

		image_filename = '/Users/alexandre/Documents/Travail/Ecole/2A/Projets/MOPSI:TDLOG/skyline_detection/output/database/' + str(n) + '_0.png'
		print(image_filename)
		edgeness_filename = '/Users/alexandre/Documents/Travail/Ecole/2A/Projets/MOPSI:TDLOG/skyline_detection/output/database_mat/' + str(n) + '.mat'

		image = cv2.imread(image_filename)
		height, width, data = image.shape
		edgeness = sio.loadmat(edgeness_filename)["maskDCSI_orgSz"]
		rows, cols = edgeness.shape
		m = 50
		L = [np.argpartition(edgeness[:, j], m)[:m] for j in range(cols)]
		L = np.array(L).transpose()

		delta = 2
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
		        if not isvalid(next_node, (rows, cols)): continue
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

		skyline = skyline[::-1]
		with open("data_" + str(n) + ".json", 'w') as file:
		    json.dump([height] + skyline, file, indent=4, cls=NumpyEncoder)

		for i in range(len(skyline)):
			skyline[i] =  height - skyline[i]
			image[skyline[i], i] = [0, 0, 0]

		cv2.imwrite("/Users/alexandre/Documents/Travail/Ecole/2A/Projets/MOPSI:TDLOG/skyline_detection/output/database_skyline/skyline_" + str(n) + ".png", image)


if __name__ == '__main__':
    main()