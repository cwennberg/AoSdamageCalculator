#!/usr/bin/python

import sys
import random
import numpy as np
import argparse

def DICE(value):
    dice = random.randint(1,value)

    return dice

class Weapon():
    def __init__(self, attacks, toHit, toWound, rend, damage, debug):
        self.attacks = attacks
        self.toHit = toHit
        self.toWound = toWound
        self.rend = rend
        self.damage = damage
        self.modifierList = []
        self.debug = debug
        self.armorSave = 7
        self.wardSave = None
        self.MWwardSave = None
        self.normalDamage = 0
        self.mortalDamage = 0
        self.rendIgnore = 0
        
    def loadModifiers(self, modifierList):
        self.modifierList = modifierList
        
    def printInfo(self):
        print "-- ATTACKING %d TIMES WITH THIS WEAPON: %d+/%d+/%d/%s --" %(self.attacks, self.toHit, self.toWound, self.rend, self.damage)
        print "THIS WEAPONS MODIFIERLIST IS:", self.modifierList
    def getAttacks(self):
        return self.attacks

    def resetStats(self):
        self.normalDamage = 0
        self.mortalDamage = 0
    
    def attack(self, armorSave, wardSave, MWwardSave, rendIgnore):
        self.armorSave = armorSave
        self.wardSave = wardSave if wardSave else 7
        self.MWwardSave = MWwardSave if MWwardSave else 7
        self.rendIgnore = rendIgnore
        toHitRoll = DICE(6)
        if self.debug:
            print "Rolled %d to hit" %toHitRoll
        if (toHitRoll == 6 and "mortalOn6ToHit" in self.modifierList) or (toHitRoll >= 5 and "mortalOn5ToHit" in self.modifierList):
            #Assumes that the attack sequence will end and number of MW = damage of the attack
            self.mortalDamage += self.doMWDamage()
            if self.debug:
                print "Did %d mortal wounds" %self.mortalDamage

            return self.normalDamage + self.mortalDamage
        elif toHitRoll == 6 and "exploding6ToHit" in self.modifierList:
            if self.debug:
                print "Did 2 hits"
            firstAttack = self.woundRoll()            
            secondAttack = self.woundRoll()
            if self.debug:
                print "Did %d damage with first hit and %d damage with second hit" %(firstAttack, secondAttack)
            return firstAttack + secondAttack
        elif (toHitRoll >= self.toHit):
            return self.woundRoll()
            
        elif toHitRoll == 1 and "reroll1ToHit" in self.modifierList:
            toHitRoll = DICE(6)
            if self.debug:
                print "Re-rolled into %d to hit" %toHitRoll
            if (toHitRoll == 6 and "mortalOn6ToHit" in self.modifierList) or (toHitRoll >= 5 and "mortalOn5ToHit" in self.modifierList):
                #Assumes that the attack sequence will end and number of MW = damage of the attack
                self.mortalDamage += self.doMWDamage()
                if self.debug:
                    print "Did %d mortal wounds" %self.mortalDamage
                    
                return self.normalDamage + self.mortalDamage
            elif toHitRoll == 6 and "exploding6ToHit" in self.modifierList:
                if self.debug:
                    print "Did 2 hits"
                firstAttack = self.woundRoll()
                secondAttack = self.woundRoll()
                if self.debug:
                    print "Did %d damage with first hit and %d damage with second hit" %(firstAttack, secondAttack)
                return firstAttack + secondAttack

            elif toHitRoll >= self.toHit:
                return self.woundRoll()
            else:
                return 0
            
        elif "rerollToHit" in self.modifierList:            
            toHitRoll = DICE(6)
            if self.debug:
                print "Re-rolled into %d to hit" %toHitRoll
            if (toHitRoll == 6 and "mortalOn6ToHit" in self.modifierList) or (toHitRoll >= 5 and "mortalOn5ToHit" in self.modifierList):
                #Assumes that the attack sequence will end and number of  MW = damage of the attack
                self.mortalDamage += self.doMWDamage()
                if self.debug:
                    print "Did %d mortal wounds" %self.mortalDamage                    
                return self.normalDamage + self.mortalDamage
            elif toHitRoll == 6 and "exploding6ToHit" in self.modifierList:
                if self.debug:
                    print "Did 2 hits"
                firstAttack = self.woundRoll()
                secondAttack = self.woundRoll()
                if self.debug:
                    print "Did %d damage with first hit and %d damage with second hit" %(firstAttack, secondAttack)
                return firstAttack + secondAttack

            elif toHitRoll >= self.toHit:
                return self.woundRoll()
            else:
                return 0
        else:        
            return 0

    def woundRoll(self):
        toWoundRoll = DICE(6)
        if self.debug:
            print "Rolled %d to wound" %toWoundRoll
        if toWoundRoll == 6 and "mortalOn6ToWound" in self.modifierList:
            #Assumes 1 MW in addition to normal damage
            if self.debug:
                print "Did 1 additional MW"
            self.mortalDamage += self.doMWDamage(1)
            return self.saveDamage()
        elif toWoundRoll >= self.toWound:
            return self.saveDamage()
        elif toWoundRoll == 1 and "reroll1ToWound" in self.modifierList:
            toWoundRoll = DICE(6)
            if self.debug:
                print "Re-rolled into %d to wound" %toWoundRoll
            if toWoundRoll == 6 and "mortalOn6ToWound" in self.modifierList:
                #Assumes 1 MW in addition to normal damage
                if self.debug:
                    print "Did 1 additional MW"
                self.mortalDamage += self.doMWDamage(1)
                return self.saveDamage()
            elif toWoundRoll >= self.toWound:
                return self.saveDamage()
            else:
                return 0
        return 0
    
    def saveDamage(self):
        #We have hit and wounded, now we take armor/ward and then calculate total damage
        totalRend = max(self.rend - self.rendIgnore, 0)
        armorSave = self.armorSave + totalRend
        saveRoll = DICE(6)
        if self.debug:
            print "Rolled %d for %d+ armor save with effective rend %d (rend %d and rendIgnore %d)" %(saveRoll, self.armorSave, totalRend, self.rend, self.rendIgnore)
        if saveRoll == 1 and "reroll1sArmorSave" in self.modifierList:
            saveRoll = DICE(6)
            if self.debug:
                print "Re-rolled %d for %d+ armor save with effective rend %d (rend %d and rendIgnore %d)" %(saveRoll, self.armorSave, totalRend, self.rend, self.rendIgnore)
            if (saveRoll < armorSave) or (saveRoll == 1):
                self.normalDamage += self.doDamage()            
        elif saveRoll < armorSave and "rerollArmorSave" in self.modifierList:
            saveRoll = DICE(6)
            if self.debug:
                print "Re-rolled %d for %d+ armor save with effective rend %d (rend %d and rendIgnore %d)" %(saveRoll, self.armorSave, totalRend, self.rend, self.rendIgnore)
            if (saveRoll < armorSave) or (saveRoll == 1):
                self.normalDamage += self.doDamage()
        elif (saveRoll < armorSave) or (saveRoll == 1):
            self.normalDamage += self.doDamage()
        
        return self.normalDamage + self.mortalDamage

    def doDamage(self):
        thisDamage = self.damage
        if type(self.damage) == str:
            #self.damage contains a term such as "d3" or "d6", we select the second value and send to DICE
            thisDamage = DICE(int(self.damage[1]))

        if self.wardSave < 7:
            savedWounds = 0
            for wound in range(0,thisDamage):
                saveRoll = DICE(6)
                if self.debug:
                    print "Rolled %d on %d+ ward save" %(saveRoll, self.wardSave)
                if saveRoll >= self.wardSave:
                    savedWounds += 1
            thisDamage -= savedWounds

        return thisDamage

    def doMWDamage(self, value=None):
        thisDamage = value if value != None else self.damage
        if (type(self.damage) == str) and value == None:
            #self.damage contains a term such as "d3" or "d6", we select the second value and send to DICE
            thisDamage = DICE(int(self.damage[1]))
        if self.debug:
            print "DID %d MWs" %(thisDamage)
        if (self.wardSave < 7) or (self.MWwardSave < 7):
            savedWounds = 0
            saveValue = min(self.wardSave, self.MWwardSave)            
            for wound in range(0,thisDamage):
                saveRoll = DICE(6)
                if self.debug:
                    print "Rolled %d on %d+ ward save" %(saveRoll, saveValue)
                if saveRoll >= saveValue:
                    savedWounds += 1
            thisDamage -= savedWounds
                    
        return thisDamage
