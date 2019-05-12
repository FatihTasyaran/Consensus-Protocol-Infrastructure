from flask import Flask, request, jsonify
import json
###ECDSA.py###
import random
import string
import sys
import ecdsa
import hashlib
import binascii
###ECDSA.py###
import threading
import requests
import time
import zmq

API_URL = "http://127.0.0.1:5000"
HOST = "127.0.0.1"
PORT = sys.argv[1]
L = int(sys.argv[2])  ##Length of transaction chain
K = int(sys.argv[3])  ##Number of required valid responses
R = int(sys.argv[4])  ##Number of rounds
SPLIT = "SPLIT"

print("K: %s" % K)

#PEERS = sys.argv[5]

filename = "chain_"+PORT+".txt"
filer = open(filename, "w+")

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

##ALWAYS SIGNATURE, BLOCK, PORT
def send_all(signature, block):
    #time.sleep(5) ##Writing to file overhead
    sig_message = signature
    block_message = block

    ONETRUEMESSAGE = signature+SPLIT+block+SPLIT+PORT

    get_nodes = requests.get(API_URL+"/nodes")
    num_nodes = len(get_nodes.json())

    #GET KEYS AND PORTS OF ALL NODES IN NETWORK
    ports = []
    keys = []
    
    for i in range(0, num_nodes):
        ports.append(get_nodes.json()[i]['PORT'])
        keys.append(get_nodes.json()[i]['KEY'])

    print("Sending Everyone!")
        
    #SEND TO ALL NODES
    for i in range(1, num_nodes): ## PORTS[0] IS PROPOSER
        context = zmq.Context()
        
        CONNECTION = 'tcp://'+HOST+':'+str(ports[i])
        sock = context.socket(zmq.REQ)
        sock.connect(CONNECTION)
        ##ALWAYS FIRST SIGNATURE THEN BLOCK THEN PORT
        sock.send(ONETRUEMESSAGE)
        admire = sock.recv()
        print("Send to %s" % ports[i])

def legitimate(message):
    print("Writing This Block!")
    signature, block, sender_port = message.split(SPLIT)
    filer.write(block)
    filer.write("\n")

            
def wait_response():
    context = zmq.Context()
    CONNECTION = 'tcp://'+HOST+':'+PORT

    sock = context.socket(zmq.REP)
    sock.bind(CONNECTION)

    wait = True

    get_len = requests.get(API_URL+"/nodes")
    length = len(get_len.json())
    PEERS = length

    print("Waiting for responses!")

    peers = 0
    k = 0
    
    while(wait):
        message = sock.recv()
        print("Got one response")
        #print(message)
        sock.send("I admire it")
        if verify(message): #Send ONETRUEMESSAGE to verify, split it there
            peers += 1
            k += 1
        if k == 2*int(K):
            print("Legitimate Block!")
            #legalizer = threading.Thread(target=legitimate, args=(message))
            #legalizer.start()
            legitimate(message)
        if peers == PEERS-1:
            wait = False
            #legalizer.join()

                


def Register():
    #time.sleep(10)
    
    port = str(sys.argv[1])
        
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc=hashlib.sha256)
    pk = sk.get_verifying_key()
    #print("public key:", binascii.hexlify(pk.to_string()))
    key = binascii.hexlify(pk.to_string())

        

    register_response = requests.post(API_URL+"/nodes", json={'PORT': str(port),'KEY': key})

    if register_response.status_code == 200:
        print("Proposer Registered")
    else:
        print("Proposer Cannot be Registered")

    #print(register_response.json())

    return sk, pk
    
    
def block(previous_hash, sk):
    #time.sleep(10)
        
    block = previous_hash
    block += "\n"   ##THIS COMES OUT AS IT IN TESTER

    #THERE WILL BE A NEWLINE
    #THEREFORE BLOCK AND PREVIOUS HASH WILL BE SEPARATED
    #AFTER, IT IS DONE
    
    for i in range(0,L):
        tx = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        block += tx + "\n"  

    h = hashlib.sha256(block.encode('utf-8')).hexdigest()

    #print ("The transaction block: \n", block)
    signature = sk.sign(block.encode('utf-8'))

    #print ("Signature for the block: ", binascii.hexlify(signature))
    return block, h, signature


def roundPrepare():
    time.sleep(5)
    sk, pk = Register() #Register itself and return keys
    h = ""
    
    ##THIS LINE WILL BE INSTANTIABLE
    result, h, signature = block(h, sk) ##Hash of first block

    _input = False

    print("Input start After Register Validators to Start Round!")
    while(not _input):
        _input = raw_input()
        
    print("Starting Round 1!")
    #time.sleep(15)
    sender = threading.Thread(target=send_all, args=(signature, result))
    sender.start()
    sender.join()
    print("Sent everyone!")

    waiter = threading.Thread(target=wait_response)
    waiter.start()
    waiter.join()
    print("Succesfully Waited!")

    rounds = 1

    while(rounds < R):
        print("Wait for new round!")
        time.sleep(10)
        rounds += 1
        print("Starting round %d!" %rounds)
        
        result, h, signature = block(h, sk)
        sender = threading.Thread(target=send_all, args=(signature, result))
        sender.start()
        sender.join()
        print("Sent everyone!")

        waiter = threading.Thread(target=wait_response)
        waiter.start()
        waiter.join()
        print("Succesfully Waited!")
        

app = Flask(__name__)
nodes = [] ##This is da database

@app.route("/")
def ret():
    return jsonify(nodes)


@app.route("/nodes", methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        node=request.get_json()
        #print(node)
        nodes.append(node)
        return jsonify("Node Added To List")

    if request.method == 'GET':
        return jsonify(nodes)



#registrer = threading.Thread(target=Register)
#registrer.start()

rounder = threading.Thread(target=roundPrepare)
rounder.start() ##PROGRAM STARTS FROM HERE

app.run(debug=False, port=int('5000')) ##ZMQ CONFLICTS WHEN ARG PORT

filer.close()
