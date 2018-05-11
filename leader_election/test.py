from postoffice import *
from mpi4py import MPI
import string
import time
import os
import math
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


_PO_SIZE = 3
numberOfUnits = _PO_SIZE
nOf_nodes = comm.size
po_ids = list(x*_PO_SIZE for x in range(1, math.ceil(nOf_nodes/_PO_SIZE)))

if rank == 0:
   pass
else:
    sys.stdout = open(f'./logs/{rank}_output.txt', 'w')
    po_topic = math.ceil(rank/_PO_SIZE)
    if rank % _PO_SIZE == 0:
        print(datetime.now(), '\n\n\n ------------ Wanting to create post office... \n\n')
        #This is the Post Office
        po = PostOffice(rank, po_topic, po_ids)
        pNumber = 0
        for r in range(0, 100):
            for i in range(rank-numberOfUnits+1, rank):
                po.send("Package{}".format(pNumber), i)
            pNumber += 1
            time.sleep(0.1)
            if po._is_bully and r > nOf_nodes-rank:
                print(datetime.now(), 'I\'m bully, so I quit\n-----')
                exit()
    else:
        #this is a delivery unit
        du = DeliveryUnit(rank, po_topic)
        du.receiveAndDeliver()