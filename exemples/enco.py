"""testing status:
- [X] verified working
"""

from smbus2 import SMBus
import time

# Define I2C bus number (e.g., 1 for Raspberry Pi 2/3/4)
I2C_BUS_NUMBER = 1
# Define the I2C address of your slave device (e.g., from i2cdetect)
DEVICE_ADDRESS = 0x06   # Example: MT6701 address
# Define the register address within the device to read/write
REGISTER_DIR = 0x29 #DIR = 1 for CW (bit 1)
REGISTER_ANGLE_MSB = 0x03   # Angle<13:6>
REGISTER_ANGLE_LSB = 0x04   # Angle<5:0>


#Ce type de filtre ne fonctionne pas avec les angles (passage de 360 à 0 !!!!)
filtered_angle = 0
alpha = 0.1 # must be between 0 and 1 inclusive


def low_pass_filter(prev_value, new_value):
    return alpha * prev_value + (1 - alpha) * new_value


try:
    while True:
        # Open the I2C bus
        with SMBus(I2C_BUS_NUMBER) as bus:
        
            # Read DIR REGISTER
            bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_DIR)
            #Set direction clockwise
            bytes1 = bytes1 |  0b00000010   #DIR = 1 for CW (bit 1)
            # Write DIR REGISTER
            bus.write_byte_data(DEVICE_ADDRESS, REGISTER_DIR, bytes1)
                
            #Read Angle MSB Register (Angle<13:6>) ... Bit7 to Bit0
            bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_MSB)
            #print(f"Read byte from register {hex(REGISTER_ADDRESS_MSB)}: {hex(bytes1)}")
        
            #Read Angle LSB Register (Angle<5:0>) ... Bit7 to Bit2
            bytes2 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_LSB)
            #print(f"Read byte from register {hex(REGISTER_ADDRESS_LSB)}: {hex(bytes2)}")
        
            # Concatenate bytes2 with bytes1
            angle_int = bytes2 >> 2
            angle_int = (bytes1 << 6) | angle_int 
        
            # Compute angle in degrees (14 bits)
            new_angle = angle_int * (360.0/16384.0)

            print(f"Angle is: {new_angle:.0f}")
            
            #filtered_angle = low_pass_filter(filtered_angle, new_angle)
            #print(f"Angle is: {filtered_angle:.0f}")

            time.sleep(0.5)     

except FileNotFoundError:
    print(f"Error: I2C bus {I2C_BUS_NUMBER} not found. Ensure I2C is enabled.")
except OSError as e:
    print(f"Error communicating with I2C device: {e}")
    print("Check device address, connections, and permissions.")