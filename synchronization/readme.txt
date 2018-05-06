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

In our example, the postoffice.py file contains the implementation of bully. 
For the example, we have several types of messages:
  _master_sync_id = 1000            # Message that contains sync info for post offices
  _bully_election_tag = 1001        # Bully election messages
  _bully_ok_tag = 1002              # Bully ok messages
  _bully_coordinator_tag = 1003     # bully coordinator messages

Since we are using mpi, we identify each message using mpi tags with the values from above.
Here, post offices go through a series of checks to see if there are any active leaders who send master sync messages.
If a certain time (_elect_timeout) has passed from the last sync message, then the current post office initiates an election.
We track how long it has been from the last sync message using the _time_to_elect var.
The time is incremented randomly, to reduce the chance that two nodes start an election at the same time.

Before starting the election, the nodes do a check to see if there was a successful election already, and there is a coordinator message for them.
If not, nodes check if there is an existing election started. If there is, they run the elect_bully algorithm using the initiator id.
If there is no election started (they didn't receive any election message), then the node initiates a new election.
The elect bully algorithm is as described, except skipping a small step: After sending election messages to candidates, we simply wait for a coordinator message.
We skipped the part that waits for ok messages from all the candidates. This seems unnecessary, since if there will be a coordinator among the candidates, this will send the coord message.
Thus it is not necessary to also wait for ok messages. If no coordinator message arrives, we assume no candidate is online and the node becomes the new leader.

In our examples, every 3rd node is a post office. Text files 3, 6, 9, 12 belong to post offices. These contain the logs for the leaders.
After being leader for a while, each node will quit. It can be seen in the logs that first node 12 is the leader. Then 9 or 6 takes the lead (it depends on the synchronization, sometimes 9 won't become leader for too long).
In the end, number 3 will be leader, when none of the other nodes are alive.