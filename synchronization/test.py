from postoffice import *
from mpi4py import MPI
import string
import time
import os

# def chatReceivesMessages():
#   dudes = {"P1":Dude(1), "P2":Dude(2)}
#   dudes["P1"].send("Hej, jeg hedder P1!")
#   dudes["P2"].send("Hej P1, jeg hedder P2.")
#   dudes["P1"].send("Hvad taler du, P2?")
#   dudes["P2"].send("Jeg taler Python!")

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

numberOfUnits = comm.size

if rank == 0:
    #This is the Post Office
    po = PostOffice()
    for pNumber in range(1, 5):
        for i in range(1, numberOfUnits):
            po.send("Package{}".format(pNumber), i)
else:
    #this is a delivery unit
    du = DeliveryUnit(rank)
    du.receiveAndDeliver("lamp")