# coding=utf-8
import pyauparser


class EFSMParser(object):
    def __init__(self, grammar_file):
        self.g = pyauparser.Grammar.load_file(grammar_file)
        self.input_params = {}

    def get_grammar(self):
        return self.g

    def get_production_index(self, s):
        return self.g.get_production(s).index

    def parse_boolean(self, str):
        d = {'true': True, '1': True, 'false': False, '0': False}
        return d[str]

    # 解析文本结点，得到初步的context_vars input_params
    def analysis(self, node, context_var, input_param):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <input_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<input_event> ::= ? <Port> . <function_expr>"):
                lambda c: (e(c[1]), e(c[3])),
            self.get_production_index("<Port> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Port> ::= T"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<function_expr> ::= <Func ID> ( <Params> )"):
                lambda c: e(c[2]),
            self.get_production_index("<function_expr> ::= <Func ID> ( )"):
                lambda c: (),
            self.get_production_index("<Func ID> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Params> ::= <Param> , <Params>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Params> ::= <Param>"):
                lambda c: e(c[0]),
            self.get_production_index("<Param> ::= Id"):
                lambda c: self.input_params.__setitem__(c[0].token.lexeme, {
                    'value': None,
                    'type': None
                })
                if c[0].token.lexeme not in context_var else None,
            # output function
            self.get_production_index("<Statement> ::= <output_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<output_event> ::= ! <Port> . <function_expr>"):
                lambda c: (e(c[3])),

            # predicate function
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: _update_input(e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: '{0} + {1}'.format(e(c[0]), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: '{0} - {1}'.format(e(c[0]), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: '{0} * {1}'.format(e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: '{0} / {1}'.format(e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: '{0} % {1}'.format(e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),
            self.get_production_index("<Value> ::= StringLiteral"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),

            # update function
            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: (e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := <Expression>"):
                lambda c:
                (context_var.__setitem__(e(c[0]), {
                    'value': e(c[2]),
                    'type': type(e(c[2]))
                })
                 if e(c[0]) not in input_param and e(c[0]) not in self.input_params and e(c[0]) not in context_var else None),
            self.get_production_index("<AssignmentStatement> ::= <VAR> += <Expression>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> -= <Expression>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := min ( <Expression> , <Expression> )"):
                lambda c:
                e(c[0]),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := max ( <Expression> , <Expression> )"):
                lambda c:
                e(c[0]),
            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme

        }

        def _update_input(left, right):
            if left not in input_param and left in self.input_params and self.input_params[left]['type'] is None:
                if right in context_var:
                    self.input_params.__setitem__(left, {
                        'value': context_var[right]['value'],
                        'type': context_var[right]['type']
                    })
                else:
                    self.input_params.__setitem__(left, {
                         'value': right,
                         'type': type(right)
                    })
            elif left in context_var and right in input_param and input_param[right]['type'] is None:
                self.input_params.__setitem__(right, {
                    'value': context_var[left]['value'],
                    'type': context_var[left]['type']
                })



        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 更新 上下文变量表
    def evaluate(self, node, context_var, input_param):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <input_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<input_event> ::= ? <Port> . <function_expr>"):
                lambda c: None,
            self.get_production_index("<Port> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Port> ::= T"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<function_expr> ::= <Func ID> ( <Params> )"):
                lambda c: e(c[2]),
            self.get_production_index("<function_expr> ::= <Func ID> ( )"):
                lambda c: (),
            self.get_production_index("<Func ID> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Params> ::= <Param> , <Params>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Params> ::= <Param>"):
                lambda c: e(c[0]),
            self.get_production_index("<Param> ::= Id"):
                lambda c: None,

            # output function
            self.get_production_index("<Statement> ::= <output_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<output_event> ::= ! <Port> . <function_expr>"):
                lambda c: (e(c[3])),

            # predicate function
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]) and e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]) == e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]) != e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]) < e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]) > e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]) <= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]) >= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]) + e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]) - e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]) * e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]) / e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]) % e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c:
                context_var[e(c[0])]
                if e(c[0]) not in input_param else input_param[e(c[0])],
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),  # strtobool(c[0].token.lexeme),
            self.get_production_index("<Value> ::= StringLiteral"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),

            # update function
            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: (e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := <Expression>"):
                lambda c:
                context_var.__setitem__(e(c[0]), e(c[2]))
                if e(c[0]) not in input_param else input_param.__setitem__(e(c[0]), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> += <Expression>"):
                lambda c:
                context_var.__setitem__(e(c[0]), context_var[e(c[0])] + e(c[2]))
                if e(c[0]) not in input_param else input_param.__setitem__(e(c[0]), input_param[e(c[0])] + e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> -= <Expression>"):
                lambda c:
                context_var.__setitem__(e(c[0]), context_var[e(c[0])] - e(c[2]))
                if e(c[0]) not in input_param else input_param.__setitem__(e(c[0]), input_param[e(c[0])] - e(c[2])),

            self.get_production_index("<AssignmentStatement> ::= <VAR> := min ( <Expression> , <Expression> )"):
                lambda c:
                context_var.__setitem__(e(c[0]), min(e(c[4]), e(c[6])))
                if e(c[0]) not in input_param else input_param.__setitem__(e(c[0]), e(c[2])),

            self.get_production_index("<AssignmentStatement> ::= <VAR> := max ( <Expression> , <Expression> )"):
                lambda c:
                context_var.__setitem__(e(c[0]), max(e(c[4]), e(c[6])))
                if e(c[0]) not in input_param else input_param.__setitem__(e(c[0]), e(c[2])),

            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]) or e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme,

        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 判断 变迁是否能通过
    def judge(self, node, context_var, input_param):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),

            # predicate function
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: e(c[0]),

            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),

            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]) or e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]) and e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]) == e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]) != e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]) < e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]) > e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]) <= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]) >= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]) + e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]) - e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]) * e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]) / e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]) % e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c:
                context_var[e(c[0])]
                if e(c[0]) not in input_param else input_param[e(c[0])],
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme
        }
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),

            # predicate function
            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<AssignmentStatement> ::= <VAR> = <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), "="),
            self.get_production_index("<AssignmentStatement> ::= <VAR> <> <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), "<>"),
            self.get_production_index("<AssignmentStatement> ::= <VAR> < <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), "<"),
            self.get_production_index("<AssignmentStatement> ::= <VAR> <= <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), "<="),
            self.get_production_index("<AssignmentStatement> ::= <VAR> > <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), ">"),
            self.get_production_index("<AssignmentStatement> ::= <VAR> >= <Expression>"):
                lambda c: j(e(c[0]), e(c[2]), ">="),

            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),

            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]) or e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]) and e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]) == e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]) != e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]) < e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]) > e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]) <= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]) >= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]) + e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]) - e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]) * e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]) / e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]) % e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c:
                context_var[e(c[0])]
                if e(c[0]) not in input_param else input_param[e(c[0])],
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),



        }

        def j(a, b_val, op):
            a_val = context_var[a] if a not in input_param else input_param[a]
            b_val = operation(op, a_val, b_val)
            context_var.__setitem__(a, b_val) if a not in input_param else input_param.__setitem__(a, b_val)
            return True

        def operation(op, a, b):
            if op == "=":
                if not a == b:
                    return b
            elif op == "<>":
                if not a != b:
                    return a
                return b
            elif op == "<":
                if not a < b:
                    return b-1
            elif op == "<=":
                if not a <= b:
                    return b
            elif op == ">":
                if not a > b:
                    return b+1
            elif op == ">=":
                if not a >= b:
                    return b
            return a

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 判断 变迁是否能通过
    def judge_ipsg(self, node, context_var, input_param):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),

            # predicate function
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: e(c[0]),

            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),

            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]) or e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]) and e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]) == e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]) != e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]) < e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]) > e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]) <= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]) >= e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]) + e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]) - e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]) * e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]) / e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]) % e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c:
                context_var[e(c[0])]
                if e(c[0]) not in input_param else input_param[e(c[0])],
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme
        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 分析 变迁中的 左中右详细内容
    def analysis_guard_content(self, node, express_content, compare_op, logic_op):
        h = {
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),

            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: e(c[0]),

            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),

            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), logic_op.append(c[1].token.lexeme), e(c[2])),

            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), logic_op.append(c[1].token.lexeme), e(c[2])),

            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),

            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),

            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]), compare_op.append(c[1].token.lexeme), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]), express_content.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c:
                (e(c[0])),
            self.get_production_index("<Value> ::= Integer"):
                lambda c: express_content.append(int(c[0].token.lexeme)),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: express_content.append(self.parse_boolean(c[0].token.lexeme)),
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: express_content.append(c[0].token.lexeme)
        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 分析 define var
    def analysis_define(self, node, define_var):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <input_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<input_event> ::= ? <Port> . <function_expr>"):
                lambda c: (e(c[3])),
            self.get_production_index("<function_expr> ::= <Func ID> ( <Params> )"):
                lambda c: e(c[2]),
            self.get_production_index("<function_expr> ::= <Func ID> ( )"):
                lambda c: (),
            self.get_production_index("<Params> ::= <Param> , <Params>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Params> ::= <Param>"):
                lambda c: e(c[0]),
            self.get_production_index("<Param> ::= Id"):
                lambda c: (define_var.add(c[0].token.lexeme)),

            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: (e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := <Expression>"):
                lambda c:
                define_var.add(e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> += <Expression>"):
                lambda c:
                define_var.add(e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> -= <Expression>"):
                lambda c:
                define_var.add(e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := min ( <Expression> , <Expression> )"):
                lambda c:
                define_var.add(e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := max ( <Expression> , <Expression> )"):
                lambda c:
                define_var.add(e(c[0])),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme

        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    # 用于 分析 use var
    def analysis_use(self, node, use_var):
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: e(c[0]),
            self.get_production_index("<Port> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Port> ::= T"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<function_expr> ::= <Func ID> ( <Params> )"):
                lambda c: e(c[2]),
            self.get_production_index("<function_expr> ::= <Func ID> ( )"):
                lambda c: (),
            self.get_production_index("<Params> ::= <Param> , <Params>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Params> ::= <Param>"):
                lambda c: e(c[0]),
            self.get_production_index("<Param> ::= Id"):
                lambda c: use_var.add(c[0].token.lexeme),
            # output function
            self.get_production_index("<Statement> ::= <output_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<output_event> ::= ! <Port> . <function_expr>"):
                lambda c: (e(c[3])),

            # predicate function
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c: use_var.add(e(c[0])),
            self.get_production_index("<Value> ::= Integer"):
                lambda c: int(c[0].token.lexeme),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: self.parse_boolean(c[0].token.lexeme),
            self.get_production_index("<Value> ::= StringLiteral"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: e(c[1]),

            # update function
            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: (e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := <Expression>"):
                lambda c: (e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> += <Expression>"):
                lambda c: (e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> -= <Expression>"):
                lambda c: (e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := min ( <Expression> , <Expression> )"):
                lambda c:
                (e(c[4]), e(c[6])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := max ( <Expression> , <Expression> )"):
                lambda c:
                (e(c[4]), e(c[6])),
            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: c[0].token.lexeme

        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    def  analysis_element(self, node, element):
        element = element
        h = {
            # input function
            self.get_production_index("<Statements> ::= <Statement> ; <Statements>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Statements> ::= <Statement> ;"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme)),
            self.get_production_index("<Statement> ::= <input_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<input_event> ::= ? <Port> . <function_expr>"):
                lambda c: (e(c[1]), e(c[3])),
            self.get_production_index("<Port> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Port> ::= T"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<function_expr> ::= <Func ID> ( <Params> )"):
                lambda c: e(c[2]),
            self.get_production_index("<function_expr> ::= <Func ID> ( )"):
                lambda c: (),
            self.get_production_index("<Func ID> ::= Id"):
                lambda c: c[0].token.lexeme,
            self.get_production_index("<Params> ::= <Param> , <Params>"):
                lambda c: (e(c[0]), e(c[2])),
            self.get_production_index("<Params> ::= <Param>"):
                lambda c: e(c[0]),
            self.get_production_index("<Param> ::= Id"):
                lambda c: (),
            # output function
            self.get_production_index("<Statement> ::= <output_event>"):
                lambda c: e(c[0]),
            self.get_production_index("<output_event> ::= ! <Port> . <function_expr>"):
                lambda c: (e(c[3])),

            # predicate function
            self.get_production_index("<And Exp> ::= <Equality Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<And Exp> ::= <And Exp> && <Equality Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> = <Compare Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Equality Exp> <> <Compare Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Equality Exp> ::= <Compare Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> < <Add Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> > <Add Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> <= <Add Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Compare Exp> >= <Add Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Compare Exp> ::= <Add Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Add Exp> ::= <Add Exp> + <Mult Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Add Exp> - <Mult Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Add Exp> ::= <Mult Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> * <Value>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> / <Value>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Mult Exp> % <Value>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Mult Exp> ::= <Value>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= <VAR>"):
                lambda c: e(c[0]),
            self.get_production_index("<Value> ::= Integer"):
                lambda c: element.append(int(c[0].token.lexeme)),
            self.get_production_index("<Value> ::= Bool"):
                lambda c: element.append(c[0].token.lexeme),
            self.get_production_index("<Value> ::= StringLiteral"):
                lambda c: element.append(c[0].token.lexeme),
            self.get_production_index("<Value> ::= ( <Expression> )"):
                lambda c: (element.append(c[0].token.lexeme), e(c[1]), element.append(c[0].token.lexeme)),

            # update function
            self.get_production_index("<Statement> ::= <AssignmentStatement>"):
                lambda c: e(c[0]),
            self.get_production_index("<Statement> ::= <Expression>"):
                lambda c: (e(c[0])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := <Expression>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> += <Expression>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> -= <Expression>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := min ( <Expression> , <Expression> )"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), element.append(c[2].token.lexeme),
                           element.append(c[3].token.lexeme),  e(c[4]),
                           element.append(c[5].token.lexeme), e(c[6]), element.append(c[7].token.lexeme)),
            self.get_production_index("<AssignmentStatement> ::= <VAR> := max ( <Expression> , <Expression> )"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), element.append(c[2].token.lexeme),
                           element.append(c[3].token.lexeme), e(c[4]),
                           element.append(c[5].token.lexeme), e(c[6]), element.append(c[7].token.lexeme)),
            self.get_production_index("<Expression> ::= <Or Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<Or Exp> ::= <Or Exp> || <And Exp>"):
                lambda c: (e(c[0]), element.append(c[1].token.lexeme), e(c[2])),
            self.get_production_index("<Or Exp> ::= <And Exp>"):
                lambda c: e(c[0]),
            self.get_production_index("<VAR> ::= Id"):
                lambda c: element.append(c[0].token.lexeme)

        }

        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)

        return e(node)

    def get_input_params(self):
        return self.input_params

    def get_context_vars(self):
        pass