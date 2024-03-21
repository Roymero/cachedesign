from math import log
from cache import Cache
from memory import Memory

class Simulator:
	def __init__(self, cache_size, mem_size, block_size, assoc, replace_pol, write_pol):
		self.cache = Cache(cache_size, mem_size, block_size, assoc, replace_pol, write_pol)
		self.memory = Memory(mem_size, block_size, assoc)
		
		self.write_pol = write_pol
		
		# hit and miss metrics
		self.hit = 0
		self.miss = 0
		
	def read(self, addr):
		# read from cache
		out = self.cache.read(addr)
		if out != None:
			self.hit += 1
		else:
			self.miss += 1
			blk = self.memory.get_block(addr)
			if self.write_pol == 'WB':
				oldblk = self.cache.load(addr, blk)
				self.memory.load(oldblk.item)
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
				oldblk = self.cache.load(addr, blk)
				
				self.memory.load(oldblk.item)
				
				self.cache.write(addr, word)
			
	
	
