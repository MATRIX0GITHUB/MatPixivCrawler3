#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to add a example to call class lib

import dataload
from privmatrix import Matrix
from modeoption import RankingTop as rtn
from modeoption import RepertoAll as ira

def main():
    print(Matrix.__doc__)

    mode = input(dataload.SHELLHEAD + 'select mode: ')
    if mode == 'rtn' or mode == '1':
        build_task = rtn(dataload.RANK_DIR, dataload.LOG_PATH, dataload.HTML_PATH)
        build_task.start()
    elif mode == 'ira' or mode == '2':
        build_task = ira(dataload.REPO_DIR, dataload.LOG_NAME, dataload.HTML_NAME)
        build_task.start()
    elif mode == 'help' or mode == '3':
        print(Matrix.__doc__)
    else:
        print(dataload.SHELLHEAD + "argv(s) error\n")

if __name__ == '__main__':
    main()

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
