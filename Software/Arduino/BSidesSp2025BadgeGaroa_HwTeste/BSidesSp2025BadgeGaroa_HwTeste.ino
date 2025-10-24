/*
 BSidesSp2025BadgeGaroa_HwTeste.ino
  incluir na mesma pasta: "pitches.h" 

  SD card read/write

  

  created   Nov 2010
  by David A. Mellis
  modified 9 Apr 2012
  by Tom Igoe

  This example code is in the public domain.

*/

#include <SPI.h>
#include <SD.h>
#include "pitches.h"  
#include <Wire.h>

//Pinos do ESP p/ OLed 1.3 pol
// SDA => D1
// SCL => D2


#include<SH1106.h>  // ref.: ESP8266_and_ESP32_OLED_driver_for_SSD1306_displays
SH1106 display(0x3C, SDA, SCL); // 1.3 pol:

int melody[] = { NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4 };
int noteDurations[] = { 4, 8, 8, 4, 4, 4, 4, 4 }; // note durations: 4 = quarter note, 8 = eighth note, etc.:

#define LED_BUILTIN 2

#define btn_1 0x00
#define btn_2 0x0C
#define btn_3 0x0D
#define btn_qtd  3

void printFooter(String txt, int xpos, int yPos = 0);

bool btn_last_state[btn_qtd];
const int btn[btn_qtd] = { btn_1, btn_2, btn_3 };

long t_tick = 0;

long rnd;
String sdReadLine = "";

File myFile;


void telainicial()
{
  //Apaga o display
  display.clear();
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  //Seleciona a fonte
  display.setFont(ArialMT_Plain_16);
  display.drawString(63, 0, "ESP8266");
  display.drawString(63, 16, "Wifi Badge");
//  display.drawString(63, 32, "BSIDES SP 2025");
  display.display();
}

void graficos()
{
  display.clear();
  //Desenha um quadrado
  display.drawRect(12, 12, 30, 30);
  //Desenha um quadrado cheio
  display.fillRect(20, 20, 35, 35);
  //Desenha circulos
  for (int i = 1; i < 8; i++)
  {
    display.setColor(WHITE);
    display.drawCircle(92, 32, i * 3);
  }
  display.display();
}

void ProgressBar()
{
  for (int counter = 0; counter <= 100; counter++)
  {
    display.clear();
    
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 0, "GAROA Hacker Clube");
    
    //Desenha a barra de progresso
    display.drawProgressBar(0, 32, 120, 10, counter);
    //Atualiza a porcentagem completa
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.drawString(64, 15, String(counter) + "%");
    display.display();
    delay(20);
  }
}

void melodyOne() 
{
  for (int thisNote = 0; thisNote < 8; thisNote++) 
  {
    // to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(16, melody[thisNote], noteDuration);
    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(16); // stop the tone playing:
  }
}


int check_btn_press()
{
  for(int i=0; i < btn_qtd; i++)
  {
    int btnRead = digitalRead(btn[i]);

    if( !btnRead && ! btn_last_state[i])
    {
      Serial.print(" btn PRESSIONADO > ");
      Serial.println(btn[i]);
      btn_last_state[i] = true;

      String txt = "SW On: " + String(btn[i]);
      printFooter(txt, 0);
    }
    else if (btnRead && btn_last_state[i] )
    {
      btn_last_state[i] = false;

      Serial.print(" btn Solto > ");
      Serial.println(btn[i]);
      
      String txt = "SW Off: " + String(btn[i]);
      printFooter(txt, 0);  
    }
        
  }
  return 0;
}

void printFooter(String txt, int xpos, int yPos)
{
  display.setColor(BLACK); // alternate colors
  display.setFont(ArialMT_Plain_10);

  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.fillRect(xpos, 53, txt.length() * 10, 10 ); // dados da fonte abaixo
  display.display();

  display.setColor(WHITE);  // Reset back to WHITE

  display.drawString(xpos, 53, txt);
  display.display();
  

// Font:
// Width: 16
// Height: 19
}

void setup() {
  int retries = 3;
  int j=0;
  
  sdReadLine.reserve(128);

  for(int i=0; i < btn_qtd; i++)
    btn_last_state[i] = false;

  delay(500);
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  Serial.println("\r\nIniciando...");

  randomSeed(analogRead(0));
  
  pinMode(LED_BUILTIN, OUTPUT);  // LED_BUILTIN

  display.init();
  display.flipScreenVertically();
  display.clear();

  ProgressBar();
  digitalWrite(LED_BUILTIN, LOW);  
  delay(750);

  melodyOne();

  Serial.println("Initializing SD card ");

  while (!SD.begin(15) && retries-- !=0) {
    Serial.print(".");
    delay(1000);
  }

  if( retries <= 0)
  {
    Serial.println("initialization Fail");
  }  
  else
  {
    Serial.println("initialization OK ");

    rnd = random(100, 999);
    // open the file. note that only one file can be open at a time,
    // so you have to close this one before opening another.
    myFile = SD.open("texto.txt", FILE_WRITE); // 

    // if the file opened okay, write to it:
    if (myFile) {
      Serial.print(" Writing to texto.txt: ");
      Serial.print(rnd);
      Serial.print(" ...");
      myFile.println(rnd);
      // close the file:
      myFile.close();
      Serial.println("done.");
    } else {
      // if the file didn't open, print an error:
      Serial.println("error opening texto.txt");
    }
  
    myFile = SD.open("texto.txt"); // re-open the file for reading:"texto.txt"
    if (myFile) 
    {
      uint32_t lineStart = 0;
      while (myFile.available()) {
        lineStart = myFile.position();
        if (!myFile.find((char*) "\n"))
          break;
      }
      myFile.seek(lineStart);
      Serial.print(" Lido texto.txt: ");

      while (myFile.available())    
        Serial.write(myFile.read());
      
      myFile.close();
    } 
    else 
    {
      Serial.println("error opening texto.txt");
    }
  }

  if( retries <= 0) // após leitura do cartão SD foi detectado ? pois compatilham pinos
  {
    for(int i=0; i < btn_qtd; i++)    
    {    
      Serial.print(btn[i]);
      Serial.print(" ");
      pinMode(btn[i], INPUT_PULLUP);
    }
  }

  telainicial();

  if( retries <= 0)
  {
    printFooter("SD: No", 90);
  }
  else
  {
    printFooter("SD: OK", 90);
  }
      

}

void loop() 
{
  
  while(true)
  {
    if(millis() - t_tick >= 500)
    {
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));     
      Serial.println(" Ping ..."); 
      t_tick = millis();
    }   

    check_btn_press();

    yield();
  }

  yield();
}


