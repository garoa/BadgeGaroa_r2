# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import os, machine
#os.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()


from machine import Pin, I2C
from time import sleep
import sh1106
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

display.sleep(False)
display.fill(0)
display.flip()
display.text('Garoa', 40, 00, 1)
display.text('Hacker', 40,10, 1)
display.text('Clube', 40, 20, 1)
display.text('Micro Python', 20, 54, 1)
display.show()
sleep(0.1)

#display.rect(0,0,128,64,1)
#display.show()


with open('guardachuvaGAROA.pbm', 'r') as file:
    content = file.read()  # Read the entire content of the file
    l = content.split('\r\n')
    if l[0] == "P1":#detects .pbm file
        print("File .pbm")
        col, lin = l[2].split(' ')
        for n in range(int(lin)):
            for m in range(int(col)):
                display.pixel(m,n,int(l[n+3][m]))
        display.show()
        
