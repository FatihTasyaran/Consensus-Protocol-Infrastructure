from flask import Flask, request, jsonify
import json
import requests
import sys
###ECDSA.py###
import random
import string
import sys
import ecdsa
import hashlib
import binascii
###ECDSA.py###
import zmq
import threading
import time

HOST = '127.0.0.1'
API_URL = 'http://127.0.0.1:5000'
PORT = sys.argv[1]
SPLIT = "SPLIT"
K = int(sys.argv[2])
#N = sys.argv[3]

filename = "chain_"+PORT+".txt"
filer = open(filename, "w+")

print("Validator in port %s started" % PORT)
sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc = hashlib.sha256)
pk = sk.get_verifying_key()
#print("public key:", binascii.hexlify(pk.to_string()))
key = binascii.hexlify(pk.to_string())

register_response = requests.post(API_URL+"/nodes", json={'PORT': str(PORT), 'KEY': key})

print(register_response.json())

##GLOBAL LISTENER##
context = zmq.Context()
connection = 'tcp://'+HOST+':'+PORT
listener_sock = context.socket(zmq.REP)
listener_sock.bind(connection)
##GLOBAL LISTENER##


def prepare_send(onemessage):
    sender_signature, block, sender_port = onemessage.split(SPLIT)
    signature = sk.sign(block.encode('utf-8'))
    
    sender = threading.Thread(target=send_to_all, args=(signature, block))
    waiter = threading.Thread(target=wait_response)

    waiter.start()
    sender.start()

    sender.join()
    waiter.join()

## ALWAYS SIGNATURE, BLOCK, PORT
def send_to_all(signature, block):
    time.sleep(15)
    get_response = requests.get(API_URL+"/nodes")
    length = len(get_response.json())
    ports = []
    keys = []

    ##GETS PORT AND KEYS
    for i in range (0, length):
        ports.append(get_response.json()[i]['PORT'])
        keys.append(get_response.json()[i]['KEY'])

    ONETRUEMESSAGE = signature+SPLIT+block+SPLIT+PORT
    
    for i in range (0, length):
        if ports[i] != sys.argv[1]:
            CONNECTION = 'tcp://'+HOST+':'+ports[i]
            context = zmq.Context()
            sock = context.socket(zmq.REQ)
            sock.connect(CONNECTION)
            
            sock.send(ONETRUEMESSAGE)
            admire = sock.recv() ##THIS GUY PREVENTS DEADLOCK
            print("I sent to %s" % ports[i])

def legitimate(message):
    print("Writing This Block!")
    signature, block, sender_port = message.split(SPLIT)
    filer.write(block)
    filer.write("\n")

def wait_response():
    get_len = requests.get(API_URL+"/nodes")
    length = len(get_len.json())
    N = length

    wait = True

    print("Waiting for response")
    print("Number of peers: %d" %N)
    n = 0
    k = 0

    while(wait):
        ONETRUEMESSAGE = listener_sock.recv()
        #print("Got it in wait_response, message: %s" % message)
        listener_sock.send("I admire it")
        if verify(ONETRUEMESSAGE):
            n += 1
            k += 1
        if k == 2*int(K):
            print("Legimate Block!")
            #legalizer = threading.Thread(target=legitimate, args=(ONETRUEMESSAGE))
            #legalizer.start()
            legitimate(ONETRUEMESSAGE)
        if(n == N-2):#ONE FOR PROPOSER ONE FOR ITSELF
            wait = False
            #legalizer.join()
                
    #if k == K:
        #proceed()
        

def verify(ONETRUEMESSAGE):
    get_response = requests.get(API_URL+"/nodes")
    length = len(get_response.json())
    ports = []
    keys = []

    signature, block, sender_port = ONETRUEMESSAGE.split(SPLIT)

    ##GETS PORT AND KEYS
    for i in range (0, length):
        ports.append(get_response.json()[i]['PORT'])
        keys.append(get_response.json()[i]['KEY'])

    for i in range(0, length):
        if ports[i] == sender_port:
            sender_key = keys[i]

    #print("Found sender key: %s" %sender_key)

    sender_key = binascii.unhexlify(sender_key)

    verifying_key = ecdsa.VerifyingKey.from_string(sender_key, curve=ecdsa.NIST256p, hashfunc = hashlib.sha256)

    try:
        verifying_key.verify(signature, block.encode('utf-8'))
        print("Signature of %s Verified!" % sender_port)
        return True
    except:
        print("Signature of %s Not Verified!" % sender_port)
        return False
    
    
    #proceed()


##WAIT FROM PROPOSER MAIN LOOP

#context = zmq.Context()
#connection = 'tcp://'+HOST+':'+port
#sock = context.socket(zmq.REP)
#sock.bind(connection)    

while(True):
    ##COMMUNICATION
    print("Listening Proposer")
    onefirstmessage = listener_sock.recv()
    #print("Got it in main loop, message: %s" % message)
    listener_sock.send("I admire it")
    ##COMMUNICATION
    if verify(onefirstmessage):
        prepare_send(onefirstmessage)
        

##WAIT FROM PROPOSER MAIN LOOP

filer.close() ##CLOSE FILE





