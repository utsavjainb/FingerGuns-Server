import  datetime, requests, time, threading
from flask import Flask, render_template, request, jsonify
from collections import Counter
#from flask_restful import Resource, Api
app = Flask(__name__)

moves = {"READY" : "0","RELOAD" : "1" ,"SHIELD" : "2" ,"SHOOT" : "3" }

class Game:
    def __init__(self):
        self.p1id = "1"  
        self.p2id = "2" 
        self.p1url = ""
        self.p2url = ""
        self.started = False
        self.readystate = {self.p1id: False, self.p2id: False} 
        self.currmove = {self.p1id: False, self.p2id: False} 
        #self.bullets = {self.p1id: 0, self.p2id: 0} 
        self.bullets = Counter({self.p1id: 0, self.p2id: 0})
        self.decrementbullet = Counter({self.p1id: 1, self.p2id: 1})
        self.winner = None

    def startgame(self):
        self.started = True
        while (not all(self.readystate.values())):
            #print("waiting for players to ready up...")
            #print("gamestate: ", game.readystate)
            time.sleep(2)
        print("Players Ready!")
    
    def requestmove(self, pid, purl):
        data = { "msg" : "SENDMOVE" , "bulletcnt" : self.bullets[pid] }
        res = (requests.post(url=purl, data = packet)).json()   
        self.currmove[res["pid"]] = res["move"]
    
    def hasbullets(self, pid):
        if self.bullets[pid] > 0:
            return True
        return False
         
    def evalmoves(self):
        p1move = self.currmove[self.p1id]         
        p2move = self.currmove[self.p2id]         
        if p1move = moves["RELOAD"]:
            self.bullets[self.p1id] += 1
        if p2move = moves["RELOAD"]:
            self.bullets[self.p2id] += 1
            
        #both shoot 
        if p1move == p2move == moves["SHOOT"] 
            if self.bullets[self.p1id] > 0 and self.bullets[self.p2id] > 0 :
                #tie
                self.bullets -= self.decrementbullet
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
            

    def gameloop(self):
        while(self.winner is None):
            t1 = threading.Thread(target=self.requestmove, args=(self.p1id, self.p1url, ))
            t2 = threading.Thread(target=self.requestmove, args=(self.p2id, self.p2url, ))
            t1.start()
            t2.start()

            #spin until both players have entered a move
            while(not all(self.currmove.values())):
                pass

            self.evalmoves()

            #reset currmoves to False
            for pid in self.currmove:
                self.currmove[pid] = False
    
        print(self.winner)
        
        data = { "msg" : "GAMEOVER" , "winner" : winnerid}
        post(data)

    

@app.route('/receiver', methods = ['POST'])
#function receives player moves
def receiver():
    data = request.form
    if data["move"] == moves["READY"]:
        pid = data["player"]
        game.readystate[pid] = True
        ret = jsonify(result=1, msg= "PLAYER_READY")
        return ret
    elif data["move"] == moves["RELOAD"]:
        pass
    elif data["move"] == moves["SHIELD"]:
        pass
    elif data["move"] == moves["SHOOT"]:
        pass
    else:
        return jsonify(result=1, msg= " NOT OK")
    ret = jsonify(result=1, msg= "OK")
    return ret

def flaskThread(portnum):
    app.run(port=portnum, debug=False)

if __name__ == '__main__':
    game = Game()
    ft = threading.Thread(target=flaskThread, args=(8080,)) 
    ft.start()
    game.startgame()