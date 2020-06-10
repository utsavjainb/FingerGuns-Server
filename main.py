import  datetime, requests, time, threading, logging, json
from flask import Flask, render_template, request, jsonify
from collections import Counter
#from flask_restful import Resource, Api
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

moves = {"READY" : "0","RELOAD" : "1" ,"SHIELD" : "2" ,"SHOOT" : "3" }
rmoves = {"0": "READY" ,  "1": "RELOAD" ,"2": "SHIELD", "3" :"SHOOT"} 

class Game:
    def __init__(self):
        self.p1id = "1"  
        self.p2id = "2" 
        self.urls = {self.p1id: "", self.p2id: ""} 
        self.started = False
        self.readystate = {self.p1id: False, self.p2id: False} 
        self.currmove = {self.p1id: False, self.p2id: False} 
        self.prevmove = {self.p1id: False, self.p2id: False} 
        #self.bullets = {self.p1id: 0, self.p2id: 0} 
        self.bullets = Counter({self.p1id: 0, self.p2id: 0})
        self.onebullet = Counter({self.p1id: 1, self.p2id: 1})
        self.winner = None
        self.roundnum = 1
        self.p1move_dist = {"RELOAD" : 0 ,"SHIELD" : 0 ,"SHOOT" : 0} 
        self.p2move_dist = {"RELOAD" : 0 ,"SHIELD" : 0 ,"SHOOT" : 0} 

    def startgame(self):
        self.started = True
        while (not all(self.readystate.values())):
            #print("waiting for players to ready up...")
            #print("gamestate: ", game.readystate)
            time.sleep(2)
        print("Players Ready!")
    
    def requestmove(self, pid):
        if pid == self.p1id:
            packet = { "msg" : "SENDMOVE" , "bulletcnt" : self.bullets[pid], "roundnum" : self.roundnum ,"pmove" : self.prevmove[self.p1id], "oppmove": self.prevmove[self.p2id] }
        else:
            packet = { "msg" : "SENDMOVE" , "bulletcnt" : self.bullets[pid], "roundnum" : self.roundnum ,"pmove" : self.prevmove[self.p2id], "oppmove": self.prevmove[self.p1id] }
        res = (requests.post(url=self.urls[pid], data = packet)).json()   
        self.currmove[res["pid"]] = res["move"]
         
    def hasbullets(self, pid):
        if self.bullets[pid] > 0:
            return True
        return False
         
    def evalmoves(self):
        p1move = self.currmove[self.p1id]         
        p2move = self.currmove[self.p2id]         

        #storing in movedist
        print('incrementing move count')
        self.p1move_dist[rmoves[p1move]] += 1
        self.p2move_dist[rmoves[p2move]] += 1
        print(self.p1move_dist)

        print("p1move: ", rmoves[p1move])
        print("p2move: ", rmoves[p2move])
        if p1move == moves["RELOAD"]:
            self.bullets[self.p1id] += 1
        if p2move == moves["RELOAD"]:
            self.bullets[self.p2id] += 1
            
        #both shoot 
        if p1move == p2move == moves["SHOOT"]:
            if self.bullets[self.p1id] > 0 and self.bullets[self.p2id] > 0 :
                #tie
                self.bullets -= self.onebullet
            elif self.bullets[self.p1id] > 0: 
                #p2 does not have bullets, p1 wins
                self.winner = self.p1id
            else:
                #p1 does not have bullets, p2 wins
                self.winner = self.p2id

        #p1 shoots       
        elif p1move == moves["SHOOT"] and self.bullets[self.p1id] > 0:
            if p2move == moves["SHIELD"]:
                #p2 blocks p1 bullet
                self.bullets[self.p1id] -= 1
            else:
                #p2 is reload but shot by p1, p1 wins
                self.winner = self.p1id

        #p2 shoots        
        elif p2move == moves["SHOOT"] and self.bullets[self.p2id] > 0:
            if p1move == moves["SHIELD"]:
                #p1 blocks p2 bullet
                self.bullets[self.p2id] -= 1
            else:
                #p1 is reload but shot by p2, p2 wins
                self.winner = self.p2id
                
        #dont need to handle cases if one player reload and other shields, or if both are shielding
            
    def sendround(self):
        packet = { "msg" : "ROUNDRES" , "pmove" : self.currmove[self.p1id], "oppmove": self.currmove[self.p2id] }
        res = requests.post(url=self.urls[self.p1id], data = packet)   
        packet = { "msg" : "ROUNDRES" , "pmove" : self.currmove[self.p2id], "oppmove": self.currmove[self.p1id] }
        res = requests.post(url=self.urls[self.p2id], data = packet)  
           
 

    def gameovermsg(self, pid):
        if pid == self.p1id:
            #packet = { "msg" : "GAMEOVER" , "winner" : self.winner, "PStats": self.p1move_dist, "OppStats": self.p2move_dist}
            packet = { "msg" : "GAMEOVER" , "winner" : self.winner, "P_RELOAD": self.p1move_dist["RELOAD"], "P_SHIELD": self.p1move_dist["SHIELD"], "P_SHOOT": self.p1move_dist["SHOOT"], "O_RELOAD": self.p2move_dist["RELOAD"], "O_SHIELD": self.p2move_dist["SHIELD"], "O_SHOOT": self.p2move_dist["SHOOT"], "pmove" : self.currmove[self.p1id], "oppmove": self.currmove[self.p2id] }

        else:
            packet = { "msg" : "GAMEOVER" , "winner" : self.winner, "O_RELOAD": self.p1move_dist["RELOAD"], "O_SHIELD": self.p1move_dist["SHIELD"], "O_SHOOT": self.p1move_dist["SHOOT"], "P_RELOAD": self.p2move_dist["RELOAD"], "P_SHIELD": self.p2move_dist["SHIELD"], "P_SHOOT": self.p2move_dist["SHOOT"] , "pmove" : self.currmove[self.p2id], "oppmove": self.currmove[self.p1id] }

        #joutput = json.dumps(output)
        #packet = json.dumps(packet)
        #packet = jsonify(packet)
        print("packet: ", packet)
        try:
            print("sending game stats")
            res = requests.post(url=self.urls[pid], data = packet)
            print("Game over acked: ", res)
        except:
            print("no response")
    
    def gameloop(self):
        print("starting main game loop")
        while(self.winner is None):
            t1 = threading.Thread(target=self.requestmove, args=(self.p1id, ))
            t2 = threading.Thread(target=self.requestmove, args=(self.p2id, ))
            t1.start()
            t2.start()

            #spin until both players have entered a move
            while(not all(self.currmove.values())):
                time.sleep(2)
                pass
            t1.join()
            t2.join()

            self.sendround()

            self.evalmoves()
            self.roundnum += 1

            #reset currmoves to False
            for pid in self.currmove:
                self.prevmove[pid] = self.currmove[pid]
                self.currmove[pid] = False
    
        print("winner: ", self.winner)
        t1 = threading.Thread(target=self.gameovermsg, args=(self.p1id, ))
        t2 = threading.Thread(target=self.gameovermsg, args=(self.p2id, ))
        t1.start()
        t2.start()
        

    

@app.route('/receiver', methods = ['POST'])
#function receives player moves
def receiver():
    data = request.form

    pid = data["pid"]
    purl = data["purl"] + "/receiver"

    if data["move"] == moves["READY"]:
        game.readystate[pid] = True
        game.urls[pid] = purl 
        ret = jsonify(result=1, msg= "PLAYER_READY")
        return ret
    elif data["move"] == moves["RELOAD"]:
        pass
    elif data["move"] == moves["SHIELD"]:
        pass
    elif data["move"] == moves["SHOOT"]:
        pass
    else:
        return jsonify(result=1, msg= "NOT OK")
    ret = jsonify(result=1, msg= "OK")
    return ret

def flaskThread(portnum):
    app.run(port=portnum, debug=False)

if __name__ == '__main__':
    game = Game()
    ft = threading.Thread(target=flaskThread, args=(8080,)) 
    ft.start()
    while(True):
        game.startgame()
        game.gameloop()
        game = Game()

