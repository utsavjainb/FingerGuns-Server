import datetime, json, sys, time, threading, socket, logging
from flask import Flask, render_template, request, jsonify
import requests
import socket, io

s = socket.socket()
print("Starting Fog Server")
listening = True
piport = 12345 
s.bind(('', piport))
print("socket binded to %s" % (piport))
s.listen(5)
print("socket is listening")
c = None
if not c:
    print("waiting for pi connect")
    c, addr = s.accept()
    print("Got connection from ", addr)


app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

moves = {"READY" : "0","RELOAD" : "1" ,"SHIELD" : "2" ,"SHOOT" : "3" }
rmoves = {"0": "READY" ,  "1": "RELOAD" ,"2": "SHIELD", "3" :"SHOOT"}
url = "http://127.0.0.1:8080/receiver"
#url = "http://a1705e88.ngrok.io/receiver"
#url = "https://nodal-figure-276104.wl.r.appspot.com/receiver"
# url = "https://finger-guns-278401.wl.r.appspot.com/receiver"

class Player:
    def __init__(self):
        self.pid = "99" 
        self.pport = ""
        self.purl = ""
        self.gameover = False
        self.winner = None


@app.route('/receiver', methods = ['POST'])
def receiver():
    data = request.form
    packet = {"pid" : player.pid, "move" : moves["READY"] } 
    if data['msg'] == "SENDMOVE":
        print(f"Round {data['roundnum']} , Bullet count {data['bulletcnt']}")
        #get move from RPi
        #pmove = input("Enter your move: ")
        #pmove["move"] = getmove()  
        output = 'Make Move'
        c.send(output.encode('utf-8'))
        pidata = c.recv(1024).decode('utf-8')
        #pidata = {"action": pidata}        
        
        packet["move"] = pidata 

        #packet["move"] = pmove
        return jsonify(packet)
    

    elif data['msg'] == "ROUNDRES":
        #printout round resutl
        print("Your move: ", rmoves[data["pmove"]])
        print("Opp move: ", rmoves[data["oppmove"]])
        return jsonify(packet)
    
    elif data['msg'] == "GAMEOVER":
        packet = {"pid" : player.pid, "msg": "game over ack"} 
        player.gameover = True
        player.winner = data['winner'] 
        return jsonify(packet)
    return "OK"
    
        

#keep sending readyup until game starting message receieved back
def readyup():
    data = {"pid" : player.pid, "move" : moves["READY"], "purl": player.purl }
    packet = json.loads(json.dumps(data))
    time.sleep(2)
    #x = input("ready for game?")
    print("Readying up...")
    while(True):
        res1  = requests.post(url=url, data = packet)
        print(res1)
        res = res1.json()
    
        if res['msg'] == "PLAYER_READY":
            break
        time.sleep(3)
    print("Game has acked you")  

   
def playgame():

    while(True): 
        readyup()
        while(not player.gameover):
            pass
        if player.winner == player.pid:
            print("Won Game! :) ")
        else:
            print("Lost game! :( ")
        player.gameover = False
        player.winner = None


def connectpi():
    c = None
    while not c:
        c, addr = s.accept()
        print("Got connection from ", addr)

def flaskThread(portnum):
    app.run(port=portnum, debug=False)

if __name__ == '__main__':
    player = Player()
    player.pid = sys.argv[1]
    player.pport = sys.argv[2]
    player.purl = sys.argv[3] 
    
    ft = threading.Thread(target=flaskThread, args=(player.pport,)) 
    ft.start()
    playgame()
