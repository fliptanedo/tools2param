#! /usr/bin/env python
# Tools3Param.py version 3.1
# Flip Tanedo, 17 June 2012
# Revised 22 August 2012: error with squared soft mass matrices
#   ... thanks to Felix Frensch and Benjamin Fuks
#
# This script takes NMSSMTools (SLHA 1) output files and converts them
# into strictly SLHA 2 compliant parameter cards for the NMSSM implementaiton
# in FeynRules (UFO model) which can then be used in Madgraph 5. 
# LIMITATIONS: does not pass GUT scale info, does not pass metadata
#
# Requires: SLHAblock.py.
#
# Example use: python Tools2Param.py spectr1.dat decay1.dat param_card.dat
#                     (this file)    (spectrum)  (decays)   (output file)
#
# REMARK: Actually, I don't *strictly* adhere to SLHA2 since I don't order
# my squarks by mass. This, however, makes it easier to work with models
# in which the third generation is special (as assumed in SLHA1) since one
# doesn't have to figure out which particle ID corresponds to which squark.
#
# Remark: MG uses gauge couplings derived from SM inputs, so BLOCK GAUGE
# doesn't seem to used for anything.

# -------------------------------------------------------------------------- #

import sys # module for accessing arguments
from SLHAblock import SLHAblock # the SLHAblock class

spectfile = open(sys.argv[1],'r')	# Open spectrum file for reading
decayfile = open(sys.argv[2],'r')	# Open spectrum file for reading
writefile = open(sys.argv[3],'w')	# Create file for writing

blocklist = [] # List of blocks

# Print out a list of caveats

# print "Tools2Param version 3.0, alpha version"
# print "by Flip Tanedo, 3 June 2012... use at your own risk"

print "\n"

print "########################################################"
print "## Tools2Param: convert SLHA1 to SLHA2                ##"
print "##  by Flip Tanedo, pt267@cornell.edu                 ##"
print "##  Version 3; 3 June 2012... use at your own risk!   ##"
print "########################################################\n"

print "Memo: No QNUMBER blocks printed, please include these"
print "      by hand if you will eventually pass to Pythia."
print "Memo: Non-recognized blocks are dropped. Please modify"
print "      if you want to include vestigial blocks."

print "\n"

for line in spectfile: # load data
    if line.split() == []: # if the line is whitespace
        continue # skip this line
    if (len(blocklist) == 0) & (line.split()[0].upper() != 'BLOCK'):
        # if no blocks yet defined and this line isn't a new block
        continue # skip this line
    if line.split()[0].upper()=='BLOCK': # start new block
        if line.split()[1].upper()=='SPINFO': 
            continue # skip metadata at beginning of file 
            # If you want you can re-read spectfile and output
            #   the metadata to put into the param card
        else:
            blocklist.append(SLHAblock(line))
    elif (line.split()[0] == '#') | (line.split()[0] == ''):
        continue # skip this line
    else: # then this must be data
        blocklist[len(blocklist)-1].add_line(line)

spectfile.close()        

# for item in blocklist: # print data
#     item.printblock()
#     print '' # newline is implicit

# -------------------------------------------------------------------------- #

## Processing
# write a dictionary mapping block and blockname (handy for choosing to print)

block_dictionary = dict() # Initialize dictionary
for item in blocklist:
    if 'GUT' in item.input_data.upper():
        continue #  don't want no stinkin' GUT parameters in our param_card
    else:
        block_dictionary[item.name] = item

# List of required blocks
required_blocks = [
    'MASS',
    'GAUGE',
    'HMIX',
    'NMHMIX',
    'NMAMIX',
    'NMNMIX',
    'UMIX',
    'VMIX',
    'STOPMIX',
    'SBOTMIX',
    'STAUMIX',
    'YU',
    'YD',
    'YE',
    'AU',
    'AD',
    'AE',
    'NMSSMRUN'
    ]

