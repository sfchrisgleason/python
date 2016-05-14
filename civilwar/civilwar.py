#!/usr/bin/env python3
#
#
# A quick script to create a civil war game
#
# Chris Gleason 2015

##################
# IMPORT MODULES #
##################


import os
from random import randint


#####################
# DECLARE VARIABLES #
#####################


### Armies = [Inf,Cav,Art] ###

global compdefmult
global compattmult
global compchoice
global userdefmult
global userattmult
global userchoice
comparmy = [100,50,10]
userarmy = [100,50,10]



###########################
# DEFINE GLOBAL FUNCTIONS #
###########################

def clearscreen():

    """
    A function that will clear the screen depending on if it's NTOS or not.
    Does not cover all bases and is not completely portable, but this is
    A basic game script. I'm not writing this for the entire world.
    """

    os.system("cls" if os.name == "nt" else "clear")


def newstart():

    """
    Primary function that to start the UI. First cunftion that is called.
    Will call all other functions
    """

    clearscreen()
    print ('''

 CCCC  IIIII  V    V  IIIII  L 		W   W   W  AA  RRRR
C        I     V  V     I    L  	 W  W  W  A  A R   R 
C        I      VV      I    L  	  W W W   AAAA RRRR
 CCCC  IIIII    VV    IIIII  LLLL	  WW WW   A  A R   R

This is Civil War!

You will have Infantry, Calvalry and Artillery to win the battles you need to turn the tide of the war.

Now, General, take your place in history!

    ''')

def printstatus():
    print ('Your total Infantry are:' , userarmy[0])
    print ('Your total Calvalry are:' , userarmy[1])
    print ('Your total Artillery are:' , userarmy[2])
    print ('')
    print ('Computers total Infantry are:' , comparmy[0])
    print ('Computers total Calvalry are:' , comparmy[1])
    print ('Computers total Artillery are:' , comparmy[2])
    print ('')
    mainmenu()


####################
# MAIN BATTLE CODE #
####################

def compdigger():	

    """
    Compdigger (couldn't think of a relevant name at the time) is the main AI function.
    It decides which troop set to use, then calculates the computers defense and
    attack multipliers for the battle.
    """

    global compchoice
    global compdefmult
    global compattmult
    compchoice = randint(1,3)
    if compchoice == 1:
        if comparmy[0] == 0:
            compdigger()
        else:
            compchoice = "Infantry"
            compdefmult = 3
            compattmult = 3
    elif compchoice == 2:
        if comparmy[1] == 0:
            compdigger()
        else:
            compchoice = "Calvalry"
            compdefmult = 4
            compattmult = 2
    else:
        if comparmy[2] == 0:
            compdigger()
        else:
            compchoice = "Artillery"
            compdefmult = 2
            compattmult = 4
    return compchoice
    return compdefmult
    return compattmult

