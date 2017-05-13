from VirtualMachine.Stack import Stack
from VirtualMachine.OpCode import OpCode

from Interpreter.Environment import Environment
from Interpreter.Object import Object
from Interpreter.ControlExceptions import ReturnException
from Interpreter.ESException import ESException
from Interpreter.Function import Function
from Interpreter.Property import Property

class Executor:
  '''
  Execute the code of a program or function
  '''
  def __init__(self, environment = Environment()):
    self.environment = environment
    self.stack  = Stack()
    self.current_index = 0
    self.return_values = Stack() # Stack to push/pop return values
    self.try_addresses = Stack() # Stack to push/pop addresses

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
    self.opmaps[OpCode.RET] = Executor.execute_ret
    self.opmaps[OpCode.SWITCH] = Executor.execute_switch
    # Exceptions
    self.opmaps[OpCode.TRY_PUSH] = Executor.execute_try_push
    self.opmaps[OpCode.THROW] = Executor.execute_throw
    self.opmaps[OpCode.TRY_POP] = Executor.execute_try_pop
    # Array and Objects creation
    self.opmaps[OpCode.MAKE_ARRAY] = Executor.execute_make_array
    self.opmaps[OpCode.MAKE_OBJECT] = Executor.execute_make_object
    self.opmaps[OpCode.MAKE_FUNC] = Executor.execute_make_func
    self.opmaps[OpCode.MAKE_GETTER] = Executor.execute_make_getter
    self.opmaps[OpCode.MAKE_SETTER] = Executor.execute_make_setter
    # Binary arithmetic operation
    self.opmaps[OpCode.ADD] = Executor.execute_add
    self.opmaps[OpCode.SUB] = Executor.execute_sub
    self.opmaps[OpCode.DIV] = Executor.execute_div
    self.opmaps[OpCode.MUL] = Executor.execute_mul
    self.opmaps[OpCode.MOD] = Executor.execute_mod
    self.opmaps[OpCode.LEFT_SHIFT] = Executor.execute_left_shift
    self.opmaps[OpCode.RIGHT_SHIFT] = Executor.execute_right_shift
    self.opmaps[OpCode.UNSIGNED_RIGHT_SHIFT] = Executor.execute_unsigned_right_shift
    # Binary bolean operation
    self.opmaps[OpCode.SUPPERIOR] = Executor.execute_superior
    self.opmaps[OpCode.SUPPERIOR_EQUAL] = Executor.execute_superior_equal
    self.opmaps[OpCode.INFERIOR] = Executor.execute_inferior
    self.opmaps[OpCode.INFERIOR_EQUAL] = Executor.execute_inferior_equal
    self.opmaps[OpCode.EQUAL] = Executor.execute_equal
    self.opmaps[OpCode.DIFFERENT] = Executor.execute_different
    self.opmaps[OpCode.AND] = Executor.execute_and
    self.opmaps[OpCode.OR] = Executor.execute_or
    # Unary operations
    self.opmaps[OpCode.NEG] = Executor.execute_neg
    self.opmaps[OpCode.TILDE] = Executor.execute_tilde
    self.opmaps[OpCode.NOT] = Executor.execute_not
   
    
  
  def execute(self, program):
    '''
    Execute the program given in argument
    '''
    self.current_index = 0

    while self.current_index < len(program.instructions):
      inst = program.instructions[self.current_index]
      f = self.opmaps[inst.opcode]
      
      try:
        f(self, *inst.params)
      except ESException as e:
        if self.try_addresses.size() == 0: # Check if we have an address to jump to
          raise e
        else:
          self.current_index = self.try_addresses.pop()
          self.stack.push(e.value)
      except ReturnException as e:
        if self.environment.parent == None: # Check if we're not executing a function
          raise e
        else:
          self.return_values.push(e.value)

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
    popped = self.stack.pop()
    self.environment.setVariable(varName, popped)
    self.execute_push(popped)
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
    obj = self.stack.pop()
    member = None
    if isinstance(obj, list):
      if isinstance(varName, int):
        member = obj[varName]
      else:
        member = len(obj)
    else:
      member = getattr(obj, varName)
    self.stack.push(member)

  def execute_store_member(self, varName):
    '''
    Execture the STORE_MEMBER instruction
    '''
    obj = self.stack.pop()
    val = self.stack.pop()
    if isinstance(obj, list):
      obj[varName] = val
    else:
      setattr(obj, varName, val)

    self.stack.push(val)
    
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
    if self.stack.pop():
      self.current_index = idx - 1 # -1 to current_index because we add 1 after function return

  def execute_unlessjmp(self, idx):
    '''
    Execute the UNLESSJMP instruction
    '''
    if not self.stack.pop():
      self.current_index = idx - 1 # -1 for the same reason as above

  def execute_call(self, argCount):
    '''
    Execute the CALL instruction
    '''
    func = self.stack.pop()
    args = []
    if argCount > 0:
      args = self.execute_pop(argCount)

    old_index = self.current_index
    func(None, *args)
    self.current_index = old_index

    if self.return_values.size() == 0:
      self.execute_push(None)
    else:
      self.execute_push(self.return_values.pop())

  def execute_new(self, argCount):
    '''
    Execute the NEW instruction
    '''
    func = self.stack.pop()
    args = []
    obj = Object()
    if argCount > 0:
      args = self.execute_pop(argCount)

    args = list(reversed(args))

    func(obj, *args)

    self.execute_push(obj)

  def execute_ret(self):
    '''
    Execute the RET instruction
    '''
    return_value = self.stack.pop()
    raise ReturnException(return_value)

  def execute_switch(self, default):
    '''
    Execute the SWITCH instruction
    '''
    s = self.execute_pop(self.stack.size())

    index_map = s[0] # Probably iterate stack here to find map
    if s[-1] in index_map:
      self.current_index = index_map[s[-1]] - 1
    else:
      self.current_index = default - 1

  def execute_try_push(self, idx):
    '''
    Execute the TRY_PUSH instruction
    '''
    self.try_addresses.push(idx)

  def execute_throw(self):
    '''
    Execute the THROW instruction
    '''
    raise ESException(self.stack.pop())

  def execute_try_pop(self):
    '''
    Execute the TRY_POP instruction
    '''
    self.try_addresses.pop()

  def execute_make_array(self, count):
    '''
    Execute the MAKE_ARRAY instruction
    '''
    arr = self.execute_pop(count)
    self.stack.push(arr[::-1])

  def execute_make_object(self, count):
    '''
    Execute the MAKE_OBJECT instruction
    '''
    arr = self.execute_pop(count*2)
    obj = Object()

    for i in range(0,len(arr),2):
      setattr(obj, arr[i], arr[i+1])
    self.stack.push(obj)

  def execute_make_func(self):
    '''
    Execute the MAKE_FUNC instruction
    '''
    code = self.stack.pop()
    args = self.stack.pop()
    def fun(env):
      old_env = self.environment
      self.environment = env
      self.execute(code)
      self.environment = old_env

    self.stack.push(Function(args, self.environment, fun))

  def execute_make_getter(self):
    '''
    Execute the MAKE_GETTER instruction
    '''
    name = self.stack.pop()
    func = self.stack.pop()
    obj = self.stack.pop()

    if hasattr(obj, name):
      prop = getattr(obj, name)
      prop.getter = func
    else:
      prop = Property(obj)
      prop.getter = func
      setattr(obj, name, prop)
    self.stack.push(obj)

  def execute_make_setter(self):
    '''
    Execute the MAKE_SETTER instruction
    '''
    name = self.stack.pop()
    func = self.stack.pop()
    obj = self.stack.pop()

    if hasattr(obj, name):
      prop = getattr(obj, name)
      prop.setter = func
    else:
      prop = Property(obj)
      prop.setter = func
      setattr(obj, name, prop)
    self.stack.push(obj)

  def bnry_helper(self, operator_func):
    '''
    Helper function for binary arithmetic operations
    '''
    op2 = self.stack.pop()
    op1 = self.stack.pop()
    self.stack.push(operator_func(op1, op2))
    
  def execute_add(self):
    '''
    Execute the ADD instruction
    '''
    self.bnry_helper(lambda x, y: x + y)

  def execute_sub(self):
    '''
    Execute the SUB instruction
    '''
    self.bnry_helper(lambda x, y: x - y)

  def execute_div(self):
    '''
    Execute the DIV instruction
    '''
    self.bnry_helper(lambda x, y: x / y)

  def execute_mul(self):
    '''
    Execute the MUL instruction
    '''
    self.bnry_helper(lambda x, y: x * y)

  def execute_mod(self):
    '''
    Execute the MOD instruction
    '''
    self.bnry_helper(lambda x, y: x % y)

  def execute_left_shift(self):
    '''
    Execute the LEFT_SHIFT instruction
    '''
    self.bnry_helper(lambda x, y: int(x) << int(y))

  def execute_right_shift(self):
    '''
    Execute the RIGHT_SHIFT instruction
    '''
    self.bnry_helper(lambda x, y: int(x) >> int(y))

  def execute_unsigned_right_shift(self):
    '''
    Execute the UNSIGNED_RIGHT_SHIFT instruction
    '''
    self.bnry_helper(lambda x, y: (int(x) % 0x100000000) >> int(y))

  def execute_superior(self):
    '''
    Execute the SUPPERIOR instruction
    '''
    self.bnry_helper(lambda x, y: x > y)

  def execute_superior_equal(self):
    '''
    Execute the SUPPERIOR_EQUAL instruction
    '''
    self.bnry_helper(lambda x, y: x >= y)

  def execute_inferior(self):
    '''
    Execute the INFERIOR instruction
    '''
    self.bnry_helper(lambda x, y: x < y)

  def execute_inferior_equal(self):
    '''
    Execute the INFERIOR_EQUAL instruction
    '''
    self.bnry_helper(lambda x, y: x <= y)

  def execute_equal(self):
    '''
    Execute the EQUAL instruction
    '''
    self.bnry_helper(lambda x, y: x == y)

  def execute_different(self):
    '''
    Execute the DIFFERENT instruction
    '''
    self.bnry_helper(lambda x, y: x != y)

  def execute_and(self):
    '''
    Execute the AND instruction
    '''
    self.bnry_helper(lambda x, y: x and y)

  def execute_or(self):
    '''
    Execute the OR instruction
    '''
    self.bnry_helper(lambda x, y: x or y)

  def unary_helper(self, operator_func):
    '''
    Helper function for unary expressions
    '''
    op = self.stack.pop()
    self.stack.push(operator_func(op))

  def execute_neg(self):
    '''
    Execute the NEG instruction
    '''
    self.unary_helper(lambda x: -x)

  def execute_tilde(self):
    '''
    Execute the TILDE instruction
    '''
    self.unary_helper(lambda x: ~int(x))

  def execute_not(self):
    '''
    Execute the NOT instruction
    '''
    self.unary_helper(lambda x: not x)
