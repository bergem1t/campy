"""
"""
import sys
import time
import logging
import numpy as np
import matplotlib as mpl
mpl.use('Qt5Agg') # disregard qtapp warning...
import matplotlib.pyplot as plt
plt.ion()

def DrawFigure(num):
	mpl.rcParams['toolbar'] = 'None' 

    figure = plt.figure(num)
    #ax = plt.axes([0,0,1,1], frameon=False)
    if len(size)==2:
        max_size = max(size)
        xpos = (1-size[0]/max_size)/2
        ypos = (1-size[1]/max_size)/2
        ax = plt.axes([xpos,ypos,size[0]/max_size,size[1]/max_size], frameon=False)
    else:
        ax = plt.axes([0,0,1,1], frameon=False)
        

    plt.axis('off')
    plt.autoscale(tight=True)
    #plt.ion()

    imageWindow = ax.imshow(np.zeros((1,1), dtype='uint8'),
        cmap='gray',vmin=0,vmax=255,interpolation='none')

    figure.canvas.draw()
    plt.show(block=False)

    return figure, imageWindow

def DisplayFrames(cam_params, dispQueue):
	if not (sys.platform=='win32' and cam_params['cameraMake'] == 'basler'):
		figure, imageWindow = DrawFigure(cam_params["n_cam"]+1)
		while(True):
			try:
				if dispQueue:
					img = dispQueue.popleft()
					try:
						imageWindow.set_data(img)
						figure.canvas.draw()
						figure.canvas.flush_events()
					except Exception as e:
						logging.error('Caught exception: {}'.format(e))
				else:
					time.sleep(0.01)
			except KeyboardInterrupt:
				break
		plt.close(figure)
