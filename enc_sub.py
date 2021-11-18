import paho.mqtt.client as mqtt
from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from datetime import datetime, timedelta
import os
import ast
import xlwt
from xlwt import Workbook

wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
sheet1.write(0, 0, 'Messages')
sheet1.write(0, 1, 'Delay')
j=1
g=1
def excels(delay,texts):
    global j
    global g
    sheet1.write(j,0,texts)
    sheet1.write(g,1,delay)
    j+=1
    g+=1
    wb.save('xlwt coba2.xls')

i=1
avg_delay=0
def decrypt(enc_dict, password):
    # decode the dictionary entries from base64
    salt = b64decode(enc_dict['salt'])
    cipher_text = b64decode(enc_dict['cipher_text'])
    iv = b64decode(enc_dict['iv'])

    # generate the private key from the password and salt
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=16)

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_CBC, iv=iv)

    # decrypt the cipher text
    decrypted = unpad(cipher.decrypt(cipher_text), 16)
    return decrypted

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print("Topic    | Message --> Delay\n")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mqtt/rafly")

def times(time_dict):
    cur_time = datetime.now()
    h = time_dict["hours"]
    m = time_dict["minutes"]
    s = time_dict["sec"]
    ms = time_dict["mikro"]
    time = cur_time - timedelta(hours=h, minutes=m, seconds=s, microseconds=ms)
    hours = int(format(time, '%H'))*3600
    mhour=hours*1000000
    minutes = int(format(time, '%M'))*60*1000
    mminute=minutes*1000000
    sec = int(format(time, '%S'))*1000000
    mikros = int(format(time, '%f'))
    delay = mhour+mminute+sec+mikros
    f = open("subfile.csv", "a")
    tim=str(cur_time)+" Delay : "+str(delay)+"\n"
    f.write(tim)
    return str(delay)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    enkr = msg.payload.decode("UTF-8")
    msgg = ast.literal_eval(enkr)
    delay = times(msgg)
    decrypted = decrypt(msgg, "mbkm2021")
    #change from bytes to string
    w = decrypted.decode('UTF-8')
    global avg_delay
    global i
    avg_delay=(avg_delay+int(delay))/i
    i += 1
    print(msg.topic+"   | "+w+" --> "+delay+" mikroS")
    print("average delay: "+str("%.2f" % avg_delay)+"\n")
    excels(delay,w)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.mqtt-dashboard.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()