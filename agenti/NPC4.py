import time
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour
from spade import quit_spade

# Agent 4 - Baka

# sva pitanja koja se mogu postaviti NPC-ju po
mogucaPitanjaArr = [
    "1. Kako si bako?",
    "2. Tko misliš da bi mogao biti krivac?"
]
# prva pitanja u obliku stringa da lakše možemo slati
mogucaPitanja= "\n".join(mogucaPitanjaArr)

# Dodana pitanja koja se otvaraju ovisno o stanju
dodatnaPitanjaPoStanjima = {
  2: "3. Baš se pitam... Ali ne brini otkriti će se sve!",
  3: "4. Čujem da je ta narukvica baš puno značila dedi... Koja je priča ovdje?"
}

# odgovori NPC-ja na pitanja - odgovaraju  indexi
moguciOdgovori = [
    "Baš sam potresena... Tko bi mogao napraviti nešto takvo?",
    "Ja i dalje ne mogu vjerovati da bi to netko napravio... Moguće da ju je sama negdje zametnula, nebi me čudilo."
]

# Dodani odgovori koji se otvaraju ovisno o stanju
dodatniMoguciOdgovori = {
  2: "Hmmm...",
  3: "Evo on ti je dobio tu narukvicu još od svoje mame koja je nestala par dana nakon što mu ju je dala. Zato se tvoj djed nikad nije htio odvojiti od nje i čak se šalio da je nikome neće dati ni kada umre... Ali je ipak na kraju dao tvojoj mami.",
}

