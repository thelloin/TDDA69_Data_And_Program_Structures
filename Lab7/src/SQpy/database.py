from .ast import token, ast
from collections import namedtuple


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
      #print('time for deletion')
      where = self.execute(query.where)
      # Iterate entire table
      rows = self.rows[query.table]
      for row in rows:
        #print(row)
        if where(row._asdict()):
          #print('row:', row, 'DELETE')
          rows.remove(row)
        #else:
        #  print('row:', row, 'DO NOT DELETE')

    elif query.token == token.update:
      #print('time for a update')
      #print(query.set)
      where = self.execute(query.where)
      rows = self.rows[query.table]
      for i in range(len(rows)):
        #print(i, rows[i])
        if where(rows[i]._asdict()):
          #print("this should change")
          for item in query.set:
            #print(item[0], item[1])
            #print("poi", rows[i].name)
            #print("asdfa",rows[i][item[0]])
            #rows[i][item[0]] = item[1]
            #print(rows[i]._asdict()[item[0]])
            #print(i, rows[i])
            rows[i] = rows[i]._replace(**{item[0] : item[1]} )
            #rows[i] = rows[i]._replace(item)

    elif query.token == token.select:
      print("select statement")
      #print(query.columns)
      #print(type(query.columns))
      #print(query.from_table)
      res = []
      count = 0
      is_count = False
      avg = []
      is_avg = False
      # check for where clause
      where = None
      if hasattr(query, 'where'):
        where = self.execute(query.where)

      if isinstance(query.columns, ast) and query.columns.token == token.star:
        #print(self.rows[query.from_table])
        res = self.rows[query.from_table]
      else:
        col_names = self.get_column_names(query.columns)
        Row = namedtuple('Row', col_names)
        vals = []
        for row in self.rows[query.from_table]:
          for col in query.columns:
            if isinstance(col, str):
              if where == None or where(row._asdict()):
                vals.append(row._asdict()[col])
                #print("vals", vals)
            elif isinstance(col, tuple):
              #print('FOUND A TUPLE')
              #print("one col:", col)
              fun = self.execute(col[0])
              #print("fun:",fun)
              if isinstance(fun, tuple):
                print("fun is a tuple and its values is:", fun)
                if where == None or where(row._asdict()):
                  if fun[1] == 'count':
                    count += 1
                    is_count = True
                  elif fun[1] == 'avg':
                    # Handle average here
                    print("here we should handle average case", fun)
                    avg.append(row._asdict()[fun[0]])
                    is_avg = True
              else:
                print('where:', where)
                if where == None or where(row._asdict()):
                  vals.append(fun(row._asdict()))
          if vals:
            res.append(Row._make(vals))
          vals = []

      print('count', count)
      print('avg', avg)
      print(sum(avg)/len(avg))
      print(res)
      # Check for where clause
      #if hasattr(query, 'where'):
      #  where = self.execute(query.where)
      #  for row in res:
      #    if not where(row._asdict()):
      #      res.remove(row)
      return res

    elif query.token == token.fn_count:
      return (query.field, 'count')

    elif query.token == token.fn_avg:
      return (query.field, 'avg')

    elif query.token == token.op_and:
      def fun(row):
        op1 = self.execute(query.operands[0])
        #print('op1', op1)
        op2 = self.execute(query.operands[1])
        if op1(row) and op2(row):
          return True
        else:
          return False
      return fun
    elif query.token == token.op_equal:
      def fun(row):
        col_name = self.execute(query.operands[0])
        #print(col_name)
        #return row[query.operands[0].identifier[0]] == query.operands[1]
        return row[col_name] == query.operands[1]
      return fun
    elif query.token == token.op_inferior:
      def fun(row):
        col_name = self.execute(query.operands[0])
        return row[col_name] < query.operands[1]
      return fun
    elif query.token == token.op_superior:
      def fun(row):
        col_name = self.execute(query.operands[0])
        return row[col_name] > query.operands[1]
      return fun
    elif query.token == token.op_divide:
      def fun(row):
        col_name = self.execute(query.operands[0])
        return row[col_name] / query.operands[1]
      return fun
      return 1
    elif query.token == token.identifier:
      return query.identifier[0]

  def get_column_names(self, columns):
    res = []
    for col in columns:
      if isinstance(col, str):
        res.append(col)
      elif isinstance(col, tuple):
        res.append(col[1])
      else:
        print('MAJOR ERROR IN GET COLUMNS NAMES!!!!!')
    return res

  '''
  def op_eval(self, ast):

    print('TOKEN', ast.token)
    if ast.token == token.op_and:
      #def fun(row):
      print("len(ast.operands):", len(ast.operands))
      def fun(row):
        op1 = self.op_eval(ast.operands[0])
        #print('op1', op1)
        op2 = self.op_eval(ast.operands[1])
        if op1(row) and op2(row):
          return True
        else:
          return False
      return fun
    elif ast.token == token.op_equal:
      #print(dir(ast.op_equal.__dict__))
      #print(ast.operands)
      #print(ast.operands[0].identifier[0])
      def fun(row):
        #if row[ast.operands[0].identifier[0]] == ast.operands[1]:
        #  print('RETURNING TRUE FROM OP_EQUAL')
        #  return True
        #else:
        #  return False
        return row[ast.operands[0].identifier[0]] == ast.operands[1]
      return fun
    elif ast.token == token.op_inferior:
      def fun(row):
        if row[ast.operands[0].identifier[0]] < ast.operands[1]:
          print('RETURNING TRUE FORM OP_INFERIOR')
          return True
        else:
          return False
      return fun
    return 'hej'
    
    if hasattr(ast, 'where'):
      print('in where')
      return self.op_eval(table, getattr(ast, 'where'))
    elif hasattr(ast, 'op_eq'):
      print('in op_eq')
      return True
    elif hasattr(ast, 'op_and'):
      print('in op_and')
      print('op_and', ast.op_and)
      print('op_and.operands:', ast.operands)
      return self.op_eval(table, ast.operands[0]) and self.op_eval(table, ast.operands[1])
    else:
      return False
    '''
    
