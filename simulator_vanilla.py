from math import log
from cache import Cache
from memory import Memory

import argparse
import random
import json
import os

#####################################################
# HARDCODED L1 and L2 ACCESS TIMES AND MISS PENALTY #
#####################################################
L1T = 2
L2T = 15
L2MT = 90

class L1Simulator:
    def __init__(self, mem_size, cache_size1, assoc1, block_size, replace_pol):
        self.cache = Cache(cache_size1, block_size, assoc1, mem_size, replace_pol)
        print('cache1 loaded with size:', cache_size1)
        self.memory = Memory(mem_size, block_size, assoc2)
        print('mem loaded with size:', mem_size)
        
        # enable or disable prefetch
        self.window = [0]
        
        for i in range(1, pfch_window + 1):
            ele = [i, -i]
            self.window.extend(ele)
        
        if pfch_window == -1:
            self.window = [0,1]
            
        print("prefetch window width: " + str(pfch_window) +"\n")
	    
	    # hit, miss, and average access time metrics
        self.hit = 0
        self.miss = 0
          
    def read(self, addr, addrlen):
        window = self.window
        
        out, offset = self.cache.read(addr) # read from l1 
       
        if out != None:
            self.hit +=1
        else:
            self.miss += 1
            blk = self.memory.get_block(addr)
            dirty, oldblk = self.cache.load(addr, blk)
            if dirty: # write to mem from l1
                self.memory.load_block(addr, oldblk)
            out, offset = self.cache.read(addr)
        
        return out.item[offset]
        
    def write(self, addr, word):
        window = self.window
        written = self.cache.write(addr, word) # write to l1
        
        if written:
            self.hit +=1
        else:
            self.miss += 1
            blk = self.memory.get_block(addr)
            dirty, oldblk = self.cache.load(addr, blk)
            if dirty: # write to mem from l1
                self.memory.load_block(addr, oldblk)
            self.cache.write(addr, word)
        
    def AAT(self):
        L1MR = self.miss/(self.hit + self.miss)

        return L1T + L1MR * L2MT

