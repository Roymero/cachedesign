from math import log
from cache import Cache
from memory import Memory

import argparse
import random

class Simulator:
    def __init__(self, mem_size, cache_size1, assoc1, cache_size2, assoc2, block_size, replace_pol, write_pol):
        self.cache = Cache(cache_size1, block_size, assoc1, mem_size, replace_pol, write_pol)
        print('cache1 loaded with size:', cache_size1)
        self.cache2 = Cache(cache_size2, block_size, assoc2, mem_size, replace_pol, write_pol)
        print('cache2 loaded with size:', cache_size2)
        self.memory = Memory(mem_size, block_size, assoc2)
        print('mem loaded with size:', mem_size)
	    
        self.write_pol = write_pol
	    
	    # hit and miss metrics
        self.hit = 0
        self.miss = 0
        self.hit2 = 0
        self.miss2 = 0
    '''    
    def read(self, addr):
        out, offset = self.cache.read(addr) # read from cache1
        if out != None: # if hit1
            self.hit += 1
        else: # if miss1
            self.miss += 1
            blk = self.memory.get_block(addr) # get block from memory
            dirty, oldblk = self.cache.load(addr, blk)
            if self.write_pol == 'WB' and dirty: # if WB, write to memory
                self.memory.load_block(oldblk)
            out, offset = self.cache.read(addr)
		    
        return out.item[offset]
	    
    def write(self, addr, word):
        written = self.cache.write(addr, word) # write to cache1
	    
        if written: # if block-to-write exists in cache1
            self.hit += 1
        else: #if block-to-write not in cache1
            self.miss += 1
		    
        if self.write_pol == 'WT':
            blk = self.memory.get_block(addr) # get block from memory
            self.cache.load(addr, blk) # load block to cache1
            self.cache.write(addr, word) # write to cache1
            self.memory.write(addr, word) # write to memory
        elif self.write_pol == 'WB':
            if not written:
                blk = self.memory.get_block(addr)
                if self.write_pol == 'WB':
                    dirty, oldblk = self.cache.load(addr, blk)
                    if dirty:
                        self.memory.load(oldblk)
                else:
                    self.cache.load(addr, blk)
		        
                self.cache.write(addr, word)
    '''            
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
                if self.write_pol == 'WB' and dirty: # if WB, write to memory
                    self.memory.load(oldblk)
                    
                out, offset = self.cache2.read(addr) # read from cache2
                dirty, oldblk = self.cache.load(addr, out) # load block onto cache1
                if self.write_pol == 'WB' and dirty: # if WB, write to cache2
                    dirty, oldblk = self.cache2.load(addr, blk)
                    if self.write_pol == 'WB' and dirty: # if WB, write to memory
                        self.memory.load(oldblk)
                out, offset = self.cache.read(addr) # read from cache1
            else:
                self.hit2 += 1
                dirty, oldblk = self.cache.load(addr, out) # load block onto cache1
                if self.write_pol == 'WB' and dirty: # if WB, write to cache2
                    dirty, oldblk = self.cache2.load(addr, oldblk)
                    if self.write_pol == 'WB' and dirty: # if WB, write to memory
                        self.memory.load(oldblk)
                out, offset = self.cache.read(addr) # read from cache1
        return out.item[offset]
        
    def write(self, addr, word):
        if self.write_pol == 'WT': # write to l1
            written = self.cache.write(addr, word)
            
            if written: # write to l2
                self.hit += 1
                written = self.cache2.write(addr, word)
                
                if written: # write to mem
                    self.hit2 += 1
                    self.memory.write(addr, word)
                else: # load blk to l2 from mem, then write to l2, mem
                    self.miss2 += 1
                    blk = self.memory.get_block(addr)
                    self.cache2.load(addr, blk)
                    self.cache2.write(addr, word)
                    self.memory.write(addr, word)
            else: # load blk to l1 from l2
                self.miss += 1
                out, offset = self.cache2.read(addr) # read from cache2
                if out == None: # load blk to l2 from mem, then load blk to l1 from l2
                    self.miss2 += 1
                    blk = self.memory.get_block(addr)
                    self.cache2.load(addr, blk)
                    self.cache.load(addr, blk)
                else:
                    self.hit2 += 1
                self.cache.write(addr, word)
                self.cache2.write(addr, word)
                self.memory.write(addr, word)
        elif self.write_pol == 'WB': # write to l1
            written = self.cache.write(addr, word)
            
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
                        self.memory.load(oldblk)
                    out, offset = self.cache2.read(addr) # read from l2
                    dirty, oldblk = self.cache.load(addr, out) # load to l1 from l2
                    if dirty: # write to l2 from l1
                        dirty, oldblk = self.cache2.load(addr, oldblk)
                        if dirty: # write to mem from l2
                            self.memory.load(oldblk)
                else:
                    self.hit2 += 1
                    dirty, oldblk = self.cache.load(addr, out) # load to l1 from l2
                    if dirty: # write to l2 from l1
                        dirty, oldblk = self.cache2.load(addr, oldblk)
                        if dirty: # write to mem from l2
                            self.memory.load(oldblk)
                    self.cache.write(addr, word) # write to l1

# from decimal to binary
def decpaddedaddr(addr, z):
    return bin(int(addr))[2:].zfill(z)

# from hexadecimal to binary
def hexpaddedaddr(addr, z):
    return bin(int(addr,16))[2:].zfill(z)
	
if __name__ == '__main__':
    replacement_policies = ["LRU", "LFU", "FIFO", "RAND"]
    write_policies = ["WB", "WT"]
    
    parser = argparse.ArgumentParser(description="Simulate the cache of a CPU.")
    parser.add_argument("MEMORY", metavar="MEMORY", type=int,
                        help="Size of main memory in 2^N bytes")
    parser.add_argument("CACHE2", metavar="CACHE", type=int,
                        help="Size of the cache1 in 2^N bytes")
    parser.add_argument("ASSOC2", metavar="MAPPING", type=int,
                        help="Mapping policy for cache1 in 2^N ways")
    parser.add_argument("CACHE1", metavar="CACHE", type=int,
                        help="Size of the cache2 in 2^N bytes")
    parser.add_argument("ASSOC1", metavar="MAPPING", type=int,
                        help="Mapping policy for cache2 in 2^N ways")
    parser.add_argument("BLOCK", metavar="BLOCK", type=int,
                        help="Size of a block of memory in 2^N bytes")
    parser.add_argument("REPLACE", metavar="REPLACE", choices=replacement_policies,
                        help="Replacement policy for cache {"+", ".join(replacement_policies)+"}")
    parser.add_argument("WRITE", metavar="WRITE", choices=write_policies,
                        help="Write policy for cache {"+", ".join(write_policies)+"}")
    args = parser.parse_args()

    mem_size = 2 ** args.MEMORY
    cache_size1 = 2 ** args.CACHE1
    assoc1 = 2 ** args.ASSOC1
    cache_size2 = 2 ** args.CACHE2
    assoc2 = 2 ** args.ASSOC2
    block_size = 2 ** args.BLOCK
    replace_pol = args.REPLACE
    write_pol = args.WRITE
    
    addrlen = args.MEMORY
    
    simulator = Simulator(mem_size,
                          cache_size1,
                          assoc1,
                          cache_size2,
                          assoc2,
                          block_size,
                          replace_pol,
                          write_pol)

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
