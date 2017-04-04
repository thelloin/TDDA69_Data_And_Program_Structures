import Utils

class ReadOnlyException(Exception):
  '''
  Exception thrown when accessing a read only property
  '''
  def __init__(self):
    super().__init__("ReadOnlyException")

class WriteOnlyException(Exception):
  '''
  Exception thrown when accessing a write only property
  '''
  def __init__(self):
    super().__init__("WriteOnlyException")

class Property:
  '''
  Define an ECMAScript style property. This should contains three members:
  * getter a Function that is called when accessing the value
  * setter a Function that is called when setting the value
  * this the object to which this property belongs
  '''
  def __init__(self, this, getter = None, setter = None):
    self.this = this
    self.getter = getter
    self.setter = setter

  def get(self):
    '''
    Get the value or raise WriteOnlyException
    '''
    #print('This should be called @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    if self.getter == None:
      raise WriteOnlyException()
    else:
      return self.getter(self.this)
    
  def set(self, value):
    '''
    Set the value or raise ReadOnlyException
    '''
    #print('This should not be called @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    if self.setter == None:
      raise ReadOnlyException()
    else:
      self.setter(self.this, value)
 
  def merge(self, other):
    '''
    Merge two properties.
    '''
    if not other.this == None:
      self.this = other.this
    if not other.getter == None:
      self.getter = other.getter
    if not other.setter == None:
      self.setter = other.setter

  def clone(self):
    '''
    Clone a property (useful when creating new objects).
    '''
    new_prop = Property(self.this, self.getter, self.setter)

    return new_prop
