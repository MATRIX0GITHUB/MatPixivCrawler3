#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to provide modes for crawler

import re
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

    @staticmethod
    def target_confirm(logpath):
        """
        input option and confirm target
        :param logpath: log save path
        :return:        request mainpage url, mode
        """
        logContext = 'gather ranking list======>'
        pvmx.logprowork(logpath, logContext)
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
        pvmx.logprowork(logpath, logContext)

        return req_url, ormode

    def gather_rankingdata(self, option, logpath):
        """
        crawl dailyRank list
        :param self:    self class
        :param option:  user choose option
        :param logpath: log save path
        :return:        original images urls list
        """
        page_url = option[0]
        ormode = option[1]
        response = pvmx.opener.open(fullurl=page_url,
                                    data=pvmx.getData,
                                    timeout=30)
        if response.getcode() == dataload.reqSuccessCode:
            logContext = 'website response successed'
        else:
            logContext = 'website response fatal, return code %d' % response.getcode()
        pvmx.logprowork(logpath, logContext)
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
            pvmx.logprowork(logpath, logContext)
            basePages.append(dataload.baseWebURL + i[4])            # every picture url address: base_url address + picture_id

        return targetURLs, basePages

    def start(self):
        """
        class main call process
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        pvmx.camouflage_login(self.logpath)

        option = self.target_confirm(self.logpath)
        datas = self.gather_rankingdata(option, self.logpath)

        pvmx.download_alltarget(datas[0], datas[1], self.workdir, self.logpath)
        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(self.logpath)

class IllustratorRepos(object):
    """
    every illustrator in Pixiv has own mainpage
    this class include fuction will crawl all of those page all images
    """
    def __init__(self, workdir, logname, htmlname):
        """
        :param workdir:     work directory
        :param logname:     log name
        :param htmlname:    html name
        """
        targetID = input(dataload.SHELLHEAD
                    + 'target crawl illustrator pixiv-id: ')
        self.illustInputID = targetID
        self.workdir = workdir + self.illustInputID                 # use id name folder
        self.logpath = self.workdir + logname
        self.htmlpath = self.workdir + htmlname

    @staticmethod
    def gather_preloadinfo(illust_id):
        """
        crawler need to know how many images do you want
        :param illust_id:   illustrator id
        :return:            request images count
        """
        # get illust artwork whole count mainpage url
        cnt_url = dataload.mainPage + illust_id
        response = pvmx.opener.open(fullurl=cnt_url,
                                    data=pvmx.getData,
                                    timeout=30)
        web_src = response.read().decode("UTF-8", "ignore")

        # mate illustrator name
        illustNamePattern = re.compile(dataload.illustNameRegex, re.S)
        arthorNames = re.findall(illustNamePattern, web_src)
        # if login failed, this step will raise an error
        arthorName = None
        if len(arthorNames) == 0:
            print(dataload.SHELLHEAD + "login failed, please check method call")
            exit()
        else:
            arthorName = arthorNames[0]

        # mate max count
        pattern = re.compile(dataload.illustAWCntRegex, re.S)
        maxCntword = re.findall(pattern, web_src)[1][:-1]
        maxCnt = int(maxCntword)

        return maxCnt, arthorName

    @staticmethod
    def crawl_onepage_data(illust_id, array, logpath):
        """
        crawl all target url about images
        page request regular:
        no.1 referer: &type=all request url: &type=all&p=2
        no.2 referer: &type=all&p=2 request url: &type=all&p=3
        no.3 referer: &type=all&p=3 request url: &type=all&p=4
        :param self:        self class
        :param illust_id:   illustrator id
        :param array:       count cut to every 20 images from each page, they have an array
        :param logpath:     log save path
        :return:            use regex to mate web src thumbnail images url
        """
        step1url = dataload.mainPage + illust_id + dataload.mainPagemiddle
        if array == 1:
            urlTarget = step1url
        elif array == 2:
            urlTarget = step1url + dataload.mainPagetail + str(array)
        else:
            urlTarget = step1url + dataload.mainPagetail + str(array)
        response = pvmx.opener.open(fullurl=urlTarget,
                                    data=pvmx.getData,
                                    timeout=30)
        if response.getcode() == dataload.reqSuccessCode:
            logContext = "mainpage %d response successed" % array
        else:
            logContext = "mainpage %d response timeout, failed" % array
        pvmx.logprowork(logpath, logContext)
        # each page cut thumbnail image url
        web_src = response.read().decode("UTF-8", "ignore")

        # size info in webpage source
        imgWholeInfoPattern = re.compile(dataload.imgWholeInfoRegex, re.S)
        imageNamePattern = re.compile(dataload.imagesNameRegex, re.S)
        sizerResult = pvmx.data_sizer(imgWholeInfoPattern, imageNamePattern, web_src)
        targetURLs = sizerResult[0]
        imageNames = sizerResult[1]

        logContext = "mainpage %d data gather finished" % array
        pvmx.logprowork(logpath, logContext)

        return targetURLs, imageNames

    def crawl_allpage_target(self, illust_id, nbr, arthor_name, logpath):
        """
        package all gather url
        :param self:        self class
        :param illust_id:   illustrator id
        :param nbr:         package images count
        :param arthor_name: arthor name
        :param logpath:     log save path
        :return:            build original images urls list
        """
        # calcus nbr need request count
        if nbr <= 20:
            needPagecnt = 1                                         # nbr <= 20, request once
        else:
            needPagecnt = int(nbr / 20) + 1                         # only need integer

        # gather all data(thumbnail images and names)
        allTargeturls = []
        allArtworkName = []
        for i in range(needPagecnt):
            dataCapture = self.crawl_onepage_data(illust_id, i + 1, logpath)
            allTargeturls += dataCapture[0]
            allArtworkName += dataCapture[1]
        # collection target count
        aliveTargetcnt = len(allTargeturls)

        # input want image count
        capCnt = int(input(dataload.SHELLHEAD
                + 'gather all repo %d, whole target(s): %d, enter you want count: ' % (nbr, aliveTargetcnt)))
        # count error
        while (capCnt > aliveTargetcnt) or (capCnt <= 0):
            capCnt = int(input(dataload.SHELLHEAD
                + 'error, input count must <= %d and not 0: ' % aliveTargetcnt))
        logContext = "check crawl illustrator id:" + self.illustInputID + " image(s):%d" % capCnt
        pvmx.logprowork(logpath, logContext)

        artworkIDs = []                                             # images id list
        capTargets = []
        basePages = []                                              # image basic page
        for i in allTargeturls[:capCnt]:
            capTargets.append(i)                                    # cut need count
            img_id = i[57:-7]
            artworkIDs.append(img_id)                               # image id list
            basePage = dataload.baseWebURL + img_id
            basePages.append(basePage)                              # basic page list
        # log images info
        logContext = 'illustrator: ' + arthor_name + ' id: ' + self.illustInputID + ' artworks info====>'
        pvmx.logprowork(logpath, logContext)

        for k, i in enumerate(allArtworkName[:capCnt]):
            logContext = 'no.%d image: [%s | id: %s | url: %s]' % ((k + 1), i, artworkIDs[k], capTargets[k])
            pvmx.logprowork(logpath, logContext)

        return capTargets, basePages

    def start(self):
        """
        include this class run logic
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        pvmx.camouflage_login(self.logpath)                         # login website, key step

        # gather info and data
        info = self.gather_preloadinfo(self.illustInputID)
        datas = self.crawl_allpage_target(self.illustInputID, info[0], info[1], self.logpath)

        pvmx.download_alltarget(datas[0], datas[1], self.workdir, self.logpath)
        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(self.logpath)

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
