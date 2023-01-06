import time
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour
from spade import quit_spade

# Agent 1 - Ujak

# sva pitanja koja se mogu postaviti NPC-ju 
mogucaPitanjaArr = [
    "1. Što si radio zadnjih par sati?",
    "2. Što ti znaš o toj narukvici?",
]
# prva pitanja u obliku stringa da lakše možemo slati
mogucaPitanja= "\n".join(mogucaPitanjaArr)

# Dodana pitanja koja se otvaraju ovisno o stanju
dodatnaPitanjaPoStanjima = {
  2: "3. Možda bi si trebao pregledati taj mjehur, jer znam da si bio danas više od 5 puta na WC-u.",
  3: "4. Jako zanimljivo...",
  4: "5. A da tebi ta narukvica nije malo više značila? Djedu je bila najdraža narukvica i nikome je nije htio dati, a na kraju završi kod tvoje mlađe sestre umjesto kod tebe?",
  5: "6. *uperi prstom u njega i zastraši ga pogledom*"
}

# odgovori NPC-ja na pitanja - odgovaraju  indexi
moguciOdgovori = [
    "Ništa posebno družio se tu s vama... 2 puta bio na WC-u radi mog slabog mjehura, znaš kako mi je to...",
    "Ma to je bila neka dedina... ",
]

# Dodani odgovori koji se otvaraju ovisno o stanju
dodatniMoguciOdgovori = {
  2: "Ma možda sam i toliko... star sam već, tko bi sve to zapamtio? haha",
  3: "Hmmm....",
  4: "Možda mi je bila lijepa i sve i još je srebrna, ali nebi ja tako nešto napravio...",
  5: "(drhtavim tihim glasom...) O moj bože što sam postao????"
}

