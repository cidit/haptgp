
# code moteur
import time
#import smbus
from smbus2 import SMBus
 
DRV_ADDR = 0x5A
#bus = smbus.SMBus(1)
bus = SMBus(1)
 
# Registres principaux
REG_MODE = 0x01
REG_GO = 0x0C
REG_SEQ0 = 0x04
REG_OVERDRIVE = 0x0D
REG_LIB_SEL = 0x03
 
# Mettre en mode Internal Trigger
bus.write_byte_data(DRV_ADDR, REG_MODE, 0x00)
 
# Choisir la librairie 1 (ER/ERM motors)
bus.write_byte_data(DRV_ADDR, REG_LIB_SEL, 0x01)
 
# Option : overdrive pour plus de vibration
bus.write_byte_data(DRV_ADDR, REG_OVERDRIVE, 0xFF) # max
effect_id = 1
while(1) :
    effect_id += 1
    if effect_id > 123:
        effect_id = 1
 
# Choisir un effet fort (ex: effet n°1 = Strong Click)
bus.write_byte_data(DRV_ADDR, REG_SEQ0, effect_id)
# Lancer l'effet
bus.write_byte_data(DRV_ADDR, REG_GO, 0x01)
print(effect_id)
print("Effet lancé !")
time.sleep(1)
 
