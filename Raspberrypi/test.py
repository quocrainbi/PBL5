from imutils.video import VideoStream

camera = VideoStream(src=0).start()
while True:
    cap = camera.read()