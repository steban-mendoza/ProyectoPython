import network, time, urequests
from utime import sleep, sleep_ms
from hcsr04 import HCSR04
from machine import Pin, ADC, PWM, I2C
import network, time, urequests
import utime
from ssd1306 import SSD1306_I2C

alto= 64
ancho= 128

sensor = HCSR04(trigger_pin=15, echo_pin=5, echo_timeout_us=25000)
sensorMQ135 = ADC(Pin(32))

i2c=I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(ancho, alto, i2c)
sensorMQ135.width(ADC.WIDTH_10BIT)
sensorMQ135.atten(ADC.ATTN_11DB)

def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True

if conectaWifi ("Esteman", "123456789011"):

    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())

    url="https://api.thingspeak.com/update?api_key=2Q8AOZYXBK7WFB21"

    while True:
      distance = sensor.distance_cm()
      print ("Distancia", distance, "cm")
      sleep(1)
      
      lecturaMQ135 = int(sensorMQ135.read())
      utime.sleep(0.5)

      ppm = 1200 / 1023
      co = ppm * lecturaMQ135
      print ("Monoxido de carbono: ",co, "ppm")
      utime.sleep_ms(1000)

      if co <= 350:
        print ("Alta calidad de aire")
      elif 350 < co <= 800:
        print ("Moderada calidad de aire")
      elif 800 < co <= 1200:
        print ("Baja calidad de aire")
      else:
        print ("Mala calidad de aire")
  
      oled.fill(0)
      oled.pixel(64, 60, 1)
      oled.vline(0, 0, 20, 1)
      oled.vline(120, 0, 20, 1)
      oled.hline(0, 0, 120, 1)
      oled.hline(0, 21, 120, 1)
      oled.text("Dista y PPM", 10, 10, 1)
      oled.text("DISTA", 0, 30, 1) #
      oled.text("PPM", 0, 40, 1) #
      oled.text(str(distance), 60, 30, 1)
      #oled.text("cm", 100, 30, 1)
      oled.text(str(co), 60, 40, 1) #
      #oled.text("%", 100, 40, 1)
      oled.show()

      respuesta = urequests.get(url+"&field1="+str(distance)+"&field2="+str(co))# para thingspeak
      #respuesta = urequests.get(url+"&value1="+str(tem)+"&value2="+str(hum))# para ifttt
      print(respuesta.text)
      print(respuesta.status_code)
      respuesta.close ()
      time.sleep(1)

 
else:
       print ("Imposible conectar")
       miRed.active (False)