# Change bound_checking_decorator to handle function with multiple arguments

def bound_checking_decorator(*args):
  def make_decorator(func):
    def decorator(*x):
      for i in range(len(x)):
        if(x[i] < args[i*2] or x[i] > args[i*2+1]):
          raise Exception()
      return func(*x)
    return decorator
  return make_decorator
