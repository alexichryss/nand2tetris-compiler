#!/usr/bin/python
"""compiler: takes in a .jack file or directory and compiles to .vm files, after tokenizing"""

__author__  = "Alexi Chryssanthou"
__email__   = "alexichryss@uchicago.edu"

# import modules
import sys
import os
from bin import tokenizer
from sys import version_info
from pathlib import Path

# define
FILETYPE = '.vm'

# methods
# takes a file, and analyzes for jack syntax, writing parsed syntax to output xml
def parse(dir, name, wm):
    found_file = False
    # if filename suffix is a valid input file, then processes file
    if tokenizer.is_INPUT(name):
        found_file = True
        filename = name.split('.')
        PREFIX = '.'.join(filename[:-1])
        out_filename =  PREFIX + FILETYPE
        block_comment = False
        tokens = []

        # processes file and writes to output file
        try:
            # open file to write to
            direc = Path(dir)
            with open(direc / out_filename, wm) as s:
                # open file to read from
                with open(direc / name, 'r') as f:

                    # cleans line of comments, then feeds line to tokenizer
                    for line in f:
                        # clear comments
                        (line, block_comment) = tokenizer.comment(line, block_comment)

                        # if empty line, skip it
                        if line.strip() == '':
                            continue

                        # if the line is not empty, feed to tokenizer
                        if line != '\n':
                            tokens += tokenizer.feed(line)

                    # get tags parsed from processed tokens and write to file
                    for element in tokenizer.getTags(tokens):
                        s.write(element)

            # print message on successful output
            if os.path.isfile(direc / out_filename):
                print(out_filename + " has been created.\n")
        except:
            # prints message if something goes wrong
            print("Could not process: " + name + '\n')
    # returns True if file was processed
    return found_file

def clean(name):
    direc = Path(name)
    directory = os.listdir(name)
    files = [file for file in directory if file.endswith(FILETYPE)]
    for file in files:
        if os.path.isfile(direc / file):
            os.remove(direc / file)
            print('Deleted: ' + file + " in " + name + "\n")

# takes a name and tries to process the file or directory, returns result as boolean
def prepare(name):
    for suffix in tokenizer.SUFFIX:
        # if inputted name contains a suffix, write 1 file
        if name.find(suffix) != -1:
            found = parse('', name, 'w')
        else:
            found = False
            try:
                directory = os.listdir(name)
                clean(name)
                # list of files with .vm suffix
                files = [file for file in directory if file.endswith(suffix)]
                # for each file, parse, add a start or end loop if first or last file
                for filename in files:
                    temp = parse(name, filename,'w')
                    # if we found at least one file, update found
                    if temp:
                        found = True
            except:
                # couldn't find the directory
                print("No such directory: " + name)
    # return found
    return found

# takes filename and prompts user if file cannot be found
def main():
    # get arguments minus script name
    args = sys.argv[1:]
    # attempts to parse given filename and returns boolean
    if args:
        found_file = prepare(args[0])

    # if no arguments or file was not found, allow user to enter new filename
    if not args or not found_file:
        while True:
            try:
                text = input("Enter new name or press Enter to quit: ")
                if not text:
                    break
                else:
                    found = prepare(text)
                    if not found:
                        print(text + " is not a valid file or directory.")
            except:
                # if something breaks, tell user
                print("Failed. Something went wrong getting input.\n")
                break

# main boilerplate
if __name__ == "__main__":
    main()