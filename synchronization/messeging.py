from mpi4py import MPI

comm = MPI.COMM_WORLD

class Message:
  def __init__(self, msg):
    self.Message = msg

class TimestampedMessage(Message):
  def __init__(self, msg, timestamp):
     Message.__init__(msg)
     self.Timestamp = timestamp

class Dude:
  def __init__(self, id):
    self.Id = id
    self.Rank = comm.Get_rank()

  def send(self, message):
    return
  