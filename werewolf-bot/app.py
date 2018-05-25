from flask import Flask, request, send_file
import json
import requests
import random

global roles
roles = ['']*5
roles.append('Werewolf Doctor Seer Hunter Villager')
roles.append('Werewolf Doctor Seer Hunter Villager Villager')
roles.append('Werewolf Doctor Seer Hunter Villager Villager Villager')
roles.append('Werewolf Doctor Seer Hunter Villager Villager Villager Villager')
roles.append('Werewolf Doctor Seer Hunter Villager Villager Villager Villager Villager')
roles.append('Werewolf Doctor Seer Hunter Villager Villager Villager Villager Villager Villager')

global desc
desc = dict()
desc ['Werewolf'] = '[Warewolf] \ uDBC0 \ uDC5E \ n memiliki Kemampuan Aktif pada malam hari. Anda dapat memilih untuk membunuh salah satunya. \ UDBC0 \ uDC77 Kiat! \ N Cobalah melarikan diri. Tertangkap oleh orang lain (berbohong) bertahan sampai dua yang terakhir dalam lingkaran (termasuk serigala) dan sisanya bukan Hunter, jadi ini kemenangan! '
desc ['Doctor'] = '[Villager] \ uDBC0 \ uDC90 \ n memiliki Kemampuan Aktif selama malam. | \ Tip UDBC0 \ uDC77! \ Saya mencoba membantu orang-orang yang kemungkinan besar dibunuh oleh serigala, seperti banyak bicara'
desc ['Seer'] = '[Villager] \ uDBC0 \ uDC90 \ n memiliki Kemampuan Aktif pada malam hari. | \ UdBC0 \ uDC77 Kiat! \ N Cobalah untuk mengambil serigala secepat mungkin dan cobalah untuk tidak berbicara terlalu banyak sehingga serigala tahu itu Pelihat karena itu akan dibunuh.'
desc ['Hunter'] = 'Villager memiliki Kemampuan Pasif. Jika Anda bertahan hidup, Jadilah pemenang! | \ UDBC0 \ uDC77 Kiat! \ N Cobalah untuk tetap tenang. Tunggu permainan selesai. Jangan terbunuh sebelum akhir permainan atau mencoba membantu dokter'
desc ['Villager'] = 'Team [Villager] \ uDBC0 \ uDC90 \ n Tidak dapat melakukan apa pun selain Buffy yang lain dan membantu menemukan serigala. \ uDBC0 \ uDC95 | \ uDBC0 \ uDC77 Kiat! \ n Mencoba saling membantu, lawan 5555 '

global LINE_API_KEY
LINE_API_KEY = 'Ue2ee3be0d0f82914581b33b764d3d282'

app = Flask(__name__)

@app.route('/')
def index():
    return 'This is chatbot server.'

@app.route('/img')
def img():
    filename = 'img/'+request.args.get('role')+'.jpg'
    return send_file(filename, mimetype='image/jpeg')

