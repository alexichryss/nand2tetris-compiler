# Project 10: compiler.py

A Python script to tokenize, parse and then compile a .jack file or files and output to .vm. The tokenizer was written and tested first. After verifying a successful tokenizing stage, the parser was added second. Finally, the parser was refactored into the compiler, removing unecessary token tags in the process.

## Getting Started

This script can be run in Python 3 (3.5 or later). Python 2 (2.7 or later) support was removed due to a lack of a pathLib library, which this script relies on in order to traverse the jack directory.

The input file must be of a type declared in SUFFIXES, currently set to '.jack (defined in tokenizer.py).

compiler.py takes a filename or directory provided as a command line parameter and attempts to tokenize, parse and then compile the subsequent file(s). Each file is output to a new file with the same name, but ending in .vm

## Running

To run, call the script with the file or directory you would like to translate. The path can be relative or absolute. If the directory is in the same folder as the script, then just the name is sufficient.

```bash
$ python compiler.py Pong

Deleted: PongGame.vm in Pong

Deleted: Main.vm in Pong

Deleted: Bat.vm in Pong

Ball.vm has been created.

Main.vm has been created.

PongGame.vm has been created.

Bat.vm has been created.

$
```

The output file will appear in the same directory as the input file.

ATTENTION: If previous .vm files of the same name already exist in the directory, they will be deleted and replaced.

## Troubleshooting

If the specified file cannot be found or no filename is given, then the user will be prompted for a new filename.

```bash
Enter new filename or press Enter to quit:
```

Pressing Enter without any other keystrokes will quit the script.

## Testing

The script was tested with every program provided by nand2tetris and the custom game created for project 9. All programs worked flawlessly, without exception, and behaved exactly as they would if compiled by the provided compiler.

## Authors

* Alexi Chryssanthou
