# SLHAblock class by Flip 31 May 2012 -------------------------------------- #
# Last updated 10 June 2012 ------------------------------------------------- #
# Flip Tanedo (pt267@cornell.edu) ------------------------------------------ #
# REMARKS: I haven't done any formal error handling, just printed messages

class SLHAblock:
    """Carries all data from a SLHA block and some tools to access them.
    
    Attributes: input_data, name, data
    Methods: add_line, add_data datastring, get, exists,
        printblock, writeblock
    """
        
    def __init__(self, input_line):  # input: string starting with 'BLOCK'
        self.input_data = input_line # save for printing purposes
        self.name = input_line.split()[1] # name of block, for ID purposes
        self.data = [] # initialize to empty list, to fill with block data
        self.data_dimension = 0 # specify vector or matrix, for reading
        
    def add_line(self, input_line): # add a line of data
        # input: string containing an SLHA data line
        if len(input_line.split('#',1)) == 2:
            comment = input_line.split('#',1)[1].rstrip('\n')
        else:
            comment = ''
        separated_data_str = input_line.split('#',1)[0].split()
        separated_data = []
        if self.data_dimension == 0: # specify vector of matrix
            self.data_dimension = len(separated_data_str) - 1
        elif (len(separated_data_str)-1) != self.data_dimension:
            print "ERROR in SLHAblock.add_line(): dim doesn't match"
        if self.data_dimension == 1:
            separated_data.append(int(separated_data_str[0]))
            separated_data.append(float(separated_data_str[1]))
        elif self.data_dimension == 2:
            separated_data.append(int(separated_data_str[0]))
            separated_data.append(int(separated_data_str[1]))
            separated_data.append(float(separated_data_str[2]))
        else:
            print "ERROR in SLHAblock.add_line(): dimension "
            print "Dimension is " + str(self.data_dimension)
        separated_data.append(comment) # this is now a complete line of data
        self.data.append(separated_data)
        
    def add_data(self, *args): # add or modify an element
        # input: index (1 or 2) and value, optional comment (w/ leading space)
        num_args = len(args)
        has_comment = isinstance(args[num_args-1],str)
        comment = ''
        if has_comment: # save comment
            num_args = num_args - 1 # e.g. num_args = 3 for matrix
            comment = ' ' + args[num_args]
        if self.data_dimension != 0: # test if dimensions match
            if self.data_dimension != (num_args - 1):
                print "ERROR in SLHAblock.add_data(): dims don't match"
        if self.data_dimension == 0: # this is the first data point
            self.data_dimension = num_args - 1
        already_exists = False 
        if (num_args - 1) == 1:
            for datum in self.data:
                if datum[0] == args[0]:
                    already_exists = True
                    datum[1] = args[1]
                    datum[2] = comment
        elif (num_args - 1) == 2:
            for datum in self.data:
                if datum[0] == args[0]:
                    if datum[1] == args[1]:
                        already_exists = True
                        datum[2] = args[2]
                        datum[3] = comment
        else:
            print "ERROR in SLHAblock.add_data(): dim not 1 or 2"
        if already_exists == False:
            new_datum = []
            for x in range(0,num_args):
                new_datum.append(args[x])
            new_datum.append(comment)
            self.data.append(new_datum)
            # self.data.append(args)
            # Note: will not insert a leading space into the comment!

    def datastring(self, datum): # output string with line of data
        mydatum = 'error in SLHAblock.datastring()'
        if len(datum) == 3:
            mydatum = str(datum[0]).rjust(6) 
            if datum[1] >= 0:
                mydatum = mydatum + '     %.8E' % datum[1] 
            else:
                mydatum = mydatum + '    %.8E' % datum[1] 
            mydatum  = mydatum + '   #' + str(datum[2])
        elif len(datum) == 4:
            mydatum = str(datum[0]).rjust(3) + str(datum[1]).rjust(3) 
            if datum[2] >= 0:
                mydatum = mydatum + '     %.8E' % datum[2] 
            else:
                mydatum = mydatum + '    %.8E' % datum[2]
            mydatum = mydatum + '   #' + str(datum[3])
        else:
            print "ERROR: length of data line not 3 or 4"
        return mydatum
            
    def get(self, *args): # retrieve data (either 1 or 2 args)
        found_value = False
        if len(args) > 2:
            print "ERROR: only 1 or 2 arguments allowed in SLHAblock.exists"
        if len(args) == 0:
            print "ERROR: at least one argument required for SLHAblock.get"
        if len(args) != self.data_dimension:
            print "ERROR: data dim doesn't match # of args in SLHAblock.get"
        if len(args) == self.data_dimension:
            if len(args) == 1:
                for datum in self.data:
                    if datum[0] == args[0]:
                        found_value = True
                        return datum[1]
            if len(args) == 2:
                for datum in self.data:
                    if ( (datum[0] == args[0]) 
                        & (datum[1] == args[1]) ):
                        found_value = True
                        return datum[2]
            if found_value == False:
                print self.name + " does not have an element " + str(args)
        else:
            print "ERROR in SLHAblock.get"
            
    def exists(self, *args): # check if data exists (either 1 or 2 args)
        found_value = False
        if len(args) > 2:
            print "ERROR: only 1 or 2 arguments allowed in SLHAblock.get"
        if len(args) == 0:
            print "ERROR: at least one argument required for SLHAblock.exists"
        if len(args) != self.data_dimension:
            print "ERROR: dim doesn't match # of args in SLHAblock.exists"
        if len(args) == self.data_dimension:
            if len(args) == 1:
                for datum in self.data:
                    if datum[0] == args[0]:
                        found_value = True
            if len(args) == 2:
                for datum in self.data:
                    if ( (datum[0] == args[0]) 
                        & (datum[1] == args[1]) ):
                        found_value = True
        return found_value
        
    def printblock(self): # print block contents
        print self.input_data.rstrip('\n')
        for x in self.data:
            print self.datastring(x)
    
    def write(self,outstream): # output block to file
        outstream.write(self.input_data)
        for x in self.data:
            outstream.write(self.datastring(x)+'\n')



