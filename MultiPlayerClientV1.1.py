import socket
import threading
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame_textinput
import random
import time
import pygame
import json
import zlib
from colorama import init
from termcolor import colored
import hashlib
 
init()

animation = [".      ", "..     ", "...    ", "..     ", ".      ", "       "]

for i in range(5):
    time.sleep(0.1)
    sys.stdout.write(colored("\rBooting" + animation[i % len(animation)], 'blue'))
    sys.stdout.flush()

print("")

Running = True
Players = []
lastPing = 0

class Player:
    def __init__(self):
        self.pN = "FlamingRCCars"
        self.address = ""
        self.x = 50
        self.y = 50

class Network:
    def __init__(self):
        self.bufferSize = 200
        self.serverAddressPort = ("127.0.0.1", 20001)
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientSocket.settimeout(5)

    def attemptConnect(self, Username, password, address, port):
        global localPlayer

        try:
            results = socket.getaddrinfo(address, port, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        except socket.gaierror:
            print(f"Failed to resolve address {address}")
            return "invalidAddress"
        password = password.encode()
        password = hashlib.sha3_512(password)
        password = password.hexdigest()
        msgFromClient = "RequestID," + Username + "," + password
        bytesToSend = str.encode(msgFromClient)
        bytesToSend = zlib.compress(bytesToSend)
        self.serverAddressPort = (address, int(port))
        self.UDPClientSocket.sendto(bytesToSend, (address, int(port)))
        try:
            msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
        except TimeoutError:
            print(f"Server didn't respond. (2)")
            return "serverNotResponding"
        except ConnectionResetError:
            print(f"Server didn't respond. (1)")
            return "serverNotResponding"
        msgFromServer = zlib.decompress(msgFromServer[0]).decode()
        if msgFromServer == "InvalidPass":
            return "invalidPass"
        msg = msgFromServer.split("@")
        localPlayer.pN = Username
        localPlayer.x = int(msg[0])
        localPlayer.y = int(msg[1])
        return "success"

def MessageHandler(object):
    global Running
    global Players
    while Running:
        message, address = object.UDPClientSocket.recvfrom(object.bufferSize)
        
        message = zlib.decompress(message)
        
        output = json.loads(message.decode())
        Players = []
        for p in output:
            player = Player()
            player.x = p["x"]
            player.y = p["y"]
            player.pN = p["pN"]
            Players.append(player)

def write(text, x, y, color="grey",):
    text = font.render(text, 1, pygame.Color(color))
    text_rect = text.get_rect(center=(x, y))
    return text, text_rect        

def updateServer(netObject):
    global localPlayer
    global lastLocalPlayer
    global lastPing
    global Running
    while Running:
        if lastLocalPlayer.x != localPlayer.x or lastLocalPlayer.y != localPlayer.y or lastLocalPlayer.pN != localPlayer.pN:
            msgFromClient = str(localPlayer.pN) + "@" + str(localPlayer.x) + "@" + str(localPlayer.y)
            bytesToSend = str.encode(msgFromClient)
            bytesToSend = zlib.compress(bytesToSend)
            netObject.UDPClientSocket.sendto(bytesToSend, netObject.serverAddressPort)
            lastLocalPlayer.x = localPlayer.x
            lastLocalPlayer.y = localPlayer.y
            lastLocalPlayer.pN = localPlayer.pN
        elif lastPing == 120:
            msgFromClient = "tick"
            bytesToSend = str.encode(msgFromClient)
            bytesToSend = zlib.compress(bytesToSend)
            netObject.UDPClientSocket.sendto(bytesToSend, netObject.serverAddressPort)
            lastPing = 0
        else:
            lastPing += 1
        time.sleep(0.03)

class getFPS:
    def __init__(self):
        self.timesList = [0.01, 0.01, 0.01, 0.01, 0.01]
        self.pos = 0
        self.startTime = time.time()
    def FPS(self):
        tempFPS = time.time() - self.startTime
        tempFPS = 1/tempFPS
        self.timesList[self.pos] = tempFPS
        self.startTime = time.time()
        self.pos += 1
        if self.pos == 5:
            self.pos = 0
        fps = self.timesList[0]
        fps += self.timesList[1]
        fps += self.timesList[2]
        fps += self.timesList[3]
        fps += self.timesList[4]
        fps = fps/5
        return fps

class Cloud:
    def __init__(self, x, y, speed, aspeed, cloudimg):
        self.cloudimg = cloudimg
        self.pos = 0
        self.x = x
        self.y = y
        self.speed = speed
        self.aspeed = aspeed
    def update(self, win):
        global WIDTH
        self.pos+=1
        self.x += self.speed
        if self.pos < 20:
            self.y += self.aspeed
        elif self.pos > 19:
            self.y-= self.aspeed
        if self.pos == 39:
            self.pos = 0
        if self.x > WIDTH + 200:
            self.x = int(random.uniform(-2000, -40))
            self.y = int(random.uniform(180, 0))
        win.blit(self.cloudimg, (self.x, self.y))

localPlayer = Player()
lastLocalPlayer = Player()
Net = Network()


WIDTH = 1000
HEIGHT = 800

pygame.init()
pygame.key.set_repeat(200, 25) # press every 50 ms after waiting 200 ms
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("MultiplayerClientV1.1")
clock = pygame.time.Clock()

codepath = os.getcwd()
configpath = codepath + r'\config.txt'

backgroundpath = codepath + r'\textures\background.png'
cloudonepath = codepath + r'\textures\cloudone.png'
cloudpath = codepath + r'\textures\cloud.png'

defaultData = "address,\nport,\nusername,\n"
fontpath = codepath + r'\textures\Font.font'
font = pygame.font.Font(fontpath, 29)
manager = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 13)
managerport = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 13)
managername = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 13)
managerpass = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 13)
textinput = pygame_textinput.TextInputVisualizer(manager=manager, font_object=font)
textinputname = pygame_textinput.TextInputVisualizer(manager=managername, font_object=font)
textinputport = pygame_textinput.TextInputVisualizer(manager=managerport, font_object=font)
textinputpass = pygame_textinput.TextInputVisualizer(manager=managerpass, font_object=font)
field_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, pygame.RESIZABLE)

