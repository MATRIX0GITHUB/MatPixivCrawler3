#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to create a private library use in this crawler

import urllib.request, urllib.parse, urllib.error, http.cookiejar
from bs4 import BeautifulSoup
from retrying import retry
import threading
from PIL import Image
from collections import OrderedDict
import time, random, re, os
import dataload

# global var init value
proxyHascreated = False
allDownloadpool = 0

class Matrix:
    """
    #####################################################################################################################################
    #    ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗██╗██╗   ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗ ██████╗   #
    #    ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝██║██║   ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗╚════██╗  #
    #    ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ ██║██║   ██║██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝ █████╔╝  #
    #    ██║╚██╔╝██║██╔══██║   ██║   ██╔═══╝ ██║ ██╔██╗ ██║╚██╗ ██╔╝██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗ ╚═══██╗  #
    #    ██║ ╚═╝ ██║██║  ██║   ██║   ██║     ██║██╔╝ ██╗██║ ╚████╔╝ ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║██████╔╝  #
    #    ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝   #
    #                                                                                                                                   #
    #    Copyright (c) 2017 @T.WKVER </MATRIX> Neod Anderjon(LeaderN)                                                                   #
    #    Version: 1.2.0 LTE                                                                                                             #
    #    Code by </MATRIX>@Neod Anderjon(LeaderN)                                                                                       #
    #    MatPixivCrawler Help Page                                                                                                      #
    #    1.rtn  ---     RankingTopN, crawl Pixiv daily/weekly/month rank top N artwork(s)                                               #
    #    2.ira  ---     illustRepoAll, crawl Pixiv any illustrator all artwork(s)                                                       #
    #    help   ---     print this help page                                                                                            #
    #####################################################################################################################################
    """
    def __init__(self):
        # from first login save cookie and create global opener
        self.getData = dataload.loginData[2]                        # request images and pages GET way
        self.cookie = http.cookiejar.LWPCookieJar()                 # create a cookie words
        self.cookieHandler = urllib.request.HTTPCookieProcessor(self.cookie) # add http cookie words
        self.opener = urllib.request.build_opener(self.cookieHandler) # build the opener
        urllib.request.install_opener(self.opener)                  # install it

    @staticmethod
    def logprowork(logpath, savecontent):
        """
        universal work log save
        :param logpath:     log save path
        :param savecontent: log save content
        :return:            none
        """
        # this log file must be a new file
        logFile = open(logpath, 'a+', encoding='utf-8')             # add context to file option 'a+'
        print(dataload.SHELLHEAD + savecontent)                     # with shell header
        print(dataload.SHELLHEAD + savecontent, file=logFile)       # write to log

    def mkworkdir(self, logpath, folder):
        """
        create a crawler work directory
        :param self:    self class
        :param logpath: log save path
        :param folder:  folder create path
        :return:        folder create path
        """
        # create a folder to save picture
        print(dataload.SHELLHEAD + 'crawler work directory setting: ' + folder)
        isFolderExisted = os.path.exists(folder)
        if not isFolderExisted:
            os.makedirs(folder)
            logContext = 'folder create successed'
        else:
            logContext = 'the folder has already existed'
        # remove old log file
        if os.path.exists(logpath):
            os.remove(logpath)
        # this step will create a new log file
        self.logprowork(logpath, logContext)

        return folder

    def getproxyserver(self, logpath):
        """
        catch a proxy server when crwaler crawl many times website forbidden host ip
        :param logpath: log save path
        :return:        proxy server, add to opener
        """
        req_ps_url = dataload.proxyServerRequestURL
        psHeaders = dataload.ucUserAgent()
        request = urllib.request.Request(url=req_ps_url,
                                        headers=psHeaders)
        response = urllib.request.urlopen(request,
                                          timeout=30)
        proxyRawwords = []
        if response.getcode() == dataload.reqSuccessCode:
            logContext = 'crawl proxy successed'
            web_src = response.read().decode("UTF-8", "ignore")
            proxyRawwords = BeautifulSoup(web_src, 'lxml').find_all('tr') # mate tr tag class
        else:
            logContext = 'crawl proxy failed, return code: %d' % response.getcode()
        self.logprowork(logpath, logContext)
        ip_list = []
        for i in range(1, len(proxyRawwords)):
            ip_info = proxyRawwords[i]
            tds = ip_info.find_all('td')                            # mate td tag class
            # build a format: ip:port
            ip_list.append('http://' + tds[1].text + ':' + tds[2].text)

        proxy_ip = random.choice(ip_list)                           # random choose a proxy
        proxyServer = {'http': proxy_ip}                            # setting proxy server
        logContext = 'choose proxy server: ' + proxy_ip
        self.logprowork(logpath, logContext)

        return proxyServer

    def gatherpostkey(self, logpath):
        """
        POST way login need post-key
        :return:    post way request data
        """
        # request a post key
        response = self.opener.open(dataload.postKeyGeturl, timeout=30)
        if response.getcode() == dataload.reqSuccessCode:
            logContext = 'post-key response successed'
        else:
            logContext = 'post-key response failed, return code: %d' % response.getcode()
        self.logprowork(logpath, logContext)
        # cookie check
        for item in self.cookie:
            logContext = 'cookie: [name:' + item.name + '-value:' + item.value + ']'
            self.logprowork(logpath, logContext)
        # mate post key
        web_src = response.read().decode("UTF-8", "ignore")
        postPattern = re.compile(dataload.postKeyRegex, re.S)
        postKey = re.findall(postPattern, web_src)[0]
        logContext = 'get post-key: ' + postKey
        self.logprowork(logpath, logContext)

        # build basic dict
        postTabledict = OrderedDict()                               # this post data must has a order
        postTabledict['pixiv_id'] = dataload.loginData[0]
        postTabledict['password'] = dataload.loginData[1]
        postTabledict['captcha'] = ""
        postTabledict['g_recaptcha_response'] = ""
        postTabledict['post_key'] = postKey
        postTabledict['source'] = "pc"
        postTabledict['ref'] = dataload.login_ref
        postTabledict['return_to'] = dataload.hostWebURL
        # transfer to json data format
        post_data = urllib.parse.urlencode(postTabledict).encode("UTF-8")

        return post_data

    def camouflage_login(self, logpath):
        """
        camouflage browser to login
        :param logpath: log save path
        :return:        none
        """
        # login init need to commit post data to Pixiv
        postData = self.gatherpostkey(logpath)                      # get post-key and build post-data
        response = self.opener.open(fullurl=dataload.originHost,
                                    data=postData,
                                    timeout=40)
        # first must login to website then can request page
        if response.getcode() == dataload.reqSuccessCode:
            logContext = 'login response successed'
        else:
            logContext = 'login response fatal, return code %d' % response.getcode()
        self.logprowork(logpath, logContext)

    def save_test_html(self, workdir, content, logpath):
        """
        save request web source page in a html file, test use
        :param workdir: work directory
        :param content: save content
        :param logpath: log save path
        :return:        none
        """
        htmlfile = open(workdir + dataload.storage[1] + 'test.html', "w")
        htmlfile.write(content)
        htmlfile.close()
        logContext = 'save request html page ok'
        self.logprowork(logpath, logContext)

    @staticmethod
    def data_sizer(wholePattern, infoPattern, web_src):
        """
        a sizer for all of imags in a pages
        :param wholePattern:    whole info data regex compile pattern
        :param infoPattern:     image info regex compile pattern
        :param web_src:         webpage source
        :return:                original target urls, image infos
        """
        infoGroup = []
        urlGroup = []
        datasrcPattern = re.compile(dataload.datasrcRegex, re.S)
        spanPattern = re.compile(dataload.imgSpancnt, re.S)
        imgWholeInfo = re.findall(wholePattern, web_src)
        # image have 3 format: jpg/png/gif
        # this crawler will give gif format up and crawl png or jpg
        # pixiv one repo maybe have multi-images
        for item in imgWholeInfo:
            thumbnail = re.findall(datasrcPattern, item)[0]         # mate thumbnail image
            judgeWord = thumbnail[-18:]                             # _p0_master1200.jpg
            # check jpg/png or gif
            if judgeWord == dataload.judgeWord:
                span_nbr = re.findall(spanPattern, item)
                # catch vaild word from thumbnail url
                vaildWord = thumbnail[44:-18]                       # cut vaild words
                # try to check multi-span images
                if len(span_nbr) != 0:                              # non-empty list
                    for p in range(int(span_nbr[0])):
                        # gather image info
                        info = re.findall(infoPattern, item)[0]
                        infoGroup.append(info)
                        # build original image url
                        target_url = dataload.imgOriginalheader + vaildWord + dataload.imgOriginaltail(p)
                        urlGroup.append(target_url)
                else:
                    # gather image info
                    info = re.findall(infoPattern, item)[0]
                    infoGroup.append(info)
                    # build original image url
                    target_url = dataload.imgOriginalheader + vaildWord + dataload.imgOriginaltail(0)
                    urlGroup.append(target_url)
            # give up gif format
            else:
                pass

        return urlGroup, infoGroup

    @retry
    def save_oneimage(self, index, url, basepages, savepath, logpath):
        """
        download one target image, then multi-process will call here
        add retry decorator, if first try failed, it will auto-retry
        :param index:       image index
        :param url:         image urls list
        :param basepages:   referer basic pages list
        :param savepath:    image save path
        :param logpath:     log save path
        :return:            none
        """
        # set images download arguments
        global allDownloadpool                                      # whole download pool
        global proxyHascreated
        timeout = 30                                                # default set to 30s
        imgDatatype = 'png'                                         # default png format
        image_name = url[57:-4]                                     # id+_px

        # preload proxy, just once
        proxy_handler = None
        if proxyHascreated is False:
            proxyHascreated = True                                  # no reset
            proxy = self.getproxyserver(logpath)
            proxy_handler = urllib.request.ProxyHandler(proxy)

        # setting headers
        headers = dataload.build_original_headers(basepages[index])
        list_headers = dataload.dict_transto_list(headers)
        self.opener.addheaders = list_headers
        urllib.request.install_opener(self.opener)                  # must install new
        response = None

        try:
            response = self.opener.open(fullurl=url,
                                        timeout=timeout)
        # timeout or image data type error
        except urllib.error.HTTPError as e:
            ## logContext = str(e.code)
            ## self.logprowork(logpath, logContext)

            # http error 404, change image type
            if e.code == dataload.reqNotFound:
                imgDatatype = 'jpg'                                 # change data type
                changeToJPGurl = url[0:-3] + imgDatatype
                try:
                    response = self.opener.open(fullurl=changeToJPGurl,
                                                timeout=timeout)
                except urllib.error.HTTPError as e:
                    ## logContext = str(e.code)
                    ## self.logprowork(logpath, logContext)

                    # not 404 change proxy, cause request server forbidden crawler
                    if e.code != dataload.reqNotFound:
                        # if timeout, use proxy reset request
                        logContext = "change proxy server"
                        self.logprowork(logpath, logContext)
                        self.opener = urllib.request.build_opener(proxy_handler) # add proxy handler
                        response = self.opener.open(fullurl=changeToJPGurl,
                                                    timeout=timeout)
                    else:
                        pass
            # if timeout, use proxy reset request
            else:
                logContext = "change proxy server"
                self.logprowork(logpath, logContext)
                self.opener = urllib.request.build_opener(proxy_handler) # add proxy handler
                response = self.opener.open(fullurl=url,
                                            timeout=timeout)
        # save request bin data file
        if response.getcode() == dataload.reqSuccessCode:
            # save response data to image format
            imgBindata = response.read()
            sourceSize = float(len(imgBindata) / 1024)              # get image size
            allDownloadpool += sourceSize                           # calcus download source whole size
            logContext = 'capture target no.%d image ok, image size: %dKB' % (index + 1, sourceSize)
            self.logprowork(logpath, logContext)
            # this step will delay much time
            with open(savepath + dataload.storage[1] + image_name + '.' + imgDatatype, 'wb') as img:
                img.write(imgBindata)
            logContext = 'download no.%d image finished' % (index + 1)
            self.logprowork(logpath, logContext)

    class MultiThreading(threading.Thread):
        """
        overrides its run method by inheriting the Thread class
        this class can be placed outside the main class, you can also put inside
        threads are the smallest unit of program execution flow that is less burdensome than process creation
        """
        def __init__(self, lock, i, img_url, base_pages, imgPath, logPath):
            """
            commit class arguments
            :param lock:        object lock
            :param i:           image index
            :param img_url:     image url
            :param base_pages:  referer basic page
            :param imgPath:     image save path
            :param logPath:     log save path
            """
            # callable class init
            threading.Thread.__init__(self)
            # arguments transfer to global
            self.lock = lock
            self.i = i
            self.img_url = img_url
            self.base_pages = base_pages
            self.imgPath = imgPath
            self.logPath = logPath

        def run(self):
            """
            overwrite threading.thread run() method
            :return:    none
            """
            # cancel lock release will let multi-process change to easy process
            ## self.lock.acquire()
            Matrix().save_oneimage(self.i, self.img_url, self.base_pages, self.imgPath, self.logPath)
            ## self.lock.release()

    def download_alltarget(self, urls, base_pages, workdir, logpath):
        """
        multi-process download all image
        test speed: daily-rank top 50 whole crawl elapsed time 1min
        :param urls:        all original images urls
        :param base_pages:  all referer basic pages
        :param workdir:     work directory
        :param logpath:     log save path
        :return:            none
        """
        queueLength = len(urls)
        logContext = 'start to download %d target(s)======>' % queueLength
        self.logprowork(logpath, logContext)

        lock = threading.Lock()                                     # object lock
        sub_thread = None
        aliveThreadCnt = queueLength                                # init value
        for i, img_url in enumerate(urls):
            # create overwrite threading.Thread object
            sub_thread = self.MultiThreading(lock, i, img_url, base_pages, workdir, logpath)
            sub_thread.setDaemon(False)                             # set every download sub-process is non-daemon process
            sub_thread.start()                                      # start download
            time.sleep(0.1)                                         # confirm thread has been created, delay cannot too long
        # parent thread wait all sub-thread end
        while aliveThreadCnt > 1:                                   # finally only parent process
            sub_thread.join()                                       # parent thread wait sub-threads over
            time.sleep(3)
            aliveThreadCnt = threading.active_count()
            logContext = 'currently remaining sub-thread(s): %d/%d' % (aliveThreadCnt - 1, queueLength)
            self.logprowork(logpath, logContext)
        logContext = 'all of threads reclaim, download process end'
        self.logprowork(logpath, logContext)

    def htmlpreview_build(self, workdir, htmlpath, logpath):
        """
        build a html file to browse image
        :param self:        class self
        :param workdir:     work directory
        :param htmlpath:    html file save path
        :param logpath:     log save path
        :return:            none
        """
        htmlFile = open(htmlpath, "w")                              # write html file
        # build html background page text
        htmlFile.writelines("<html>\r\n<head>\r\n<title>MatPixivCrawler3 ResultPage</title>\r\n</head>\r\n<body>\r\n")
        htmlFile.writelines("<script>window.onload = function(){"
                            "var imgs = document.getElementsByTagName('img');"
                            "for(var i = 0; i < imgs.length; i++){"
                            "imgs[i].onclick = function(){"
                            "if(this.width == this.attributes['oriWidth'].value && this.height == this.attributes['oriHeight'].value){"
                            "this.width = this.attributes['oriWidth'].value * 1.0 / this.attributes['oriHeight'].value * 200;"
                            "this.height = 200;"
                            "}else{this.width = this.attributes['oriWidth'].value ;"
                            "this.height = this.attributes['oriHeight'].value;}}}};</script>")
        for i in os.listdir(workdir):
            if i[-4:len(i)] in [".png", ".jpg", ".bmp"]:            # support image format
                width, height = Image.open(workdir + dataload.storage[1] + i).size
                i = i.replace("#", "%23")
                ## htmlFile.writelines("<a href = \"%s\">"%("./" + filename))
                # set image source line
                htmlFile.writelines(
                    "<img src = \"%s\" width = \"%dpx\" height = \"%dpx\" oriWidth = %d oriHeight = %d />\r\n"
                    % ("./" + i, width * 1.0 / height * 200, 200, width, height)) # limit display images size
                ## htmlFile.writelines("</a>\r\n")
        # end of htmlfile
        htmlFile.writelines("</body>\r\n</html>")
        htmlFile.close()
        logContext = 'image browse html generate finished'
        self.logprowork(logpath, logContext)

    def work_finished(self, elapsedTime, logpath):
        """
        work finished log
        :param elapsedTime: elapsed time
        :param logpath:     log save path
        :return:            none
        """
        # calcus average download speed and whole elapesd time
        global allDownloadpool
        averageDownloadSpeed = float(allDownloadpool / elapsedTime)
        logContext = "elapsed time: %0.2fs, average download speed: %0.2fKB/s" % (elapsedTime, averageDownloadSpeed)
        self.logprowork(logpath, logContext)

        # end time log
        rtc = time.localtime()                                      # real log get
        ymdhms = '%d-%d-%d %d:%d:%d' % (rtc[0], rtc[1], rtc[2], rtc[3], rtc[4], rtc[5])
        logContext = "crawler work finished, log time: " + ymdhms
        self.logprowork(logpath, logContext)

        # logo display
        logContext = \
            dataload.__laboratory__ + ' ' + dataload.__organization__ \
            + ' technology support\n'                                   \
            'Code by ' + dataload.__organization__ + '@' + dataload.__author__

        # open work directory, check result
        self.logprowork(logpath, logContext)
        os.system(dataload.storage[2] + ' ' + dataload.storage[0])

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
