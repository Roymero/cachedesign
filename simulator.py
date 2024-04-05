from math import log
from cache import Cache
from memory import Memory

import argparse
import random

class Simulator:
    def __init__(self, mem_size, cache_size1, assoc1, cache_size2, assoc2, block_size, replace_pol):
        self.cache = Cache(cache_size1, block_size, assoc1, mem_size, replace_pol)
        print('cache1 loaded with size:', cache_size1)
        self.cache2 = Cache(cache_size2, block_size, assoc2, mem_size, replace_pol)
        print('cache2 loaded with size:', cache_size2)
        self.memory = Memory(mem_size, block_size, assoc2)
        print('mem loaded with size:', mem_size)
	    
	    # hit and miss metrics
        self.hit = 0
        self.miss = 0
        self.hit2 = 0
        self.miss2 = 0
          
    def read(self, addr):
        out, offset = self.cache.read(addr) # read from cache1
        if out != None:
            self.hit +=1
        else:
            self.miss += 1
            out, offset = self.cache2.read(addr) # read from cache2
            if out == None:
                self.miss2 += 1
                blk = self.memory.get_block(addr) # read from memory
                dirty, oldblk = self.cache2.load(addr, blk) # load block onto cache2
                if dirty: # if WB, write to memory
                    self.memory.load_block(addr, oldblk)
                    
                out, offset = self.cache2.read(addr) # read from cache2
                dirty, oldblk = self.cache.load(addr, out) # load block onto cache1
                if dirty: # if WB, write to cache2
                    dirty, oldblk = self.cache2.load(addr, blk)
                    if dirty: # if WB, write to memory
                        self.memory.load_block(addr, oldblk)
                out, offset = self.cache.read(addr) # read from cache1
            else:
                self.hit2 += 1
                dirty, oldblk = self.cache.load(addr, out) # load block onto cache1
                if dirty: # if WB, write to cache2
                    dirty, oldblk = self.cache2.load(addr, oldblk)
                    if dirty: # if WB, write to memory
                        self.memory.load_block(addr, oldblk)
                out, offset = self.cache.read(addr) # read from cache1
        return out.item[offset]
        
    def write(self, addr, word):
        written = self.cache.write(addr, word) # write to l1
        
        if written:
            self.hit +=1
        else:
            self.miss += 1
            out, offset = self.cache2.read(addr) # read from l2
            if out == None:
                self.miss2 += 1
                blk = self.memory.get_block(addr) # read from mem
                dirty, oldblk = self.cache2.load(addr, blk) # load to l2 from mem
                if dirty: # write to mem from l2
                    self.memory.load_block(addr, oldblk)
                out, offset = self.cache2.read(addr) # read from l2
                dirty, oldblk = self.cache.load(addr, out) # load to l1 from l2
                if dirty: # write to l2 from l1
                    dirty, oldblk = self.cache2.load(addr, oldblk)
                    if dirty: # write to mem from l2
                        self.memory.load_block(addr, oldblk)
            else:
                self.hit2 += 1
                dirty, oldblk = self.cache.load(addr, out) # load to l1 from l2
                if dirty: # write to l2 from l1
                    dirty, oldblk = self.cache2.load(addr, oldblk)
                    if dirty: # write to mem from l2
                        self.memory.load_block(addr, oldblk)
                self.cache.write(addr, word) # write to l1

# from decimal to binary
def decpaddedaddr(addr, z):
    return bin(int(addr))[2:].zfill(z)

# from hexadecimal to binary
def hexpaddedaddr(addr, z):
    return bin(int(addr,16))[2:].zfill(z)
	
if __name__ == '__main__':
    replacement_policies = ["LRU", "LFU", "FIFO", "RAND"]
    
    parser = argparse.ArgumentParser(description="Simulate the cache of a CPU.")
    '''
    parser.add_argument("MEMORY", metavar="MEMORY", type=int,
                        help="Size of main memory in 2^N bytes", default=32)
    '''
    parser.add_argument("BLOCK", metavar="BLOCK", type=int,
                        help="Size of a block of memory in 2^N bytes")
    parser.add_argument("CACHE1", metavar="CACHE1", type=int,
                        help="Size of the cache1 in 2^N bytes")
    parser.add_argument("ASSOC1", metavar="ASSOC1", type=int,
                        help="Mapping policy for cache1 in 2^N ways")
    parser.add_argument("CACHE2", metavar="CACHE2", type=int,
                        help="Size of the cache2 in 2^N bytes")
    parser.add_argument("ASSOC2", metavar="ASSOC2", type=int,
                        help="Mapping policy for cache2 in 2^N ways")
    parser.add_argument("REPLACE", metavar="REPLACE", choices=replacement_policies,
                        help="Replacement policy for cache {"+", ".join(replacement_policies)+"}")
    args = parser.parse_args()

    #mem_size = 2 ** args.MEMORY
    mem_size = 2 ** 32
    cache_size1 = 2 ** args.CACHE1
    assoc1 = 2 ** args.ASSOC1
    cache_size2 = 2 ** args.CACHE2
    assoc2 = 2 ** args.ASSOC2
    block_size = 2 ** args.BLOCK
    replace_pol = args.REPLACE
    
    #addrlen = args.MEMORY
    addrlen = 32
    
    simulator = Simulator(mem_size,
                          cache_size1,
                          assoc1,
                          cache_size2,
                          assoc2,
                          block_size,
                          replace_pol)
    
    command = None

    while (command != "quit"):
        try:
            operation = input("> ")
        except EOFError:
            print('hits1:', simulator.hit, 'misses1:', simulator.miss)
            print('> hits2:', simulator.hit2, 'misses2:', simulator.miss2)
            break
        operation = operation.split()

        command = operation[0]
        params = operation[1:]

        if command == "read" and len(params) == 1:
            addr = decpaddedaddr(params[0], addrlen)
            out = simulator.read(addr)
            print(command, params[0], out)
        elif command == "write" and len(params) == 2:
            addr = decpaddedaddr(params[0], addrlen)
            word = int(params[1])
            out = simulator.write(addr, word)
            print(command, params[0], params[1])
        elif command == "r" and len(params) == 1:
            addr = hexpaddedaddr(params[0], addrlen)
            out = simulator.read(addr)
            print(command, params[0], out)
        elif command == "w" and len(params) == 1:
            addr = hexpaddedaddr(params[0], addrlen)
            word = random.randint(0, 10)
            out = simulator.write(addr, word)
            print(command, params[0], word)
        elif command == "stats":
            print('hits1:', simulator.hit, 'misses1:', simulator.miss)
            print('hits2:', simulator.hit2, 'misses2:', simulator.miss2)
        elif command != "quit":
            print('hits1:', simulator.hit, 'misses1:', simulator.miss)
            print('hits2:', simulator.hit2, 'misses2:', simulator.miss2)
            print("\nERROR: invalid command\n")
