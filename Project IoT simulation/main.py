topic_sub_relay1 = b'device/relay1'
topic_sub_relay2 = b'device/relay2'
topic_sub_servo = b'device/button1'

topic_pub_relay1 = b'device1/relay1'
topic_pub_relay2 = b'device1/relay2'
topic_pub_servo = b'device1/button1'

relay1 = Pin(25, Pin.OUT)
relay2 = Pin(26, Pin.OUT)
p15 = Pin(15,Pin.OUT)

touch1 = Pin(16, Pin.IN,Pin.PULL_UP)
touch2 = Pin(17, Pin.IN,Pin.PULL_UP )
touch3 = Pin(18, Pin.IN,Pin.PULL_UP)
touch4 = Pin(19, Pin.IN,Pin.PULL_UP )
servo = PWM(p15,freq=50,duty=25)

def debounce(pin):
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

def button_callback(pin):
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        relay1.value(not relay1.value())        
        if relay1.value() == 1:
            client.publish(topic_pub_relay1,"ON")
        else:
            client.publish(topic_pub_relay1,"OFF")
            
touch1.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

def button_callback1(pin):
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        relay2.value(not relay2.value())
        if relay2.value() == 1:
            client.publish(topic_pub_relay2,"ON")
        else:
            client.publish(topic_pub_relay2,"OFF")
        
        
touch2.irq(trigger=Pin.IRQ_FALLING, handler=button_callback1)        

def button_callback2(pin):
    d = debounce(pin)
    dem = 0
    if d == None:
        return
    elif not d:
        servo = PWM(p15,freq=50,duty=120)
        client.publish(topic_pub_servo,"ON")
       
touch3.irq(trigger=Pin.IRQ_FALLING, handler=button_callback2)

def button_callback3(pin):
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        servo = PWM(p15,freq=50,duty=25)
        client.publish(topic_pub_servo,"OFF")

        
touch4.irq(trigger=Pin.IRQ_FALLING, handler=button_callback3)

def sub_cb(topic, msg):
  print ('Received Message %s from topic %s' %(msg, topic))
  if msg == b'off2':
    relay2.value(0)
    print('LED2 is now OFF')
  elif msg == b'on2' :
    relay2.value(1)
    print('LED2 is now ON')
  elif msg == b'off1':
    relay1.value(0)
    print('LED1 is now OFF')
  elif msg == b'on1':
    relay1.value(1)
    print('LED1 is now ON')
  elif msg == b'on':
    servo = PWM(p15,freq=50,duty=120)
  elif msg == b'off':
    servo = PWM(p15,freq=50,duty=25)
    
def display():
    oled.text('Temperature:' ,0,10)
    oled.text('%s C' %temp ,0,20)
    oled.text('Humidity:' ,0,30)
    oled.text('%s %%' %hum,0,40)
    oled.show()
    oled.fill(0)

def connect_mqtt():
  global client_id, mqtt_server,topic_sub_relay1,topic_sub_relay2
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub_relay1)
  client.subscribe(topic_sub_relay2)
  print('Connected to %s MQTT broker' % (mqtt_server))
  oled.text('connect MQTT',0,20)
  oled.show()
  oled.fill(0)
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  oled.text('Failed cn MQTT',0,20)
  oled.show()
  oled.fill(0)
  time.sleep(10)
  machine.reset()

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  
  try:
    new_msg = client.check_msg()
    if (time.time() - last_message) > message_interval:
      sensor.measure()
      temp = sensor.temperature()
      hum = sensor.humidity()
      temp = ('{0:3.1f}'.format(temp))
      hum =  ('{0:3.1f}'.format(hum))
      display()
      print('Temperature: %s' %temp, 'Humidity: %s' %hum)
      client.publish(TOPIC_PUB_TEMP, temp)
      print('Published message %s to topic %s' %(temp,TOPIC_PUB_TEMP))
      client.publish(TOPIC_PUB_HUM, hum)
      print('Published message %s to topic %s' %(hum,TOPIC_PUB_HUM))
      print()
      last_message = time.time()
      
  except OSError as e:
    restart_and_reconnect()
    

    