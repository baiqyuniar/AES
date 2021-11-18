import paho.mqtt.client as mqtt
import time
from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad
from datetime import datetime
import os
import json
import timeit

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))

def encrypt(plain_text, password):
    # generate a random value for salt
    salt = get_random_bytes(16) 
    # use the Scrypt KDF to get a key from the password using salt
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=16)
    # create cipher config
    cipher = AES.new(private_key, AES.MODE_CBC)
    #from plain text to chiper text
    data = bytes(plain_text, 'utf-8')
    cipher_text = cipher.encrypt(pad(data, 16))
    # return a dictionary with the encrypted text
    return {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'iv': b64encode(cipher.iv).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8')
    }

def times(msg1):
    t = datetime.now()
    hrs = int(format(t, '%H'))
    mnt = int(format(t, '%M'))
    sec = int(format(t, '%S'))
    ms = int(format(t, '%f'))
    f = open("pubfile.csv", "a")
    print(t)
    spb=msg1['cipher_text']
    ivpb=spb+" ; "+str(t)+"\n"
    lgt=len(ivpb)
    strfix=ivpb+"; "+str(t)+"; "+str(lgt)+"\n"
    f.write(strfix)
    return hrs, mnt, sec, ms

client = mqtt.Client() #creating new instance
client.on_connect = on_connect
broker="broker.mqtt-dashboard.com"

client.connect(broker,1883,60)
while True:
    start = timeit.default_timer()
    x=input("pesan: ")
    password = "mbkm2021"
    for i in range(5):
        # First let us encrypt secret message
        encrypted = encrypt(x, password)
        hours, minutes, sec, ms = times(encrypted)
        encrypted["hours"] = hours
        encrypted["minutes"] = minutes
        encrypted["sec"] = sec
        encrypted["mikro"] = ms
        #print(encrypted)
        encode_data = json.dumps(encrypted, indent=2).encode('utf-8')
        client.publish("mqtt/rafly", payload=encode_data , qos=1)
        print("Just published message to topic mqtt/rafly")
        time.sleep(5)
    stop = timeit.default_timer() # catat waktu selesai
    lama_eksekusi = stop - start # lama eksekusi dalam satuan detik
    print("kecepetan Komputasi : "+str(lama_eksekusi))
    time.sleep(1)

    