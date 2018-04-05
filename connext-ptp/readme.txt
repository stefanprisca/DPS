In this assignmet we prove the functionality of PTP using Connext-RTI.
The two main interacting component are the syncMessagePublisher and syncMessageSubscriber.

1) The syncMessagePublisher acts as the master clock in an PTP setting. It will send syncMessages to a predefined topic.
These messages will pass along the master clock, used to sync the salves. In order to simplify the implementation  (have only one publisher), the master is also responsible for initiating delay and offset corrections. A syncMessage with the DELAY_MESSAGE id will be generated every 5 messages. All the other message have the SYNC_MESSAGE id. The DELAY_MESSAGE id is recognized by the slaves, and will cause them to run the delay correction algorithm. In all other cases, the sync correction will run.

2) The syncMessageSubscriber acts as the slave clock in a PTP setting. It contains the logic to synchronize itself to the master clocks received via syncMessages. As mentioned above, if it receives a SYNC_MESSAGE, it will run the sync correction algorithm, and if it receives a DELAY_MESSAGE, it runs the delay correction algorithm. The logic is split among oservers (to react to messages) and the SyncComputer which calculates the synchronization, delay and offset errors. The syncMessageSubscriber will then adjust its timer according to the computer results.
The slave also randomizes the clock cycle correction, so there will always be a synchronization difference between the two clocks.

In order to have more control over the clocks used in this system, we implemented our own virtual clock (myTimer.java). This is a small wrapper over the javax.swing.Timer class, which allows us to update the delay of the clock, and the offset. The maintained clock is incremented with each tick of the underlying Timer, and can be modified (incremented/decremented) via the updateClock() method.

The results can be seen in the slave.log file. The slave and master clocks are started with different tick delays (10 vs 100). It can be seen that in the begining, since the slave is started first, there is a big difference between the two clocks. Also, their cycles are different because of the different delays with which they were created.
After a while, the cycle differences become small due to synchronization corrections. Note that because we include a random number in the sync correction, there will be continuous synch differences, but these will be small.
Also, it can be seen that the initial delay caused by starting the slave first and master after is corrected. Eventually the clocks will become synced and will continue to stay that way with small errors. 
