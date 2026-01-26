# Opens a window with the Basler ACE USB camera feed.
# From this tutorial: https://pythonforthelab.com/blog/getting-started-with-basler-cameras/

from pypylon import pylon

tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
for device in devices:
    print(device.GetFriendlyName())