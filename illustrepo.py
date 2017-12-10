#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to get a illust all repo images

import re
import time
import dataload, privmatrix

pvmx = privmatrix.Matrix()

class IllustratorRepos(object):
    """
    every illustrator in Pixiv has own mainpage
    this class include fuction will crawl all of those page all images
    """
    def __init__(self, iid, workdir, logname, htmlname):
        """
        :param iid:         illustrator id
        :param workdir:     work directory
        :param logname:     log name
        :param htmlname:    html name
        """
        self.illustInputID = iid
        self.workdir = workdir + self.illustInputID
        self.logpath = self.workdir + logname
        self.htmlpath = self.workdir + htmlname

    def gather_preloadinfo(self):
        """
        crawler need to know how many images do you want
        :param self:    self class
        :param logpath: log save path
        :return:        request images count
        """
        # get illust artwork whole count mainpage url
        cnt_url = dataload.mainPage + self.illustInputID
        response = pvmx.opener.open(fullurl=cnt_url,
                                    data=pvmx.getData,
                                    timeout=30)
        web_src = response.read().decode("UTF-8", "ignore")

        # mate illustrator name
        illustNamePattern = re.compile(dataload.illustNameRegex, re.S)
        arthor_name = re.findall(illustNamePattern, web_src)[0]

        # mate max count
        pattern = re.compile(dataload.illustAWCntRegex, re.S)
        maxCntword = re.findall(pattern, web_src)[1][:-1]
        maxCnt = int(maxCntword)

        return maxCnt, arthor_name

    def crawl_onepage_data(self, array, logpath):
        """
        crawl all target url about images
        page request regular:
        no.1 referer: &type=all request url: &type=all&p=2
        no.2 referer: &type=all&p=2 request url: &type=all&p=3
        no.3 referer: &type=all&p=3 request url: &type=all&p=4
        :param self:    self class
        :param array:   count cut to every 20 images from each page, they have an array
        :param logpath: log save path
        :return:        use regex to mate web src thumbnail images url
        """
        step1url = dataload.mainPage + self.illustInputID + dataload.mainPagemiddle
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
        imageName = sizerResult[1]

        logContext = "mainpage %d data gather finished" % array
        pvmx.logprowork(logpath, logContext)

        return targetURLs, imageName

    def crawl_allpage_target(self, nbr, arthor_name, logpath):
        """
        package all gather url
        :param self:        self class
        :param nbr:         package images count
        :param arthor_name: arthor name
        :param logpath:     log save path
        :return:            build original images urls list
        """
        # calcus nbr need request count
        if nbr <= 20:
            needPagecnt = 1                                         # nbr <= 20, request once
        else:
            needPagecnt = int(nbr / 20) + 1                         # calcus need request count

        # gather all data(thumbnail images and names)
        allTargeturls = []
        allArtworkName = []
        for i in range(needPagecnt):
            dataCapture = self.crawl_onepage_data(i + 1, logpath)
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
            logContext = 'no.%d image: [%s id: %s url: %s]' % ((k + 1), i, artworkIDs[k], capTargets[k])
            pvmx.logprowork(logpath, logContext)

        return capTargets, basePages

    def start(self):
        """
        include this class run logic
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        starttime = time.time()

        pvmx.camouflage_login(self.logpath)                         # login website, key step
        # gather info and data
        info = self.gather_preloadinfo()
        datas = self.crawl_allpage_target(info[0], info[1], self.logpath)
        # download images
        pvmx.download_alltarget(datas[0], datas[1], self.workdir, self.logpath)

        endtime = time.time()
        logContext = "elapsed time: %0.2fs" % (endtime - starttime)
        pvmx.logprowork(self.logpath, logContext)

        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(self.logpath)

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
