#!/usr/bin/env python3

from smbus2 import SMBus

DRV_ADDR = 0x5A   
PREMIER_REG = 0x00
DERNIER_REG = 0x22  
   
def main():
	bus = SMBus(1)
	print("Start")
	try:
		status = bus.read_byte_data(DRV_ADDR, 0x00)
		device_id = (status >> 5) & 0b111
		print(f"DEVICE_ID : {device_id}")
	except OSError as e:
		print(e)
		return

	print("Reg   Hex   Binaire       Decimal")
	print("-------------------------------------")

	for reg in range(PREMIER_REG, DERNIER_REG + 1):
		try:
			val = bus.read_byte_data(DRV_ADDR, reg)
		except OSError as e:
			print(f"0x{reg:02X} : ERREUR : {e}")
			continue

		print(f"0x{reg:02X}  0x{val:02X}  {val:08b}   {val:3d}")

	print("\nFIN.")
 
if __name__ == "__main__":
	main()