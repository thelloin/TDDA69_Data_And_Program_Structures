import antlr4
import Utils

from ECMAScriptParser import ECMAScriptVisitor
from ECMAScriptParser import ECMAScriptLexer
from ECMAScriptParser import ECMAScriptParser
import Interpreter

from Interpreter.Console import Console
from Interpreter.Math import MathModule
from Interpreter.Environment import Environment
from Interpreter.Object import Object, ObjectModule
from Interpreter.Property import Property
from Interpreter.Function import Function

from pprint import pprint # for printing attributes of an object

class InterpreterVisitor(ECMAScriptVisitor):

    def __init__(self, environment = Environment(), input=None):
      self.environment = environment
      self.environment.defineVariable("console", Console())
      self.environment.defineVariable("Math", MathModule())
      self.environment.defineVariable("Object", ObjectModule())

    def visitTerminal(self, node):
      if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.BooleanLiteral: # 54
          if node.symbol.text == 'true':
              return True
          elif node.symbol.text == 'false':
              return False
      elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.DecimalLiteral: # 55
          # Not sure if were supposed to ever return int
          # Changes this because test 02_expression/01_addition expects float as result
          # Change back to make the implementation of binary_ops easier
          try:
              return int(node.symbol.text)
          except ValueError:
              return float(node.symbol.text)
      elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.HexIntegerLiteral: # 56
          return float(int(node.symbol.text, 0))
      elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.StringLiteral: # 101
          # Assume that a string atleast contains ""?
          return node.symbol.text[1:-1]
      else:
          return node.symbol.text
    
    # Visit a parse tree produced by ECMAScriptParser#PropertyExpressionAssignment.
    def visitPropertyExpressionAssignment(self, ctx):
        # Example of input: <name>:<expression>
        # NOTE: convert expr to float if int
        name = ctx.children[0].accept(self)
        expr = ctx.children[2].accept(self)
        if isinstance(expr, int):
            expr = float(expr)
        return (name, expr)



    # Visit a parse tree produced by ECMAScriptParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx):
        # Returns a lambda which performs the right operator
        node = ctx.children[0]
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Assign: # 11
            return lambda x, y: y
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.PlusAssign: # 43
            return lambda x, y: x + y
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.MinusAssign: # 44
            return lambda x, y: x - y
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.MultiplyAssign: # 40
            return lambda x, y: x * y
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.DivideAssign: # 41
            return lambda x, y: x / y
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#eos.
    def visitEos(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#program.
    def visitProgram(self, ctx):
        self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#argumentList.
    def visitArgumentList(self, ctx):
        args = []
        
        for c in ctx.children:
            if(not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl)): # Skip ","
                value = c.accept(self)
                if isinstance(value, Property):
                    args.append(value.get())
                else:
                    args.append(value)
        return args


    # Visit a parse tree produced by ECMAScriptParser#ArgumentsExpression.
    def visitArgumentsExpression(self, ctx):
        func = ctx.children[0].accept(self)
        args = ctx.children[1].accept(self)

        if(args == None): args = []


        res = None
        if isinstance(func, tuple):
            res = func[1](func[0], *args)
        elif str(type(func)) == "<class 'builtin_function_or_method'>":
            return func(*args)
        else:
            res = func(None, *args)

        if isinstance(res, int):
            res = float(res)
        #print('THE RES FROM ARGEXPR:', res)
        return res


    # Visit a parse tree produced by ECMAScriptParser#ThisExpression.
    def visitThisExpression(self, ctx):
        return self.environment.value("this")


    # Visit a parse tree produced by ECMAScriptParser#identifierName.
    def visitIdentifierName(self, ctx):
        return ctx.children[0].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#BinaryExpression.
    def visitBinaryExpression(self, ctx):
        node = ctx.children[1]

        # Handle AND and OR first to achieve normal-order evaluation
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.And: # 38
            return ctx.children[0].accept(self) and ctx.children[2].accept(self)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Or: # 39
            return ctx.children[0].accept(self) or ctx.children[2].accept(self)

        op1 = ctx.children[0].accept(self)
        op2 = ctx.children[2].accept(self)
        # Only convert to int if type is float
        if isinstance(op1, float) and op1 == int(op1):
            op1 = int(op1)
        if isinstance(op2, float) and op2 == int(op2):
            op2 = int(op2)
        
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Plus: # 17
            if isinstance(op1, int):
                return float(op1 + op2)
            else:
                return op1 + op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Minus: # 18
            return float(op1 - op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Multiply: # 21
            return float(op1 * op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Divide: # 22
            return float(op1 / op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Modulus: # 23
            return float(op1 % op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.LeftShiftArithmetic: # 25
            return float(op1 << op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.RightShiftArithmetic: # 24
            return float(op1 >> op2)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.RightShiftLogical: # 26
            return float( (op1 % 0x100000000)>>op2 )
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.LessThan: # 27
            return op1 < op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.MoreThan: # 28
            return op1 > op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.LessThanEquals: # 29
            return op1 <= op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.GreaterThanEquals: # 30
            return op1 >= op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Equals: # 31
            return op1 == op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.NotEquals: # 32
            return not op1 == op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.IdentityEquals: # 33
            return op1 is op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.IdentityNotEquals: # 34
            return op1 is not op2
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#futureReservedWord.
    def visitFutureReservedWord(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#initialiser.
    def visitInitialiser(self, ctx):
        return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#statementList.
    def visitStatementList(self, ctx):
        res = None
        for c in ctx.children:
            res = c.accept(self)
            if res == "BREAK-LOOP":
                return "BREAK-LOOP"
            elif res == "CONTINUE-LOOP":
                # Skip the remaining statements
                return "CONTINUE-LOOP"
            elif isinstance(res, tuple) and res[0] == "THROW":
                return res
        return res


    # Visit a parse tree produced by ECMAScriptParser#PropertyGetter.
    def visitPropertyGetter(self, ctx):
        name = ctx.children[1].accept(self)
        getter_body = ctx.children[-2].children[0]

        def func(env):
            previous_env = self.environment
            self.environment = env
            return_val = getter_body.accept(self)
            if isinstance(return_val, tuple):
                return_val = return_val[1]
            self.environment = previous_env
            return return_val

        return ('get', name, Function([], self.environment, func))
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#block.
    def visitBlock(self, ctx):
        res = ctx.children[1].accept(self)
        return res


    # Visit a parse tree produced by ECMAScriptParser#expressionStatement.
    def visitExpressionStatement(self, ctx):
      return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#keyword.
    def visitKeyword(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#elementList.
    def visitElementList(self, ctx):
        array = []
        for c in ctx.children:
            if(not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl)): # Skip ","
                res = c.accept(self)
                # NOTE: Conversion of int to float, should it be done here?
                if isinstance(res, int):
                    res = float(res)
                array.append(res)
        return array


    # Visit a parse tree produced by ECMAScriptParser#numericLiteral.
    def visitNumericLiteral(self, ctx):
        return ctx.children[0].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#ForInStatement.
    def visitForInStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#emptyStatement.
    def visitEmptyStatement(self, ctx):
        return


    # Visit a parse tree produced by ECMAScriptParser#labelledStatement.
    def visitLabelledStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#PropertySetter.
    def visitPropertySetter(self, ctx):
        name = ctx.children[1].accept(self)
        param = ctx.children[3].accept(self)
        setter_body = ctx.children[-2].children[0]

        def func(env):
            previous_env = self.environment
            self.environment = env
            return_value = setter_body.accept(self)
            self.environment = previous_env
            return return_value

        return ('set', name, Function([param], self.environment, func))
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#NewExpression.
    def visitNewExpression(self, ctx):
        obj = ctx.children[1].accept(self)
        params = ctx.children[2].accept(self)

        if params == None:
            params = []

        if isinstance(obj, ObjectModule):
            return obj
        elif isinstance(obj, Function):
            new_obj = ObjectModule()
            obj(obj, *params)
            obj2 = new_obj.create(None, obj)
            setattr(obj2, "prototype", obj)
            obj = obj2
            return obj
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#LiteralExpression.
    def visitLiteralExpression(self, ctx):
      return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ArrayLiteralExpression.
    def visitArrayLiteralExpression(self, ctx):
        return ctx.children[0].accept(self)
        


    # Visit a parse tree produced by ECMAScriptParser#MemberDotExpression.
    def visitMemberDotExpression(self, ctx):
        obj    = ctx.children[0].accept(self)
        member = ctx.children[2].accept(self)

        if isinstance(obj, tuple):
            obj = obj[0]

        returnval = None
        if hasattr(obj, member):
            returnval = getattr(obj, member)
        elif isinstance(obj, list) and member == 'length':
            returnval = float(len(obj))
        else:
            returnval = getattr(getattr(obj, "prototype"), member)

        if isinstance(returnval, Function):
            return (obj, returnval)
        return returnval


    # Visit a parse tree produced by ECMAScriptParser#withStatement.
    def visitWithStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#MemberIndexExpression.
    def visitMemberIndexExpression(self, ctx):
        obj = ctx.children[0].accept(self)
        idx = ctx.children[2].accept(self)

        if (isinstance(obj, Object)):
            return getattr(obj, str(idx))
        else:
            return obj[int(idx)]


    # Visit a parse tree produced by ECMAScriptParser#formalParameterList.
    def visitFormalParameterList(self, ctx):
        params = [param.accept(self) for param in ctx.children[0::2]]

        return params


    # Visit a parse tree produced by ECMAScriptParser#incrementOperator.
    def visitIncrementOperator(self, ctx):
        # Return a lambda based on what type of operator
        if ctx.children[0].symbol.type == ECMAScriptLexer.ECMAScriptLexer.PlusPlus:
            return lambda x: x + 1
        elif ctx.children[0].symbol.type == ECMAScriptLexer.ECMAScriptLexer.MinusMinus:
            return lambda x: x - 1
        else:
            raise Utils.UnimplementedVisitorException(ctx)
        
    ###########################################################################
    ############### Helper functions for AssignmentOperatorExpression #########
    ###########################################################################

    def objectExpression(self, ctx, var):
        member = ctx.children[2].accept(self)
        op = None
        val = None
        if isinstance(ctx.children[3], antlr4.tree.Tree.TerminalNodeImpl):
            op = ctx.children[4].accept(self)
            val = ctx.children[5].accept(self)
            #print(ctx.children[5].children)
        else:
            op = ctx.children[3].accept(self)
            val = ctx.children[4].accept(self)
            #print(ctx.children[4].children)
        if isinstance(val, int):
            val = float(val)
        if hasattr(var, member):
            attr = getattr(var, member)
            if isinstance(attr, Property):
                attr.set(val)
                return val
        setattr(var, member, val)
        return val

    def prototypeExpression(self, ctx):
        prototype = ctx.children[0].accept(self)

        if isinstance(prototype, tuple):
            prototype = prototype[0]
        member = ctx.children[2].accept(self)
        value = ctx.children[4].accept(self)

        # if value is an object, add each member
        if isinstance(value, Object):
            for attr in dir(value):
                if attr.startswith('__'): continue
                val = getattr(value, attr)

                if isinstance(val, tuple):
                    val = list(val)
                    val[0] = prototype
                    val = (val[0], val[1])
                setattr(prototype, attr, val)
        else:
            setattr(prototype, member, value)

    # Visit a parse tree produced by ECMAScriptParser#AssignmentOperatorExpression.
    def visitAssignmentOperatorExpression(self, ctx):

        if isinstance(ctx.children[0], ECMAScriptParser.ECMAScriptParser.IdentifierExpressionContext):
            var = ctx.children[0].accept(self)
            #print('Type of var:',type(var))
            if isinstance(var, Object) or isinstance(var, ObjectModule):
                return self.objectExpression(ctx, var)
            elif isinstance(var, Function):
                return self.prototypeExpression(ctx)
            else: # Handle the case when assigning to array element
                #print('IN ARRAY CASE')
                res = ctx.children[5].accept(self)
                if isinstance(res, int):
                    res = float(res)
                var[ctx.children[2].accept(self)] = res
                return
        elif isinstance(ctx.children[0], ECMAScriptParser.ECMAScriptParser.ThisExpressionContext):
            return self.objectExpression(ctx, ctx.children[0].accept(self))
        elif isinstance(ctx.children[0], ECMAScriptParser.ECMAScriptParser.MemberDotExpressionContext):
            return self.prototypeExpression(ctx)
        var_name = ctx.children[0].accept(self)
        func = ctx.children[1].accept(self)
        value = ctx.children[2].accept(self)

        res = func(self.environment.value(var_name), value)
        self.environment.setVariable(var_name, res)



    # Visit a parse tree produced by ECMAScriptParser#PostUnaryAssignmentExpression.
    def visitPostUnaryAssignmentExpression(self, ctx):
        var_name = ctx.children[0].accept(self)
        func = ctx.children[1].accept(self)
        old_value = self.environment.value(var_name)
        res = func(old_value)
        self.environment.setVariable(var_name, res)
        return float(old_value)


    # Visit a parse tree produced by ECMAScriptParser#TernaryExpression.
    def visitTernaryExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#tryStatement.
    def visitTryStatement(self, ctx):
        res = ctx.children[1].accept(self)

        if isinstance(res, tuple) and res[0] == "THROW": # There was a throw in the try-block
            var_name, block = ctx.children[2].accept(self)

            # Create new environment for the catch block
            self.environment = Environment(self.environment)
            self.environment.defineVariable(var_name.accept(self), res[1].accept(self))
            block.accept(self)
            # Set back the environment
            self.environment = self.environment.parent

        # Check for finally-clause and evaluate if so
        if len(ctx.children) == 4:
            ctx.children[3].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#debuggerStatement.
    def visitDebuggerStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#DoStatement.
    def visitDoStatement(self, ctx):
        ctx.children[1].accept(self)

        while ctx.children[4].accept(self):
            if ctx.children[1].accept(self) == "BREAK-LOOP":
                break
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ObjectLiteralExpression.
    def visitObjectLiteralExpression(self, ctx):
        obj = Object()
        
        # res is a list of tuples
        res = ctx.children[0].accept(self)

        for value in res:
            if len(value) == 3:
                prop = Property(obj)
                if value[0] == 'get':
                    prop.getter = value[-1]
                else:
                    prop.setter = value[-1]
                setattr(obj, str(value[1]), prop)
            else:
                setattr(obj, str(value[0]), value[1])
        return obj
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#arrayLiteral.
    def visitArrayLiteral(self, ctx):
        return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#elision.
    def visitElision(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#statements.
    def visitStatements(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#UnaryExpression.
    def visitUnaryExpression(self, ctx):
        node = ctx.children[0]
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Minus: # 18
            return - float(ctx.children[1].accept(self))
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Plus: # 17
            return float(ctx.children[1].accept(self))
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.BitNot: # 19
            return float(~ int(ctx.children[1].accept(self)))
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Not: # 20
            return not bool(ctx.children[1].accept(self))
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#WhileStatement.
    def visitWhileStatement(self, ctx):
        while ctx.children[2].accept(self):
            res = ctx.children[4].accept(self)
            if res == "BREAK-LOOP":
                break
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#returnStatement.
    def visitReturnStatement(self, ctx):
        return ("RETURN", ctx.children[1].accept(self))


    # Visit a parse tree produced by ECMAScriptParser#switchStatement.
    def visitSwitchStatement(self, ctx):
        val_to_switch = ctx.children[2].accept(self)

        case_found = False # Indicates a case without break has been found
        cases = ctx.children[4].accept(self)
        for case in cases:
            if val_to_switch == case[0] or case_found:
                if case[1].accept(self) == "BREAK-LOOP":
                    return
                case_found = True

        # Handle default case here
        if not case_found:
            for case in cases:
                if case[0] == "DEFAULT":
                    case[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#expressionSequence.
    def visitExpressionSequence(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#literal.
    def visitLiteral(self, ctx):
      res = ctx.children[0].accept(self)
      return res


    # Visit a parse tree produced by ECMAScriptParser#variableStatement.
    def visitVariableStatement(self, ctx):
        # TODO: should probably somehow check if the variable already has been declared /
        # perhaps return variable_name and value as a tuple and then check...
        args = ctx.children[1].accept(self)
        for name, value in args:
            self.environment.defineVariable(name, value)
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#FunctionExpression.
    def visitFunctionExpression(self, ctx):

        # Now uses the Function class

        # Check if it is an anonomous function
        if ctx.children[1].symbol.type == ECMAScriptLexer.ECMAScriptLexer.OpenParen: # 5
            # Check if there are any params
            if isinstance(ctx.children[2], ECMAScriptParser.ECMAScriptParser.FormalParameterListContext):
                params = ctx.children[2].accept(self)
                body = ctx.children[5].accept(self)
            else:
                params = []
                body = ctx.children[4].accept(self)
            new_func_to_return = Function(params, self.environment, body)
            setattr(new_func_to_return, "prototype", new_func_to_return)
            return new_func_to_return
        elif  ctx.children[1].symbol.type == ECMAScriptLexer.ECMAScriptLexer.Identifier: # 100 variable declaration
            func_name = ctx.children[1].accept(self)
            # Check if there are any params
            if isinstance(ctx.children[3], ECMAScriptParser.ECMAScriptParser.FormalParameterListContext):
                params = ctx.children[3].accept(self)
                body = ctx.children[6].accept(self)
            else:
                params = []
                body = ctx.children[5].accept(self)
            new_func = Function(params, self.environment, body)
            setattr(new_func, "prototype", new_func)
            self.environment.defineVariable(func_name, new_func)
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#defaultClause.
    def visitDefaultClause(self, ctx):
        return ("DEFAULT", ctx.children[2])


    # Visit a parse tree produced by ECMAScriptParser#statement.
    def visitStatement(self, ctx):
        res = ctx.children[0].accept(self)
        return res

    class MockExpression(object):
        def __init__(self):
            self.v = True
        def accept(self, ctx):
            return True

    # Visit a parse tree produced by ECMAScriptParser#ForStatement.
    def visitForStatement(self, ctx):
        # This is working for the tests but there are alot of variations
        # of the for-loop that will not break, most of which will happen
        # when there is a variable definition in a statement.
        expression1 = InterpreterVisitor.MockExpression()
        expression2 = InterpreterVisitor.MockExpression()
        expression3 = InterpreterVisitor.MockExpression()
        # Three different cases to consider: 0,1,2 och 3(all) statements missing
        if len(ctx.children) == 10:
            # Not a really good solution, not generic at all...
            args = ctx.children[3].accept(self)
            for name, value in args:
                self.environment.defineVariable(name,value)
            expression2 = ctx.children[5]
            expression3 = ctx.children[7]
        elif len(ctx.children) == 9: # All statements provided
            expression1 = ctx.children[2]
            expression2 = ctx.children[4]
            expression3 = ctx.children[6]
        elif len(ctx.children) == 8: # One statement missing
            # Find which one
            if isinstance(ctx.children[2], antlr4.tree.Tree.TerminalNodeImpl): # First missing
                expression2 = ctx.children[3]
                expression3 = ctx.children[5]
            elif isinstance(ctx.children[4], antlr4.tree.Tree.TerminalNodeImpl): # Sec missing
                expression1 = ctx.children[2]
                expression3 = ctx.children[5]
            else: # third(last) missing
                expression1 = ctx.children[2]
                expression2 = ctx.children[4]
        elif len(ctx.children) == 7: # Two statements missing
            # Find which one exists
            if isinstance(ctx.children[2], ECMAScriptParser.ECMAScriptParser.ExpressionSequenceContext): # First provided
                expression1 = ctx.children[2]
            elif isinstance(ctx.children[3], ECMAScriptParser.ECMAScriptParser.ExpressionSequenceContext): # Second provided
                expression2 = ctx.children[3]
            else: # Third provided
                expression3 = ctx.children[4]
        #else: # all missing, no need to do anythin
        #print("In FOR-LOOP")
        #raise Utils.UnimplementedVisitorException(ctx)
        # Evaluate the for-loop:
        expression1.accept(self)
        while expression2.accept(self):
            # Execute the body
            if ctx.children[-1].accept(self) == "BREAK-LOOP":
                break
            # Execute last statement in for-loop
            expression3.accept(self)


    # Visit a parse tree produced by ECMAScriptParser#caseBlock.
    def visitCaseBlock(self, ctx):
        res = []
        for c in ctx.children:
            if(not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl)): # Skip ","
                res.append(c.accept(self))
        return res
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ParenthesizedExpression.
    def visitParenthesizedExpression(self, ctx):
        return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#objectLiteral.
    def visitObjectLiteral(self, ctx):
        res = []

        for i in range(1, len(ctx.children), 2):
            res.append(ctx.children[i].accept(self))
        return res
        # raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#throwStatement.
    def visitThrowStatement(self, ctx):
        #raise Utils.UnimplementedVisitorException(ctx)
        return ("THROW", ctx.children[1])


    # Visit a parse tree produced by ECMAScriptParser#breakStatement.
    def visitBreakStatement(self, ctx):
        #raise Utils.UnimplementedVisitorException(ctx)
        return "BREAK-LOOP"


    # Visit a parse tree produced by ECMAScriptParser#ifStatement.
    def visitIfStatement(self, ctx):
        if not len(ctx.children) == 5 and not len(ctx.children) == 7:
            raise Utils.UnimplementedVisitorException(ctx)
        if ctx.children[2].accept(self):
            return ctx.children[4].accept(self)
        elif len(ctx.children) == 7:
            return ctx.children[6].accept(self)
        else:
            # The expression evaluated to false and no else clause:
            return None
            


    # Visit a parse tree produced by ECMAScriptParser#reservedWord.
    def visitReservedWord(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx):
        
        variable_name = ctx.children[0].accept(self)
        value = None
        if len(ctx.children) == 2:
            value = ctx.children[1].accept(self)
            #print('######', value)
            #pprint(vars(value))

        return (variable_name, value)
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#finallyProduction.
    def visitFinallyProduction(self, ctx):
        #raise Utils.UnimplementedVisitorException(ctx)
        return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#IdentifierExpression.
    def visitIdentifierExpression(self, ctx):
        res = self.environment.value(ctx.children[0].accept(self))
        if isinstance(res, int):
            return float(res)
        else:
            return res


    # Visit a parse tree produced by ECMAScriptParser#propertyName.
    def visitPropertyName(self, ctx):
        return ctx.children[0].accept(self)
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#catchProduction.
    def visitCatchProduction(self, ctx):
        return (ctx.children[2], ctx.children[4])


    # Visit a parse tree produced by ECMAScriptParser#continueStatement.
    def visitContinueStatement(self, ctx):
        return "CONTINUE-LOOP"


    # Visit a parse tree produced by ECMAScriptParser#caseClause.
    def visitCaseClause(self, ctx):
        return (ctx.children[1].accept(self), ctx.children[3])


    # Visit a parse tree produced by ECMAScriptParser#arguments.
    def visitArguments(self, ctx):
        if len(ctx.children) == 2:
            return None
        else:
            return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#variableDeclarationList.
    def visitVariableDeclarationList(self, ctx):
        args = []
        for c in ctx.children:
            if(not isinstance(c, antlr4.tree.Tree.TerminalNodeImpl)): # Skip ","
                args.append(c.accept(self))
        return args


    # Visit a parse tree produced by ECMAScriptParser#functionBody.
    def visitFunctionBody(self, ctx):
        # construct the function to be returned so this
        # body can be called
        def func(env):
            previous_environment = self.environment
            self.environment = Environment(env)

            for c in ctx.children:
                res = c.accept(self)
                if isinstance(res, tuple) and res[0] == "RETURN":
                    res = res[1]
                    break
            self.environment = previous_environment
            return res

        return func


    # Visit a parse tree produced by ECMAScriptParser#eof.
    def visitEof(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#UnaryAssignmentExpression.
    def visitUnaryAssignmentExpression(self, ctx):
        # It seems as if there is no way to determine if its pre- or postincrement
        # other than the position of IncrementOperatorContext in children
        # NOTE: It seem post increment is handled elsewhere...
        # Handle preincrement first
        if isinstance(ctx.children[1], antlr4.tree.Tree.TerminalNodeImpl):
            func = ctx.children[0].accept(self)
            var_name = ctx.children[1].accept(self)
            res = func(self.environment.value(var_name))
            self.environment.setVariable(var_name, res)
            return float(res)
        else:
            raise Utils.UnimplementedVisitorException(ctx)


