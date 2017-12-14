#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to get pixiv rank top images

import re
import time
import dataload, privmatrix

pvmx = privmatrix.Matrix()

class DWMRankingTop(object):
    """
    Pixiv website has a rank top, ordinary and R18, daily, weekly, monthly
    this class include fuction will gather all of those rank
    """
    def __init__(self, workdir, logpath, htmlpath):
        """
        :param workdir:     work directory
        :param logpath:     log save path
        :param htmlpath:    html save path
        """
        self.workdir = workdir
        self.logpath = logpath
        self.htmlpath = htmlpath

    @staticmethod
    def gather_essential_info(ormode, whole_nbr):
        """
        get input image count
        :param ormode:      select ranktop ordinary or r18 mode
        :param whole_nbr:   whole ranking crawl count
        :return:            crawl images count
        """
        # transfer ascii string to number
        imgCnt = ''
        if ormode == 'o' or ormode == '1':
            # input a string for request image number
            imgCnt = int(input(dataload.SHELLHEAD +
                        'gather whole ordinary vaild target %d, enter you want: ' % whole_nbr))
            while imgCnt > whole_nbr:
                print(dataload.SHELLHEAD + 'input error, rank top at most %d' % whole_nbr)
                imgCnt = int(input(dataload.SHELLHEAD +
                        'enter again(max is %d): ' % whole_nbr))
        elif ormode == 'r' or ormode == '2':
            # input a string for request image number
            imgCnt = int(input(dataload.SHELLHEAD +
                        'gather whole R18 vaild target %d, enter you want: ' % whole_nbr))
            while imgCnt > whole_nbr:
                print(dataload.SHELLHEAD + 'input error, rank R18 top at most %d' % whole_nbr)
                imgCnt = int(input(dataload.SHELLHEAD +
                        'enter again(max is %d): ' % whole_nbr))
        else:
            pass

        return imgCnt

    def target_confirm(self):
        """
        input option and confirm target
        :param self:    self class
        :return:        request mainpage url, mode
        """
        logContext = 'gather ranking list======>'
        pvmx.logprowork(self.logpath, logContext)
        rankWord = None
        req_url = None
        ormode = input(dataload.SHELLHEAD + 'select ranking type, ordinary(o|1) or r18(r|2): ')
        if ormode == 'o' or ormode == '1':
            dwm = input(dataload.SHELLHEAD + 'select daily(1)|weekly(2)|monthly(3) ordinary ranking type: ')
            if dwm == '1':
                req_url = dataload.dailyRankURL
                rankWord = 'daily'
            elif dwm == '2':
                req_url = dataload.weeklyRankURL
                rankWord = 'weekly'
            elif dwm == '3':
                req_url = dataload.monthlyRankURL
                rankWord = 'monthly'
            else:
                print(dataload.SHELLHEAD + "argv(s) error\n")
            logContext = 'crawler set target to %s rank top' % rankWord
        elif ormode == 'r' or ormode == '2':
            dwm = input(dataload.SHELLHEAD + 'select daily(1)/weekly(2) R18 ranking type: ')
            if dwm == '1':
                req_url = dataload.dailyRankURL_R18
                rankWord = 'daily'
            elif dwm == '2':
                req_url = dataload.weeklyRankURL_R18
                rankWord = 'weekly'
            else:
                print(dataload.SHELLHEAD + "argv(s) error\n")
            logContext = 'crawler set target to %s r18 rank top' % rankWord
        else:
            print(dataload.SHELLHEAD + "argv(s) error\n")
            logContext = None
        pvmx.logprowork(self.logpath, logContext)

        return req_url, ormode

    def gather_rankingdata(self):
        """
        crawl dailyRank list
        :param self:    self class
        :return:        original images urls list
        """
        option = self.target_confirm()
        page_url = option[0]
        ormode = option[1]
        response = pvmx.opener.open(fullurl=page_url,
                                    data=pvmx.getData,
                                    timeout=30)
        if response.getcode() == dataload.reqSuccessCode:
            logContext = 'website response successed'
        else:
            logContext = 'website response fatal, return code %d' % response.getcode()
        pvmx.logprowork(self.logpath, logContext)
        web_src = response.read().decode("UTF-8", "ignore")

        # size info in webpage source
        imgRankInfoPattern = re.compile(dataload.rankSectionRegex, re.S)
        infoPattern = re.compile(dataload.rankTitleRegex, re.S)
        sizerResult = pvmx.data_sizer(imgRankInfoPattern, infoPattern, web_src)
        targetURLs = sizerResult[0]
        imgInfos = sizerResult[1]

        aliveTargets = len(targetURLs)
        img_nbr = self.gather_essential_info(ormode, aliveTargets)
        logContext = 'gather rankingtop ' + str(img_nbr) + ' info======>'
        pvmx.logprowork(self.logpath, logContext)
        basePages = []                                              # request original image need referer
        for k, i in enumerate(imgInfos[:img_nbr]):
            # rank-array    image-name  arthur-name     arthur-id   original-image-url
            logContext = 'no.%d image: [%s | name: %s | illustrator: %s | id: %s | url: %s]' \
                         % (k + 1, i[0], i[1], i[2], i[4], targetURLs[k])
            pvmx.logprowork(self.logpath, logContext)
            basePages.append(dataload.baseWebURL + i[4])            # every picture url address: base_url address + picture_id

        return targetURLs, basePages

    def start(self):
        """
        class main call process
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        starttime = time.time()

        pvmx.camouflage_login(self.logpath)                         # login website, key step
        datas = self.gather_rankingdata()                           # gather data
        # download images
        pvmx.download_alltarget(datas[0], datas[1], self.workdir, self.logpath)

        endtime = time.time()
        elapseTime = endtime - starttime
        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(elapseTime, self.logpath)

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
