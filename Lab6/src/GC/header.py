def header_get_garbage_flag(heap, pointer):
  return (heap[pointer+3] & 0x80) == 0x80

def header_set_garbage_flag(heap, pointer, value):
  if value:
    heap[pointer + 3] = heap[pointer + 3] | 0x80
  else:
    heap[pointer + 3] = heap[pointer + 3] & 0x7f

def header_get_used_flag(heap, pointer):
  return (heap[pointer + 3] & 0x40) == 0x40
  
def header_set_used_flag(heap, pointer, value):
  if value:
    heap[pointer + 3] = heap[pointer + 3] | 0x40
  else:
    heap[pointer + 3] = heap[pointer + 3] & 0xbf

def header_is_pointers_array(heap, pointer):
  return (heap[pointer+3] & 0x20) == 0x20
  
def header_mark_as_pointers_array(heap, pointer):
  heap[pointer + 3] = heap[pointer + 3] | 0x20

def header_mark_as_bytes_array(heap, pointer):
  heap[pointer + 3] = heap[pointer + 3] & 0xdf
  
def header_get_size(heap, pointer):
  # TODO: Maybe use int.from_bytes here instead
  x1 = heap[pointer]
  x2 = heap[pointer + 1] << 8
  x3 = heap[pointer + 2] << 16
  x4 = (heap[pointer + 3] & 0b00011111) << 24
  return x1 + x2 + x3 + x4

def header_set_size(heap, pointer, size):
  arr = bytearray( (size).to_bytes(4, byteorder='little') )
  reserved_bits = heap[pointer + 3] & 0b11100000
  arr[3] = arr[3] | reserved_bits
  heap[pointer:pointer + 4] = arr