@app.route('/bot', methods=['POST'])
def bot():
    #locked = getLockingStatus()
    replyStack = []
    msg_in_json = request.get_json()
    msg_in_string = json.dumps(msg_in_json)
    replyToken = msg_in_json["events"][0]['replyToken']

    userID =  msg_in_json["events"][0]['source']['userId']
    msgType =  msg_in_json["events"][0]['message']['type']
    
    if msgType != 'text':
        reply(replyToken, ['Only text is allowed.'])
        return 'OK',200
    
    text = msg_in_json["events"][0]['message']['text'].lower().strip()
    '''
    if text in ['!lock','!locked']:
        lock()
        pushSticker(userID,"1","408")
        reply(replyToken, ['See you! chatbot is locked.'])
        return 'OK',200

    if locked:
        if text == 'qwertyasd11':
            unlock()
            pushSticker(userID,"2","144")
            reply(replyToken, ['Yay! chatbot is ready.'])
            return 'OK',200
        pushSticker(userID,"2","39")
        replyStack.append('Chatbot is locked!')
        replyStack.append('Passcode needed.')
        reply(replyToken, replyStack)
        return 'OK',200
    '''
    if text in ['join','play']:
        # Acknowledge all player that already in room.
        name = getProfiles(userID)['displayName']
        number_of_player = countPlayer()+1
        with open('db/registered.txt','r') as data_file:
            for line in data_file:
                push(line,[name +' has joined the room! ('+str(number_of_player)+')'])

        # Acknowledge player that recently joined the room.
        with open('db/registered.txt','a') as data_write:
            data_write.write(userID+"\n")
        replyStack.append('You have joined the room! ('+str(number_of_player)+')')
        reply(replyToken, replyStack)
        return 'OK',200

    elif text in ['quit']:
        # Acknowledge all player that already in room.
        name = getProfiles(userID)['displayName']
        number_of_player = countPlayer()-1
        saved = list()
        with open('db/registered.txt','r') as data_file:
            for line in data_file:
                if line[:-1] == userID:
                    continue
                saved.append(line[:-1])
                push(line,[name +' has left the room! ('+str(number_of_player)+')'])
        open('db/registered.txt', 'w').close()

        # Acknowledge player that recently left the room.
        with open('db/registered.txt','a') as data_write:
            for player in saved:
                data_write.write(player+"\n")
        replyStack.append('You have left the room!')
        reply(replyToken, replyStack)
        return 'OK',200
        
    elif text == 'reset':
        with open('db/registered.txt','r') as data_file:
            for line in data_file:
                pushSticker(userID,"2","23")
                push(line,['You have been kicked!'])
        open('db/registered.txt', 'w').close()
        return 'OK',200

    elif text in ['ls','list']:
        lists = 'Users List\n'
        count = 0
        with open('db/registered.txt','r') as data_file:
            for line in data_file:
                if len(line) == 0:
                    continue
                count += 1
                try:
                    name = getProfiles(line[:-1])['displayName']
                    lists += "- " + name + "\n"
                except:
                    pass
        if lists == 'Users List\n':
            lists = 'Room is empty.'
        else:
            lists += str(count) + ' user(s) in room.'
        reply(replyToken, [lists])
        return 'OK',200
    elif text in ['go']:
        number_of_player = countPlayer()
        if number_of_player < 5:
            pushSticker(userID,"1","107")
            reply(replyToken, ['Sorry, minimum players is 5'])
            return 'OK',200
        role = roles[number_of_player].split()
        with open('db/registered.txt','r') as data_file:
            for line in data_file:
                draw = ''
                while len(draw) <= 0:
                    lucky = random.randrange(number_of_player)
                    draw = role[lucky]
                    role[lucky] = ''
                pushImage(line,draw)
                description = desc[draw].split('|')
                push(line,['\uDBC0\uDC35 '+draw+' \uDBC0\uDC35', description[0], description[1]])
        open('db/registered.txt', 'w').close()
        return '0K',200
    elif text in ['cara bermain?']:
         replyStack.append ('\ uDBC0 \ uDC77 Cara Bermain?')
         replyStack.append ('yang ingin memainkan game, ketik play atau join ')
         replyStack.append ('yang ingin keluar dari game, ketik quit atau quit ')
         replyStack.append ('Saat orang memainkan 5+ orang, ketik start game atau go ')
    else:
         replyStack.append('\uDBC0\uDC5E Ketik ? Untuk melihat cara menggunakan')
    reply(replyToken, replyStack[:5])
    return 'OK',200

def countPlayer():
    count = 0
    with open('db/registered.txt','r') as data_file:
        for line in data_file:
            if len(line) == 0:
                continue
            count += 1
    return count
 
def getLockingStatus():
    with open('db/locked.txt','r') as data_file:
        for line in data_file:
            if line.strip() == 'unlocked':
                return False
    return True

def lock():
    open('db/locked.txt', 'w').close()
    return

def unlock():
    with open('db/locked.txt','a') as data_write:
            data_write.write('unlocked')
    return

def reply(replyToken, textList):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = []
    for text in textList:
        msgs.append({
            "type":"text",
            "text":text
        })
    data = json.dumps({
        "replyToken":replyToken,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return

def pushSticker(userID, packId, stickerId):
    LINE_API = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = [{
        "type": "sticker",
        "packageId": packId,
        "stickerId": stickerId
    }]
    data = json.dumps({
        "to": userID,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return
    
def pushImage(userID, role):
    LINE_API = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = [{
        "type": "image",
        "originalContentUrl": "https://werewolf-bot-server.herokuapp.com/img?role="+role,
        "previewImageUrl": "https://werewolf-bot-server.herokuapp.com/img?role="+role+"_p"
    }]
    data = json.dumps({
        "to": userID,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return
    

def push(userID, textList):
    LINE_API = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = []
    for text in textList:
        msgs.append({
            "type":"text",
            "text":text
        })
    data = json.dumps({
        "to": userID,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return

def getContent(id):
    LINE_API = 'https://api.line.me/v2/bot/message/'+str(id)+'/content'
    r = requests.get(LINE_API, headers={'Authorization': LINE_API_KEY})
    r = r.content
    return r

def getProfiles(id):
    LINE_API = 'https://api.line.me/v2/bot/profile/'+str(id)
    r = requests.get(LINE_API, headers={'Authorization': LINE_API_KEY})
    r = r.content
    return json.loads(r.decode('utf8'))

if __name__ == '__main__':
    app.run()