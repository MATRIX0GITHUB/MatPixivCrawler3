#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to add a example to call class lib

import dataload                                                     # storage data and strings
import privmatrix                                                   # private crawler library
from modeoption import DWMRankingTop, IllustratorRepos

def main():
    print(privmatrix.Matrix().__doc__)

    mode = input(dataload.SHELLHEAD + 'select mode: ')
    if mode == 'rtn' or mode == '1':
        buildTask = DWMRankingTop(
            dataload.ranking_folder,
            dataload.logfile_path,
            dataload.htmlfile_path)
        buildTask.start()
    elif mode == 'ira' or mode == '2':
        buildTask = IllustratorRepos(
            dataload.repo_folder,
            dataload.logfile_name,
            dataload.htmlfile_name)
        buildTask.start()
    elif mode == 'help' or mode == '3':
        print(privmatrix.Matrix().__doc__)
    else:
        print(dataload.SHELLHEAD + "argv(s) error\n")

if __name__ == '__main__':
    main()

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
