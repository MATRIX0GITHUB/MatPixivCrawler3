#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to add a example to call class lib

import dataload                                                     # storage data and strings
import privmatrix                                                   # private crawler library
import rankingtop, illustrepo                                       # two mode task class

if __name__ == '__main__':
    print(privmatrix.Matrix().__doc__)

    mode = input(dataload.SHELLHEAD + 'select mode: ')
    if mode == 'rtn' or mode == '1':
        # create work class
        rtn_work = rankingtop.DWMRankingTop(
            dataload.ranking_folder,
            dataload.logfile_path,
            dataload.htmlfile_path)
        rtn_work.start()
    elif mode == 'ira' or mode == '2':
        targetID = input(dataload.SHELLHEAD
                         + 'target crawl illustrator pixiv-id: ')
        # create work class
        ira_work = illustrepo.IllustratorRepos(
            targetID,
            dataload.work_dir,
            dataload.logfile_name,
            dataload.htmlfile_name)
        ira_work.start()
    elif mode == 'help' or mode == '3':
        print(privmatrix.Matrix().__doc__)
    else:
        print(dataload.SHELLHEAD + "argv(s) error\n")

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
