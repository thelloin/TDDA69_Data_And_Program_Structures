import time

class FunctionInfo:
  def __init__(self, func_name, func_args, func_result, start, end):
    self.func_name = func_name
    self.func_args = func_args
    self.func_result = func_result
    self.start = start
    self.end = end

class Logger:
  '''
  Logger class. It should contains an array of objects containing the information about function calls
  '''
  
  def __init__(self):
    self.function_calls = []

  def log_function_call(self, func_name, func_args, func_result, start, end):
    '''
    Call this function after the function has finished been executed
    func_name: name of the function
    func_args: list of arguments of the function
    func_result: return value from the function call
    start: time when the function was started
    end:   time when the function has finish execution
    '''
    #print("calling log_function_call")
    self.function_calls.append(FunctionInfo(func_name, func_args, func_result, start, end))

def logtiming(logger):
  '''
  Decorator that will add an entry in logger after a function call
  '''
  def make_decorator(func):
    def decorator(*x):
      #measure start time
      start = time.time()
      #call function and save to res variable
      res = func(*x)
      #measure end time
      end = time.time()
      # store to function_calls
      logger.log_function_call(func.__name__,x, res, start, end)
      # return res
      #print(func.__name__)
      #print(x)
      return res
    return decorator
  return make_decorator