def takeaction():
    
    """
    Take action function is the main funtion called when running the attack loop
    It contains all the variables for the battle alrogithm and does the reconciliation
    of the troop reduction
    """

    print ('Infantry have an offensive multiplier of 3 and a defensive multiplier of 3')
    print ('Calvalry have an offensive multiplier of 2 and a defensive multiplier of 4')
    print ('Artillery have an offensive multiplier of 4 and a defensive multiplier of 2')
    print ('')
    print ('''

Do you want to use:

1) Infantry
2) Calvalry
3) Artillery

    ''')
    print ("")
    action = input ("Choose one -> : ");
    if action == "1":
        userchoice = "Infantry"
        print ("")
        if userarmy[0] == 0:
            print ("You don't have any more infantry! Please choose another troop set!")
            takeaction()
        else:
            print ("MAAAAARRRRCH!!!!!")
            defmult = 3
            attmult = 3
            print ("")
    elif action == "2":
        userchoice = "Calvalry"
        print ("")
        if userarmy[1] == 0:
            print ("You don't have any more calvalry! Please choose another troop set!")
            takeaction()
        else:
            print ("CHAAAAARRRGE!!!!!!")
            defmult = 4
            attmult = 2
            print ("")
    elif action == "3":
        userchoice = "Artillery"
        print ("")
        if userarmy[2] == 0:
            print ("You don't have any more artillery! Please choose another troop set!")
            takeaction()
        else:
            print ("FIIIIIIIRE!!!!!!")
            defmult = 2
            attmult = 4
            print ("")
    else:
        print ("")
        print ("You did not choose 1,2 or 3. Please choose a valid answer")
        print ("")
        takeaction()

    print ("")

    userdefroll = randint(1,12)
    userattroll = randint(1,12)

    print ("Your defensive roll was ", userdefroll)
    print ("Your attack roll was " , userattroll)

    compdefroll = randint(1,12)
    compattroll = randint(1,12)

    print ("")

    print ("Computers defensive roll was " , compdefroll)
    print ("Computers attack roll was " , compattroll)


    print ("")

    userattack = int(attmult) * int(userattroll)
    userdefense = int(defmult) * int(userdefroll)

    print ("")
    print ("Defense total is multiplier %s times roll %s which has a total of %s " % (defmult, userdefroll , userdefense)) 
    print ("Attack total is miltiplier %s times roll %s which has a total of %s " % (attmult, userattroll, userattack))
    print ("")

    compdigger()

    compdefense = int(compdefmult) * int(compdefroll)
    compattack = int(compattmult) * int(compattroll)

    print ("")
    print ("The computer chose ", compchoice)
    print ("")
    print ("Computers total Defense multiplier is %s times it's roll %s which has a total of %s " % (compdefmult, compdefroll, compdefense))
    print ("Computers total Attack multiplier is %s times it's roll %s which has a total of %s " % (compattmult, compattroll, compattack))
    print ("")

    print ("")
    if compdefense >= userattack:
        print ("The computer defended your attack without troop loss")
    else:
        userdiff = int(userattack) - int(compdefense)
        print ("Computer lost %s  %s " % (userdiff , compchoice))
        if compchoice == "Infantry":
            comparmy[0] -= int(userdiff)
            if comparmy[0] < 0:
               comparmy[0] = 0
        elif compchoice == "Calvalry":
            comparmy[1] -= int(userdiff)
            if comparmy[1] < 0:
                comparmy[1] = 0
        else:
            comparmy[2] -= int(userdiff)
            if comparmy[2] < 0:
                comparmy[2] = 0 

    if userdefense >= compattack:
        print ("You defended the computers attack without troop loss")
    else:
        compdiff = int(compattack) - int(userdefense)
        print ("You lost %s  %s " % (compdiff , userchoice))
        if userchoice == "Infantry":
            userarmy[0] -= int(compdiff)
            if userarmy[0] < 0:
                userarmy[0] = 0
        elif userchoice == "Calvalry":
            userarmy[1] -= int(compdiff)
            if userarmy[1] < 0:
                userarmy[1] = 0
        else:
            userarmy[2] -= int(compdiff)
            if userarmy[2] < 0:
                userarmy[2] = 0

    if userarmy[0] == 0 and userarmy[1] == 0 and userarmy[2] == 0:
        print ("Your army has been decemated! RETREAT!")
        exit(0)

    if comparmy[0] == 0 and comparmy[1] == 0 and comparmy[2] ==0:
        print ("The computers army has been decemated! VICTORY!")
        exit(0)

    print ("")


    mainmenu()


def mainmenu():
    print ('''

MAIN MENU
---------

1) Print out army status
2) ATTACK!
3) Save game (not implemented yet)
4) Load game (not implemented yet)
5) Quit

''')

    menuaction = input ("Please choose an option -> : ");
    if menuaction == "1":
        printstatus()
    elif menuaction == "2":
        takeaction()
    elif menuaction == "3":
        print ("Not implemented yet!")
        mainmenu()
    elif menuaction == "4":
        print ("Not implemented yet!")
        mainmenu()
    elif menuaction == "5":
        print ("Good bye!")
        exit (0)
    else:
        print ("You did not choose 1,2,3 or 4. Please choose a valid option!")
        mainmenu()

newstart()
mainmenu()