class Simulator:
    def __init__(self, mem_size, cache_size1, assoc1, cache_size2, assoc2, block_size, replace_pol, inclusion_pol, pfch_window):
        self.cache = Cache(cache_size1, block_size, assoc1, mem_size, replace_pol)
        print('cache1 loaded with size:', cache_size1)
        self.cache2 = Cache(cache_size2, block_size, assoc2, mem_size, replace_pol)
        print('cache2 loaded with size:', cache_size2)
        self.memory = Memory(mem_size, block_size, assoc2)
        print('mem loaded with size:', mem_size)
        
        # enable or disable prefetch
        self.window = [0]
        
        for i in range(1, pfch_window + 1):
            ele = [i, -i]
            self.window.extend(ele)
        
        if pfch_window == -1:
            self.window = [0,1]
            
        print("prefetch window width: " + str(pfch_window) +"\n")
	    
	    # hit, miss, and average access time metrics
        self.hit = 0
        self.miss = 0
        self.hit2 = 0
        self.miss2 = 0
        
        self.include = True
        if inclusion_pol == "NON":
            self.include = False
          
    def read(self, addr, addrlen):
        window = self.window
        
        out, offset = self.cache.read(addr) # read from l1 
       
        if out != None:
            self.hit +=1
        else:
            self.miss += 1
            for x in window: # fetch a window of blks, first blk is the desired blk
                current_block = (x*block_size)
                current_addr = int(addr, 2) + current_block #int
                addr_bin = decpaddedaddr(current_addr, addrlen) #decimal to binary
                
                out, offset = self.cache2.read(addr_bin) # read from l2
                
                if out == None: #L2 miss
                    if x == 0: # if first blk in window
                        self.miss2 += 1
                    blk = self.memory.get_block(addr_bin) # read from memory
                    dirty, oldblk = self.cache2.load(addr_bin, blk) # load block onto l2
                    if dirty: # if dirty, write to memory
                        self.memory.load_block(addr_bin, oldblk)
                    if self.include: # if inclusion
                        dirty, oldblk = self.cache.purge(addr_bin)
                        if dirty: # write to mem directly from l1
                            self.memory.load_block(addr_bin, oldblk)
                    out, offset = self.cache2.read(addr_bin) # read from l2
                    dirty, oldblk = self.cache.load(addr_bin, out) # load block onto l1
                    if dirty: # if dirty, write to l2
                        dirty, oldblk = self.cache2.load(addr_bin, blk)
                        if dirty: # if dirty, write to memory
                            self.memory.load_block(addr_bin, oldblk)
                    if x == 0: # if first blk in window
                        out, offset = self.cache.read(addr_bin) # read from l1
                else:
                    if x == 0: # if first blk in window
                        self.hit2 += 1
                    dirty, oldblk = self.cache.load(addr_bin, out) # load block onto l1
                    if dirty: # if dirty, write to l2
                        dirty, oldblk = self.cache2.load(addr_bin, oldblk)
                        if dirty: # if dirty, write to memory
                            self.memory.load_block(addr_bin, oldblk)
                    if x == 0: # if first blk in window
                        out, offset = self.cache.read(addr_bin) # read from l1
        
        return out.item[offset]
        
    def write(self, addr, word):
        window = self.window
        written = self.cache.write(addr, word) # write to l1
        
        if written:
            self.hit +=1
        else:
            self.miss += 1
            for x in window:
                current_block = (x*block_size)
                current_addr = int(addr, 2) + current_block #int
                if current_addr < 0:
                    continue
                addr_bin = decpaddedaddr(current_addr, addrlen) #decimal to binary
            
                out, offset = self.cache2.read(addr_bin) # read from l2
                if out == None:
                    if x == 0: # if first blk in window
                        self.miss2 += 1
                    blk = self.memory.get_block(addr_bin) # read from mem
                    dirty, oldblk = self.cache2.load(addr_bin, blk) # load to l2 from mem
                    if dirty: # write to mem from l2
                        self.memory.load_block(addr_bin, oldblk)
                    if self.include: # if inclusion
                        dirty, oldblk = self.cache.purge(addr_bin)
                        if dirty: # write to mem directly from l1
                            self.memory.load_block(addr_bin, oldblk)
                    out, offset = self.cache2.read(addr_bin) # read from l2
                    dirty, oldblk = self.cache.load(addr_bin, out) # load to l1 from l2
                    if dirty: # write to l2 from l1
                        dirty, oldblk = self.cache2.load(addr_bin, oldblk)
                        if dirty: # write to mem from l2
                            self.memory.load_block(addr_bin, oldblk)
                    if x == 0: # if first blk in window
                        self.cache.write(addr_bin, word) # write to l1
                else:
                    if x == 0: # if first blk in window
                        self.hit2 += 1
                    dirty, oldblk = self.cache.load(addr_bin, out) # load to l1 from l2
                    if dirty: # write to l2 from l1
                        dirty, oldblk = self.cache2.load(addr_bin, oldblk)
                        if dirty: # write to mem from l2
                            self.memory.load_block(addr_bin, oldblk)
                    if x == 0: # if first blk in window
                        self.cache.write(addr_bin, word) # write to l1
        
    def AAT(self):
        L1MR = self.miss/(self.hit + self.miss)
        L2MR = self.miss2/(self.hit2 + self.miss2)

        return L1T + L1MR * L2T + L1MR * L2MR * L2MT

# from decimal to binary
def decpaddedaddr(addr, z):
    return bin(int(addr))[2:].zfill(z)

# from hexadecimal to binary
def hexpaddedaddr(addr, z):
    return bin(int(addr,16))[2:].zfill(z)
	
