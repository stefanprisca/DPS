If we look at the log files, it is seen that the ones that don't run lamport (nolamp*) miss the delivery of the last packages.
Looking at the lamp1 & lamp2 logs we notice that adding the lamport synchronization for delivery units ensures that these will deliver all packages.
The lamport implementation is on line 