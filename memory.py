from math import log
import random

class Memory:

    def __init__(self, mem_size, block_size, assoc):
        # Defining memory parameters
        self.block_size = block_size
        self.mem_size = mem_size
        self.assoc = assoc

        self.n_set = self.mem_size // (self.block_size * self.assoc)

        # address params
        self.nb_offset = int(log(self.block_size, 2))  # number of offset bits
        self.nb_index = int(log(self.n_set, 2))  # number of index bits
        self.nb_tag = int(log(self.mem_size, 2)) - self.nb_index - self.nb_offset  # number of tag bits

        # Creating Memory
        self.set = {}
        for i in range(mem_size):
            self.set[i] = random.randint(0,10)

    def read(self, addr):
        out = None

        addr_decimal = int(addr, 2)
        if addr_decimal in self.set:
            out = self.set[addr_decimal]

        return out

    def write(self, addr, word):

        addr_decimal = int(addr, 2)
        self.set.update({addr_decimal:word})

    def get_block(self, addr):

        addr_decimal = int(addr, 2)
        block = []
        start = addr_decimal - (addr_decimal % self.block_size)
        end = start + self.block_size

        for i in range(start, end):
            hold = self.set[i]
            block.append(hold)

        return block
        
    #get block and prefetch n blocks
    #prefetch = 
    def get_block_pfch(self, addr, prefetch):

        addr_decimal = int(addr, 2)     #convert address to binary
        
        block_pfch = []
        start = addr_decimal - (addr_decimal % self.block_size)
        end = start + self.block_size
        
        #addr_pfch = addr_decimal + int(prefetch, 2)     #add blocks to prefetch to address
        #start_pfch = addr_decimal - (addr_pfch % self.block_size)
        
        end_pfch = start + prefetch*self.block_size
        
        #loop to append fetch and prefetch
        for p in range(start, end_pfch, self.block_size):
            for i in range(start, end):
                hold = self.set[i]
                block_pfch.append(hold)
                
        return block_pfch
        
    def load_block(self,addr,blk):
        addr_decimal = int(addr, 2)
        block = []
        start = addr_decimal - (addr_decimal % self.block_size)
        end = start + self.block_size

        j = 0
        for i in range(start, end):
            self.set[i] = blk[j]
            j += 1
            
    def get_fields(self, address):
        tag = address[:self.nb_tag]
        index = address[self.nb_tag:self.nb_tag + self.nb_index]
        offset = address[self.nb_tag + self.nb_index: self.nb_tag + self.nb_index + self.nb_offset]
        return tag, index, offset