# Check for required blocks
block_check = True
for item in required_blocks:
    if not (item in block_dictionary):
        print "ERROR: missing " + item + " from input file" 
        block_check = False

if block_check:
    print "All required blocks present. Good for you."

# -------------------------------------------------------------------------- #

## Now modify the appropriate blocks

## Trilinear scalar couplings: convert from A to T

if 'TU' in block_dictionary:
    print "WARNING: TU already defined, overwriting"
    
block_dictionary['TU'] = SLHAblock(
    "BLOCK TU # generated by Tools2Param: Tii = Aii yii\n")
for i in range(0,3):
    if ( block_dictionary['YU'].exists(i+1,i+1) &
         block_dictionary['AU'].exists(i+1,i+1) ):
            block_dictionary['TU'].add_data(i+1,i+1, 
                block_dictionary['AU'].get(i+1,i+1)*
                block_dictionary['YU'].get(i+1,i+1))

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

if 'TD' in block_dictionary:
    print "WARNING: TD already defined, overwriting"
    
block_dictionary['TD'] = SLHAblock(
    "BLOCK TD # generated by Tools2Param: Tii = Aii yii\n")
for i in range(0,3):
    if ( block_dictionary['YD'].exists(i+1,i+1) &
         block_dictionary['AD'].exists(i+1,i+1) ):
            block_dictionary['TD'].add_data(i+1,i+1, 
                block_dictionary['AD'].get(i+1,i+1)*
                block_dictionary['YD'].get(i+1,i+1))

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

if 'TE' in block_dictionary:
    print "WARNING: TE already defined, overwriting"
    
block_dictionary['TE'] = SLHAblock(
    "BLOCK TE # generated by Tools2Param: Tii = Aii yii\n")
for i in range(0,3):
    if ( block_dictionary['YE'].exists(i+1,i+1) &
         block_dictionary['AE'].exists(i+1,i+1) ):
            block_dictionary['TE'].add_data(i+1,i+1, 
                block_dictionary['AE'].get(i+1,i+1)*
                block_dictionary['YE'].get(i+1,i+1))

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

## Sfermion mixing: only third generation

if 'USQMIX' in block_dictionary:
    print "WARNING: USQMIX already defined, overwriting"
    
block_dictionary['USQMIX'] = SLHAblock(
    "BLOCK USQMIX # generated by Tools2Param from STOPMIX\n")
for i in range(0,5): # initialize with unit matrix
    block_dictionary['USQMIX'].add_data(i+1,i+1,1)

block_dictionary['USQMIX'].add_data(3,3,
    block_dictionary['STOPMIX'].get(1,1)
    )
    
block_dictionary['USQMIX'].add_data(3,6,
    block_dictionary['STOPMIX'].get(1,2)
    )
    
block_dictionary['USQMIX'].add_data(6,3,
    block_dictionary['STOPMIX'].get(2,1)
    )
    
block_dictionary['USQMIX'].add_data(6,6,
    block_dictionary['STOPMIX'].get(2,2)
    )
    
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

if 'DSQMIX' in block_dictionary:
    print "WARNING: DSQMIX already defined, overwriting"
    
block_dictionary['DSQMIX'] = SLHAblock(
    "BLOCK DSQMIX # generated by Tools2Param from SBOTMIX\n")
for i in range(0,5): # initialize with unit matrix
    block_dictionary['DSQMIX'].add_data(i+1,i+1,1)

block_dictionary['DSQMIX'].add_data(3,3,
    block_dictionary['SBOTMIX'].get(1,1)
    )
    
block_dictionary['DSQMIX'].add_data(3,6,
    block_dictionary['SBOTMIX'].get(1,2)
    )
    
block_dictionary['DSQMIX'].add_data(6,3,
    block_dictionary['SBOTMIX'].get(2,1)
    )
    
block_dictionary['DSQMIX'].add_data(6,6,
    block_dictionary['SBOTMIX'].get(2,2)
    )
    
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

