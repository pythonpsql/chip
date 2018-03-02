#! /usr/bin/env python3
import os
import sys
import common_functions as cf

f = sys.argv[1]
# print(f)
commit_cmd = "git commit -a -m " + "'" + f + "'"
print(commit_cmd)
os.system(commit_cmd)
# git add .
# git commit -m "first commit"
confirm_  = cf.prompt_("Do you want to push?", ['y','n'], unique_ = "existing")
if confirm_ == "y":
    push_cmd = 'git push -u origin master'
    print(push_cmd)
    os.system(push_cmd)
