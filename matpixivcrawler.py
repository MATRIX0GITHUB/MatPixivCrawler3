#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================y
# this python script is built to add a example to call class lib

import dataload, privmatrix, rankingtop, illustrepo                 # call private lib

if __name__ == '__main__':
    print(privmatrix.Matrix().__doc__)
    mode = input(dataload.SHELLHEAD + 'select a mode: ')            # choose mode
    if mode == 'rtn' or mode == '1':
        print(dataload.SHELLHEAD + "check mode: RankingTopN")
        rtn_work = rankingtop.DWMRankingTop(dataload.ranking_folder,
                                            dataload.logfile_path,
                                            dataload.htmlfile_path)
        rtn_work.start()
    elif mode == 'ira' or mode == '2':
        print(dataload.SHELLHEAD + "check mode: illustRepoAll")
        global_id = input(dataload.SHELLHEAD
                          + 'target crawl illustrator pixiv-id: ')
        ira_work = illustrepo.IllustratorRepos(global_id,
                                               dataload.work_dir,
                                               dataload.logfile_name,
                                               dataload.htmlfile_name)
        ira_work.start()
    elif mode == 'help':
        print(privmatrix.Matrix().__doc__)
    else:
        print(dataload.SHELLHEAD + "argv(s) error\n")

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
