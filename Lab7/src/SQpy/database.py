from .ast import token, ast
from collections import namedtuple
from itertools import product

class Select:
  """ select [columns] from [tables] where [condition] """
  def __init__(self, columns, tables, condition):
    self.columns = columns
    self.tables = tables
    self.condition = condition
    self.make_row = create_make_row(self.columns)
  def execute(self, env):
    """ Join, filter and map rows from tables to columns """
    from_rows = join(self.tables, env)
    filtered_rows = filter(self.filter_fn, from_rows)
    return map(self.make_row, filtered_rows)
  def filter_fn(self, row):
    if self.condition:
      return eval(self.condition, row)

def create_make_row(description):
  """ Returns a function from an input environment (dict) to an output row.
      description -- a comma-separated list of [expression] as [column name] """
  columns = description.split(',')
  expressions, names = [], []
  for column in columns:
    if 'as' in column:
      expression, name = column.split('as')
    else:
      expression, name = column, column
    expressions.append(expression)
    names.append(name.lstrip())
  row = namedtuple('Row', names)
  return lambda env: row(*[eval(e, env) for e in expressions])

def join(tables, env):
  """ Returns an iterator over dictionaries from names to values in a row """
  names = tables.split(',')
  joined_rows = product(*[env[name] for name in names])
  return map(lambda rows: make_env(rows, names), joined_rows)

def make_env(rows, names):
  """ Create an environment of names bound to values """
  env = dict(zip(names, rows))
  for row in rows:
    for name in row._fields:
      env[name] = getattr(row, name)
  return env

class database(object):
  def __init__(self):
    ''' Create a new database '''
    self.tables_dict = {}
    self.rows = {}

  def tables(self):
    return list(self.tables_dict.keys())

  def fields(self, name):
    return list(self.tables_dict[name]._fields)

  def dump_table(self, name):
    return self.rows[name]

  def execute(self, query):
    ''' Execute a query '''

    if isinstance(query, int):
      return str(query)
    if isinstance(query, str):
      return "'" + query + "'"

    if query.token == token.create_table:
      Table = namedtuple(query.name, query.columns)
      self.tables_dict[query.name] = Table
      self.rows[query.name] = []
    elif query.token == token.insert_into:
      if hasattr(query, 'columns'):
        # Fill in None values for not provided
        row_as_dict = dict(zip( query.columns, query.values  ))
        for key in self.tables_dict[query.table]._fields:
          if key not in row_as_dict:
            row_as_dict[key] = None
        self.rows[query.table].append(self.tables_dict[query.table](**row_as_dict))
      else:
        # Assume all columns are provided?
        self.rows[query.table].append(self.tables_dict[query.table]._make(query.values))
    elif query.token == token.delete_from:
      where = self.execute(query.where)
      # Iterate entire table
      rows_for_one = self.rows[query.table]
      for row in rows_for_one:
        if eval(where, row._asdict()):
          rows_for_one.remove(row)

    elif query.token == token.update:
      where = self.execute(query.where)
      rows_for_one = self.rows[query.table]
      for i in range(len(rows_for_one)):
        if eval(where, rows_for_one[i]._asdict()):
          for item in query.set:
            rows_for_one[i] = rows_for_one[i]._replace(**{item[0] : item[1]} )


    elif query.token == token.select:

      tables = query.from_table
      where_new = "True"
      if hasattr(query, 'where'):
        where_new = self.execute(query.where)
      if hasattr(query, 'joins'):
        where_new = ''
        for join in query.joins:
          tables += ',' + join.table
          if where_new == '':
            where_new = self.execute(join.on)
          else:
            where_new += ' and ' + self.execute(join.on)
      columns_str, count, avg = self.create_columns_str(query.columns, query.from_table)
      sel = Select(columns_str, tables, where_new)
      result = list(sel.execute(self.rows))

      # Handle count and average here
      if count != None or avg != None:
        r = []
        count_res = 0
        avg_res = 0
        if count != None:
          count_res = len(result)
          if avg != None:
            for row in result:
              avg_res += row._asdict()[avg]
            avg_res = avg_res / len(result)
        if count and avg:
          Row = namedtuple('Row', [count, avg])
          r.append(Row._make([count_res, avg_res]))
          return r
        elif count:
          Row = namedtuple('Row', [count])
          r.append(Row._make([count_res]))
          return r
        elif avg:
          Row = namedtuple('Row', [avg])
          r.append(Row._make([avg_res]))
          return r

      return result
         
    elif query.token == token.fn_count:
      return ('count', query.field)

    elif query.token == token.fn_avg:
      return ('avg', query.field)

    elif query.token == token.op_and:
      op1 = self.execute(query.operands[0])
      op2 = self.execute(query.operands[1])
      return op1 + ' and ' + op2

    elif query.token == token.op_equal:
      op1 = self.execute(query.operands[0])
      op2 = self.execute(query.operands[1])
      return op1 + ' == ' + op2
    elif query.token == token.op_inferior:
      op1 = self.execute(query.operands[0])
      op2 = self.execute(query.operands[1])
      return op1 + ' < ' + op2

    elif query.token == token.op_superior:
      op1 = self.execute(query.operands[0])
      op2 = self.execute(query.operands[1])
      return op1 + ' > ' + op2
    elif query.token == token.op_divide:
      dividend = self.execute(query.operands[0])
      divisor = self.execute(query.operands[1])
      return dividend + ' / ' + divisor
    elif query.token == token.identifier:
      if len(query.identifier) == 1:
        return query.identifier[0]
      else:
        return query.identifier[0] + '.' + query.identifier[1]

  def create_columns_str(self, columns, from_table):
    """ Returns a correctly formatted string of columns """
    count = None
    avg = None
    if isinstance(columns, ast) and columns.token == token.star:
        return (','.join(self.fields(from_table)), count, avg)
    else:
      res = []
      for column in columns:
        if isinstance(column, str):
          res.append(column)
        if isinstance(column, tuple):
          res_from_first = self.execute(column[0])
          res_from_sec = self.execute(column[1])[1:-1]
          if isinstance(res_from_first, tuple): # hacky thing for count and average
            if res_from_first[0] == 'count':
              count = res_from_sec
            else:
              avg = res_from_sec
            res.append(res_from_first[1] + ' as ' + res_from_sec)
          else:
            res.append(res_from_first + ' as ' + res_from_sec)

      return (','.join(res), count, avg)

