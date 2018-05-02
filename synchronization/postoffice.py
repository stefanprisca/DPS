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

  _master_sync_id = 1000
  _bully_election_tag = 1001
  _bully_ok_tag = 1002
  _bully_coordinator_tag = 1003
  _time_to_elect = 0.2
  _elect_timeout = 0.2

  _is_bully = False

  def __init__(self, id, topic_id, po_ids):
    self.id = id
    self.clock = random.randint(0, 10)
    # print('Created post office')
    self.topic_id = int(topic_id)
    self.po_ids = po_ids
  
  def send(self, contents, dest):

    # before sending, check if there is any sync message for the master clock
    # if there is none, do a Bully ellection
    if not self._is_bully:
      self.sync_clock_or_elect()
    else:
      self.send_master_sync()

    self.clock += 1
    package = Package(contents, self.clock)
    comm.send(package, dest=dest, tag=self.topic_id)
    print('Sent package', self.topic_id, dest, self.clock)

  def sync_clock_or_elect(self):
    print(self.id, 'synching...')
    sync_pkg = waitForPackage(self._master_sync_id)
    if sync_pkg is None:
      self._time_to_elect += random.random()
      if self._time_to_elect >= self._elect_timeout:
        existing_coordinator = waitForPackage(self._bully_coordinator_tag)
        if existing_coordinator is not None:
          self.clock = existing_coordinator.Timestamp
          return

        existing_election = waitForPackage(self._bully_election_tag)
        if existing_election is not None:
          print(self.id, '**** Continuing existing election...')
          self.elect_bully(existing_election.Contents)
        else:
          print(self.id, '+++++ Starting new election')
          self.elect_bully(None)
        
        self._time_to_elect = 0
        
    else:
      self.clock = sync_pkg.Timestamp
    return

  def elect_bully(self, initiator):
    i = self.po_ids.index(self.id)
    print(self.id, 'Electing bully')
    
    empty_pckg = Package(self.id, None)
    #TODO: send OK to initiator
    if initiator is not None:
      comm.send(empty_pckg, initiator, tag=self._bully_ok_tag)
    
    candidates = self.po_ids[i+1:]
    print(self.id, 'Candidates during bully election: ', candidates)
    if len(candidates) == 0:
      print('no candidates, sending coordinator...')
      self.send_coordinator()
    else:
      #TODO: send elect messages to candidates
      for candidate in candidates:
        comm.send(empty_pckg, candidate, tag=self._bully_election_tag)
      
      #TODO: wait for OK messages...
      quit_ = True
      for candidate in candidates:
        ok = None #waitForPackage(self._bully_ok_tag)
        if ok is not None:
          quit_ = False
          break
      
      if quit_:
        coord = waitForPackage(self._bully_coordinator_tag)
        if coord is not None:
          print(self.id, 'got coordinator:', coord.Contents)
      else:
        self.send_coordinator()
    return

  def send_coordinator(self):
    i = self.po_ids.index(self.id)
    coord_package = Package(self.id, self.clock)
    followers = self.po_ids[:i]
    print(self.id, 'sending coord messages', followers)
    for follower in followers:
      comm.send(coord_package, follower, tag=self._bully_coordinator_tag)
    self._is_bully = True
  
  def send_master_sync(self):
    i = self.po_ids.index(self.id)
    sync = Package(self.id, self.clock)
    followers = self.po_ids[:i]
    print(self.id, 'sending sync messages', followers)
    for follower in followers:
      comm.send(sync, follower, tag=self._master_sync_id)
    self._is_bully = True
    time.sleep(0.2)

# Delivery unit that receives delivery requests from the PO.
# It will only deliver the packages with a timestamp up to the delivery date
class DeliveryUnit:
  def __init__(self, id, topic_id):
    self.id = id
    self.topic_id = topic_id

    # Use a system clock to decide what will be delivered.
    # Only packages that have been received until this time (their timestamp is less) will be delivered.
    self.clock = 0

    # Use separate clock to determine the delivery period.
    # This is different from the base clock. It just determines when we should deliver, not what we deliver.
    self.delivery_clock = 0
    self.delivery_period = 2

  def receiveAndDeliver(self, log_name):
    file = open("./logs/{}{}.txt".format(log_name, self.id), "w")
    packages = []
    while True:
        package = waitForPackage(self.topic_id)
        if package == None:
          # PO stopped sending packages. Stop our loop as well
          time.sleep(1)
          continue 
        
        print(self.id, 'Got package')
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
def waitForPackage(topic_id):
  timeout = 0
  # Wait to receive something
  
  print('Waiting for package', topic_id)
  while not comm.Iprobe(source=MPI.ANY_SOURCE, tag=topic_id) and timeout < 10:
      time.sleep(random.random())
      timeout += 1
  if timeout == 10:
      print('timed out...no package received', topic_id)
      return None
  return comm.recv(tag=topic_id)
    