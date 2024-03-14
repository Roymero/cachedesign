from math import log


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

        return out

    def write(self, addr, word):

        addr_decimal = int(addr, 2)
        self.set.update({addr_decimal:word})

    def get_block(self, address):

        start = address - (address % self.block_size)

    def get_fields(self, address):
        tag = address[:self.nb_tag]
        index = address[self.nb_tag:self.nb_tag + self.nb_index]
        offset = address[self.nb_tag + self.nb_index: self.nb_tag + self.nb_index + self.nb_offset]
        return tag, index, offset