if 'SELMIX' in block_dictionary:
    print "WARNING: SELMIX already defined, overwriting"
    
block_dictionary['SELMIX'] = SLHAblock(
    "BLOCK SELMIX # generated by Tools2Param from STAUMIX\n")
for i in range(0,5): # initialize with unit matrix
    block_dictionary['SELMIX'].add_data(i+1,i+1,1)

block_dictionary['SELMIX'].add_data(3,3,
    block_dictionary['STAUMIX'].get(1,1)
    )
    
block_dictionary['SELMIX'].add_data(3,6,
    block_dictionary['STAUMIX'].get(1,2)
    )
    
block_dictionary['SELMIX'].add_data(6,3,
    block_dictionary['STAUMIX'].get(2,1)
    )
    
block_dictionary['SELMIX'].add_data(6,6,
    block_dictionary['STAUMIX'].get(2,2)
    )

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

## Soft masses in the chiral basis, extract from EXTPAR

if 'MSQ2' in block_dictionary:
    print "WARNING: MSQ2 already defined, overwriting"
if 'MSU2' in block_dictionary:
    print "WARNING: MSU2 already defined, overwriting"
if 'MSD2' in block_dictionary:
    print "WARNING: MSD2 already defined, overwriting"
if 'MSL2' in block_dictionary:
    print "WARNING: MSL2 already defined, overwriting"
if 'MSE2' in block_dictionary:
    print "WARNING: MSE2 already defined, overwriting"

block_dictionary['MSQ2'] = SLHAblock(
    "BLOCK MSQ2 # generated by Tools2Param from EXTPAR\n")
block_dictionary['MSU2'] = SLHAblock(
    "BLOCK MSU2 # generated by Tools2Param from EXTPAR\n")
block_dictionary['MSD2'] = SLHAblock(
    "BLOCK MSD2 # generated by Tools2Param from EXTPAR\n")
block_dictionary['MSL2'] = SLHAblock(
    "BLOCK MSL2 # generated by Tools2Param from EXTPAR\n")
block_dictionary['MSE2'] = SLHAblock(
    "BLOCK MSE2 # generated by Tools2Param from EXTPAR\n")
    
for i in range (0,3):
    if block_dictionary['EXTPAR'].exists(31+i):
        block_dictionary['MSL2'].add_data(i+1, i+1, 
            pow(block_dictionary['EXTPAR'].get(31+i),2))
    if block_dictionary['EXTPAR'].exists(34+i):
        block_dictionary['MSE2'].add_data(i+1, i+1, 
            pow(block_dictionary['EXTPAR'].get(34+i),2))
    if block_dictionary['EXTPAR'].exists(41+i):
        block_dictionary['MSQ2'].add_data(i+1, i+1, 
            pow(block_dictionary['EXTPAR'].get(41+i),2))
    if block_dictionary['EXTPAR'].exists(44+i):
        block_dictionary['MSU2'].add_data(i+1, i+1, 
            pow(block_dictionary['EXTPAR'].get(44+i),2))
    if block_dictionary['EXTPAR'].exists(47+i):
        block_dictionary['MSD2'].add_data(i+1, i+1, 
            pow(block_dictionary['EXTPAR'].get(47+i),2))

## Fix MSOFT to only include gauginos and higgsino masses (strip others)
## ... acutually, so what if there's extra info? Worry about this later.

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

## Unit matrix for CKM and PMNS

if 'VCKM' in block_dictionary:
    print "WARNING: VCKM already defined, overwriting"
if 'UPMNS' in block_dictionary:
    print "WARNING: UPMNS already defined, overwriting"

block_dictionary['VCKM'] = SLHAblock(
    "BLOCK VCKM # generated by Tools2Param: unit matrix\n")
block_dictionary['UPMNS'] = SLHAblock(
    "BLOCK UPMNS # generated by Tools2Param: unit matrix\n")

