import datetime, requests, json, sys, time, threading, socket
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

moves = {"READY" : "0","RELOAD" : "1" ,"SHIELD" : "2" ,"SHOOT" : "3" }
pid = 99 
pport = ""
purl = ""
url = "http://127.0.0.1:8080/receiver"
gameover = False


@app.route('/receiver', methods = ['POST'])
def receiver():
    data = request.form
    packet = {"player" : pid, "move" : moves["READY"] } 
    if data['msg'] == "SENDMOVE":
        print("Enter your move: ")
        #get move from RPi
        #pmove["move"] = getmove()  
        res = requests.post(url=url, data = packet)
    
    elif data['msg'] == "GAMEOVER":
        gameover = True
    
        

#keep sending readyup until game starting message receieved back
def readyup():
    url = "http://127.0.0.1:8080/receiver"
    data = {"pid" : pid, "move" : moves["READY"], "purl": purl }
    packet = json.loads(json.dumps(data))
    time.sleep(2)
    while(True):
        res = (requests.post(url=url, data = packet)).json()
        if res['msg'] == "PLAYER_READY":
            break
        time.sleep(3)
    print("Game has acked you")  

   
def playgame():
    while(not gameover):
        pass
    print(winner)
     

def mainloop():
    readyup()
    playgame()

'''
@app.route('/listener', methods = ['POST'])
def listener():
    pass
'''

def flaskThread(portnum):
    app.run(port=portnum, debug=False)

if __name__ == '__main__':
    pid = sys.argv[1]
    pport = sys.argv[2]
    purl = sys.argv[3] 
    
    ft = threading.Thread(target=flaskThread, args=(pport,)) 
    ft.start()
    mainloop()
