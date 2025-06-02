import serial
import time

"Application Level Driver For the DL225 Stage"
"Provides a simple interface to interact with the DL225 stage device."

class NewPort_Delay_Stage_225:
   
    # This is the constructor for the class, it initializes the serial connection to the stage.

    # The default port is set to 'COM5' and baud rate to 9600, be sure to change the COM port to the one the stage is connected to.
    # You can also change the baud rate if needed, but 9600 is the standard for the DL225 so it should work fine without any adjustments.
    
    def __init__(self, port='COM5', baud=9600):
        self.ser = serial.Serial(port=port, baudrate=baud, bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        time.sleep(2)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.initialize_stage()

    # This function sends a command to the stage and waits for a response.
    def send_command(self, cmd):
        full = cmd + '\r\n'
        print(f">>> {cmd}")
        self.ser.write(full.encode('ascii'))
        self.ser.flush()
        time.sleep(0.1)

    # This function reads the response from the stage within a specified timeout period.
    def read_response(self, timeout=2.0):
        self.ser.timeout = 0.1
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.ser.readline().decode('ascii', errors='ignore').strip()
            if line:
                print(f"<<< {line}")
                return line
        return None
    
    # This function initializes the stage with default settings (You can modify these settings as needed).
    def initialize_stage(self):
        self.send_command("1AC100")  # Acceleration (set to 100 mm/s^2) as the LabVIEW code had
        self.read_response()
        self.send_command("1VA0.02")  # Velocity (set to 0.02 mm/s) 
        self.read_response()
        self.send_command("1MO")      # Motor ON
        self.read_response()

    # This function moves the stage to a specified position.
    def move_to(self, pos):
        self.send_command(f"1PA{pos}") # Move to position defined in the send_command function
        self.read_response()
        self.send_command("1WS")
        self.read_response()


    # This function assists with quick sweep for reading the max value 
    def quick_sweep(self, start, stop, coarse_step):
        print("Starting Quick Sweep Scan")
        self.send_command("1AC100")  # Temporary high acceleration (check labVIEW code for value)
        self.read_response()
        self.send_command("1VA1")     # Temporary high velocity (check labVIEW code for value)
        self.read_response()
        positions = []
        pos = start
        while pos <= stop:
            self.move_to(round(pos, 2)) 
            positions.append(round(pos, 2))
            time.sleep(0.2) 
            pos += coarse_step
        self.send_command("1AC100")  
        self.read_response()
        self.send_command("1VA0.02")
        self.read_response()
        return positions
    
    def home_stage(self):
        self.send_command("1PA0")
        self.read_response()
        self.send_command("1MO")
        self.read_response()
        self.send_command("1WS")
        self.read_response()
        

    # This function closes the serial connection to the stage.
    def close(self):
        self.ser.close()