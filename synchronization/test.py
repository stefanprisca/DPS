from postoffice import *
from mpi4py import MPI
import string
import time
import os
import math

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


_PO_SIZE = 3
numberOfUnits = _PO_SIZE
nOf_nodes = comm.size
po_ids = list(x*_PO_SIZE for x in range(1, math.ceil(nOf_nodes/_PO_SIZE)))

if rank == 0:
   pass
else:
    po_topic = math.ceil(rank/_PO_SIZE)
    if rank % _PO_SIZE == 0:
        print('\n\n\n ------------ Wanting to create post office... \n\n')
        #This is the Post Office
        po = PostOffice(rank, po_topic, po_ids)
        pNumber = 0
        while True:
            for i in range(rank-numberOfUnits+1, rank):
                po.send("Package{}".format(pNumber), i)
            pNumber += 1
            time.sleep(0.1)
    else:
        #this is a delivery unit
        du = DeliveryUnit(rank, po_topic)
        du.receiveAndDeliver("new_proto")