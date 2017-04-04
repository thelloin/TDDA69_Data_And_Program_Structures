from VirtualMachine.Stack import Stack
from VirtualMachine.OpCode import OpCode
#from VirtualMachine.Environment import Environment

from Interpreter.Environment import Environment
from Interpreter.Object import Object

class Executor:
  '''
  Execute the code of a program or function
  '''
  def __init__(self, environment = Environment()):
    self.environment = environment
    self.stack  = Stack()
    self.current_index = 0

    # The following code acts as a switch statements for OpCodes
    self.opmaps  = {}
    # Stack
    self.opmaps[OpCode.PUSH] = Executor.execute_push
    self.opmaps[OpCode.POP] = Executor.execute_pop
    self.opmaps[OpCode.DUP] = Executor.execute_dup
    self.opmaps[OpCode.SWAP] = Executor.execute_swap
    # Environment and objects manipulation
    self.opmaps[OpCode.LOAD] = Executor.execute_load
    self.opmaps[OpCode.STORE] = Executor.execute_store
    self.opmaps[OpCode.DCL] = Executor.execute_dcl
    self.opmaps[OpCode.LOAD_MEMBER] = Executor.execute_load_member
    self.opmaps[OpCode.STORE_MEMBER] = Executor.execute_store_member
    self.opmaps[OpCode.LOAD_INDEX] = Executor.execute_load_index
    self.opmaps[OpCode.STORE_INDEX] = Executor.execute_store_index
    # Control
    self.opmaps[OpCode.JMP] = Executor.execute_jmp
    self.opmaps[OpCode.IFJMP] = Executor.execute_ifjmp
    self.opmaps[OpCode.UNLESSJMP] = Executor.execute_unlessjmp
    self.opmaps[OpCode.CALL] = Executor.execute_call
    self.opmaps[OpCode.NEW] = Executor.execute_new
    # Exceptions
    # Array and Objects creation
    # Binary arithmetic operation
    # Binary bolean operation
    # Unary operations
   
    
  
  def execute(self, program):
    '''
    Execute the program given in argument
    '''

    while self.current_index < len(program.instructions):
      inst = program.instructions[self.current_index]
      f = self.opmaps[inst.opcode]
      
      f(self, *inst.params)
      self.current_index += 1

  def execute_push(self, value):
    '''
    Execute the PUSH instruction
    '''
    self.stack.push(value)
  
  def execute_pop(self, count):
    '''
    Execute the POP instruction
    '''
    popped = []
    for i in range(0, count):
      popped.append(self.stack.pop())
    return popped

  def execute_dup(self):
    '''
    Execute the DUP instruction
    '''
    self.stack.dup()

  def execute_swap(self):
    '''
    Execute the SWAP instruction
    '''
    self.stack.swap()

  def execute_load(self, varName):
    '''
    Execute the LOAD instruction
    '''
    value = self.environment.value(varName)
    self.execute_push(value)

  def execute_store(self, varName):
    '''
    Execute the STORE instruction
    '''
    popped = self.execute_pop(1)
    self.environment.setVariable(varName, popped[0])
    self.execute_push(popped[0])
    # Alternative: dup -> pop -> setvariable

  def execute_dcl(self, varName):
    '''
    Execute the DCL instruction
    '''
    self.environment.defineVariable(varName)

  def execute_load_member(self, varName):
    '''
    Execute the LOAD_MEMBER instruction
    '''
    obj = self.execute_pop(1)[0]
    member = None
    if isinstance(obj, list):
      if isinstance(varName, int):
        member = obj[varName]
      else:
        member = len(obj)
    else:
      member = getattr(obj, varName)
    self.execute_push(member)

  def execute_store_member(self, varName):
    '''
    Execture the STORE_MEMBER instruction
    '''
    obj = self.execute_pop(1)[0]
    val = self.execute_pop(1)[0]
    if isinstance(obj, list):
      obj[varName] = val
    else:
      setattr(obj, varName, val)

    # Push back the value
    self.execute_push(val)
    
  def execute_load_index(self):
    '''
    Execute the LOAD_INDEX instruction
    '''
    stack = self.execute_pop(2)

    # Handle two cases of object(2nd stack element), list and Object
    if isinstance(stack[1], list):
      if isinstance(stack[0], int):
        self.execute_push(stack[1][stack[0]])
      elif isinstance(stack[0], str) and stack[0] == 'length':
        self.execute_push(len(stack[1]))
    else:
      self.execute_push(getattr(stack[1], stack[0]))

  def execute_store_index(self):
    '''
    Execute the STORE_INDEX instruction
    '''
    stack = self.execute_pop(3)

    # Handle two cases of object(2nd stack element), list and Object
    if isinstance(stack[1], list):
      stack[1][stack[0]] = stack[2]
    else:
      setattr(stack[1], stack[0], stack[2])

    self.execute_push(stack[2])

  def execute_jmp(self, idx):
    '''
    Execute the JMP instruction
    '''
    self.current_index = idx - 1 # -1 to current_index because we add 1 after function return

  def execute_ifjmp(self, idx):
    '''
    Execute the IFJMP instruction
    '''
    if self.execute_pop(1)[0]:
      self.current_index = idx - 1 # -1 to current_index because we add 1 after function return

  def execute_unlessjmp(self, idx):
    '''
    Execute the UNLESSJMP instruction
    '''
    if not self.execute_pop(1)[0]:
      self.current_index = idx - 1 # -1 for the same reason as above

  def execute_call(self, argCount):
    '''
    Execute the CALL instruction
    '''
    
    func = self.execute_pop(1)[0]
    args = []
    if argCount > 0:
      args = self.execute_pop(argCount)
    
    self.execute_push(func.call(None, Object(), *args))

  def execute_new(self, argCount):
    '''
    Execute the NEW instruction
    '''
    pass
