# Opens a window with the Basler ACE USB camera feed.
# From this tutorial: https://pythonforthelab.com/blog/getting-started-with-basler-cameras/
import os
import time
from pypylon import pylon

os.system('reset')

tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
for device in devices:
    print(device.GetFriendlyName())
    
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())

camera.Open()
camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
i = 0
print('Starting to acquire')
t0 = time.time()
while camera.IsGrabbing():
    grab = camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
    if grab.GrabSucceeded():
        i += 1
    if i == 100:
        break

print(f'Acquired {i} frames in {time.time()-t0:.0f} seconds')
camera.Close()