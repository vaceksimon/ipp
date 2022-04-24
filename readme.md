# Principles of Programming Languages Project
Author: Šimon Vacek

This project is split into 2 parts. The first one is a parser written in PHP, which takes a 3 address code
in IPPcode22 as an input, performs lexical and syntax check and stores the output as an xml file
afterwards.

The second part is an interpreter written in Python, which loads the XML representation of code from the parser,
checks the semantics, and then executes it.
