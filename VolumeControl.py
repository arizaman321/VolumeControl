from RPi_GPIO_Rotary import rotary
import RPi.GPIO as GPIO
import time
import threading
import soco
import os

#LED Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.OUT, initial = GPIO.LOW) #Blue
GPIO.setup(13, GPIO.OUT) #Green
GPIO.setup(12, GPIO.OUT) #Red
GPIO.setup(7, GPIO.OUT, initial = GPIO.HIGH)
greenLED = GPIO.PWM(13, 100) #pin and freq
greenLED.ChangeDutyCycle(0) 
greenLED.start(50) #duty cycle
redLED = GPIO.PWM(12, 40)
redLED.start(15)

# Initalized Variables
favorites = {}
freeSpin = 0
count3 = 0

# Discovering zones using soco and picking zone we want
for item in soco.discover():
    if item.uid == "RINCON_7828CA12D8C601400":
        zone = item
        redLED.ChangeDutyCycle(0)
        print ("Found ", zone.player_name)
        break

# Volume Knob Functions
def cwTurn():
    zone.play()
    
    zone.volume += 5
    
    threading.Thread(target = updateUI(1)).start() #Update UI
    
    print ("Volume Increase... New Level = ", zone.volume)
    
def ccwTurn():
    zone.play()
    zone.volume -= 5
    
    threading.Thread(target = updateUI(1)).start() #Update UI
    
    if zone.volume == 0:
        zone.pause()
    
    
    
    print ("Volume Decrease... New Level = ", zone.volume)
    
def buttonPushed():
    pass #Does nothing as button is unusable in design
    
    
def valueChanged(count):
    pass #Unused Library Funciton
    
# Bass Knob Functions
def cwTurn2():
    zone.bass += 1
    threading.Thread(target = checkBass).start()
    print ("Bass Increase... New Level = ", zone.bass)
    
def ccwTurn2():
    zone.bass -= 1
    threading.Thread(target = checkBass).start()
    print ("Bass Decrease... New Level = ", zone.bass)
    
def buttonPushed2():
    if zone.volume == 0:
        freeSpin(1)
    else:
        if zone.loudness == 1:
            zone.loudness = 0
            GPIO.output(26, GPIO.LOW)
        else:
            zone.loudness = 1
            GPIO.output(26, GPIO.HIGH)
            
        print ("Bass Button Pushed, Loudness Setting = ", zone.loudness)
        
def buttonPushedOFF():
    freeSpin(0)
    
def valueChanged2(count2):
    pass #unused Library Funciton

#Knob 3 Funcitions
# Treble Knob Functions
def cwTurn3():
    zone.treble += 1
    print ("Treble Increase... New Level = ", zone.treble)
    
def ccwTurn3():
    zone.treble -= 1
    print ("Treble Decrease... New Level = ", zone.treble)
    
def buttonPushed3():
    print ("Treble Button Pushed... Favorite Stored...")
    threading.Thread(target = storeFavorite()).start()
    
def valueChanged3(count3):
    #freeSpin(0)
    pass #unused Library Funciton

# My Functions
#Flashes GLED at speed relaitve to volume on change
def updateGreenLED(): 
    if zone.volume != 0:
        tempCycle = .5
        tempCycle = (25*(zone.volume/(99)))
        greenLED.ChangeFrequency(tempCycle)
        time.sleep(.25)
        greenLED.ChangeFrequency(100)
        
def checkVolume(): #Checks volume to trigger LED on warnings
    if zone.volume >= 80:
        redLED.ChangeDutyCycle(100)
    if zone.volume < 80:
        redLED.ChangeDutyCycle(0)
        
    if zone.volume <= 30:
        zone.loudness = 1
        GPIO.output(26, GPIO.HIGH)
    if zone.volume > 30:
        zone.loudness = 0
        GPIO.output(26, GPIO.LOW)
    
    if zone.volume == 0:
        greenLED.ChangeFrequency(15)
        time.sleep(.5)
        greenLED.ChangeFrequency(100)
                
def updateUI(knob):
    
    if knob == 1:
        threading.Thread(target = updateGreenLED).start()
        threading.Thread(target = checkVolume).start()
        