for i in range (0,3):
    block_dictionary['VCKM'].add_data(i+1,i+1,1)
    block_dictionary['UPMNS'].add_data(i+1,i+1,1)
    
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#

## unit sneutrino mixing matrix

if 'SNUMIX' in block_dictionary:
    print "WARNING: SNUMIX already defined, overwriting"

block_dictionary['SNUMIX'] = SLHAblock(
    "BLOCK SNUMIX # generated by Tools2Param: unit matrix\n")

for i in range (0,3):
    block_dictionary['SNUMIX'].add_data(i+1,i+1,1)


# -------------------------------------------------------------------------- #

## Writing: try this ordering

# BLOCK SMINPUTS
# BLOCK MASS
# BLOCK UPMNS
# BLOCK VCKM
# BLOCK GAUGE

# BLOCK USQMIX
# BLOCK DSQMIX
# BLOCK SELMIX
# BLOCK SNUMIX
# BLOCK UMIX
# BLOCK VMIX
# BLOCK HMIX
# BLOCK NMAMIX
# BLOCK NMHMIX
# BLOCK NMNMIX
# BLOCK NMSSMRUN

# BLOCK MSQ2
# BLOCK MSU2
# BLOCK MSD2
# BLOCK MSE2
# BLOCK MSL2
# BLOCK MSOFT (WHAT'S NOT IN OTHER BLOCKS)

# BLUCK YU
# BLOCK YD
# BLOCK YE
# BLOCK TD
# BLOCK TE
# BLOCK TU

# DECAY BLOCKS


# EXTRA
# BLOCK MINPAR
# BLOCK EXTPAR
# BLOCK LOWEN?

# QUANTUM NUMBERS (AUTO GEN BY FEYNRULES)



# Now write to file
# Place a header
writefile.write("########################################################\n")
writefile.write("## PARAM_CARD generated by MCSSMTools and Tools2Param ##\n")
writefile.write("##  by Flip Tanedo, pt267@cornell.edu                 ##\n")
writefile.write("##  Version 3; 3 June 2012... use at your own risk!   ##\n")
writefile.write("########################################################\n")
writefile.write("\n")


# # Now fill it up: old version, fill from blocklist
# for item in blocklist:
#     item.write(writefile)
#     writefile.write('\n')

# # Now fill it up: new version, fill from block_dictionary
# for item in block_dictionary:
#     block_dictionary[item].write(writefile)
#     writefile.write('\n')

# order of blocks to be written
write_blocks = [
    'SMINPUTS',
    'MASS',
    'UPMNS',
    'VCKM',
    'GAUGE', 
#
    'USQMIX',
    'DSQMIX',
    'SELMIX',
    'SNUMIX',
    'UMIX',
    'VMIX',
    'HMIX',
    'NMAMIX',
    'NMHMIX',
    'NMNMIX',
    'NMSSMRUN',
#
    'MSQ2',
    'MSU2',
    'MSD2',
    'MSL2',
    'MSE2',
    'MSOFT',
#
    'YU',
    'YD',
    'YE',
    'TU',
    'TD',
    'TE',
#
    'MINPAR',
    'EXTPAR',
    'LOWEN'
    ]

for item in write_blocks:
    block_dictionary[item].write(writefile)
    writefile.write('\n')

# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .#
# DECAY DATA

writefile.write('\n')
writefile.write("########################################################\n")
writefile.write("## DECAY TABLE, copied directly from source           ##\n")
writefile.write("########################################################\n")


writefile.write('\n')
for line in decayfile:
    writefile.write(line)

decayfile.close()


# QUANTUM NUMBERS (AUTO GEN BY FEYNRULES)


writefile.close()

# Things to do here: look at writefile and check for data
# to do: skip GUT blocks use "in" command
#   convert Y to T
#   convert sfermion...
#   sort blocks which are used and those which are vestigial