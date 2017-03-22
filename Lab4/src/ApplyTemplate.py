#!/usr/bin/env python3

import inspect
import ast

def apply_template(bs, f_body, rs, f_return):
    def t(f):
        f_ast = ast.parse(inspect.getsource(f))
        f_ast.body[0].decorator_list = []

        body_ast = ast.parse(inspect.getsource(f_body)).body[0]
        body_node = body_ast.body[0]

        return_ast = ast.parse(inspect.getsource(f_return)).body[0]
        return_node = return_ast.body[0]

        class T(ast.NodeTransformer):
            def visit_Expr(self, node):
                if (node.value.id == bs):
                    return body_node
                elif (node.value.id == rs):
                    return return_node
                else:
                    return node

        exec(compile(T().visit(f_ast), __file__, mode='exec'))
        return locals()[f_ast.body[0].name]
    return t