class AgentNPC1(Agent):
  # treba dohvatiti odgovorena pitanja agenta NPC2 jer neka pitanja ovise o njegovima
  class DohvatiOdgovorenaPitanjaAgenata(PeriodicBehaviour):
    async def run(self):
      # Dohvati odgovore drugih agenata (NPC3 - mama)
      if self.agent.odgovorNPC3 == False:
        print("Dohvaćanje odgovora NPC3.")
        msgDohvatiOdgovore = spade.message.Message(
          to="iva-vas-projekt-npc3@5222.de",
          body="REQUEST_ANSWERED",
        )
        await self.send(msgDohvatiOdgovore)   
        
      # Dohvati odgovore drugih agenata (NPC4 - Baba)
      if self.agent.odgovorNPC3 == True and self.agent.odgovorNPC4 == False:
        print("Dohvaćanje odgovora NPC4.")
        msgDohvatiOdgovore = spade.message.Message(
          to="iva-vas-projekt-npc4@5222.de",
          body="REQUEST_ANSWERED",
        )
        await self.send(msgDohvatiOdgovore)   
  
  # Konačni automat  
  class FSMAgentBehaviour(FSMBehaviour): 
    async def on_start(self):
      # postavi sve varijable
      self.agent.odgovorenaPitanja = []
      self.agent.odgovorNPC3 = False
      self.agent.odgovorNPC4 = False
      self.agent.pitanja = mogucaPitanja
      self.agent.odgovori = moguciOdgovori
      self.agent.dodatnaPitanja = dodatnaPitanjaPoStanjima
      self.agent.dodatniOdgovori = dodatniMoguciOdgovori
      self.agent.resetMe = False
      print("Starting NPC1 - Ujak")
      print("\nČekam poruku...\n")

    async def on_end(self):
      print("Shutting down NPC1 - Ujak")
  
  class Stanje1(State):
    async def run(self):
      print("\nU stanju 1.\n")

      # čekaj poruke
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
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja
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
        # dohvaćeni odgovori agenta NPC3
        elif isinstance(msg.body, str) and msg.body.startswith("ANSWERED_") and str(msg.sender).find("npc3") != -1:
            answered = msg.body.split("_")[1].split(";;")
            # ako ima traženo pitanje prebaci ga u stanje2
            if answered.__contains__("2") == True:
              self.agent.odgovorNPC3 = True
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorenaPitanja.__contains__(1) == True and self.agent.odgovorNPC3 == True):
          self.set_next_state("Stanje2")
      else:  
          self.set_next_state("Stanje1")
     
  class Stanje2(State):
    async def run(self):
      print("\nU stanju 2.\n")
      
      # čekaj poruke
      msg = await self.receive(timeout=5)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply() 

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n\n" + self.agent.dodatnaPitanja.get(2)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2)
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
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorenaPitanja.__contains__(2) == True):
          self.set_next_state("Stanje3")
      else:  
          self.set_next_state("Stanje2")
   
  class Stanje3(State):
    async def run(self):
      print("\nU stanju 3.\n")

      # čekaj poruke
      msg = await self.receive(timeout=5)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply() 

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
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
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        # dohvaćeni odgovori agenta NPC3
        elif isinstance(msg.body, str) and msg.body.startswith("ANSWERED_") and str(msg.sender).find("npc4") != -1:
            answered = msg.body.split("_")[1].split(";;")
            # ako ima traženo pitanje prebaci ga u stanje2
            if answered.__contains__("3") == True:
              self.agent.odgovorNPC4 = True
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorenaPitanja.__contains__(3) == True and self.agent.odgovorNPC4 == True):
          self.set_next_state("Stanje4")
      else:  
          self.set_next_state("Stanje3") 
      
  class Stanje4(State):
    async def run(self):
      print("\nU stanju 4.\n")
      
      # čekaj poruke
      msg = await self.receive(timeout=5)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply() 

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "3":
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        elif msg.body == "4":
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        elif msg.body == "5":
            novaPoruka.body = self.agent.dodatniOdgovori.get(4) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3)  + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 4 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(4)
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorenaPitanja.__contains__(3) == True and self.agent.odgovorNPC4 == True):
          self.set_next_state("Stanje5")
      else:  
          self.set_next_state("Stanje4") 
          
          
  class Stanje5(State):
    async def run(self):
      print("\nU stanju 5.\n")
      
      # čekaj poruke
      msg = await self.receive(timeout=5)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply() 

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "3":
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        elif msg.body == "4":
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        elif msg.body == "5":
            novaPoruka.body = self.agent.dodatniOdgovori.get(4) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 4 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(4)
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      elif(self.agent.odgovorenaPitanja.__contains__(4)):
          self.set_next_state("Stanje6")
      else:  
          self.set_next_state("Stanje5") 
          
  
  class Stanje6(State):
    async def run(self):
      print("\nU stanju 6.\n")
      
      # čekaj poruke
      msg = await self.receive(timeout=5)
      
      # ako nema poruke na radi ništa
      if(msg):
        print(f"Primatelj: Primio sam poruku {msg.body}")
        novaPoruka = msg.make_reply() 

        # odgovori ovisno o poruci igrača
        if msg.body == "Bok":
            novaPoruka.body = self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
        elif msg.body == "1":
            novaPoruka.body = self.agent.odgovori[0] + "\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 0 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(0)
        elif msg.body == "2":
            novaPoruka.body = self.agent.odgovori[1] + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 1 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(1)
        elif msg.body == "3":
            novaPoruka.body = self.agent.dodatniOdgovori.get(2) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 2 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(2)
        elif msg.body == "4":
            novaPoruka.body = self.agent.dodatniOdgovori.get(3) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 3 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(3)
        elif msg.body == "5":
            novaPoruka.body = self.agent.dodatniOdgovori.get(4) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4) + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 4 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(4)
        elif msg.body == "6":
            novaPoruka.body = self.agent.dodatniOdgovori.get(5) + "\n\n" + self.agent.pitanja + "\n" + self.agent.dodatnaPitanja.get(2) + "\n" + self.agent.dodatnaPitanja.get(3) + "\n" + self.agent.dodatnaPitanja.get(4)  + "\n" + self.agent.dodatnaPitanja.get(5)
            await self.send(novaPoruka)
            # dodaj u odgovorena pitanja index pitanja
            if 5 not in self.agent.odgovorenaPitanja:
              self.agent.odgovorenaPitanja.append(5)
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
            novaPoruka.body = "ANSWERED_" + ";;".join(str(x) for x in self.agent.odgovorenaPitanja)
            await self.send(novaPoruka)
        
        # treba biti ovo jer se iz nekog razloga dva puta izvršava ovaj dio
        # pa se 2 puta šalje odgovor
        msg.body = ""

      # postavi next_state ovisno o okolnostima      
      if(self.agent.resetMe == True):
        self.agent.resetMe = False
        self.set_next_state("Stanje1")
      else:  
          self.set_next_state("Stanje6") 
      

  async def setup(self):   
    fsm = self.FSMAgentBehaviour()
    self.add_behaviour(fsm)
    
    fsm.add_state(name="Stanje1", state=self.Stanje1(), initial=True)
    fsm.add_state(name="Stanje2", state=self.Stanje2())
    fsm.add_state(name="Stanje3", state=self.Stanje3())
    fsm.add_state(name="Stanje4", state=self.Stanje4())
    fsm.add_state(name="Stanje5", state=self.Stanje5())
    fsm.add_state(name="Stanje6", state=self.Stanje6())
    
    fsm.add_transition(source="Stanje1", dest="Stanje1")
    fsm.add_transition(source="Stanje2", dest="Stanje2")
    fsm.add_transition(source="Stanje3", dest="Stanje3")
    fsm.add_transition(source="Stanje4", dest="Stanje4")
    fsm.add_transition(source="Stanje5", dest="Stanje5")
    fsm.add_transition(source="Stanje6", dest="Stanje6")
    fsm.add_transition(source="Stanje1", dest="Stanje2")
    fsm.add_transition(source="Stanje2", dest="Stanje1")
    fsm.add_transition(source="Stanje2", dest="Stanje3")
    fsm.add_transition(source="Stanje3", dest="Stanje1")
    fsm.add_transition(source="Stanje3", dest="Stanje4")
    fsm.add_transition(source="Stanje4", dest="Stanje1")
    fsm.add_transition(source="Stanje4", dest="Stanje5")
    fsm.add_transition(source="Stanje5", dest="Stanje1")
    fsm.add_transition(source="Stanje5", dest="Stanje6")
    fsm.add_transition(source="Stanje6", dest="Stanje1")
    
    self.add_behaviour(fsm)
    
    fsm = self.DohvatiOdgovorenaPitanjaAgenata(period=5)
    self.add_behaviour(fsm)
   
    
if __name__ == "__main__":
  npc1 = AgentNPC1("iva-vas-projekt-npc1@5222.de", "12345678")
  pokretanje = npc1.start()
  pokretanje.result()

  npc1.web.start(hostname="127.0.0.1", port="10001")

  while npc1.is_alive():
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      break

  npc1.stop()
  quit_spade()
        