start_time = time.time()

background = pygame.image.load(backgroundpath).convert()
cloud = [pygame.image.load(cloudonepath).convert_alpha(), pygame.image.load(cloudpath).convert_alpha()]

image_width, image_height = background.get_size()
scale_factor = max(WIDTH/image_width, HEIGHT/image_height)
scaled_width = int(image_width * scale_factor)
scaled_height = int(image_height * scale_factor)
background = pygame.transform.scale(background, (scaled_width, scaled_height))
x_pos = int((WIDTH - scaled_width) / 2)
y_pos = int((HEIGHT - scaled_height) / 2)

clock = pygame.time.Clock()
cloudList = [Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud)),Cloud(int(random.uniform(-2000, -40)), int(random.uniform(180, 0)) , random.uniform(2, 0.5), random.uniform(0.4, 0.1), random.choice(cloud))]
FPS = getFPS()

isSelected = False
isSelectedPort = False
isSelectedName = False
isSelectedPass = False
notConnected = True
Net
error = ""

if os.path.exists(configpath):
    with open(configpath, 'r+') as f:
        read = f.read()
        if not "address" in read:
            f.write("address,\n")
            f.read
        if not "port" in read:
            f.write("port,\n")
            f.read
        if not "username" in read:
            f.write("username,\n")
            f.read
        f.close()
        with open(configpath, 'r') as f:
            data=f.readlines()
            for entry in data:
                formatedEntry = entry.strip()
                formatedEntry = formatedEntry.split(",")
                if formatedEntry[0] == "address":
                    textinput.value = formatedEntry[1]
                    manager.cursor_pos = len(formatedEntry[1])
                if formatedEntry[0] == "port":
                    textinputport.value = formatedEntry[1]
                    managerport.cursor_pos = len(formatedEntry[1])
                if formatedEntry[0] == "username":
                    textinputname.value = formatedEntry[1]
                    managername.cursor_pos = len(formatedEntry[1])
            f.close
            



else:
    with open(configpath, 'w') as f:
        f.write(defaultData)
        f.close()


