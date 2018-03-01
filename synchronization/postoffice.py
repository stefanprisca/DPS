from mpi4py import MPI
import time
import random
comm = MPI.COMM_WORLD

class Package:
  def __init__(self, contents, timestamp):
     self.Contents = contents
     self.Timestamp = timestamp
  
  def __repr__(self):
    return "<- Contents: <{}> ; Timestamp:<{}> ->".format(self.Contents, self.Timestamp)

PO_RANK = 0

class PostOffice:
  def __init__(self):
    self.clock = 0
  
  def send(self, contents, dest):
    self.clock += 1
    package = Package(contents, self.clock)
    comm.send(package, dest)

class DeliveryUnit:
  def __init__(self, id):
    self.ID = id
    self.clock = 0
    self.delivery_period = 2

  def receiveAndDeliver(self):
    file = open("./logs/du_log{}.txt".format(self.ID), "w")
    packages = []
    while True:
        package = self.waitForPackage()
        if package == None:
          # PO stopped sending packages. Stop our loop as well
          break 
        
        self.clock += 1
        packages.append(package)
        file.write("Delivery unit got package {} \n".format(package))
        if self.clock % self.delivery_period == 0:
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
    