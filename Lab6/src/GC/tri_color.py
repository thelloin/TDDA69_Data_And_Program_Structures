from .header import * 
from .pointers_array import *

class tri_color(object):
  def __init__(self, heap):
    self.heap = heap
    self.root = 0

  # This function should collect the memory in the heap
  def collect(self):
    # Divide objects into initial sets
    black_set = set()
    grey_set = {self.root}
    white_set = set()
    current = header_get_size(self.heap.data, self.root) + 4
    while True:
      if header_get_used_flag(self.heap.data, current) == True:
        white_set.add(current)
      current += header_get_size(self.heap.data, current) + 4
      if current >= len(self.heap.data):
        break

    # Continue until no more pointers in grey_set
    while len(grey_set) > 0:
      current = grey_set.pop()
      black_set.add(current)
      for i in range(pointer_array_count(self.heap.data, current)):
        reachable = pointer_array_get(self.heap.data, current, i)
        if reachable in white_set:
          white_set.remove(reachable)
          grey_set.add(reachable)

    # Set used flag to false for objects in the white_set
    for ptr in white_set:
      header_set_used_flag(self.heap.data, ptr, False)
