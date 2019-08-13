# import
import os
import string
from bin import tags

# define
SUFFIX = ['jack']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
           '-', '*', '/', '&', '|', '<', '>', '=', '~']
KEYWORDS = ['class', 'constructor', 'function', 'method', 'field',
            'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
            'false','null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
OP = ['+', '_', '*', '/', '&', '|', '<', '>', '=']
UNARYOP = ['-', '~']
KEYWORDCONST = ['true', 'false', 'null', 'this']

# methods
# takes a filename and checks if file type is allowed and the file exists
def is_INPUT(name):
    filename = name.split('.')
    if filename[-1] in SUFFIX:
        return True
    return False

# removes comment, returns line and true if in block comment
def comment(line, blockcomment):
    ln_cmt = line.find('//') # get index of line comment
    opn_cmt = line.find('/*') # get index of open block comment
    cls_cmt = line.find('*/') # get index of close block comment
    count_quotes = lambda w,x,y,z: w.count(x,y,z) 

    if blockcomment:
        if cls_cmt > -1:
            line = line[cls_cmt+2:]
            return comment(line, False)
        else:
            return ('', True)

    # if block comment, trim and return line and true
    if opn_cmt > -1 and (opn_cmt < ln_cmt or ln_cmt < 0) and count_quotes(line,'\"',0,opn_cmt) % 2 == 0:
        if cls_cmt > -1:
            line = line[:opn_cmt] + line[cls_cmt+2:]
            return(line, False)
        line = line[:opn_cmt] + '\n'
        return(line, True)
    
    # if line comment, trim and return line and false
    if ln_cmt > -1 and (ln_cmt < opn_cmt or opn_cmt < 0) and count_quotes(line,'\"',0,ln_cmt) % 2 == 0:
        line = line[:ln_cmt] + '\n'
        return(line, False)

    # otherwise, no comment, trim whitespaces and return
    line = line.strip() + '\n'
    return (line, False)

# takes an element and splits up the relevant symbols
def symbolize(line):
    prefix = ''
    suffix = ''
    index = 0
    # split symbols and add newline, return string
    for char in line:
        index += 1
        suffix = line[index:]
        if char in SYMBOLS:
            if char == '<':
                char = '&lt;'
            elif char == '>':
                char = '&gt;'
            elif char == '\"':
                char == '&quot;'
            elif char == '&':
                char = '&amp;'
            temp = "<symbol> " + char + " </symbol>\n"

            if len(suffix) != 0:
                temp += toElements(suffix)
            if len(prefix) != 0:
                temp = toElements(prefix) + temp

            return temp
        else:
            prefix += char
    # there were no symbols in the element, could be an integer or an identifier
    try:
        num = int(prefix) % 32768
        temp = "<integerConstant> " + str(num) + " </integerConstant>\n"
    except:
        temp = "<identifier> " + prefix + " </identifier>\n"

    return temp

# splits line into relative elements
def toElements(line):
    elements = []

    # look for double quotes to separate out string Constants
    while '\"' in line:
        if line.find('\"') == 0:
            temp = line[1:].find('\"')
            elements += [line[:temp+2]]
            line = line[temp+2:]
        else:
            elements += [line[:line.find('\"')]]
            line = line[line.find('\"'):]
    elements += [line]

    line = ''

    for element in elements:
        # if the element is a stringConstant
        if element[0] == '\"' and element[-1] == '\"':
            # tokenize
            temp = "<stringConstant> " + element[1:-1] + " </stringConstant>\n"
            line += temp

        else:
            # split each element into component parts and tokenize
            element = element.split(' ')
            for item in element:
                item = item.strip()
                if item != '':
                    if item in KEYWORDS:
                        temp = "<keyword> " + item + " </keyword>\n"
                        line += temp
                    else:
                        line += symbolize(item)
    return line

# accepts file strings, tokenizes and adds to tokens
def feed(line):
    tokens = []
    line = toElements(line)
    line = line.split('\n')
    for element in line[:-1]:
        tokens += [element + '\n']
    return tokens

# returns parsed tokens from tags
def getTags(tokens):
    return tags.parse(tokens)