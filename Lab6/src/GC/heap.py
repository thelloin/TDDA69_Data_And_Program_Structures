from .header import * 
from .pointers_array import *

class heap(object):
  # size: the size (in bytes) of the heap
  def __init__(self, size):
    self.data             = bytearray(size)
    self.NULL = size + 1
    self.free_space = size - 4
    self.allocated_space = 0
    header_set_used_flag(self.data, 0, False)
    header_set_size(self.data, 0, size - 4)
    self.free = 0
    pointer_array_set(self.data, self.free, 0, self.NULL)
  
  # helper function for allocate for finding the pointer to the best
  # fit and the previous pointer
  def get_best_fit_and_prev(self, size):
    # Find the best fit
    p = self.free
    prev = self.free
    min_size = len(self.data)
    p_smallest = self.free # variable for storing the best free slot
    prev_smallest = self.free # variable for storing a pointer to the previous free pointer

    while True:
      free_left = header_get_size(self.data, p) - size
      if free_left >=4 and free_left < min_size:
        min_size = free_left
        p_smallest = p
        prev_smallest = prev
      if free_left == 0:
        p_smallest = p
        prev_smallest = prev
        break
      if pointer_array_get(self.data, p, 0) == self.NULL:
        break
      prev = p
      p = pointer_array_get(self.data, p, 0)
    return (p_smallest, prev_smallest)

  # return the index to the begining of a block with size (in bytes)
  def allocate(self, size):
    if size < 4:
      size = 4
    self.free_space -= size+4
    self.allocated_space += size

    # Get the pointer to the best fist and the previous free pointer
    (pointer, prev) = self.get_best_fit_and_prev(size)

    free_slot_space = header_get_size(self.data, pointer)
    # Set up new allocated memory header
    header_set_used_flag(self.data, pointer, True)
    header_set_size(self.data, pointer, size)
    if free_slot_space == size:
      # Perfect match..
      next_free = pointer_array_get(self.data, pointer, 0)
      pointer_array_set(self.data, pointer, 0, 0)
      if prev < pointer:
        pointer_array_set(self.data, prev, 0, next_free)
      if self.free == pointer:
        self.free = next_free
    else:
      next_free_ptr = pointer_array_get(self.data, pointer, 0)

      # Set up next header
      ptr_to_next_header = pointer + size + 4
      header_set_used_flag(self.data, ptr_to_next_header, False)
      header_set_size(self.data, ptr_to_next_header, free_slot_space - size - 4)
      #ptr_to_next_free = pointer + size + 4
      # Set previous free ptr to point to new free memory location
      pointer_array_set(self.data, prev, 0, ptr_to_next_header)
      pointer_array_set(self.data, ptr_to_next_header, 0, next_free_ptr)

      if self.free == prev:
        self.free = ptr_to_next_header
      pointer_array_set(self.data, pointer, 0, 0)

    return pointer
  
  # unallocate the memory at the given index
  def disallocate(self, pointer):
    size_to_deallocate = header_get_size(self.data, pointer)
    pointer_to_next_memblock = pointer + 4 + size_to_deallocate
    # First free the memory
    header_set_used_flag(self.data, pointer, False)
    new_free_pointer = pointer
    # change free and allocated space
    self.free_space += size_to_deallocate
    self.allocated_space -= size_to_deallocate

    # Seach for pointer_to_next_memblock in free_pointer
    next_p = self.free
    prev = self.free
    while True:
      if next_p == pointer_to_next_memblock:
        break
      # Check if we've stepped over the memblock to deallocate
      if next_p > pointer_to_next_memblock:
        break
      prev = next_p
      next_p = pointer_array_get(self.data, next_p, 0)
      if next_p == self.NULL:
        # Searched through all free pointer, no one found
        break

    if next_p == pointer_to_next_memblock: # Next block is free, merge
      size_of_next_memblock = header_get_size(self.data, next_p)
      header_set_size(self.data, pointer, size_to_deallocate + 4 + size_of_next_memblock)
      pointer_array_set(self.data, new_free_pointer, 0, pointer_array_get(self.data, next_p, 0))
      # Remove header of old next header
      zeros = bytearray(size_of_next_memblock)
      self.data[next_p-4:next_p-4 + size_of_next_memblock] = zeros
      # 'Add' the removed header to free_space
      self.free_space += 4
    else:
      # Set the new free pointer to point to next free pointer
      pointer_array_set(self.data, new_free_pointer, 0, next_p)

    if prev < new_free_pointer:
      # There are free pointer above
      if pointer == prev + header_get_size(self.data, prev) + 4: # A free block is just above
        pointer_array_set(self.data, prev, 0, pointer_array_get(self.data, new_free_pointer, 0))

        prev_header = prev
        prev_size = header_get_size(self.data, prev_header)
        # size of deallocated block can have changed in case of merge
        cur_block_size = header_get_size(self.data, pointer)
        header_set_size(self.data, prev_header, prev_size + cur_block_size + 4)

        zeros = bytearray(header_get_size(self.data, pointer))
        self.data[pointer:pointer + len(zeros)] = zeros
        self.free_space +=4
      else:
        # Set prev free pointer to point to new free pointer
        pointer_array_set(self.data, prev, 0, new_free_pointer)
    else:
      # No free memblocks above
      self.free = new_free_pointer


  # print the heap
  def print_heap(self):
    print("#####################")
    print("##### HEAP ##########")
    print("self.free:", self.free)
    print("self.free->next:", pointer_array_get(self.data, self.free, 0))
    p = 0
    while p < self.NULL-1:
      print(p, "is in use:", header_get_used_flag(self.data, p))
      print("the size is:", header_get_size(self.data, p))
      p = p + header_get_size(self.data, p) + 4
    print("#####################")
    print("")
  
  # Return the current total (allocatable) free space
  def total_free_space(self):
    return self.free_space
  
  # Return the current total allocated memory
  def total_allocated_space(self):
    return self.allocated_space

  def allocate_array(self, count):
    pointer = self.allocate(count * 4)
    header_mark_as_pointers_array(self.data, pointer)
    return pointer

  def allocate_bytes(self, count):
    pointer = self.allocate(count)
    header_mark_as_bytes_array(self.data, pointer)
    return pointer
