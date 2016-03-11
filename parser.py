import re

debug_flag = True
regex_for_fns = r'(\w+)\((\w+)\)$'
regex_for_statements = r'^(\w+)\s?->\s?(\w+)$|^(\w+)$'
file = open('test.rx', 'r')
final_regex = []

general_tokens = {
    "new_line": r"\n",
    "carriage_return": r"\r",
    "tab": r"\t",
    "null_character": r"\0"
}

anchors = {
    "start_of_match": r"\G",
    "start_of_string": {
        "multi_line": r"^",
        "not_multi_line": r"\A"
    },
    "end_of_string": {
        "multi_line": r"$",
        "not_multi_line": r"\Z",
        "absolute": r"\z"
    },
    "word_boundary": r"\b",
    "non_word_boundary": r"\B"
}

meta_sequences = {
    "any_single_character": r".",

}

token_groups = [
    general_tokens,
    anchors
]


class InvalidToken(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidExpression(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidFunctionParameter(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoExpressionTypeFound(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Fn:
    def __init__(self, expression):
        fn_parts = re.match(regex_for_fns, expression)
        if fn_parts is None or fn_parts.group(1) is None or fn_parts.group(2) is None:
            debug("NOT a function expression")
            raise InvalidExpression(expression_error_message(expression, self))
        self.fn_name = fn_parts.group(1)
        self.parameter = fn_parts.group(2)
        self.type = "fn"
        debug("IS a function expression")


class Statement:
    def __init__(self, expression):
        statement = re.match(regex_for_statements, expression)
        if statement is None:
            debug("NOT a statement expression")
            raise InvalidExpression(expression_error_message(expression, self))
        if statement.group(2):
            self.option = statement.group(2)
            self.statement = statement.group(1)
        else:
            self.option = None
            self.statement = statement.group(0)
        self.type = "statement"
        debug("IS a statement expression")


def expression_error_message(non_valid_expression, expression_class):
    return '"' + non_valid_expression + '" is not a correct ' + expression_class.__class__.__name__ + ' expression.'


def debug(message, separator_flag=False):
    if debug_flag is True:
        separator = ""
        if separator_flag is True:
            separator = "\n"
        print(separator + '>>> ' + message)


def get_expression(raw_expression):
    stripped_expression = raw_expression.rstrip('\n')
    found_type = 0
    try:
        fn = Fn(stripped_expression)
        return fn
    except InvalidExpression:
        pass
    try:
        statement = Statement(stripped_expression)
        return statement
    except InvalidExpression:
        pass

    raise NoExpressionTypeFound('The expression ' + stripped_expression + ' doesn\'t match any type ot matches too many')


def get_token_from_expression(expression):
    if expression.type is "fn":
        return expression.fn_name
    if expression.type is "statement":
        return expression.statement


def get_regex_representation(raw_line):
    expression = get_expression(raw_line)
    token = get_token_from_expression(expression)

    for token_group in token_groups:
        if token in token_group:
            if type(token_group[token]) is dict:
                try:
                    regex_expression = token_group[token][expression.option]
                    return regex_expression
                except KeyError:
                    # TODO: this raises two exceptions
                    raise InvalidFunctionParameter("The parameter doesn't seem to be valid")
            return token_group[token]
    err = 'The provided token: "' + token + '" is not valid.'
    raise InvalidToken(err)

for index, line in enumerate(file):
    separate = True if index is not 0 else False
    debug("Starting to analyse raw expression: " + line.rstrip("\n"), separate)
    regex_representation = get_regex_representation(line)
    final_regex.append(regex_representation)

print("/" + "".join(final_regex) + "/")
