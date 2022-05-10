#!/usr/bin/python

# sort and count mysql general log
# Author: Jason
# Url: www.centos.bz
# Email: admin#centos.bz
# Created: UTC 2015-02-15 17:51:53

# 先开启general_log
# mysql> show  variables like '%general%';
# mysql> set global general_log = "ON";

# 分析完以后记得关闭,set global general_log = "OFF";

import re
import sys
import os

if len(sys.argv) == 2:
    logPath = sys.argv[1]
    if not os.path.exists(logPath):
        print("file " + logPath + " does not exists.")
        sys.exit(1)
else:
    print("Usage: " + sys.argv[0] + " logPath")
    sys.exit(1)

logFo = open(logPath)
match = 0

for line in logFo:
    line = re.sub(r"\n", "", line)
    if match == 0:
        # match line begin with numbers
        lineMatch = re.match(r"\s+[0-9]+\s+.*", line, flags=re.I)
        if lineMatch:
            lineTmp = lineMatch.group(0)
            match = match + 1
            continue

    elif match == 1:
        # match line begin with numbers
        lineMatch = re.match(r"\s+[0-9]+\s+.*", line, flags=re.I)
        if lineMatch:
            # match only query
            lineMatchQuery = re.match(r".*Query\s+(.*)", lineTmp, flags=re.I)
            if lineMatchQuery:
                lineTmp = lineMatchQuery.group(1)
                # remove extra space
                lineTmp = re.sub(r"\s+", " ", lineTmp)
                # replace values (value) to values (x)
                lineTmp = re.sub(r"values\s*\(.*?\)", "values (x)", lineTmp, flags=re.I)
                # replace filed = 'value' to filed = 'x'
                lineTmp = re.sub(r"(=|>|<|>=|<=)\s*('|\").*?\2", "\\1 'x'", lineTmp)
                # replace filed = value to filed = x
                lineTmp = re.sub(r"(=|>|<|>=|<=)\s*[0-9]+", "\\1 x", lineTmp)
                # replace like 'value' to like 'x'
                lineTmp = re.sub(r"like\s+('|\").*?\1", "like 'x'", lineTmp, flags=re.I)
                # replace in (value) to in (x)
                lineTmp = re.sub(r"in\s+\(.*?\)", "in (x)", lineTmp, flags=re.I)
                # replace limit x,y to limit
                lineTmp = re.sub(r"limit.*", "limit", lineTmp, flags=re.I)

                print(lineTmp)

            match = 1
            lineTmp = lineMatch.group(0)
        else:
            lineTmp += line
            match = 1

logFo.close()