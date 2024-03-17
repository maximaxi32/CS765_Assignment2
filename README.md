# CS765 Spring 2023 Semester, Project Part-1
# Simulation of a P2P Cryptocurrency Network


## Created By:
### Abhishek Dixit (22M0761), Rishabh Singh (22M0762) and Osim Abes (22M0825)


## Compilation

1. To install dependencies, run:
    pip install -r requirements.txt
    or
    pip3 install -r requirements.txt

2. To compile and run the project, run the following command with your own choice of parameter values:
    python3 main.py --n N --z0 Z0 --z1 Z1 --Tx TX --Itr ITR --Sim SIM \
    e.g. python3 main.py --n 15 --z0 30 --z1 90 --Tx 0.5 --Itr 1 --Sim 100


## Generated Logs

1. You will find details of all the generated Transactions in the file "TxnLog.txt"

2. You will find the Node-wise logs of generated and received blocks in the "blockLogs" directory


## Generated Images

1. You will find the graph of Network topology in the "graphs" directory under the name "_Topology.png"

2. You will find the generated visualisations of the Blockchain(s) in the "graphs" directory

3. You will find the merged image of all the Blockchains in the "graphs" directory under the name "_MergedBlockchain.png" 

