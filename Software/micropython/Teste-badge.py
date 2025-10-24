from machine import Pin, I2C
from time import sleep
import sh1106


##  BOTÕES  ##
btn_pins = [Pin(0, Pin.IN, Pin.PULL_UP),
            Pin(12, Pin.IN, Pin.PULL_UP),
            Pin(13, Pin.IN, Pin.PULL_UP)]

btn_last_state = [False] * len(btn_pins)

##  Display  ##
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)

display.sleep(False)
display.fill(0)
display.flip()
display.text('Garoa', 40, 00, 1)
display.text('Hacker', 40,20, 1)
display.text('Clube', 40, 40, 1)
display.show()

display.fill(0)
display.text('B0',0,0,1)
display.text('B12',0,10,1)
display.text('B13',0,20,1)  #Não exibe


## Buzzer ##

buz = Pin(16, Pin.OUT)
    
def buzzer(freq=1,time=1):
    for i in range(time*freq):
        buz.value(0)
        sleep(1/(2*freq))
        buz.value(1)
        sleep(1/(2*freq))
        
def morse_read(morse, t = 0.05, freq = 400):
    for i in morse:
        if i ==' ':
            sleep(3*t)
        elif i =='.':
            buzzer(freq, t)
            sleep(t)
        elif i == '-':
            buzzer(freq, 3*t)
            sleep(t)

morse = '--. .- .-. --- .-'
morse_read(morse)

## Teste dos botões ##

while True:
    sleep(0.1)
    for i, btn in enumerate(btn_pins):
        state = btn.value()
        # Lógica invertida (LOW = pressionado) se usar pull-up
        if state == 0 and not btn_last_state[i]:
            btn_last_state[i] = True
            print("Botão PRESSIONADO -->", i)
            display.fill_rect(30,i*10,30,10,0)
            display.text('ON',30,i*10,1)
        elif state == 1:
            btn_last_state[i] = False
            display.fill_rect(30,i*10,30,10,0)
            display.text('OFF',30,i*10,1)
        display.show()

