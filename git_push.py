#! /usr/bin/env python3
import os
import sys

f = sys.argv[1]
# print(f)
commit_cmd = "git commit -a -m " + "'" + f + "'"
print(commit_cmd)
os.system(commit_cmd)
# git add .
# git commit -m "first commit"
push_cmd = 'git push -u origin master'
os.system(push_cmd)
