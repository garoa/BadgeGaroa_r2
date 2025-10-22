from machine import Pin, I2C
from time import sleep
import sh1106
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

display.sleep(False)
display.fill(0)
display.flip()
display.text('Garoa', 40, 00, 1)
display.text('Hacker', 40,20, 1)
display.text('Clube', 40, 40, 1)
display.show()
sleep(0.2)

#display.rect(0,0,128,64,1)
#display.show()


with open('guardachuvaGAROA', 'r') as file:
    content = file.read()  # Read the entire content of the file
    l = content.split('\r\n')
    for n in range(len(l)):
        for m in range(len(l[0])):
            display.pixel(m,n,int(l[n][m]))
    display.show()
