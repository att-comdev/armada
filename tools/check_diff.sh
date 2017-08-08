#!/bin/bash

#yapf commands with -d (print diff for fixed source) will indicate which files and where they need to be reformatted
#-r (recursively over directories)a

#check if the files need to be reformated
#if files need to be reformatted, there will be output from the yapf command.  The output will be saved in yapf_output.txt
#otherwise, there will be no output
if [ $(yapf -d -r ./setup.py ./armada |  wc -c) -ne 0 ];then
    echo "FAIL"
    echo "$(yapf -d -r ./setup.py ./armada)" 
    exit 1
else
    echo "Great Job! Files are formatted properly."
fi

