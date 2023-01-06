import time
import spade
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade import quit_spade

# Agent koji šalje poruku ukoliko je sve

class AgentGameHostAgent(Agent):
  # treba dohvatiti odgovorena pitanja agenta 
  class DohvatiOdgovorenaPitanjaAgenata(PeriodicBehaviour):
    async def run(self):
        print("Dohvaćanje odgovora NPC1.")
        
        # Dohvati odgovore agenata (NPC1 - Ujak)
        msgNPC1 = spade.message.Message(
          to="iva-vas-projekt-npc1@5222.de",
          body="REQUEST_ANSWERED"
        )
        await self.send(msgNPC1)
        
        msg = await self.receive(timeout=10)

        
        # Pošalji poruku igraču
        msgDohvatiOdgovore = spade.message.Message(
          to="iva-vas-projekt-main@5222.de",
          body="\n\n\n\n\n\n**  Vrijeme je za odabir krivca!  **\n\n\n\n\n\n",
        )
        await self.send(msgDohvatiOdgovore)   
      
            
  async def setup(self):   
    fsm = self.DohvatiOdgovorenaPitanjaAgenata(period=5)
    self.add_behaviour(fsm)
   
    
if __name__ == "__main__":
  gameHost = AgentGameHostAgent("iva-vas-projekt-manager@5222.de", "12345678")
  pokretanje = gameHost.start()
  pokretanje.result()

  gameHost.web.start(hostname="127.0.0.1", port="10006")

  while gameHost.is_alive():
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      break

  gameHost.stop()
  quit_spade()
        