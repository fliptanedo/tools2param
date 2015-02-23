#! /usr/bin/env python
# Tools3Param.py version 3.1
# Flip Tanedo, 17 June 2012
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

# -------------------------------------------------------------------------- #

import sys # module for accessing arguments
decayfile = open(sys.argv[1],'r')	# Open decay file for reading
writefile = open(sys.argv[2],'w')	# Create file for writing

for line in decayfile:
    if line.upper().startswith('DECAY'):
        writefile.write(line)
        
decayfile.close()
writefile.close()