from .header import * 
from .pointers_array import *

class mark_sweep(object):
  def __init__(self, heap):
    self.heap = heap
    self.root = 0

  # This function should collect the memory in the heap
  def collect(self):
    # Unmark all objects
    self.__unmark_objects()
    # Mark the root object
    header_set_used_flag(self.heap.data, self.root, True)
    # Mark all the objects directly reachable by root
    self.__rec_collect(self.root)

    # Deallocate all the unreachable objects, Note: Not sure if this is suppose to happen
    # here. If not, the use of garbage_flag can be removed below..
    self.__deallocate()

  def __unmark_objects(self):
    current = self.root
    while True:
      if header_get_used_flag(self.heap.data, current) == True:
        header_set_used_flag(self.heap.data, current, False)
        # Set garbage flags to remember which one to deallocate
        header_set_garbage_flag(self.heap.data, current, True)
      current += header_get_size(self.heap.data, current) + 4
      if current >= len(self.heap.data):
        break

  def __deallocate(self):
    current = self.root
    while True:
      if header_get_used_flag(self.heap.data, current) == False and header_get_garbage_flag(self.heap.data, current) == True:
        self.heap.disallocate(current)
      current += header_get_size(self.heap.data, current) + 4
      if current >= len(self.heap.data):
        break

  def __rec_collect(self, pointer):
    for i in range(pointer_array_count(self.heap.data, pointer)):
      reachable = pointer_array_get(self.heap.data, pointer, i)
      if header_get_used_flag(self.heap.data, reachable) == False:
        # Set used flag to True and call collect on it
        header_set_used_flag(self.heap.data, reachable, True)
        self.__rec_collect(reachable)

