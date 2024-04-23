from math import log
import random
from cache import Block

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

    def read(self, addr):
        out = None

        addr_decimal = int(addr, 2)
        if addr_decimal in self.set:
            out = self.set[addr_decimal]
        else:
            self.set[addr_decimal] = random.randint(0,10)

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
            if i in self.set:
                hold = self.set[i]
            else:
                self.set[i] = random.randint(0,10)
                hold = self.set[i]
            block.append(hold)
        newblock = Block(self.block_size)
        newblock.item = block
        block = newblock # need to wrap it in Block class per Cache class' syntax

        return block
        
    def load_block(self,addr,blk):
        blk = blk.item
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
        if index == '':
            index = '0'
        offset = address[self.nb_tag + self.nb_index: self.nb_tag + self.nb_index + self.nb_offset]
        return tag, index, offset
