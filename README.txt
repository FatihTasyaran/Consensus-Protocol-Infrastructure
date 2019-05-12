 ####TERM PROJECT PHASE1####
#######FATIH TASYARAN#######

##INSTRUCTIONS FOR RUNNING CODE##

-> I wrote the project for python 2.x
-> Arguments for all the files are as following:
   -> proposer[port, L, K, R]
   -> validator[port, K]
   -> tester[L, R, N]
      -> N = Number of peers

##RUNNING THE CODE##
-> Open N terminals, 1 for proposer, n-1 for validator
-> Start proposer, it will register itself and wait "start" input to start the
   first round

-> Start validators, they will register themselves to the API and will wait for
   proposer to start the round

-> Input "start" to proposer. (Actually anything, to prevent unnecessary situations)

-> Process will start,

-> Wait until all rounds are finished
   -> You can close terminals now

-> Run tester.py with L R N (Not N-1!)
-> It will output if chains are valid and final hashes are identical

-> Thanks!
      
