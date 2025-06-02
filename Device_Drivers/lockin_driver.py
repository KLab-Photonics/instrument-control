from zhinst.ziPython import ziDAQServer
import time

"""
Application Level Driver For the Lock-In Amplifier"
This gives a simple interface to interact with the Lock-In Amplifier device.

"""
class UHFLI:
    # This is the constructor for the class, it initializes the device and connects to it.
    def __init__(self, device_id="DEV2245", host="localhost", port=8004, api_level=6):
        self.device_id = device_id
        self.daq = ziDAQServer(host, port, api_level)
        self.daq.connectDevice(self.device_id, "USB")
    
    # This function is used to average the voltage readings from the boxcar.
    def average_boxcar_voltage(self, channel, duration=5, interval=0.1):
        readings = []
        samples = int(duration / interval)
        for _ in range(samples):
            mv = self.daq.getDouble(f"/{self.device_id}/boxcars/{channel}/value") * 1000
            readings.append(mv)
            time.sleep(interval)
        return sum(readings) / len(readings)
   
    # This function is used to read the voltage from the boxcar.
    def read_boxcar_voltage(self, channel):
        return self.daq.getDouble(f"/{self.device_id}/boxcars/{channel}/value") * 1000

    # This function turns the boxcar baseline on or off for either channel 1 or 2. (aka 0 or 1)
    def set_boxcar_baseline(self, channel, state):
        if channel == 1:
            self.daq.setInt(f"/{self.device_id}/boxcars/0/baseline", int(state))    #check if its /0/ or /1/ for both channels
        elif channel == 2:
            self.daq.setInt(f"/{self.device_id}/boxcars/1/baseline", int(state))
        
    def disconnect(self):
        self.daq.disconnectDevice(self.device_id)




