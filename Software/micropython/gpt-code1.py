from machine import Pin, I2C, SPI
import time
import os
import sdcard
import uos
import urandom

import sh1106  # driver para o display SH1106

# --- Configurações de hardware / pinos ---

# Pinos I2C para display SH1106
# No seu Arduino original você usou SDA = D1, SCL = D2
# No ESP8266, D1 = GPIO5, D2 = GPIO4 (verifique seu mapeamento)
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

# Inicializa o display SH1106 (128×64) via I2C
oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3C)

# LED incluído (LED_BUILTIN). No NodeMCU, tipicamente é o GPIO2
LED = Pin(2, Pin.OUT)

# Botões — adapte os pinos corretos conforme seu hardware
# No Arduino, btn_1 = 0x00, btn_2 = 0x0C, btn_3 = 0x0D — isso parece pinos definidos via macros
# Aqui vamos supor que seus botões estão em pinos físicos, por exemplo:
btn_pins = [Pin(0, Pin.IN, Pin.PULL_UP),
            #Pin(1, Pin.IN, Pin.PULL_UP),
            Pin(2, Pin.IN, Pin.PULL_UP),
            #Pin(3, Pin.IN, Pin.PULL_UP),
            Pin(4, Pin.IN, Pin.PULL_UP),
            Pin(5, Pin.IN, Pin.PULL_UP),
            Pin(12, Pin.IN, Pin.PULL_UP),
            Pin(13, Pin.IN, Pin.PULL_UP),
            Pin(14, Pin.IN, Pin.PULL_UP),
            Pin(15, Pin.IN, Pin.PULL_UP),
            #Pin(16, Pin.IN, Pin.PULL_UP)
             ]
btn_last_state = [False] * len(btn_pins)

# Melodia (notas) — você deverá portar ou omitir dependendo da disponibilidade de gerar som no MicroPython
from NOTAS import melody
noteDurations = [4, 8, 8, 4, 4, 4, 4, 4]

# Variáveis de controle
t_tick = 0
rnd = 0

# --- Funções de display / interface gráfica ---

def tela_inicial():
    oled.fill(0)
    # Posição central aproximada (ajuste conforme seu alinhamento)
    oled.text("GAROA", 32, 0)
    oled.text("Hacker Clube", 20, 16)
    oled.text("BSIDES SP 2025", 5, 32)
    oled.show()

def graficos():
    oled.fill(0)
    oled.rect(12, 12, 30, 30, 1)
    oled.fill_rect(20, 20, 35, 35, 1)
    # círculos — usando linha a linha (SH1106 não tem método de círculo, mas você pode adaptar)
    # Para simplificar, aqui desenho alguns pontos circulares aproximados
    cx, cy = 92, 32
    for i in range(1, 8):
        # desenha pontos ao redor (exemplo simples)
        radius = i * 3
        oled.pixel(cx + radius, cy, 1)
        oled.pixel(cx - radius, cy, 1)
        oled.pixel(cx, cy + radius, 1)
        oled.pixel(cx, cy - radius, 1)
    oled.show()

def progress_bar():
    for counter in range(0, 101):
        oled.fill(0)
        # desenha a “barra de progresso”
        bar_width = 120
        w = int(bar_width * counter / 100)
        oled.fill_rect(0, 32, w, 10, 1)
        # desenha borda da barra
        oled.rect(0, 32, bar_width, 10, 1)
        # exibe percentual
        txt = "{}%".format(counter)
        oled.text(txt, 64 - len(txt)*4, 15)  # ajusta posição do texto
        oled.show()
        time.sleep_ms(20)

def print_footer(txt, xpos=0):
    # Limpa a região do rodapé (ajuste de altura) — aqui usamos retângulo preto
    height = 16
    width = len(txt) * 8
    oled.fill_rect(xpos, 32 + 16, width, height, 0)
    oled.text(txt, xpos, 32 + 16)
    oled.show()

# --- Função de checagem de botões ---

def check_btn_press():
    for i, btn in enumerate(btn_pins):
        state = btn.value()
        print(btn, state)
        # Lógica invertida (LOW = pressionado) se usar pull-up
        if state == 0 and not btn_last_state[i]:
            btn_last_state[i] = True
            txt = "SW: {}".format(i)
            print("btn PRESSIONADO >", i)
            print_footer(txt, 0)
        elif state == 1:
            btn_last_state[i] = False

# --- Função de tocar melodia (se suportado) ---

def melody_one():
    # MicroPython no ESP8266 normalmente não tem suporte nativo a “tone()” como Arduino.
    # Você teria que usar PWM em um pino ou módulo externo para gerar som.
    # Aqui deixo como stub (não faz nada).
    pass

# --- Funções de SD card / leitura e gravação ---

def init_sd(cs_pin=15, spi_id=1, baudrate=1000000):
    # Inicializa SPI para SD
    spi = SPI(spi_id, baudrate=baudrate, polarity=0, phase=0)
    cs = Pin(cs_pin, Pin.OUT)
    sd = sdcard.SDCard(spi, cs)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
    print("SD montado em /sd")
    return True

def write_random_to_sd():
    global rnd
    rnd = urandom.getrandbits(16)  # valor aleatório
    path = "/sd/texto.txt"
    try:
        with open(path, "a") as f:
            f.write(str(rnd) + "\n")
        print("Escreveu no SD:", rnd)
        return True
    except Exception as e:
        print("Erro ao escrever no SD:", e)
        return False

def read_last_line_from_sd():
    path = "/sd/texto.txt"
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        if lines:
            last = lines[-1].strip()
            print("Lido última linha:", last)
            return last
    except Exception as e:
        print("Erro ao ler SD:", e)
    return None

# --- Setup principal ---

def setup():
    print("Iniciando MicroPython versão")
    LED.value(0)  # LED apagado (dependendo da lógica do seu hardware)
    time.sleep_ms(500)

    # Inicializa display
    oled.show()
    progress_bar()
    LED.value(1)
    time.sleep_ms(750)
    LED.value(0)

    # Tocar melodia (se implementado)
    melody_one()

    # Inicializar SD
    sd_ok = False
    try:
        sd_ok = init_sd(cs_pin=15)  # ajuste o CS conforme seu hardware
    except Exception as e:
        print("Falha no SD:", e)

    if sd_ok:
        write_random_to_sd()
        ultimo = read_last_line_from_sd()
    else:
        print("SD não disponível")

    tela_inicial()
    if sd_ok:
        print_footer("SD: OK", 70)
    else:
        print_footer("SD: No", 70)

# --- Loop principal ---

def loop():
    global t_tick
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, t_tick) >= 500:
            # alterna LED
            LED.value(not LED.value())
            print("Ping ...")
            t_tick = now
        check_btn_press()
        time.sleep_ms(10)


# --- Execução principal ---

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("Parando programa")