if __name__ == '__main__':
    descriptionStr = 'Calculate combat damage for unit in Age of Sigmar 3.0'
    parser=argparse.ArgumentParser(description=descriptionStr)
    parser.add_argument('-i', '--iterations', type=int, default=10000, help='Iterations to run [default=10000]')
    parser.add_argument('-w', '--weapons', nargs='+', help='Weapon profiles in format ABCDE where A=attacks, B=toHit, C=toWound, D=rend, E=damage (write d6 if damage is d6)')
    parser.add_argument('-ward', '--ward', type=int, help='Ward save, if present')
    parser.add_argument('-MWward', '--mwward', type=int, help='Ward save against mortal wounds, if present')
    parser.add_argument('-rendIgnore', '--rendIgnore', type=int, help='Ignores this amount of rend')
    #These options below stores the input as a list of lists, which is ugly but it works for now
    parser.add_argument('--MW6HIT', nargs='+', type=list, help='Mortal wounds on 6s to hit, assumes MW=damage and end of attack sequence.')
    parser.add_argument('--MW5HIT', nargs='+', type=list, help='Mortal wounds on 5s to hit, assumes MW=damage and end of attack sequence.')
    parser.add_argument('--MW6WOUND', nargs='+', type=list, help='1 mortal wound on 6s to wound, in addition to normal damage.')
    parser.add_argument('--RRHIT', nargs='+', type=list, help='Reroll to hit')
    parser.add_argument('--RR1HIT', nargs='+', type=list, help='Reroll 1s to hit')
    parser.add_argument('--RRWOUND', nargs='+', type=list, help='Reroll to wound')
    parser.add_argument('--RR1WOUND', nargs='+', type=list, help='Reroll 1s to wound')
    parser.add_argument('--RRARMOR', nargs='+', type=list, help='Reroll armor save')
    parser.add_argument('--RR1ARMOR', nargs='+', type=list, help='Reroll 1s for armor save')
    parser.add_argument('--EXPLODING6HIT', nargs='+', type=list, help='Exploding 6s to hit')
    parser.add_argument('--debug', action='store_true', help='Print out debug-info')
    args = parser.parse_args()
        
    iterations = args.iterations
    debug = args.debug
    modifierList = []
    for i, weapon in enumerate(args.weapons):
        modifierList.append([])
        if args.RRHIT and args.RRHIT[0][i] == '1':
            modifierList[i].append("rerollToHit")
        if args.RR1HIT and args.RR1HIT[0][i] == '1':
            modifierList[i].append("reroll1ToHit")
        if args.RR1WOUND and args.RR1WOUND[0][i] == '1':
            modifierList[i].append("reroll1ToWound")
        if args.RRWOUND and args.RRWOUND[0][i] == '1':
            modifierList[i].append("rerollToWound")
        if args.MW6HIT and args.MW6HIT[0][i] == '1':
            modifierList[i].append("mortalOn6ToHit")
        if args.MW5HIT and args.MW5HIT[0][i] == '1':
            modifierList[i].append("mortalOn5ToHit")
        if args.MW6WOUND and args.MW6WOUND[0][i] == '1':
            modifierList[i].append("mortalOn6ToWound")
        if args.RRARMOR and args.RRARMOR[0][i] == '1':
            modifierList[i].append("rerollArmorSave")
        if args.RR1ARMOR and args.RR1ARMOR[0][i] == '1':
            modifierList[i].append("reroll1sArmorSave")
        if args.EXPLODING6HIT and args.EXPLODING6HIT[0][i] == '1':
            modifierList[i].append("exploding6ToHit")
    if debug:
        print "MODIFIERLIST FOR EACH WEAPON:"
        print modifierList

    wardSave = args.ward if args.ward else None
    MWwardSave = args.mwward if args.mwward else None
    rendIgnore = args.rendIgnore if args.rendIgnore else 0
    weapons = []

    for inputValue in args.weapons:
        thisWeapon=inputValue.split('/')
        weaponDict = {
            "attacks": int(thisWeapon[0]),
            "toHit": int(thisWeapon[1]),
            "toWound": int(thisWeapon[2]),
            "rend": int(thisWeapon[3])
        }
        if thisWeapon[4][0] == "d":
            weaponDict["damage"] = thisWeapon[4][0] + thisWeapon[4][1]
        else:
            weaponDict["damage"] = int(thisWeapon[4])
        weapons.append(Weapon(weaponDict["attacks"],weaponDict["toHit"],weaponDict["toWound"],weaponDict["rend"],weaponDict["damage"],debug))

    for i,weapon in enumerate(weapons):
        weapon.loadModifiers(modifierList[i])

    saveValues = [1,2,3,4,5,6]
    TotalWounds = [[],[],[],[],[],[]]

    for i in range(iterations):
        for j,armorSave in enumerate(saveValues):
            numberOfWounds = 0
            for k,weapon in enumerate(weapons):
                if debug:
                    print "--- ATTACKING AGAINST ARMOR SAVE %d+ ---" %(armorSave)
                    weapon.printInfo()

                for attack in range(0,weapon.getAttacks()):
                    damage = weapon.attack(armorSave, wardSave, MWwardSave, rendIgnore)
                    if debug and damage > 0:
                        print "--- DID %d damage ---" %damage
                    numberOfWounds += damage
                    weapon.resetStats()
            if debug:
                print "--- TOTAL NUMBER OF WOUNDS FROM ALL ATTACKS %d ---" %(numberOfWounds)
            TotalWounds[j].append(numberOfWounds)

