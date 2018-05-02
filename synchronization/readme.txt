If we look at the log files, it is seen that the ones that don't run lamport (nolamp*) miss the delivery of the last packages.
Looking at the lamp1 & lamp2 logs we notice that adding the lamport synchronization for delivery units ensures that these will deliver all packages.

Lamport is implemented on line 51 in the postoffice.py file.


-----------------------
30/04/2018: Implementing Leader Election:

The purpose of this is to show how a leader election algorithm like Bully Election can help choose a master clock in our system.
The scenario is: Given the previous prototype where we have on post office with a bunch of delivery units, we now consider having more post offices.
Each new post office now has it's own delivery units, and the post offices need to stay synchronized. There is no central unit in our system, so the post offices need to synchronize among themselves.
For this, one of them acts as the Leader, and is responsible for sending simple synchronization messages to all the others*. Thus we employ a Bully Election algorithm to choose the leader.

* Synch messages are simple. It is assumed that there is no delay in the message transmission, so we don't implement the PTP protocol here.