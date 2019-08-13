# import
import string
from bin import store

# define
OP = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
CONVERTOP = {'+': 'add', '-': 'sub', '*':'call Math.multiply 2', '/':'call Math.divide 2', 
            '&amp;':'and', '|':'or', '&lt;':'lt', '&gt;':'gt', '=':'eq'}
UNARYOP = ['-', '~']
CONVERTUN = {'-':'neg', '~':'not'}
KEYWORDCONST = ['true', 'false', 'null', 'this']
CLADECTYPE = ['static', 'field']
SUBDECTYPE = ['constructor', 'function', 'method']
TYPE = ['int', 'char', 'boolean']
STATEMENTS = ['let', 'if', 'while', 'do', 'return']
ASCII = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
ASCIIbuffer = 32

# class
# a class to handle walking through the token list, parsing for jack grammar
class tags:
    def __init__(self, tokens, spaces):
        self.tokens = tokens
        self.tags = []
        self.tables = []
        self.ifelse = 0
        self.whileloop = 0

    # takes a token and returns (token type, token body, token)
    def readToken(self, token):
        tag_end = token.find('> ')+1
        sym_end = token.find(' </')
        return (token[1:tag_end-1], token[(tag_end+1):sym_end], token)

    # returns current token
    def look(self):
        return self.readToken(self.tokens[0])

    # pop the first token off the token list and add it to tags
    def pop(self, show=False):
        temp = self.tokens[0]
        self.tokens = self.tokens[1:]
        return self.readToken(temp)[1]
    
    # pop or push symbol after checking varName exists
    def symbolWrite(self, cmd, name):
        symbol = self.tables.getSymbol(name)
        if symbol != None:
            if symbol != 'OS' and symbol != 'className':
                self.write(cmd+' '+symbol)

    # to write to tags list for writing to file
    def write(self, string):
        self.tags += [string + '\n']

    # get subroutine declarations while they last
    def subroutineDec(self):
        while self.look()[1] in SUBDECTYPE:
            self.ifelse = 0
            self.whileloop = 0
            self.tables.open()
            if self.look()[1] == 'method':
                self.tables.add('this', 'className', 'method')
            subType = self.pop() # constructor | function | method
            outType = self.pop() # void | type
            subName = self.pop() # subroutine name
            self.pop() # (
            self.parameterList() # parameterList
            self.pop() # )
            self.subroutineBody(subType, outType, subName) # subroutine body
            #self.tables.printer()
            self.tables.close()

    # get parameter list of subroutine
    def parameterList(self):
        kind = 'argument'
        while self.look()[1] != ')':
            type = self.look()[1]
            self.pop() # type
            name = self.pop() # varName
            self.tables.add(name, type, kind)
            while self.look()[1] == ',':
                self.pop() # ,
                type = self.look()[1]
                self.pop() # type
                name = self.pop() # varName
                self.tables.add(name, type, kind)

    # get subroutine Body 
    def subroutineBody(self, subType, outType, subName):
        self.pop() # {
        self.varDec('var') # varDecs*
        size = self.tables.getClassVars()
        subSize = self.tables.getSubVars()
        self.write('function '+self.tables.className+'.'+subName+' '+str(subSize))
        if subType == 'constructor':
            self.write('push constant '+str(size))
            self.write('call Memory.alloc 1')
            self.write('pop pointer 0')
        if subType == 'method':
            self.write('push argument 0')
            self.write('pop pointer 0')
        self.statement() # statements
        self.pop() # }

    # get list of variables
    def varDec(self, category):
        while self.look()[1] in category:
            kind = self.pop() # var OR static | field
            type = self.pop() # type
            name = self.pop() # varName
            self.tables.add(name, type, kind) # add symbol to table
            while self.look()[1] == ',':
                self.pop() # ,
                name = self.pop() # varName
                self.tables.add(name, type, kind) # add symbol to table
            self.pop() # ;

    # get statements
    def statement(self):
        while self.look()[1] in STATEMENTS:
            # let statement
            if self.look()[1] == 'let':
                self.pop() # let
                name = self.pop() # varName
                array = False
                if self.look()[1] == '[':
                    array = True
                    self.pop() # [
                    self.expression() # expression
                    self.pop() # ]
                    self.symbolWrite('push', name)
                    self.write('add')
                self.pop() # =
                self.expression() # expression
                self.pop() # ;
                if array:
                    self.write('pop temp 0')
                    self.write('pop pointer 1')
                    self.write('push temp 0')
                    self.write('pop that 0')
                else:
                    self.symbolWrite('pop', name)
            # if (else) statement
            elif self.look()[1] == 'if':
                thisif = str(self.ifelse)
                self.ifelse += 1
                self.pop() # if
                self.pop() # (
                self.expression() # expression
                self.pop() # )
                self.write("not")
                self.write("if-goto IF_TRUE"+thisif)
                self.pop() # {
                self.statement() # statements
                self.pop() # }
                iselse = False
                if self.look()[1] == 'else':
                    iselse = True
                    self.write("goto IF_END"+thisif)
                    self.pop() # else
                    self.pop() # {
                self.write("label IF_TRUE"+thisif)
                if iselse:
                    self.statement() # statments
                    self.pop() # }
                    self.write("label IF_END"+thisif)
            # while statement
            elif self.look()[1] == 'while':
                thisloop = str(self.whileloop)
                self.whileloop += 1
                self.pop() # while
                self.write("label WHILE_EXP"+thisloop)
                self.pop() # (
                self.expression() # expression
                self.pop() # )
                self.write("not")
                self.write("if-goto WHILE_END"+thisloop)
                self.pop() # {
                self.statement() # statements
                self.pop() # }
                self.write("goto WHILE_EXP"+thisloop)
                self.write("label WHILE_END"+thisloop)
            # do statement
            elif self.look()[1] == 'do':
                self.pop() # do
                name = self.pop() # subroutineName OR className | varName
                self.subroutineCall(name) # subroutineCall
                self.pop() # ;
                self.write('pop temp 0')
            # return statement
            elif self.look()[1] == 'return':
                temp = self.pop() # return
                if self.look()[1] != ';':
                    self.expression() # expression
                else:
                    self.write('push constant 0') # void function should return 0
                self.pop() # ;
                self.write(temp)
    
    # get expressions
    def expression(self):
        self.term() # term
        # while term (op term)
        while self.look()[1] in OP:
            op = self.pop() # op
            self.term() # term
            self.write(CONVERTOP.get(op, ''))

    # get term
    def term(self):
        if self.look()[1] in UNARYOP:
            symbol = self.pop() # unaryOp
            self.term() # term
            self.write(CONVERTUN.get(symbol, ''))
        elif self.look()[1] == '(':
            self.pop() # (
            self.expression() # expression
            self.pop() # )
        elif self.look()[0] == 'integerConstant':
            temp = self.pop() # integerConstant 
            self.write('push constant ' + temp)
        elif self.look()[0] == 'stringConstant':
            self.createString(self.pop())# stringConstant
        elif self.look()[0] == 'keyword':
            temp = self.pop() # keyword
            if temp == 'this':
                string = 'push pointer 0'
            elif temp == 'true':
                string = 'push constant 0\nnot'
            else: # false or null
                string = 'push constant 0'
            self.write(string)
        elif self.look()[0] == 'identifier':
            name = self.pop() # varName OR subroutineName OR className | varName
            array = False
            sub = False
            # accessing an array
            if self.look()[1] == '[':
                array = True
                self.pop() # [
                self.expression() # expression
                self.pop() # ]
            # subroutine call
            elif self.look()[1] in ['(', '.']:
                sub = True
                self.subroutineCall(name) # subroutineCall
            if not (array or sub):
                self.symbolWrite('push', name)
            elif array:
                self.symbolWrite('push', name)
                self.write('add')
                self.write('pop pointer 1')
                self.write('push that 0')

    # get subroutineCall
    def subroutineCall(self, name):
        fromObject = False
        fromClass = False
        # if '.' then name is class|var
        if self.look()[1] == '.':
            self.symbolWrite('push', name)
            if name[0].islower():
                fromClass = True
                name = self.tables.getType(name)
            name += self.pop() # .
            name += self.pop() # subroutineName
        # no '.' means name is subroutine
        else:
            name = self.tables.className + '.' + name
            fromObject = True
            self.write('push pointer 0')
        self.pop() # (
        count = self.expressionList() # expressionList
        self.pop() # )
        if fromObject or fromClass:
            count += 1
        self.write('call '+name+' '+str(count))

    # get expression list
    def expressionList(self):
        count = 0
        if self.look()[1] != ')':
            count += 1
            self.expression() # expression
            # continue getting expressions while there are commas
            while self.look()[1] == ',':
                count += 1
                self.pop() # ,
                self.expression() # expression
        return count

    # iterates through the token list one by one, returning a tag list
    def walk(self):
        # create only one class per file
        self.pop() # class
        name = self.pop() # className
        self.pop() # {
        self.tables = store.tables(name)
        self.tables.open()
        self.varDec(CLADECTYPE) # classVarDec*
        self.subroutineDec() # subroutineDec*
        self.tables.close()
        self.pop() # }
        return self.tags

    # turn a stringConstant into vm code
    def createString(self, string):
        size = len(string)
        self.write('push constant ' + str(size))
        self.write('call String.new 1')
        for s in string:
            num = ASCII.find(s) + ASCIIbuffer
            self.write('push constant ' + str(num))
            self.write('call String.appendChar 2')

# parse the token list and return the resultant tags
def parse(tokens):
    processed = tags(tokens, 2).walk()
    return processed
