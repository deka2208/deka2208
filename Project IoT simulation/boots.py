import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import ssd1306
from machine import Pin, SoftI2C
import dht
esp.osdebug(None)
import gc
gc.collect()

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


ssid = 'Cam Thi'
password = '77779999'
mqtt_server = '192.168.1.9' #Replace with your MQTT Broker IP

client_id = ubinascii.hexlify(machine.unique_id())
TOPIC_PUB_TEMP = b'esp/dht/temperature'
TOPIC_PUB_HUM = b'esp/dht/humidity'

last_message = 0
message_interval = 5

sensor = dht.DHT22(Pin(14))
#sensor = dht.DHT11(Pin(14))  #if using DHT11, comment the above line and uncomment this line.

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(ssid,password)
    if not wifi.isconnected():
        print('connecting..')
        timeout = 0
        while (not wifi.isconnected() and timeout < 5):
            print(5 - timeout)
            timeout = timeout + 1
            time.sleep(1)
            oled.text('connecting..' ,0,10)
            oled.text('%s'%timeout ,0,20)
            oled.show()
            oled.fill(0)
    if(wifi.isconnected()):
        print('connected')
        oled.text('connected' ,0,20)
        oled.show()
        oled.fill(0)
    else:
        print('not connected')
        oled.text('not connected' ,0,10)
        oled.show()
        oled.fill(0)
        sys.exit()
        
connect_wifi()