while notConnected:
        
    field_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, pygame.RESIZABLE)
    win.fill((0,0,0))

    win.blit(background, (x_pos, y_pos))

    cloudList[0].update(win)
    cloudList[1].update(win)
    cloudList[2].update(win)
    cloudList[3].update(win)
    cloudList[4].update(win)
    cloudList[5].update(win)
    cloudList[6].update(win)

    events = pygame.event.get()
    color = pygame.Color(40,40,40)
    pygame.draw.rect(win, color, (WIDTH/2-250, HEIGHT/4-90, 500, HEIGHT/1.435-HEIGHT/4+180))
    if not error == "":
        text, textrect = write(error, 0, 0, "black")
        win.blit(text, (15 , 15))

    if isSelected:
        textinput.update(events)
        pygame.draw.rect(win, (70, 70, 70), (WIDTH/2-210, HEIGHT/4-50, 420, 100))
        pygame.draw.rect(win, (100, 100, 100), (WIDTH/2-200, HEIGHT/4-40, 400, 80))
    else:
        pygame.draw.rect(win, (50, 50, 50), (WIDTH/2-210, HEIGHT/4-50, 420, 100))
        pygame.draw.rect(win, (80, 80, 80), (WIDTH/2-200, HEIGHT/4-40, 400, 80))
        if not len(textinput.value):
            text, textrect = write("Address",WIDTH/2-187, HEIGHT/4-18)
            win.blit(text, (WIDTH/2-187, HEIGHT/4-18))

    if isSelectedPort:
        textinputport.update(events)
        pygame.draw.rect(win, (70, 70, 70), (WIDTH/2-210, HEIGHT/2.5-50, 420, 100))
        pygame.draw.rect(win, (100, 100, 100), (WIDTH/2-200, HEIGHT/2.5-40, 400, 80))
    else:
        pygame.draw.rect(win, (50, 50, 50), (WIDTH/2-210, HEIGHT/2.5-50, 420, 100))
        pygame.draw.rect(win, (80, 80, 80), (WIDTH/2-200, HEIGHT/2.5-40, 400, 80))
        if not len(textinputport.value):
            text, textrect = write("Port",WIDTH/2-187, HEIGHT/2.5-18)
            win.blit(text, (WIDTH/2-187, HEIGHT/2.5-18))

    if isSelectedName:
        textinputname.update(events)
        pygame.draw.rect(win, (70, 70, 70), (WIDTH/2-210, HEIGHT/1.825-50, 420, 100))
        pygame.draw.rect(win, (100, 100, 100), (WIDTH/2-200, HEIGHT/1.825-40, 400, 80))
    else:
        pygame.draw.rect(win, (50, 50, 50), (WIDTH/2-210, HEIGHT/1.825-50, 420, 100))
        pygame.draw.rect(win, (80, 80, 80), (WIDTH/2-200, HEIGHT/1.825-40, 400, 80))
        if not len(textinputname.value):
            text, textrect = write("Username",WIDTH/2-187, HEIGHT/1.825-18)
            win.blit(text, (WIDTH/2-187, HEIGHT/1.825-18))

    if isSelectedPass:
        textinputpass.update(events)
        pygame.draw.rect(win, (70, 70, 70), (WIDTH/2-210, HEIGHT/1.435-50, 420, 100))
        pygame.draw.rect(win, (100, 100, 100), (WIDTH/2-200, HEIGHT/1.435-40, 400, 80))
    else:
        pygame.draw.rect(win, (50, 50, 50), (WIDTH/2-210, HEIGHT/1.435-50, 420, 100))
        pygame.draw.rect(win, (80, 80, 80), (WIDTH/2-200, HEIGHT/1.435-40, 400, 80))
        if not len(textinputpass.value):
            text, textrect = write("Password",WIDTH/2-187, HEIGHT/1-18)
            win.blit(text, (WIDTH/2-187, HEIGHT/1.435-18))

    for event in events:
        if event.type == pygame.QUIT:
            with open(configpath, 'r') as file:
                lines = file.readlines()

            for i in range(len(lines)):
                if lines[i].startswith("address"):
                    lines[i] = "address," + textinput.value +"\n"
                if lines[i].startswith("port"):
                    lines[i] = "port," + textinputport.value +"\n"
                if lines[i].startswith("username"):
                    lines[i] = "username," + textinputname.value +"\n"

            with open(configpath, 'w') as file:
                file.writelines(lines)
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

            with open(configpath, 'r') as file:
                lines = file.readlines()

            for i in range(len(lines)):
                if lines[i].startswith("address"):
                    lines[i] = "address," + textinput.value +"\n"
                if lines[i].startswith("port"):
                    lines[i] = "port," + textinputport.value +"\n"
                if lines[i].startswith("username"):
                    lines[i] = "username," + textinputname.value +"\n"

            with open(configpath, 'w') as file:
                file.writelines(lines)

            isSelected = False
            isSelectedPort = False
            isSelectedName = False
            isSelectedPass = False
            textinput.cursor_visible = False
            textinputport.cursor_visible = False
            textinputname.cursor_visible = False
            textinputpass.cursor_visible = False

            Connected = Net.attemptConnect(textinputname.value, textinputpass.value, textinput.value, textinputport.value)
            
            if Connected == "success":
                notConnected = False
                print(colored('Connected to ' + str(textinput.value + ", " + textinputport.value), 'green'))
            elif Connected == "invalidAddress":
                error = "Address invalid."
            elif Connected == "invalidPass":
                error = "Password invalid."
            elif Connected == "serverNotResponding":
                error = "Server timed out."


        if event.type == pygame.VIDEORESIZE:
            WIDTH = event.w
            HEIGHT = event.h
            surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            field_surface = pygame.Surface((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            image_width, image_height = background.get_size()

            scale_factor = max(WIDTH/image_width, HEIGHT/image_height)

            scaled_width = int(image_width * scale_factor)
            scaled_height = int(image_height * scale_factor)
            background = pygame.transform.scale(background, (scaled_width, scaled_height))

            x_pos = int((WIDTH - scaled_width) / 2)
            y_pos = int((HEIGHT - scaled_height) / 2)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            square_rect = pygame.Rect(WIDTH/2-210, HEIGHT/4-50, 420, 100)
            
            square_rectport = pygame.Rect(WIDTH/2-210, HEIGHT/2.5-50, 420, 100)

            square_rectname = pygame.Rect(WIDTH/2-210, HEIGHT/1.825-50, 420, 100)

            square_rectpass = pygame.Rect(WIDTH/2-210, HEIGHT/1.435-50, 420, 100)

            if square_rect.collidepoint(mouse_x, mouse_y):
                isSelected = True
                isSelectedPort = False
                isSelectedName = False
                isSelectedPass = False
                textinput.cursor_visible = True

            else:
                isSelected = False
                textinput.cursor_visible = False

            if square_rectport.collidepoint(mouse_x, mouse_y):
                isSelected = False
                isSelectedPort = True
                isSelectedName = False
                isSelectedPass = False
                textinputport.cursor_visible = True

            else:
                isSelectedPort = False
                textinputport.cursor_visible = False

            if square_rectname.collidepoint(mouse_x, mouse_y):
                isSelected = False
                isSelectedPort = False
                isSelectedName = True
                isSelectedPass = False
                textinputname.cursor_visible = True

            else:
                isSelectedName = False
                textinputname.cursor_visible = False

            if square_rectpass.collidepoint(mouse_x, mouse_y):
                isSelected = False
                isSelectedPort = False
                isSelectedName = False
                isSelectedPass = True
                textinputpass.cursor_visible = True

            else:
                isSelectedPass = False
                textinputpass.cursor_visible = False

    mouse_x, mouse_y = pygame.mouse.get_pos()
            
    square_rect = pygame.Rect(WIDTH/2-210, HEIGHT/4-50, 420, 100)
    square_rectport = pygame.Rect(WIDTH/2-210, HEIGHT/2.5-50, 420, 100)
    square_rectname = pygame.Rect(WIDTH/2-210, HEIGHT/1.825-50, 420, 100)
    square_rectpass = pygame.Rect(WIDTH/2-210, HEIGHT/1.435-50, 420, 100)

    if square_rect.collidepoint(mouse_x, mouse_y) or square_rectport.collidepoint(mouse_x, mouse_y) or square_rectname.collidepoint(mouse_x, mouse_y) or square_rectpass.collidepoint(mouse_x, mouse_y):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    win.blit(textinput.surface, (WIDTH/2-187, HEIGHT/4-18))
    win.blit(textinputport.surface, (WIDTH/2-187, HEIGHT/2.5-18))
    win.blit(textinputname.surface, (WIDTH/2-187, HEIGHT/1.825-18))
    win.blit(textinputpass.surface, (WIDTH/2-187, HEIGHT/1.435-18))
    text = font.render("FPS: "+str(int(FPS.FPS())), 1, pygame.Color('black'))
    win.blit(text, (WIDTH - 150, HEIGHT - 50))
    pygame.display.flip()
    clock.tick(60)

Await = threading.Thread(target=MessageHandler, args=(Net,))
updateServ = threading.Thread(target=updateServer, args=(Net,))

Await.start()
updateServ.start()

while Running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
            for i in range(10):
                time.sleep(0.1)
                sys.stdout.write(colored("\rShutting down" + animation[i % len(animation)], 'red'))
                sys.stdout.flush()
            os._exit(0)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        localPlayer.x -= 1
    if keys[pygame.K_RIGHT]:
        localPlayer.x += 1
    if keys[pygame.K_UP]:
        localPlayer.y -= 1
    if keys[pygame.K_DOWN]:
        localPlayer.y += 1

    win.fill((50, 50, 50))

    for player in Players:
        text, text_rect = write(player.pN, int(player.x) + 10, int(player.y) - 15, "Grey")
        pygame.draw.rect(win, (0, 0, 255), (int(player.x), int(player.y), 20, 20))
        win.blit(text, text_rect)
            
    pygame.display.update()
    clock.tick(75)

pygame.quit()
    