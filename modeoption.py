#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to provide modes for crawler

import re
import dataload, privmatrix

pvmx = privmatrix.Matrix()                                          # we need its class and global variable

class RankingTop(object):
    """
    Pixiv website has a rank top, ordinary and R18, daily, weekly, monthly
    this class include fuction will gather all of those ranks
    """
    def __init__(self, workdir, log_path, html_path):
        """
        :param workdir:     work directory
        :param log_path:     log save path
        :param html_path:    html save path
        """
        self.workdir = workdir
        self.logpath = log_path
        self.htmlpath = html_path

    @staticmethod
    def gather_essential_info(ormode, whole_nbr):
        """
        get input image count
        :param ormode:      select ranktop ordinary or r18 mode
        :param whole_nbr:   whole ranking crawl count
        :return:            crawl images count
        """
        # transfer ascii string to number
        img_cnt = 0
        if ormode == 'o' or ormode == '1':
            # input a string for request image number
            img_cnt = int(input(dataload.SHELLHEAD +
                        'gather whole ordinary vaild target %d, enter you want: ' % whole_nbr))
            while img_cnt > whole_nbr:
                print(dataload.SHELLHEAD + 'input error, rank top at most %d' % whole_nbr)
                img_cnt = int(input(dataload.SHELLHEAD +
                        'enter again(max is %d): ' % whole_nbr))
        elif ormode == 'r' or ormode == '2':
            # input a string for request image number
            img_cnt = int(input(dataload.SHELLHEAD +
                        'gather whole R18 vaild target %d, enter you want: ' % whole_nbr))
            while img_cnt > whole_nbr:
                print(dataload.SHELLHEAD + 'input error, rank R18 top at most %d' % whole_nbr)
                img_cnt = int(input(dataload.SHELLHEAD +
                        'enter again(max is %d): ' % whole_nbr))
        else:
            pass

        return img_cnt

    @staticmethod
    def target_confirm(log_path):
        """
        input option and confirm target
        :param log_path: log save path
        :return:        request mainpage url, mode
        """
        log_context = 'gather ranking list======>'
        pvmx.logprowork(log_path, log_context)
        rank_word = None
        req_url = None
        ormode = input(dataload.SHELLHEAD + 'select ranking type, ordinary(o|1) or r18(r|2): ')
        if ormode == 'o' or ormode == '1':
            dwm = input(dataload.SHELLHEAD + 'select daily(1)|weekly(2)|monthly(3) ordinary ranking type: ')
            if dwm == '1':
                req_url = dataload.DAILY_RANKING_URL
                rank_word = dataload.DAILY_WORD
            elif dwm == '2':
                req_url = dataload.WEEKLY_RANKING_URL
                rank_word = dataload.WEEKLY_WORD
            elif dwm == '3':
                req_url = dataload.MONTHLY_RANKING_URL
                rank_word = dataload.MONTHLY_WORD
            else:
                print(dataload.SHELLHEAD + "argv(s) error\n")
            log_context = 'crawler set target to %s rank top' % rank_word
        elif ormode == 'r' or ormode == '2':
            dwm = input(dataload.SHELLHEAD + 'select daily(1)/weekly(2) R18 ranking type: ')
            if dwm == '1':
                req_url = dataload.DAILY_RANKING_R18_URL
                rank_word = dataload.DAILY_WORD
            elif dwm == '2':
                req_url = dataload.WEEKLY_RANKING_R18_URL
                rank_word = dataload.WEEKLY_WORD
            else:
                print(dataload.SHELLHEAD + "argv(s) error\n")
            log_context = 'crawler set target to %s r18 rank top' % rank_word
        else:
            print(dataload.SHELLHEAD + "argv(s) error\n")
            log_context = None
        pvmx.logprowork(log_path, log_context)

        return req_url, ormode

    def gather_rankingdata(self, option, log_path):
        """
        crawl dailyRank list
        :param self:        self class
        :param option:      user choose option
        :param log_path:    log save path
        :return:            original images urls list
        """
        page_url = option[0]
        ormode = option[1]
        response = pvmx.opener.open(fullurl=page_url,
                                    data=pvmx.getway_data,
                                    timeout=30)
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'website response successed'
        else:
            log_context = 'website response fatal, return code %d' % response.getcode()
        pvmx.logprowork(log_path, log_context)
        web_src = response.read().decode("UTF-8", "ignore")

        # size info in webpage source
        imgitem_pattern = re.compile(dataload.RANKING_SECTION_REGEX, re.S)
        info_pattern = re.compile(dataload.RANKING_INFO_REGEX, re.S)
        sizer_result = pvmx.data_sizer(imgitem_pattern, info_pattern, web_src)
        target_urls = sizer_result[0]
        img_infos = sizer_result[1]

        alive_targets = len(target_urls)
        img_nbr = self.gather_essential_info(ormode, alive_targets)
        log_context = 'gather rankingtop ' + str(img_nbr) + ' info======>'
        pvmx.logprowork(log_path, log_context)
        basepages = []                                              # request original image need referer
        for k, i in enumerate(img_infos[:img_nbr]):
            # rank-array    image-name  arthur-name     arthur-id   original-image-url
            log_context = 'no.%d image: [%s | name: %s | illustrator: %s | id: %s | url: %s]' \
                         % (k + 1, i[0], i[1], i[2], i[4], target_urls[k])
            pvmx.logprowork(log_path, log_context)
            basepages.append(dataload.BASEPAGE_URL + i[4])          # every picture url address: base_url address + picture_id

        return target_urls, basepages

    def start(self):
        """
        class main call process
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        pvmx.camouflage_login(self.logpath)

        option = self.target_confirm(self.logpath)
        web_bias = self.gather_rankingdata(option, self.logpath)

        pvmx.download_alltarget(web_bias[0], web_bias[1], self.workdir, self.logpath)
        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(self.logpath)

class RepertoAll(object):
    """
    every illustrator in Pixiv has own mainpage
    this class include fuction will crawl all of those page all images
    """
    def __init__(self, workdir, log_name, html_name):
        """
        :param workdir:     work directory
        :param log_name:    log name
        :param html_name:   html name
        """
        target_id = input(dataload.SHELLHEAD
                    + 'target crawl illustrator pixiv-id: ')
        self.user_input_id = target_id
        self.workdir = workdir + 'illustrepo_' + self.user_input_id
        self.logpath = self.workdir + log_name
        self.htmlpath = self.workdir + html_name

    @staticmethod
    def gather_preloadinfo(illust_id):
        """
        crawler need to know how many images do you want
        :param illust_id:   illustrator id
        :return:            request images count
        """
        # get illust artwork whole count mainpage url
        cnt_url = dataload.MEMBER_ILLUST_URL + illust_id
        response = pvmx.opener.open(fullurl=cnt_url,
                                    data=pvmx.getway_data,
                                    timeout=30)
        web_src = response.read().decode("UTF-8", "ignore")

        # mate illustrator name
        illust_name_pattern = re.compile(dataload.ILLUST_NAME_REGEX, re.S)
        arthor_names = re.findall(illust_name_pattern, web_src)
        # if login failed, this step will raise an error
        arthor_name = None
        if len(arthor_names) == 0:
            print(dataload.SHELLHEAD + "login failed, please check method call")
            exit()
        else:
            arthor_name = arthor_names[0]

        # mate max count
        pattern = re.compile(dataload.REPO_WHOLE_NUMBER_REGEX, re.S)
        max_cntword = re.findall(pattern, web_src)[1][:-1]
        max_cnt = int(max_cntword)

        return max_cnt, arthor_name

    @staticmethod
    def crawl_onepage_data(illust_id, array, log_path):
        """
        crawl all target url about images
        page request regular:
        no.1 referer: &type=all request url: &type=all&p=2
        no.2 referer: &type=all&p=2 request url: &type=all&p=3
        no.3 referer: &type=all&p=3 request url: &type=all&p=4
        :param self:        self class
        :param illust_id:   illustrator id
        :param array:       count cut to every 20 images from each page, they have an array
        :param log_path:    log save path
        :return:            use regex to mate web src thumbnail images url
        """
        step1url = dataload.MEMBER_ILLUST_URL + illust_id + dataload.TYPE_ALL_WORD
        if array == 1:
            urlTarget = step1url
        elif array == 2:
            urlTarget = step1url + dataload.PAGE_NUM_WORD + str(array)
        else:
            urlTarget = step1url + dataload.PAGE_NUM_WORD + str(array)
        response = pvmx.opener.open(fullurl=urlTarget,
                                    data=pvmx.getway_data,
                                    timeout=30)
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = "mainpage %d response successed" % array
        else:
            log_context = "mainpage %d response timeout, failed" % array
        pvmx.logprowork(log_path, log_context)
        # each page cut thumbnail image url
        web_src = response.read().decode("UTF-8", "ignore")

        # size info in webpage source
        imgitem_pattern = re.compile(dataload.IMAGEITEM_REGEX, re.S)
        image_name_pattern = re.compile(dataload.IMAGE_NAME_REGEX, re.S)
        sizer_result = pvmx.data_sizer(imgitem_pattern, image_name_pattern, web_src)
        target_urls = sizer_result[0]
        image_names = sizer_result[1]

        log_context = "mainpage %d data gather finished" % array
        pvmx.logprowork(log_path, log_context)

        return target_urls, image_names

    def crawl_allpage_target(self, illust_id, nbr, arthor_name, log_path):
        """
        package all gather url
        :param self:        self class
        :param illust_id:   illustrator id
        :param nbr:         package images count
        :param arthor_name: arthor name
        :param log_path:    log save path
        :return:            build original images urls list
        """
        # calcus nbr need request count
        if nbr <= 20:
            need_pagecnt = 1                                        # nbr <= 20, request once
        else:
            need_pagecnt = int(nbr / 20) + 1                        # only need integer

        # gather all data(thumbnail images and names)
        all_targeturls = []
        all_artworknames = []
        for i in range(need_pagecnt):
            data_capture = self.crawl_onepage_data(illust_id, i + 1, log_path)
            all_targeturls += data_capture[0]
            all_artworknames += data_capture[1]
        # collection target count
        alive_targetcnt = len(all_targeturls)

        # input want image count
        nbr_capture = int(input(dataload.SHELLHEAD
                + 'gather all repo %d, whole target(s): %d, enter you want count: ' % (nbr, alive_targetcnt)))
        # count error
        while (nbr_capture > alive_targetcnt) or (nbr_capture <= 0):
            nbr_capture = int(input(dataload.SHELLHEAD
                + 'error, input count must <= %d and not 0: ' % alive_targetcnt))
        log_context = "check crawl illustrator id:" + self.user_input_id + " image(s):%d" % nbr_capture
        pvmx.logprowork(log_path, log_context)

        artwork_ids = []                                            # images id list
        target_capture = []
        basepages = []                                              # image basic page
        for i in all_targeturls[:nbr_capture]:
            target_capture.append(i)                                # cut need count
            img_id = i[57:-7]
            artwork_ids.append(img_id)                              # image id list
            basepage = dataload.BASEPAGE_URL + img_id
            basepages.append(basepage)                              # basic page list
        # log images info
        log_context = 'illustrator: ' + arthor_name + ' id: ' + self.user_input_id + ' artworks info====>'
        pvmx.logprowork(log_path, log_context)

        for k, i in enumerate(all_artworknames[:nbr_capture]):
            log_context = 'no.%d image: [%s | id: %s | url: %s]' % ((k + 1), i, artwork_ids[k], target_capture[k])
            pvmx.logprowork(log_path, log_context)

        return target_capture, basepages

    def start(self):
        """
        include this class run logic
        :return:    none
        """
        pvmx.mkworkdir(self.logpath, self.workdir)
        pvmx.camouflage_login(self.logpath)

        info = self.gather_preloadinfo(self.user_input_id)
        web_bias = self.crawl_allpage_target(self.user_input_id, info[0], info[1], self.logpath)

        pvmx.download_alltarget(web_bias[0], web_bias[1], self.workdir, self.logpath)
        pvmx.htmlpreview_build(self.workdir, self.htmlpath, self.logpath)
        pvmx.work_finished(self.logpath)

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
