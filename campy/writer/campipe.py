"""
"""
from imageio_ffmpeg import write_frames
import os
import time
import logging
import sys

def OpenWriter(cam_params):
	folder_name = os.path.join(cam_params["videoFolder"], cam_params["cameraName"])
	file_name = cam_params["videoFilename"]
	full_file_name = os.path.join(folder_name, file_name)

	if not os.path.isdir(folder_name):
		os.makedirs(folder_name)
		print('Made directory {}.'.format(folder_name))
	
	# Load defaults
	pix_fmt_out = cam_params["pixelFormatOutput"]
	codec = cam_params["codec"]
	gpu_params = []

	# CPU compression
	if cam_params["gpuID"] == -1:
		print('Opened: {} using CPU to compress the stream.'.format(full_file_name))
		if pix_fmt_out == 'rgb0':
			pix_fmt_out = 'yuv420p'
		if cam_params["codec"] == 'h264':
			codec = 'libx264'
		elif cam_params["codec"] == 'h265':
			codec = 'libx265'
		gpu_params = ['-r:v', str(cam_params["frameRate"]),
					'-preset', 'fast',
					'-tune', 'fastdecode',
					'-crf', cam_params["quality"],
					'-bufsize', '20M',
					'-maxrate', '10M',
					'-bf:v', '4',
					'-vsync', '0',] # before was 0, which would keep timestamps, but -r:v ignores timestamps again ... alternative not -r bur -framrate and here 0 ?? (we probably do not want 1 or 2 since it might result in frame drops or duplications)

	# GPU compression
	else:
		print('Opened: {} using GPU {} to compress the stream.'.format(full_file_name, cam_params["gpuID"]))
		if cam_params["gpuMake"] == 'nvidia':
			if cam_params["codec"] == 'h264':
				codec = 'h264_nvenc'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_nvenc'
			gpu_params = ['-r:v', str(cam_params["frameRate"]), # important to play nice with vsync '0'
						'-preset', 'fast', # set to 'fast', 'llhp', or 'llhq' for h264 or hevc
						'-qp', cam_params["quality"],
						'-bf:v', '0',
						'-vsync', '0', 
						'-2pass', '0',
						'-gpu', str(cam_params["gpuID"]),]
		elif cam_params["gpuMake"] == 'amd':
			if pix_fmt_out == 'rgb0':
				pix_fmt_out = 'yuv420p'
			if cam_params["codec"] == 'h264':
				codec = 'h264_amf'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_amf'
			gpu_params = ['-r:v', str(cam_params["frameRate"]),
						'-usage', 'lowlatency',
						'-rc', 'cqp', # constant quantization parameter
						'-qp_i', cam_params["quality"],
						'-qp_p', cam_params["quality"],
						'-qp_b', cam_params["quality"],
						'-bf:v', '0',
						'-hwaccel', 'auto',
						'-hwaccel_device', str(cam_params["gpuID"]),]
		elif cam_params["gpuMake"] == 'intel':
			if pix_fmt_out == 'rgb0':
				pix_fmt_out = 'nv12'
			if cam_params["codec"] == 'h264':
				codec = 'h264_qsv'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_qsv'
			gpu_params = ['-r:v', str(cam_params["frameRate"]),
						'-bf:v', '0',]

	# Initialize writer object (imageio-ffmpeg)
	while(True):
		try:
			try:
				writer = write_frames(
					full_file_name,
					[cam_params["frameWidth"], cam_params["frameHeight"]], # size [W,H]
					fps=cam_params["frameRate"],
					quality=None,
					codec=codec,
					pix_fmt_in=cam_params["pixelFormatInput"], # 'bayer_bggr8', 'gray', 'rgb24', 'bgr0', 'yuv420p'
					pix_fmt_out=pix_fmt_out,
					bitrate=None,
					ffmpeg_log_level=cam_params["ffmpegLogLevel"], # 'warning', 'quiet', 'info'
					input_params=['-an'], # '-an' no audio
					output_params=gpu_params,
					)
				writer.send(None) # Initialize the generator
				break
			except Exception as e:
				logging.error('Caught exception: {}'.format(e))
				time.sleep(0.1)

		except KeyboardInterrupt:
			break

	return writer

def WriteFrames(cam_params, writeQueue, stopQueue):
	# Start ffmpeg video writer 
	writer = OpenWriter(cam_params)
	message = ''

	# Write until interrupted or stop message received
	while(True):
		try:
			if writeQueue:
				message = writeQueue.popleft()
				if not isinstance(message, str):
					writer.send(message)
				elif message=='STOP':
					break
			else:
				time.sleep(0.001)
		except KeyboardInterrupt:
			stopQueue.append('STOP')

	# Closing up...
	print('Closing video writer for {}. Please wait...'.format(cam_params["cameraName"]))
	time.sleep(1)
	writer.close()
