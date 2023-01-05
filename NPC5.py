import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade import quit_spade

# Agent 5 - Gini (pas)

# sva pitanja koja se mogu postaviti NPC-ju
mogucaPitanjaArr = [
    "1. Jesi vidjela nešto sumnjivo?",
    "2. Evo ti keksića!",
    "3. Vau vau?"
]
# prva pitanja u obliku stringa da lakše možemo slati
mogucaPitanja= "\n".join(mogucaPitanjaArr)

# odgovori NPC-ja na pitanja - odgovaraju indexi
moguciOdgovori = [
    "Vau vau vau!",
    "Vau vau vau vau vau!!!",
    "Mijau!"
]

class AgentNPC5(Agent):  
  class PrimajOdgovarajNaPoruke(CyclicBehaviour): 
    async def on_start(self):
      # postavi sve varijable
      self.agent.pitanja = mogucaPitanja
      self.agent.odgovori = moguciOdgovori
      print("Starting NPC5 - Gini (pas)")
      print("\nČekam poruku...\n")

    async def on_end(self):
      print("Shutting down NPC5 - Gini (pas)")
      
    async def run(self): 
      msg = await self.receive(timeout=10)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        
        novaPoruka = msg.make_reply()

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        elif msg .body== "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        elif msg .body== "3":
            novaPoruka.body = self.agent.odgovori[2] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
                
  async def setup(self):
    fsm = self.PrimajOdgovarajNaPoruke()
    self.add_behaviour(fsm)


if __name__ == "__main__":
  npc5 = AgentNPC5("iva-vas-projekt-npc5@5222.de", "12345678")
  pokretanje = npc5.start()
  pokretanje.result()

  npc5.web.start(hostname="127.0.0.1", port="10005")

  while npc5.is_alive():
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      break

  npc5.stop()
  quit_spade()
        