if __name__ == '__main__':
    replacement_policies = ["LRU", "LFU", "FIFO", "RAND"]
    inclusion_policies = ["NON", "INCLUDE"]
    
    parser = argparse.ArgumentParser(description="Simulate the cache of a CPU.")
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
    parser.add_argument("INCLUSION", metavar="INCLUSION", choices=inclusion_policies,
                        help="Replacement policy for cache {"+", ".join(inclusion_policies)+"}")
    parser.add_argument("PREFETCH", metavar="PREFETCH", type=int,
                        help="L2 prefetching window width")
    parser.add_argument("--l1", action="store_true", 
                    	help="use L1 cache only, CACHE2, ASSOC2, INCLUSION and PREFETCH will be disregarded, but please put dummy variables for them") 
    args = parser.parse_args()

    mem_size = 2 ** 32
    cache_size1 = 2 ** args.CACHE1
    assoc1 = 2 ** args.ASSOC1
    cache_size2 = 2 ** args.CACHE2
    assoc2 = 2 ** args.ASSOC2
    block_size = 2 ** args.BLOCK
    replace_pol = args.REPLACE
    inclusion_pol = args.INCLUSION
    pfch_window = args.PREFETCH
    
    addrlen = 32
    
    if not args.l1:
        simulator = Simulator(mem_size,
                              cache_size1,
                              assoc1,
                              cache_size2,
                              assoc2,
                              block_size,
                              replace_pol,
                              inclusion_pol,
                              pfch_window)
    else:
    	simulator = L1Simulator(mem_size,
				              cache_size1,
				              assoc1,
				              block_size,
				              replace_pol)
    
    command = None
    while (command != "quit"):
        try:
            operation = input("> ")
        except EOFError:
            if not args.l1:
                print('prefetch window width: ' + str(pfch_window))
            print('> hits1:', simulator.hit, 'misses1:', simulator.miss)
            if not args.l1:
            	print('> hits2:', simulator.hit2, 'misses2:', simulator.miss2)
            print("Average Access Time: ", simulator.AAT())
            '''
            # save results for viz
            if 'graph_'+inclusion_pol+'.json' not in os.listdir('outputs'):
                json.dump({}, open('outputs/graph_'+inclusion_pol+'.json', 'w'))
            data = json.load(open('outputs/graph_'+inclusion_pol+'.json'))
            L1MR = simulator.miss/(simulator.hit + simulator.miss)
            data[cache_size2] = simulator.AAT()
            json.dump(data, open('outputs/graph_'+inclusion_pol+'.json', 'w'))
            '''
            break
        operation = operation.split()

        command = operation[0]
        params = operation[1:]

        if command == "read" and len(params) == 1:
            addr = decpaddedaddr(params[0], addrlen)
            out = simulator.read(addr, addrlen)
            print(command, params[0], out)
        elif command == "write" and len(params) == 2:
            addr = decpaddedaddr(params[0], addrlen)
            word = int(params[1])
            out = simulator.write(addr, word)
            print(command, params[0], params[1])
        elif command == "r" and len(params) == 1:
            addr = hexpaddedaddr(params[0], addrlen)
            out = simulator.read(addr, addrlen)
            print(command, params[0], out)
        elif command == "w" and len(params) == 1:
            addr = hexpaddedaddr(params[0], addrlen)
            word = random.randint(0, 10)
            out = simulator.write(addr, word)
            print(command, params[0], word)
        elif command == "stats":
            print('hits1:', simulator.hit, 'misses1:', simulator.miss)
            if not args.l1:
            	print('hits2:', simulator.hit2, 'misses2:', simulator.miss2)
            print("Average Access Time: ", simulator.AAT())
        elif command != "quit":
            print('hits1:', simulator.hit, 'misses1:', simulator.miss)
            if not args.l1:
            	print('hits2:', simulator.hit2, 'misses2:', simulator.miss2)
            print("Average Access Time: ", simulator.AAT())
            print("\nERROR: invalid command\n")
