# AoSdamageCalculator
Calculate damage from unit in AoS3.0

How to run:
Place script in folder and run "python damageCalculator.py -h" for a list of options

Weapon profiles are given as "python damageCalculator.py -w 10/3/3/0/1 20/4/4/2/d3" 

This will simulate 10 attacks on 3+ to hit, 3+ to wound, rend 0, and damage 1, 
combined with 20 attacks on 4+ to hit, 4+ to wound, rend 2, and damage d3

Modifiers are added using the respective option followed by 1 (applied) or 0 (not applied) 
for the respective weapon profile. In order to add reroll 1s to hit to the second weapon above
you would give this command:
"python damageCalculator.py -w 10/3/3/0/1 20/4/4/2/d3 --RR1HIT 01" 
