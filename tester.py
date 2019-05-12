import os, glob, sys
import hashlib

LENGTH_CHAIN = int(sys.argv[1])
NUM_ROUNDS = int(sys.argv[2])
NUMBER_OF_PEERS = int(sys.argv[3])

PROCEED = LENGTH_CHAIN+2

BLOCKS = [[[]for i in range(NUM_ROUNDS)] for i in range(NUMBER_OF_PEERS)]
HASHES = [[[]for i in range(NUM_ROUNDS)] for i in range(NUMBER_OF_PEERS)]

def process_one_peer(filename, index):
    #print("for file: %s" % filename)
    filer = open(filename, "r")
    tryer = filer.readlines()
    transaction_block = ""
    #for i in range(50):
        #print(tryer[i], i)
    for _round in range(NUM_ROUNDS):
        for i in range(PROCEED):    ##ELEMENTS OF ONE ROUND INCLUDING HASH AND \n
            if i == 0:
                _hash = tryer[_round*PROCEED+i]
                #print("hash: ", _hash)
                if _hash == "\n":
                    _hash = ""
                HASHES[index][_round] = _hash ##HASH OF ROUND FOR PEER
            else:
                transaction_block += tryer[_round*PROCEED+i] ## PLACE IN .txt FILE
        BLOCKS[index][_round] = transaction_block
        transaction_block = ""


file_count = 0
index = []
for filename in glob.glob('*.txt'):
    #print(filename)
    ##JUST FOR PRETTIER PRINT
    head, tail = filename.split("_")
    node_port, txt = tail.split(".")
    index.append(node_port)
    process_one_peer(filename, file_count)
    
    file_count += 1

    


print("File count %d" %file_count)

#print(HASHES[0][0])
#print(BLOCKS[0][0])
#print("HASHES[0][0]", HASHES[0][0])
#print("HASHES[0][1]", HASHES[0][1])


#INDEXING DONE
#CHECKING

print("Indexing Done!")
print("Checking!")

def checkValidTransaction():

    for peer in range(NUMBER_OF_PEERS):
        peer_valid = True
        print("Checking for node with address %s" %index[peer])
        for i in range(NUM_ROUNDS-1):
            
            pre_hash = HASHES[peer][i]   ##HASHES[1][0] MEANS HASH OF BLOCK [0][0]
            _hash = HASHES[peer][i+1]    ##IT IS ACTUALLY BLOCK#1 IN FORMULA
            ##h^r = (h^r-1||B^r)
            pre_block = BLOCKS[peer][i]  ##SINCE THERE IS NO BLOCK#-1 TO SATISFY FORMULA 
            
            l_h = len(_hash)
            _hash = _hash[:l_h-1]     ##THIS LINES REMOVES ABUNDANT ENDLINES
            ##COMES WHILE INDEXING
            l_pre_h = len(_hash)
            pre_hash = pre_hash[:l_h-1]
            
            pre_l = len(pre_block)
            pre_block = pre_block[:pre_l-1]
            
            check = pre_hash + "\n" + pre_block
            
            #print("pre_hash:", pre_hash)
            #print("_hash: ", _hash)
            #print("pre_block:", pre_block)
            #print(check)
            
            check_hash = hashlib.sha256(check.encode('utf-8')).hexdigest()
            
            #print("check_hash:", check_hash)
            
            if check_hash == _hash:
                print("Round %d holds for peer %s" %(i+1 ,index[peer]))
            else:
                print("NOO")
                peer_valid = False
        if(peer_valid):
            print("BLOCK OF TRANSACTIONS VALID FOR PEER %s!" % index[peer])
        else:
            print("BLOCK OF TRANSACTIONS NOT VALID")


checkValidTransaction()

print("Checking Final Hashes")

def finalHashes():
    final_hashes = []
    for peer in range(NUMBER_OF_PEERS):
        final_hashes.append(HASHES[peer][NUM_ROUNDS-1])

    checker = final_hashes[0]
    valid = True
    for checked in range(1, NUMBER_OF_PEERS):
        if checker != final_hashes[checked]:
            valid = False
    if(valid):
        print("ALL FINAL HASHES ARE IDENTICAL!")
    else:
        print("FINAL HASHES ARE NOT IDENTICAL")
        

finalHashes()
