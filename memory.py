from math import log


class Memory:

    def __init__(self, size, block_size):
        # Defining memory parameters
        self.block_size = block_size
        self.size = size

        # address params
        self.nb_offset = int(log(self.block_size, 2))  # number of offset bits
        self.nb_index = int(log(self.n_set, 2))  # number of index bits
        self.nb_tag = int(log(self.mem_size, 2)) - self.nb_index - self.nb_offset  # number of tag bits

        # Creating Memory
        self.set = {}

    def read(self, addr):
        out = None

        
        if self.set[addr]:
            out = self.set[addr]

        return out


    def write(self, addr, word):

        self.set.update({addr:word})


    def get_block(self, address):

        start = address - (address % self.block_size)

    def get_fields(self, address):
        tag = address[:self.nb_tag]
        index = address[self.nb_tag:self.nb_tag + self.nb_index]
        offset = address[self.nb_tag + self.nb_index: self.nb_tag + self.nb_index + self.nb_offset]
        return tag, index, offset