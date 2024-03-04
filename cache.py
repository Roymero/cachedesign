from math import log

class Block:
	def __init__(self, size):
		self.item = [None] * size
		self.use = 0
		#self.modified = 0
		self.valid = 0
		self.tag = None

class Cache:
	def __init__(self, cache_size, block_size, assoc, mem_size, replace_pol):
		# define cache parameters
		self.cache_size = cache_size
		self.block_size = block_size
		self.assoc = assoc
		self.mem_size = mem_size
		
		#define policies
		self.replace_pol = replace_pol
		
		self.n_set = self.cache_size // (self.block_size * self.assoc) # number of sets in cache
		
		# address params
		self.nb_offset = int(log(self.block_size, 2)) # number of offset bits
		self.nb_index = int(log(self.n_set, 2)) # number of index bits
		self.nb_tag = int(log(self.mem_size, 2)) - self.nb_index - self.nb_offset # number of tag bits
		
		# create cache
		self.set = []
		for s in range(self.n_set):
			row = [Block(self.block_size) for _ in range(self.assoc)]
			self.set.append(row)
		
	def read(self, address):
		'''
		inputs:
			address (str): binary address of memory element, in str format
		returns:
			None, if cache miss
			data, if cache hit
		'''
		tag, index, offset = self.get_fields(address)
		index = int(index, 2)
		offset = int(offset,2)
		
		cacheset = self.set[index]
		out = None
		for block in cacheset:
			if block.valid == 1 and block.tag == tag:
				out = block.item[offset]
				if self.replace_pol == 'LRU':
					tmp = block
					cacheset.remove(block)
					cacheset.append(tmp)
					
				elif self.replace_pol == 'LFU':
					block.use += 1
					
				elif self.replace_pol == 'FIFO':
					pass
					
				elif self.replace_pol == 'RAND':
					pass
		
		return out
		
	def load(self, address, data):
		'''
		inputs:
			address (str): binary address of memory element
			item (list): memory block to be loaded onto cache; a list of bytes
		returns:
			None
		'''
		tag, index, offset = self.get_fields(address)
		index = int(index, 2)
		cacheset = self.set[index]
		
		newblk = Block(self.block_size)
		newblk.valid = 1
		newblk.tag = tag
		newblk.item = data
		
		if self.replace_pol == 'LRU':
			self.LRU_op(cacheset, newblk)
		elif self.replace_pol == 'LFU':
			self.LFU_op(cacheset, newblk)
		elif self.replace_pol == 'FIFO':
			self.FIFO_op(cacheset, newblk)
		elif self.replace_pol == 'RAND':
			self.RAND_op(cacheset, newblk)
		
	###########################################
	# util functions to assist main functions #
	###########################################
	def get_fields(self, address):
		tag = address[:self.nb_tag]
		index = address[self.nb_tag:self.nb_tag + self.nb_index]
		offset = address[self.nb_tag + self.nb_index: self.nb_tag + self.nb_index + self.nb_offset]
		return tag, index, offset
		
	def LRU_op(self, cacheset, newblk):
		use = list(map(lambda x: x.use, cacheset))
		lru = use.index(min(use))
		cacheset.pop(lru)
		cacheset.append(newblk)
		
	def LFU_op(self, cacheset, newblk):
		cacheset.pop(0)
		cacheset.append(newblk)
	
	def FIFO_op(self, cacheset, newblk):
		cacheset.pop(0)
		cacheset.append(newblk)
		
	def RAND_op(self, cacheset, newblk):
		idx = random.randint(len(cacheset))
		cacheset.pop(idx)
		cacheset.append(newblk)
		
#################
# for debugging #
#################
if __name__ == '__main__':
	cache_size = 2**5
	mem_size = 2 ** 10
	block_size = 2 ** 3
	assoc = 2
	replace_pol = 'LFU'
	
	c = Cache(cache_size, block_size, assoc, mem_size, replace_pol)
