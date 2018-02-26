from messeging import *

def chatReceivesMessages():
  dudes = {"P1":Dude(1), "P2":Dude(2)}
  dudes["P1"].send("Hej, jeg hedder P1!")
  dudes["P2"].send("Hej P1, jeg hedder P2.")
  dudes["P1"].send("Hvad taler du, P2?")
  dudes["P2"].send("Jeg taler Python!")