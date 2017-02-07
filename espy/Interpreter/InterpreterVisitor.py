import antlr4
import Utils

from ECMAScriptParser import ECMAScriptVisitor
from ECMAScriptParser import ECMAScriptLexer

from Interpreter.Console import Console
from Interpreter.Math import MathModule
from Interpreter.Environment import Environment
from Interpreter.Object import Object, ObjectModule

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
          # Change back to make the ease of implementing binary_ops easier
          try:
              return int(node.symbol.text)
          except ValueError:
              return float(node.symbol.text)
          #return float(node.symbol.text)
      elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.HexIntegerLiteral: # 56
          return float(int(node.symbol.text, 0))
      elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.StringLiteral: # 101
          # Assume that a string atleast contains ""?
          return node.symbol.text[1:-1]
      else:
          return node.symbol.text
    
    # Visit a parse tree produced by ECMAScriptParser#PropertyExpressionAssignment.
    def visitPropertyExpressionAssignment(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx):
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
          args.append(c.accept(self))
      return args


    # Visit a parse tree produced by ECMAScriptParser#ArgumentsExpression.
    def visitArgumentsExpression(self, ctx):
        func = ctx.children[0].accept(self)
        args = ctx.children[1].accept(self)
        if(args == None): args = []
        return func(None, *args)


    # Visit a parse tree produced by ECMAScriptParser#ThisExpression.
    def visitThisExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#identifierName.
    def visitIdentifierName(self, ctx):
        return ctx.children[0].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#BinaryExpression.
    def visitBinaryExpression(self, ctx):
        #print("# of children: ", len(ctx.children))
        #print("# of children in b_context: ", len(ctx.children[0].children))
        #print("types of children in b_context: ", ctx.children[0].children)
        #print("###############################")
        #print("Type of operator: ", ctx.children[1].symbol.type)
        node = ctx.children[1]
        op1 = ctx.children[0].accept(self)
        op2 = ctx.children[2].accept(self)
        # Only convert to int if type is float
        if isinstance(op1, float) and op1 == int(op1):
            op1 = int(op1)
        if isinstance(op2, float) and op2 == int(op2):
            op2 = int(op2)
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Plus: # 17
            return float(op1 + op2)
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
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.And: # 38
            return op1 and op2
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.Or: # 39
            return op1 or op2
        else:
            raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#futureReservedWord.
    def visitFutureReservedWord(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#initialiser.
    def visitInitialiser(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#statementList.
    def visitStatementList(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#PropertyGetter.
    def visitPropertyGetter(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#block.
    def visitBlock(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#expressionStatement.
    def visitExpressionStatement(self, ctx):
      self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#keyword.
    def visitKeyword(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#elementList.
    def visitElementList(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#numericLiteral.
    def visitNumericLiteral(self, ctx):
        """print("In visitNumericalLiteral #########################")
        print("Type of context: ", type(ctx))
        print("Length of children: ", len(ctx.children))
        print("Type of children[0]: ", type(ctx.children[0]))
        node = ctx.children[0]
        if node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.DecimalLiteral:
            try:
                return int(node.symbol.text)
            except ValueError:
                return float(node.symbol.text)
        elif node.symbol.type == ECMAScriptLexer.ECMAScriptLexer.HexIntegerLiteral:
            return float(int(node.symbol.text, 0))
        """
        return ctx.children[0].accept(self)
        #raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ForInStatement.
    def visitForInStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#emptyStatement.
    def visitEmptyStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#labelledStatement.
    def visitLabelledStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#PropertySetter.
    def visitPropertySetter(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#NewExpression.
    def visitNewExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#LiteralExpression.
    def visitLiteralExpression(self, ctx):
      return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ArrayLiteralExpression.
    def visitArrayLiteralExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#MemberDotExpression.
    def visitMemberDotExpression(self, ctx):
      obj    = ctx.children[0].accept(self)
      member = ctx.children[2].accept(self)
      return getattr(obj, member)


    # Visit a parse tree produced by ECMAScriptParser#withStatement.
    def visitWithStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#MemberIndexExpression.
    def visitMemberIndexExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#formalParameterList.
    def visitFormalParameterList(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#incrementOperator.
    def visitIncrementOperator(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#AssignmentOperatorExpression.
    def visitAssignmentOperatorExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#PostUnaryAssignmentExpression.
    def visitPostUnaryAssignmentExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#TernaryExpression.
    def visitTernaryExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#tryStatement.
    def visitTryStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#debuggerStatement.
    def visitDebuggerStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#DoStatement.
    def visitDoStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ObjectLiteralExpression.
    def visitObjectLiteralExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#arrayLiteral.
    def visitArrayLiteral(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#elision.
    def visitElision(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#statements.
    def visitStatements(self, ctx):
        self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#UnaryExpression.
    def visitUnaryExpression(self, ctx):
        #print("################### ", ctx.children[0].symbol.text)
        #print("################### ", ctx.children[0].symbol.type)
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
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#returnStatement.
    def visitReturnStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#switchStatement.
    def visitSwitchStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#expressionSequence.
    def visitExpressionSequence(self, ctx):
      return self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#literal.
    def visitLiteral(self, ctx):
      #print("Type of ctx: ", type(ctx))
      #print("Length of children: ", len(ctx.children))
      #print("Type of children[0]: ", type(ctx.children[0]))
      res = ctx.children[0].accept(self)
      #print("Type of result: ", type(res))
      return res


    # Visit a parse tree produced by ECMAScriptParser#variableStatement.
    def visitVariableStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#FunctionExpression.
    def visitFunctionExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#defaultClause.
    def visitDefaultClause(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#statement.
    def visitStatement(self, ctx):
      self.visitChildren(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ForStatement.
    def visitForStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#caseBlock.
    def visitCaseBlock(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ParenthesizedExpression.
    def visitParenthesizedExpression(self, ctx):
        #print("##################################")
        #print("First child: ", ctx.children[0].symbol.text)
        #print("Second child: ", ctx.children[2].symbol.text)
        #raise Utils.UnimplementedVisitorException(ctx)
        return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#objectLiteral.
    def visitObjectLiteral(self, ctx):
        print("visitObjectLiteral - #################################")
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#throwStatement.
    def visitThrowStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#breakStatement.
    def visitBreakStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#ifStatement.
    def visitIfStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#reservedWord.
    def visitReservedWord(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#finallyProduction.
    def visitFinallyProduction(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#IdentifierExpression.
    def visitIdentifierExpression(self, ctx):
      return self.environment.value(ctx.children[0].accept(self))


    # Visit a parse tree produced by ECMAScriptParser#propertyName.
    def visitPropertyName(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#catchProduction.
    def visitCatchProduction(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#continueStatement.
    def visitContinueStatement(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#caseClause.
    def visitCaseClause(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#arguments.
    def visitArguments(self, ctx):
      return ctx.children[1].accept(self)


    # Visit a parse tree produced by ECMAScriptParser#variableDeclarationList.
    def visitVariableDeclarationList(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#functionBody.
    def visitFunctionBody(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#eof.
    def visitEof(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


    # Visit a parse tree produced by ECMAScriptParser#UnaryAssignmentExpression.
    def visitUnaryAssignmentExpression(self, ctx):
        raise Utils.UnimplementedVisitorException(ctx)


