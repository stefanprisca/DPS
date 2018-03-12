from mpi4py import MPI
import time
import random
comm = MPI.COMM_WORLD

# The package that we deliver.
# It contains a timestamp field marking the delivery date.
class Package:
  def __init__(self, contents, timestamp):
     self.Contents = contents
     self.Timestamp = timestamp
  
  def __repr__(self):
    return "<- Contents: <{}> ; Timestamp:<{}> ->".format(self.Contents, self.Timestamp)

PO_RANK = 0

# Post office handling deliveries.
class PostOffice:
  def __init__(self):
    self.clock = 0
  
  def send(self, contents, dest):
    self.clock += 1
    package = Package(contents, self.clock)
    comm.send(package, dest)

# Delivery unit that receives delivery requests from the PO.
# It will only deliver the packages with a timestamp up to the delivery date
class DeliveryUnit:
  def __init__(self, id):
    self.ID = id
    # Use a system clock to decide what will be delivered.
    # Only packages that have been received until this time (their timestamp is less) will be delivered.
    self.clock = 0

    # Use separate clock to determine the delivery period.
    # This is different from the base clock. It just determines when we should deliver, not what we deliver.
    self.delivery_clock = 0
    self.delivery_period = 2

  def receiveAndDeliver(self, log_name):
    file = open("./logs/{}{}.txt".format(log_name, self.ID), "w")
    packages = []
    while True:
        package = self.waitForPackage()
        if package == None:
          # PO stopped sending packages. Stop our loop as well
          break 
        
        # add lamport clock synch
        # This ensures that the delivery unit will deliver all received packages until the delivery time.
        self.clock = max(self.clock, package.Timestamp)

        self.clock += 1
        self.delivery_clock += 1
        packages.append(package)
        file.write("Delivery unit got package {} \n".format(package))
        if self.delivery_clock % self.delivery_period == 0:
          delivered = self.deliverPackages(packages, self.clock)
          file.write("Delivered packages {} at time {} \n".format(delivered, self.clock))
  
  def deliverPackages(self, packages, deliveryTime):
    deliveredPkgs = []
    for pkg in packages:
      if pkg.Timestamp <= deliveryTime:
        deliveredPkgs.append(pkg)
    return deliveredPkgs
  
  # Check if any package has been sent by the PO.
  # If no package received within a timeout, then assume the PO is not sending anymore. 
  def waitForPackage(self):
    timeout = 0
    # Wait to receive something
    while not comm.Iprobe(source=PO_RANK) and timeout < 10:
        time.sleep(0.1)
        timeout += 1
    if timeout == 10:
        return None
    return comm.recv(source=PO_RANK)
    