class AgentNPC4(Agent):
  # treba dohvatiti odgovorena pitanja agenta NPC2 jer neka pitanja ovise o njegovima
  class DohvatiOdgovorenaPitanjaAgenata(PeriodicBehaviour):
    async def run(self):
      # Dohvati odgovore drugih agenata (NPC2 - tata)
      if self.agent.odgovorNPC2 == False:
        print("Dohvaćanje odgovora NPC2.")
        msgDohvatiOdgovore = spade.message.Message(
          to="iva-vas-projekt-npc2@5222.de",
          body="REQUEST_ANSWERED",
        )
        await self.send(msgDohvatiOdgovore)   
  
  # Konačni automat  
  class FSMAgentBehaviour(FSMBehaviour): 
    async def on_start(self):
      # postavi sve varijable
      self.agent.odgovorenaPitanja = []
      self.agent.odgovorNPC2 = False
      self.agent.pitanja = mogucaPitanja
      self.agent.odgovori = moguciOdgovori
      self.agent.dodatnaPitanja = dodatnaPitanjaPoStanjima
      self.agent.dodatniOdgovori = dodatniMoguciOdgovori
      self.agent.resetMe = False
      print("Starting NPC4 - Baka")
      print("\nČekam poruku...\n")

    async def on_end(self):
      print("Shutting down NPC4 - Baka")
  
  class Stanje1(State):
    async def run(self):
      print("\nU stanju 1.\n")

      # čekaj poruke
      msg = None
      msg = await self.receive(timeout=5)
      
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
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        # dohvaćeni odgovori agenta NPC2
        elif isinstance(msg.body, str) and msg.body.startswith("ANSWERED_"):
            answered = msg.body.split("_")[1].split(";;")
            # ako ima traženo pitanje prebaci ga u stanje2
            if answered.__contains__("0") == True:
              self.agent.odgovorNPC2 = True
        # u slučaju da se želi resetirati igra (resetira već odgovorena pitanja kako bi 
        # se pojavila samo ona osnovna)
        elif msg.body == "RESET":
            self.agent.odgovorenaPitanja = []
            self.agent.resetMe = True
            novaPoruka.body = "\n<<ODGOVORI RESETIRANI>>\n\n" + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        # za komunikaciju između agenata - vraća popis svih odgovorenih pitanja u obliku stringa
        # odvojenih sa ;;
        elif msg.body == "REQUEST_ANSWERED":
            novaPoruka.body = ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif (self.agent.odgovorenaPitanja.__contains__(1) == True):
        self.set_next_state("Stanje2")
      elif(self.agent.odgovorNPC2 == True):
          self.set_next_state("Stanje3")
      else:  
          self.set_next_state("Stanje1")
      
       
  class Stanje2(State):
    async def run(self):
      print("\nU stanju 2.\n")

      # čekaj poruke
      msg = await self.receive(timeout=10)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply()

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "3":
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        # dohvaćeni odgovori agenta NPC2
        elif isinstance(msg.body, str) and msg.body.startswith("ANSWERED_"):
            answered = msg.body.split("_")[1].split(";;")
            # ako ima traženo pitanje prebaci ga u stanje2
            if answered.__contains__("0") == True:
              self.agent.odgovorNPC2 = True
        # u slučaju da se želi resetirati igra (resetira već odgovorena pitanja kako bi 
        # se pojavila samo ona osnovna)
        elif msg.body == "RESET":
            print(self.agent.odgovorenaPitanja)
            self.agent.odgovorenaPitanja = []
            self.agent.resetMe = True
            novaPoruka.body = "\n<<ODGOVORI RESETIRANI>>\n\n" + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        # za komunikaciju između agenata - vraća popis svih odgovorenih pitanja u obliku stringa
        # odvojenih sa ;;
        elif msg.body == "REQUEST_ANSWERED":
            novaPoruka.body = ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorNPC2 == True):
          self.set_next_state("Stanje4")
      else:  
          self.set_next_state("Stanje2")
         
                
  class Stanje3(State):
    async def run(self):
      print("\nU stanju 3.\n")

      # čekaj poruke
      msg = await self.receive(timeout=10)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply()

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "4":
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        # u slučaju da se želi resetirati igra (resetira već odgovorena pitanja kako bi 
        # se pojavila samo ona osnovna)
        elif msg.body == "RESET":
            print(self.agent.odgovorenaPitanja)
            self.agent.odgovorenaPitanja = []
            self.agent.resetMe = True
            novaPoruka.body = "\n<<ODGOVORI RESETIRANI>>\n\n" + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        # za komunikaciju između agenata - vraća popis svih odgovorenih pitanja u obliku stringa
        # odvojenih sa ;;
        elif msg.body == "REQUEST_ANSWERED":
            novaPoruka.body = ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
      
      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif (self.agent.odgovorenaPitanja.__contains__(1) == True):
          self.set_next_state("Stanje4")
      else:  
          self.set_next_state("Stanje3")

      
  class Stanje4(State):
    async def run(self):
      print("\nU stanju 4.\n") 
  
      # čekaj poruke
      msg = await self.receive(timeout=10)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply()

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "3":
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        elif msg.body == "4":
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) +  "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        # u slučaju da se želi resetirati igra (resetira već odgovorena pitanja kako bi 
        # se pojavila samo ona osnovna)
        elif msg.body == "RESET":
            print(self.agent.odgovorenaPitanja)
            self.agent.odgovorenaPitanja = []
            self.agent.resetMe = True
            novaPoruka.body = "\n<<ODGOVORI RESETIRANI>>\n\n" + "\n\n" + self.agent.pitanja
            await self.send(novaPoruka)
        # za komunikaciju između agenata - vraća popis svih odgovorenih pitanja u obliku stringa
        # odvojenih sa ;;
        elif msg.body == "REQUEST_ANSWERED":
            novaPoruka.body = ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
      
      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
          self.agent.resetMe = False
          self.set_next_state("Stanje1")
      else:  
          self.set_next_state("Stanje4")
      
      
  async def setup(self):   
    fsm = self.FSMAgentBehaviour()
    self.add_behaviour(fsm)
    
    fsm.add_state(name="Stanje1", state=self.Stanje1(), initial=True)
    fsm.add_state(name="Stanje2", state=self.Stanje2())
    fsm.add_state(name="Stanje3", state=self.Stanje3())
    fsm.add_state(name="Stanje4", state=self.Stanje4())
    
    fsm.add_transition(source="Stanje1", dest="Stanje2")
    fsm.add_transition(source="Stanje1", dest="Stanje3")
    fsm.add_transition(source="Stanje2", dest="Stanje4")
    fsm.add_transition(source="Stanje3", dest="Stanje4")
    fsm.add_transition(source="Stanje1", dest="Stanje1")
    fsm.add_transition(source="Stanje2", dest="Stanje2")
    fsm.add_transition(source="Stanje3", dest="Stanje3")
    fsm.add_transition(source="Stanje4", dest="Stanje4")
    fsm.add_transition(source="Stanje2", dest="Stanje1")
    fsm.add_transition(source="Stanje3", dest="Stanje1")
    fsm.add_transition(source="Stanje4", dest="Stanje1")
    
    self.add_behaviour(fsm)
    
    fsm = self.DohvatiOdgovorenaPitanjaAgenata(period=5)
    self.add_behaviour(fsm)
    
if __name__ == "__main__":
  npc4 = AgentNPC4("iva-vas-projekt-npc4@5222.de", "12345678")
  pokretanje = npc4.start()
  pokretanje.result()

  npc4.web.start(hostname="127.0.0.1", port="10004")

  while npc4.is_alive():
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      break

  npc4.stop()
  quit_spade()
        