if debug:
    print "WOUND LIST:"
    for j,armorSave in enumerate(saveValues):
        print "Save %d+: %s" %(armorSave, TotalWounds[j])

print "Results with one standard deviation:"
for j,armorSave in enumerate(saveValues):
    print "Save %d+: %.2f +/- %.2f wounds" %(armorSave, float(sum(TotalWounds[j]))/iterations, np.std(TotalWounds[j]))


#This is ugly but works (I hope)
for j,armorSave in enumerate(saveValues):
    print "Save %d+:" %(armorSave)
    maximumWoundsDone = np.amax(TotalWounds[j])
    numberOfWoundsList = []
    for i in range(0,maximumWoundsDone+1):
        numberOfWoundsList.append(TotalWounds[j].count(i))
    sys.stdout.write ("Minimum wounds:")
    for i, value in enumerate(numberOfWoundsList):

        if 95 > 100*float(sum(numberOfWoundsList[i:]))/sum(numberOfWoundsList) > 5:
            if i == maximumWoundsDone:
                sys.stdout.write ("%7s\n" %(i))
            else:
                sys.stdout.write ("%7s" %(i))
        else:
            if i == maximumWoundsDone:
                sys.stdout.write ("\n")
            continue

    sys.stdout.write ("Probability:   ")
    for i, value in enumerate(numberOfWoundsList):
        if 95 > 100*float(sum(numberOfWoundsList[i:]))/sum(numberOfWoundsList) > 5:
            if i == maximumWoundsDone:
                sys.stdout.write ("%7s\n" %(str(round(100*float(sum(numberOfWoundsList[i:]))/sum(numberOfWoundsList),0))+"%"))
            else:
                sys.stdout.write ("%7s" %(str(round(100*float(sum(numberOfWoundsList[i:]))/sum(numberOfWoundsList),0))+"%"))
        else:
            if i == maximumWoundsDone:
                sys.stdout.write ("\n")
            continue

sys.stdout.flush