def checkBass():
    if zone.loudness == 1:
        if zone.bass >= 0:
            GPIO.output(26, GPIO.LOW)
            time.sleep(.1)
            GPIO.output(26, GPIO.HIGH)
            
        if zone.bass < 0:
            GPIO.output(26, GPIO.LOW)
            time.sleep(.3)
            GPIO.output(26, GPIO.HIGH)
            
        if zone.bass == 10 or zone.bass == 0:
            GPIO.output(26, GPIO.LOW)
            time.sleep(.1)
            GPIO.output(26, GPIO.HIGH)
            
    if zone.loudness == 0:
        if zone.bass >= 0:
            GPIO.output(26, GPIO.HIGH)
            time.sleep(.1)
            GPIO.output(26, GPIO.LOW)
            
        if zone.bass < 0:
            GPIO.output(26, GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(26, GPIO.LOW)
            
        if zone.bass == 10 or zone.bass == 0:
            GPIO.output(26, GPIO.HIGH)
            time.sleep(.2)
            GPIO.output(26, GPIO.LOW)
        
    if zone.loudness == 1:
        GPIO.output(26, GPIO.HIGH)
    else:
        GPIO.output(26, GPIO.LOW)
        
def monitorSongs(currSong, prevSong):
    if prevSong != currSong:
        if currSong in favorites:
            threading.Thread(target = flashLEDs, args = (5, )).start()
            zone.ramp_to_volume(favorites[currSong][0], 'AUTOPLAY_RAMP_TYPE')
            zone.bass = favorites[currSong][1]
            zone.treble = favorites[currSong][2]
            zone.loudness = favorites[currSong][3]
            print ("Found this song in favorites, setting new levels...")
            print ("    Song = ", currSong, " Vol = ", favorites[currSong][0], " Bass = ", favorites[currSong][1])
        
        
def loadFavorites(favorites):
    open('SonosFavorites.txt', 'a+')
    with open('SonosFavorites.txt', 'r') as inf:
        for line in inf:
            currFav = (line.partition(" % "))
            song = currFav[0] #song title
            values = currFav[2].partition(" % ") 
            vol = int(values[0])
            values2 = values[2].partition(" % ")
            bass = int(values2[0])
            values3 = values2[2].partition(" % ")
            treble = int(values3[0])
            loudness = int(values3[2])
            favorites[song] = [vol,bass,treble,loudness]
    print(favorites)
            
def flashLEDs(numFlash):
    for x in range(0,numFlash):
        redLED.ChangeDutyCycle(100)
        greenLED.ChangeDutyCycle(100)
        GPIO.output(26,GPIO.HIGH)
        time.sleep(.2)
        redLED.ChangeDutyCycle(0)
        greenLED.ChangeDutyCycle(0)
        GPIO.output(26,GPIO.LOW)
        time.sleep(.1)
        greenLED.ChangeDutyCycle(50)
    checkVolume()
    

def storeFavorite():
    
    t = zone.get_current_track_info();
    title = t['title']
    
    if zone.loudness:
        loudness = int(1)
    else:
        loudness = int(0)
    
    if title in favorites:
        if zone.volume <= 15: #If volume is below 15, fav will delete
            del favorites[title]
            flashLEDs(1)
        else:
            favorites[title] = [zone.volume,zone.bass,zone.treble,loudness] #Python
        os.remove("SonosFavorites.txt")
        f = open("SonosFavorites.txt", "a+")
        for item in favorites:
            f.write(item) #file
            f.write(" % ")
            f.write(str(favorites[item][0]))
            f.write(" % ")
            f.write(str(favorites[item][1]))
            f.write(" % ")
            f.write(str(favorites[item][2]))
            f.write(" % ")
            f.write(str(favorites[item][3]))
            f.write("\n")
        f.close()
        
    else:
        f = open("SonosFavorites.txt", "a+")
        favorites[title] = [zone.volume,zone.bass,zone.treble,loudness] #Python
        f.write(title) #file
        f.write(" % ")
        f.write(str(zone.volume))
        f.write(" % ")
        f.write(str(zone.bass))
        f.write(" % ")
        f.write(str(zone.treble))
        f.write(" % ")
        f.write(str(loudness))
        f.write("\n")
        f.close()
    threading.Thread(target = flashLEDs, args = (1, )).start()
    print ("Favorites at end of store function: ", favorites)
    
def freeSpin(setting):
    if setting == 0:
        print ("Free Spin OFF")
        obj2.stop()
        obj2.register(pressed=buttonPushed2, onchange=valueChanged2)
        obj2.register(increment=cwTurn2, decrement=ccwTurn2)
        obj.start()
        obj3.start()
        time.sleep(.5)
        obj2.start()
        
    if setting == 1:
        print ("Free Spin ON")
        obj.stop()
        obj2.stop()
        obj3.stop()
        obj2.register(pressed=buttonPushedOFF, onchange=valueChanged2)
        obj2.register(increment=cwTurn, decrement=ccwTurn)
        time.sleep(.5)
        obj2.start()  
        
def startUp():
    print("start up")
    loadFavorites(favorites)
    redLED.ChangeDutyCycle(100)
    greenLED.ChangeFrequency(100)
    GPIO.output(26,GPIO.HIGH)
    time.sleep(1)
    redLED.ChangeDutyCycle(0)
    greenLED.ChangeDutyCycle(0)
    GPIO.output(26,GPIO.LOW)
    time.sleep(1)
    greenLED.ChangeDutyCycle(50)
    checkVolume()

# Initialize (clk,dt,sw,ticks)
# Volume Knob
obj = rotary.Rotary(18,15,14,2)
obj.register(increment=cwTurn, decrement=ccwTurn)
obj.register(pressed=buttonPushed, onchange=valueChanged)
obj.start()

# Bass Knob
obj2 = rotary.Rotary(21,20,16,2)
obj2.register(increment=cwTurn2, decrement=ccwTurn2)
obj2.register(pressed=buttonPushed2, onchange=valueChanged2)
obj2.start()

# Knob 3
obj3 = rotary.Rotary(22,27,17)
obj3.register(increment=cwTurn3, decrement=ccwTurn3)
obj3.register(pressed=buttonPushed3, onchange=valueChanged3)
GPIO.setup(4, GPIO.OUT, initial = GPIO.HIGH)
obj3.start()

# Run these funcitons at start
startUp()
    
# Main Program
#testFun()
try:
    while True:
        #Songs to compare
        t = zone.get_current_track_info();
        prevSong = t['title']
        time.sleep(2) #How often new song is checked
        t = zone.get_current_track_info();
        currSong = t['title']
        threading.Thread(target = monitorSongs, args = (currSong, prevSong) ).start()
        time.sleep(0.1)
        
except KeyboardInterrupt:
    obj.stop()
    obj2.stop()
    greenLED.stop()
    redLED.stop()
    GPIO.output(26, GPIO.LOW)
    GPIO.cleanup()
    
except:
    print ("other error")
    
finally:
    GPIO.cleanup()