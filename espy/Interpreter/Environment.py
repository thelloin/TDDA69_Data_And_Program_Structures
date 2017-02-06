from Utils import UnknownVariable

class Environment:
  """
  Environment class used to define variables.
  """
  
  def __init__(self, parent = None):
    """
    Initialise an environment. The parent is an other environment
    where value for variables can be looked up recursively.
    """
    self.parent = parent
    self.variables = {}

  def defineVariable(self, name, init = None):
    """
    Create a new variable with the name "name" and the initial value
    "init".
    """
    self.variables[name] = init

  def setVariable(self, name, value):
    """
    Set the value of a variable. If the variable is not defined in
    this environment, it should look in the parent environment.
    If it is not found in the root environment, it should raise the
    exception Utils.UnknownVariable.
    """
    if name in self.variables:
      self.variables[name] = value
    else:
      if self.parent == None:
        raise UnknownVariable("Variable not found in setVariable!")
      else:
        self.parent.setVariable(name, value)

  def value(self, name):
    """
    Get the value of a variable. If the variable is not defined in
    this environment, it should look in the parent environment.
    If it is not found in the root environment, it should raise the
    exception Utils.UnknownVariable.
    """
    if name in self.variables:
      return self.variables[name]
    else:
      if self.parent == None:
        raise UnknownVariable("Variable not found in value!")
      else:
        return self.parent.value(name)
