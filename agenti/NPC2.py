import time
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade import quit_spade

# Agent 2 - Tata

# sva pitanja koja se mogu postaviti NPC-ju
mogucaPitanjaArr = [
    "1. Reci mi što znaš o toj ogrlici?",
    "2. Što si ti radio danas kada si na 20 minuta nestao?",
    "3. Zar nisi ti nedavno kupio mami narukvicu? Jesi bio ljubomoran što tvoju nije nosila?"
]
# prva pitanja u obliku stringa da lakše možemo slati
mogucaPitanja= "\n".join(mogucaPitanjaArr)

# odgovori NPC-ja na pitanja - odgovaraju indexi
moguciOdgovori = [
    "Tvoj djed s mamine strane joj je dao tu narukvicu dok su još bili mali. Navodno mu je puno značila.",
    "Pa dobro znaš da sam išao u trgovinu, tebi nije bilo dosta luka uz ćevape!",
    "Nikad ju ne nosi i ne sviđa joj se!?!? A meni je rekla da je obožava... Morat ću je pitati kasnije, hvala milo."
]

class AgentNPC2(Agent):  
  class PrimajOdgovarajNaPoruke(CyclicBehaviour): 
    async def on_start(self):
      # postavi sve varijable
      self.agent.odgovorenaPitanja = []
      self.agent.pitanja = mogucaPitanja
      self.agent.odgovori = moguciOdgovori
      print("Starting NPC2 - Tata")
      print("\nČekam poruku...\n")

    async def on_end(self):
      print("Shutting down NPC2 - Tata")
      
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
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg .body== "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg .body== "3":
            novaPoruka.body = self.agent.odgovori[2] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        # u slučaju da se želi resetirati igra (resetira već odgovorena pitanja kako bi 
        # se pojavila samo ona osnovna)
        elif msg.body == "RESET":
            print(self.agent.odgovorenaPitanja)
            self.agent.odgovorenaPitanja = []
            novaPoruka.body = "\n<<ODGOVORI RESETIRANI>>\n\n" + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        # za komunikaciju između agenata - vraća popis svih odgovorenih pitanja u obliku stringa
        # odvojenih sa ;; sa prefixom ANSWERED_
        elif msg.body == "REQUEST_ANSWERED":
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
                
  async def setup(self):
    fsm = self.PrimajOdgovarajNaPoruke()
    self.add_behaviour(fsm)


if __name__ == "__main__":
  npc2 = AgentNPC2("iva-vas-projekt-npc2@5222.de", "12345678")
  pokretanje = npc2.start()
  pokretanje.result()

  npc2.web.start(hostname="127.0.0.1", port="10002")

  while npc2.is_alive():
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      break

  npc2.stop()
  quit_spade()
        