# import
import string

# define
JACKAPI = { "Sys": ['halt', 'error', 'wait'],
            "Memory": ['peek', 'poke', 'alloc', 'deAlloc'],
            "Keyboard": ['keyPressed', 'readChar', 'readLine', 'readInt'], 
            "Screen": ['clearScreen', 'setColor', 'drawPixel', 'drawLine', 'drawRectangle', 'drawCircle'],
            "Output": ['moveCursor', 'printChar', 'printString', 'printInt', 'println', 'backSpace'],
            "Array": ['new', 'dispose'],
            "String": ['new', 'dispose', 'length', 'charAt', 'setCharAt', 'appendChar', 'eraseLastChar',
                       'intValue', 'setInt', 'doubleQuote', 'backSpace', 'newLine'],
            "Math": ['multiply', 'divide', 'min', 'max', 'sqrt']}

# classes        
# a class for a symbol table
class table:
    def __init__(self, scope, className):
        self.vars = {}
        self.className = className
        if scope == 0:
            self.vars = { "field": [], "static": []}
        else:
            self.vars = { "argument": [], "local": [] }

    # adds a name to the symbol table
    def add(self, name, type, kind):
        if kind == 'method':
            name = 'this'
            type = self.className
            kind = 'argument'
        elif kind == 'var':
            kind = 'local' 
        self.vars[kind] = self.vars.get(kind, []) + [(name, type)]

# a class to handle tables and scope nesting
class tables:
    def __init__(self, className=''):
        self.tables = []
        self.className = className

    # opens a scope level
    def open(self):
        self.tables = [table(len(self.tables), self.className)] + self.tables

    # closes a scope level
    def close(self):
        self.tables = self.tables[1:]

    # adds a variable to the current scope level
    def add(self, name, type, kind):
        self.tables[0].add(name, type, kind)

    # get number of class vars
    def getClassVars(self):
        sum = 0
        for _,value in self.tables[-1].vars.items():
            sum += len(value)
        return sum

    # get number of current sub vars
    def getSubVars(self):
        return len(self.tables[0].vars['local'])

    # look up symbol and return vm equivalent
    def getSymbol(self, name):
        for tab in self.tables:
            for key, values in tab.vars.items():
                index = 0
                for v in values:
                    if name == v[0]:
                        if key == 'argument':
                            return ('argument '+str(index))
                        elif key == 'local':
                            return ('local '+str(index))
                        elif key == 'static':
                            return ('static '+str(index))
                        elif key == 'field':
                            return ('this '+str(index))
                    index += 1
        for key, values in JACKAPI.items():
                if name == key:
                    return 'OS'
        if name == self.className:
            return 'className'

    # takes a name and returns the type of the name
    def getType(self, name):
        for tab in self.tables:
            for _, values in tab.vars.items():
                for v in values:
                    if name == v[0]:
                        return v[1]

        return name
