from .header import * 

def pointer_array_count(heap, pointer):
  #print("#################")
  #print(header_get_size(heap, pointer))
  return header_get_size(heap, pointer) // 4

def pointer_array_get(heap, pointer, index):
  actual_idx = pointer + ((index + 1) * 4)
  return int.from_bytes(heap[actual_idx : actual_idx + 4], byteorder='little')

def pointer_array_set(heap, pointer, index, value):
  actual_idx = pointer + ((index + 1) * 4)
  #print("###")
  #print(actual_idx, type(actual_idx))
  arr = bytearray( (value).to_bytes(4, byteorder='little') )
  #print(arr, type(arr))
  heap[actual_idx:actual_idx + 4] = arr
