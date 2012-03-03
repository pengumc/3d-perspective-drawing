#! /usr/bin/env python
#Let's not bicker and argue over who killed who. 
import controller
import sys

acc = False;
if len(sys.argv) > 1:
    if sys.argv[1] == '--acc':
        acc = True;
C = controller.Controller(acc)
C.run()

