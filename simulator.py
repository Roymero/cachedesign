from math import log
from cache import Cache
from memory import Memory

import argparse
import random

#need to add # to prefetch variable
#pfch is # of blocks to prefetch

class Simulator:
    #def __init__(self, cache_size, mem_size, block_size, assoc, replace_pol, write_pol, block_pfch):
    def __init__(self, cache_size, mem_size, block_size, assoc, replace_pol, write_pol, block_pfch):
        self.cache = Cache(cache_size, block_size, assoc, mem_size, replace_pol, write_pol)
        self.memory = Memory(mem_size, block_size, assoc)
	    
        self.write_pol = write_pol
        
        self.block_pfch = block_pfch   #how many blocks to prefetch
        #block_pfch = 0, static, or random
        if block_pfch == 0:
            self.block_pfch = int(0)
        elif block_pfch == "static":
            self.block_pfch = 3
        elif block_pfch == "random":
            self.block_pfch = random.randrange(1, 10)
        print("\nblocks to prefetch: " + str(self.block_pfch) + "\n")
	    
	    # hit and miss metrics
        self.hit = 0
        self.miss = 0
	    
    def read(self, addr):
        # read from cache
        out = self.cache.read(addr)
        if out != None:
            self.hit += 1
        else:
        #cache miss
            self.miss += 1
            blk = self.memory.get_block(addr)   #get from memory
            #implement prefetch here
            
            
            
            if self.write_pol == 'WB':
                dirty, oldblk = self.cache.load(addr, blk)
                if dirty:
                    self.memory.load_block(oldblk.item)
            else:
                self.cache.load(addr, blk)
            out = self.cache.read(addr)
		    
        return out
        
        
        
    #test block(addr+1)
    def read2(self, addr):
        # read from cache
        out = self.cache.read(addr)
        if out != None:
            self.hit += 1
        else:
        #cache miss
            self.miss += 1
            #blk = self.memory.get_block(addr)   #get from memory
            #implement prefetch here
            #need to pass block_pfch to self.memory.get_block()
            blk = self.memory.get_block_pfch(addr, self.block_pfch)   #get from memory
            
            if self.write_pol == 'WB':
                dirty, oldblk = self.cache.load(addr, blk)
                if dirty:
                    self.memory.load_block(oldblk.item)
            else:
                self.cache.load(addr, blk)
            out = self.cache.read(addr)
        
        return out
        
        
        
	    
    def write(self, addr, word):
        written = self.cache.write(addr, word)
	    
        if written:
            self.hit += 1
        else:
            self.miss += 1
		    
        if self.write_pol == 'WT':
            self.memory.write(addr, word)
        elif self.write_pol == 'WB':
            if not written:
                blk = self.memory.get_block(addr)
                if self.write_pol == 'WB':
                    dirty, oldblk = self.cache.load(addr, blk)
                    if dirty:
                        self.memory.load(oldblk.item)
                else:
                    self.cache.load(addr, blk)
		        
                self.cache.write(addr, word)
                
def paddedaddr(addr, z):
    return bin(addr)[2:].zfill(z)
    
def paddedaddr2(addr2, z2):             #increment addr to give addr + 1
    return bin(addr2+1)[2:].zfill(z2)
	
if __name__ == '__main__':
    replacement_policies = ["LRU", "LFU", "FIFO", "RAND"]
    write_policies = ["WB", "WT"]
    prefetch_policies = ["0", "static", "random", "sine"]
    
    parser = argparse.ArgumentParser(description="Simulate the cache of a CPU.")
    parser.add_argument("MEMORY", metavar="MEMORY", type=int,
                        help="Size of main memory in 2^N bytes")
    parser.add_argument("CACHE", metavar="CACHE", type=int,
                        help="Size of the cache in 2^N bytes")
    parser.add_argument("BLOCK", metavar="BLOCK", type=int,
                        help="Size of a block of memory in 2^N bytes")
    parser.add_argument("ASSOC", metavar="MAPPING", type=int,
                        help="Mapping policy for cache in 2^N ways")
    parser.add_argument("REPLACE", metavar="REPLACE", choices=replacement_policies,
                        help="Replacement policy for cache {"+", ".join(replacement_policies)+"}")
    parser.add_argument("WRITE", metavar="WRITE", choices=write_policies,
                        help="Write policy for cache {"+", ".join(write_policies)+"}")
    #parser.add_argument("PFCH", metavar="PFCH", type=int,
    #                    help="Number of blocks to prefetch")
    parser.add_argument("PFCH", metavar="PFCH", choices=prefetch_policies,
                        help="Prefetch policy {"+", ".join(prefetch_policies)+"}")
    args = parser.parse_args()

    mem_size = 2 ** args.MEMORY
    cache_size = 2 ** args.CACHE
    block_size = 2 ** args.BLOCK
    assoc = 2 ** args.ASSOC
    replace_pol = args.REPLACE
    write_pol = args.WRITE
    block_pfch = args.PFCH
    
    addrlen = args.MEMORY
    
    simulator = Simulator(cache_size,
                          mem_size,
                          block_size,
                          assoc,
                          replace_pol,
                          write_pol,
                          block_pfch)

    
    command = None

    while (command != "quit"):
        operation = input("> ")
        operation = operation.split()

        command = operation[0]
        params = operation[1:]
        
        print("\nprefetch policy:" + block_pfch +"\n")
        
        if command == "read" and len(params) == 1:
            addr = paddedaddr(int(params[0]), addrlen)
            out = simulator.read(addr)
            print(out)
        elif command == "read2" and len(params) == 1:   #read addr + 1
            addr = paddedaddr2(int(params[0]), addrlen)
            out = simulator.read2(addr)
            #print("\nblocks to prefetch: " + str(block_pfch) + "\n")
            #print("\nblocks to prefetch: " + str(self.block_pfch) + "\n")
            print(out)
        elif command == "write" and len(params) == 2:
            addr = paddedaddr(int(params[0]), addrlen)
            word = int(params[1])
            out = simulator.write(addr, word)
        elif command == "randread" and len(params) == 1:
            pass
        elif command == "randwrite" and len(params) == 1:
            pass
        elif command == "stats":
            print('hits:', simulator.hit, 'misses:', simulator.miss)
        elif command != "quit":
            print("\nERROR: invalid command\n")
