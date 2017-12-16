#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to create a private library use in this crawler

import urllib.request, urllib.parse, urllib.error, http.cookiejar
from retrying import retry
import threading
from PIL import Image
from collections import OrderedDict
import time, random, re, os
import dataload

# global var init value
_PROXY_HASRUN_FLAG = False
_DOWNLOAD_POOL = 0

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
    #    Version: 1.5.0 LTE                                                                                                             #
    #    Code by </MATRIX>@Neod Anderjon(LeaderN)                                                                                       #
    #    MatPixivCrawler Help Page                                                                                                      #
    #    1.rtn  ---     RankingTopN, crawl Pixiv daily/weekly/month rank top N artwork(s)                                               #
    #    2.ira  ---     illustRepoAll, crawl Pixiv any illustrator all artwork(s)                                                       #
    #    help   ---     print this help page                                                                                            #
    #####################################################################################################################################
    """
    def __init__(self):
        # from first login save cookie and create global opener
        # call this opener must write parameter name
        self.getway_data = dataload.login_data_l[2]                        # request images and pages GET way
        self.cookie = http.cookiejar.LWPCookieJar()                 # create a cookie words
        self.cookieHandler = urllib.request.HTTPCookieProcessor(self.cookie) # add http cookie words
        self.opener = urllib.request.build_opener(self.cookieHandler) # build the opener
        urllib.request.install_opener(self.opener)                  # install it

    @staticmethod
    def logprowork(logpath, logcontent):
        """
        universal work log save
        :param logpath:     log save path
        :param logcontent: log save content
        :return:            none
        """
        # this log file must be a new file
        logFile = open(logpath, 'a+', encoding='utf-8')             # add context to file option 'a+'
        print(dataload.SHELLHEAD + logcontent)
        print(dataload.SHELLHEAD + logcontent, file=logFile)        # write into file

    def mkworkdir(self, log_path, folder):
        """
        create a crawler work directory
        :param self:    self class
        :param log_path: log save path
        :param folder:  folder create path
        :return:        folder create path
        """
        # create a folder to save picture
        print(dataload.SHELLHEAD + 'crawler work directory setting: ' + folder)
        is_folder_existed = os.path.exists(folder)
        if not is_folder_existed:
            os.makedirs(folder)
            log_context = 'folder create successed'
        else:
            log_context = 'the folder has already existed'
        # remove old log file
        if os.path.exists(log_path):
            os.remove(log_path)
        # this step will create a new log file
        self.logprowork(log_path, log_context)

        return folder

    def _getproxyserver(self, log_path):
        """
        catch a proxy server when crwaler crawl many times website forbidden host ip
        :param log_path: log save path
        :return:        proxy server, add to opener
        """
        req_ps_url = dataload.PROXYSERVER_URL
        ps_headers = dataload.uc_user_agent()
        request = urllib.request.Request(url=req_ps_url,
                                        headers=ps_headers)
        response = urllib.request.urlopen(request,
                                          timeout=30)

        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'crawl proxy successed'
        else:
            log_context = 'crawl proxy failed, return code: %d' % response.getcode()
        self.logprowork(log_path, log_context)

        web_src = response.read().decode("UTF-8", "ignore")
        proxy_pattern = re.compile(dataload.PROXYIP_REGEX, re.S)
        proxy_rawwords = re.findall(proxy_pattern, web_src)
        proxy_iplist = []
        for i in range(len(proxy_rawwords)):
            if i % 5 == 0 and proxy_rawwords[i].isdigit():           # analysis port num
                # build proxy ip string
                proxy_ip = dataload.PROXYIP_STR_BUILD(i, proxy_rawwords)
                proxy_iplist.append(proxy_ip)
            else:
                pass
        proxy_choose = random.choice(proxy_iplist)                  # random choose a proxy
        proxy_server = {'http': proxy_choose}                       # setting proxy server

        log_context = 'choose proxy server: ' + proxy_choose
        self.logprowork(log_path, log_context)

        return proxy_server

    def _gatherpostkey(self, log_path):
        """
        POST way login need post-key
        :return:    post way request data
        """
        # request a post key
        response = self.opener.open(dataload.LOGIN_POSTKEY_URL, timeout=30)
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'post-key response successed'
        else:
            log_context = 'post-key response failed, return code: %d' % response.getcode()
        self.logprowork(log_path, log_context)
        # cookie check
        for item in self.cookie:
            log_context = 'cookie: [name:' + item.name + '-value:' + item.value + ']'
            self.logprowork(log_path, log_context)
        # mate post key
        web_src = response.read().decode("UTF-8", "ignore")
        post_pattern = re.compile(dataload.POSTKEY_REGEX, re.S)
        post_key = re.findall(post_pattern, web_src)[0]
        log_context = 'get post-key: ' + post_key
        self.logprowork(log_path, log_context)

        # build basic dict
        post_tabledict = OrderedDict()                              # this post data must has a order
        post_tabledict['pixiv_id'] = dataload.login_data_l[0]
        post_tabledict['password'] = dataload.login_data_l[1]
        post_tabledict['captcha'] = ""
        post_tabledict['g_recaptcha_response'] = ""
        post_tabledict['post_key'] = post_key
        post_tabledict['source'] = "pc"
        post_tabledict['ref'] = dataload.LOGIN_POSTDATA_REF
        post_tabledict['return_to'] = dataload.HTTPS_HOST_URL
        # transfer to json data format
        post_data = urllib.parse.urlencode(post_tabledict).encode("UTF-8")

        return post_data

    def camouflage_login(self, log_path):
        """
        camouflage browser to login
        :param log_path: log save path
        :return:        none
        """
        # login init need to commit post data to Pixiv
        post_data = self._gatherpostkey(log_path)                      # get post-key and build post-data
        response = self.opener.open(fullurl=dataload.LOGIN_REQUEST_URL,
                                    data=post_data,
                                    timeout=40)
        # first must login to website then can request page
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'login response successed'
        else:
            log_context = 'login response fatal, return code %d' % response.getcode()
        self.logprowork(log_path, log_context)

    def save_test_html(self, workdir, content, log_path):
        """
        save request web source page in a html file, test use
        :param workdir:     work directory
        :param content:     save content
        :param log_path:    log save path
        :return:            none
        """
        htmlfile = open(workdir + dataload.storage_l[1] + 'test.html', "w")
        htmlfile.write(content)
        htmlfile.close()
        log_context = 'save request html page ok'
        self.logprowork(log_path, log_context)

    @staticmethod
    def data_sizer(whole_pattern, info_pattern, web_src):
        """
        a sizer for all of imags in a pages
        :param whole_pattern:   whole info data regex compile pattern
        :param info_pattern:    image info regex compile pattern
        :param web_src:         webpage source
        :return:                original target urls, image infos
        """
        info_group_l = []
        url_group_l = []
        datasrc_pattern = re.compile(dataload.DATASRC_REGEX, re.S)
        span_pattern = re.compile(dataload.SPAN_REGEX, re.S)
        img_whole_info = re.findall(whole_pattern, web_src)
        # image have 3 format: jpg/png/gif
        # this crawler will give gif format up and crawl png or jpg
        # pixiv one repo maybe have multi-images
        for item in img_whole_info:
            thumbnail = re.findall(datasrc_pattern, item)[0]         # mate thumbnail image
            judge_word = thumbnail[-18:]                             # _p0_master1200.jpg
            # check jpg/png or gif
            if judge_word == dataload.JUDGE_NOGIF_WORD:
                span_nbr = re.findall(span_pattern, item)
                # catch vaild word from thumbnail url
                vaildWord = thumbnail[44:-18]                       # cut vaild words
                # try to check multi-span images
                if len(span_nbr) != 0:                              # non-empty list
                    for p in range(int(span_nbr[0])):
                        # gather image info
                        info = re.findall(info_pattern, item)[0]
                        info_group_l.append(info)
                        # build original image url
                        target_url = dataload.ORIGINAL_IMAGE_HEAD + vaildWord + dataload.ORIGINAL_IMAGE_TAIL(p)
                        url_group_l.append(target_url)
                else:
                    # gather image info
                    info = re.findall(info_pattern, item)[0]
                    info_group_l.append(info)
                    # build original image url
                    target_url = dataload.ORIGINAL_IMAGE_HEAD + vaildWord + dataload.ORIGINAL_IMAGE_TAIL(0)
                    url_group_l.append(target_url)
            # give up gif format
            else:
                pass

        return url_group_l, info_group_l

    @retry
    def _save_oneimage(self, index, url, basepages, img_savepath, log_path):
        """
        download one target image, then multi-process will call here
        add retry decorator, if first try failed, it will auto-retry
        :param index:           image index
        :param url:             image urls list
        :param basepages:       referer basic pages list
        :param img_savepath:    image save path
        :param log_path:        log save path
        :return:                none
        """
        # set images download arguments
        global _DOWNLOAD_POOL
        global _PROXY_HASRUN_FLAG
        proxy_handler = None
        timeout = 30                                                # default set to 30s
        img_datatype = 'png'
        image_name = url[57:-4]                                     # id+_px

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
            ## log_context = str(e.code)
            ## self.logprowork(logpath, log_context)

            # http error 404, change image type
            if e.code == dataload.HTTP_NOTFOUND_CODE_404:
                img_datatype = 'jpg'                                 # change data type
                jpg_img_url = url[0:-3] + img_datatype
                try:
                    response = self.opener.open(fullurl=jpg_img_url,
                                                timeout=timeout)
                except urllib.error.HTTPError as e:
                    ## log_context = str(e.code)
                    ## self.logprowork(logpath, log_context)

                    # not 404 change proxy, cause request server forbidden crawler
                    if e.code != dataload.HTTP_NOTFOUND_CODE_404:
                        # if timeout, use proxy reset request
                        log_context = "change proxy server"
                        self.logprowork(log_path, log_context)

                        # preload proxy, just once
                        if _PROXY_HASRUN_FLAG is False:
                            _PROXY_HASRUN_FLAG = True  # no reset
                            proxy = self._getproxyserver(log_path)
                            proxy_handler = urllib.request.ProxyHandler(proxy)
                        else:
                            pass
                        self.opener = urllib.request.build_opener(proxy_handler) # add proxy handler
                        response = self.opener.open(fullurl=jpg_img_url,
                                                    timeout=timeout)
                    else:
                        pass
            # if timeout, use proxy reset request
            else:
                log_context = "change proxy server"
                self.logprowork(log_path, log_context)
                self.opener = urllib.request.build_opener(proxy_handler) # add proxy handler
                response = self.opener.open(fullurl=url,
                                            timeout=timeout)
        # save request bin data file
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            # save response data to image format
            img_bindata = response.read()
            source_size = float(len(img_bindata) / 1024)            # get image size
            _DOWNLOAD_POOL += source_size                            # calcus download source whole size
            log_context = 'capture target no.%d image ok, image size: %dKB' % (index + 1, source_size)
            self.logprowork(log_path, log_context)
            # this step will delay much time
            with open(img_savepath + dataload.storage_l[1] + image_name + '.' + img_datatype, 'wb') as img:
                img.write(img_bindata)
            log_context = 'download no.%d image finished' % (index + 1)
            self.logprowork(log_path, log_context)

    class _MultiThreading(threading.Thread):
        """
        overrides its run method by inheriting the Thread class
        this class can be placed outside the main class, you can also put inside
        threads are the smallest unit of program execution flow that is less burdensome than process creation
        """
        def __init__(self, lock, i, img_url, basepages, img_savepath, log_path):
            """
            commit class arguments
            :param lock:            object lock
            :param i:               image index
            :param img_url:         image url
            :param basepages:       referer basic page
            :param img_savepath:    image save path
            :param log_path:        log save path
            """
            # callable class init
            threading.Thread.__init__(self)
            # arguments transfer to global
            self.lock = lock
            self.i = i
            self.img_url = img_url
            self.base_pages = basepages
            self.imgPath = img_savepath
            self.logPath = log_path

        def run(self):
            """
            overwrite threading.thread run() method
            :return:    none
            """
            # cancel lock release will let multi-process change to easy process
            ## self.lock.acquire()
            Matrix()._save_oneimage(self.i, self.img_url, self.base_pages, self.imgPath, self.logPath)
            ## self.lock.release()

    def download_alltarget(self, urls, basepages, workdir, log_path):
        """
        multi-process download all image
        test speed: daily-rank top 50 whole crawl elapsed time 1min
        :param urls:        all original images urls
        :param basepages:   all referer basic pages
        :param workdir:     work directory
        :param log_path:    log save path
        :return:            none
        """
        global _DOWNLOAD_POOL
        queueLength = len(urls)
        log_context = 'start to download %d target(s)======>' % queueLength
        self.logprowork(log_path, log_context)

        lock = threading.Lock()                                     # object lock
        sub_thread = None
        aliveThreadCnt = queueLength                                # init value
        starttime = time.time()                                     # log download elapsed time
        for i, img_url in enumerate(urls):
            # create overwrite threading.Thread object
            sub_thread = self._MultiThreading(lock, i, img_url, basepages, workdir, log_path)
            sub_thread.setDaemon(False)                             # set every download sub-process is non-daemon process
            sub_thread.start()                                      # start download
            time.sleep(0.1)                                         # confirm thread has been created, delay cannot too long
        # parent thread wait all sub-thread end
        while aliveThreadCnt > 1:                                   # finally only parent process
            sub_thread.join()                                       # parent thread wait sub-threads over
            time.sleep(3)
            aliveThreadCnt = threading.active_count()
            log_context = 'currently remaining sub-thread(s): %d/%d' % (aliveThreadCnt - 1, queueLength)
            self.logprowork(log_path, log_context)
        # calcus average download speed and whole elapesd time
        endtime = time.time()
        elapesd_time = endtime - starttime
        average_download_speed = float(_DOWNLOAD_POOL / elapesd_time)
        log_context = "all of threads reclaim, elapsed time: %0.2fs, " \
                     "average download speed: %0.2fKB/s" % (elapesd_time, average_download_speed)
        self.logprowork(log_path, log_context)

    def htmlpreview_build(self, workdir, html_path, log_path):
        """
        build a html file to browse image
        :param self:        class self
        :param workdir:     work directory
        :param html_path:   html file save path
        :param log_path:    log save path
        :return:            none
        """
        html_file = open(html_path, "w")                            # write html file
        # build html background page text
        html_file.writelines("<html>\r\n<head>\r\n<title>MatPixivCrawler3 ResultPage</title>\r\n</head>\r\n<body>\r\n")
        html_file.writelines("<script>window.onload = function(){"
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
                width, height = Image.open(workdir + dataload.storage_l[1] + i).size
                i = i.replace("#", "%23")
                ## html_file.writelines("<a href = \"%s\">"%("./" + filename))
                # set image source line
                html_file.writelines(
                    "<img src = \"%s\" width = \"%dpx\" height = \"%dpx\" oriWidth = %d oriHeight = %d />\r\n"
                    % ("./" + i, width * 1.0 / height * 200, 200, width, height)) # limit display images size
                ## html_file.writelines("</a>\r\n")
        # end of htmlfile
        html_file.writelines("</body>\r\n</html>")
        html_file.close()
        log_context = 'image browse html generate finished'
        self.logprowork(log_path, log_context)

    def work_finished(self, log_path):
        """
        work finished log
        :param log_path:     log save path
        :return:            none
        """
        # end time log
        rtc = time.localtime()                                      # real log get
        ymdhms = '%d-%d-%d %d:%d:%d' % (rtc[0], rtc[1], rtc[2], rtc[3], rtc[4], rtc[5])
        log_context = "crawler work finished, log time: " + ymdhms
        self.logprowork(log_path, log_context)

        # logo display
        log_context = \
            dataload.LABORATORY + ' ' + dataload.ORGANIZATION \
            + ' technology support\n'                                   \
            'Code by ' + dataload.ORGANIZATION + '@' + dataload.DEVELOPER

        # open work directory, check result
        self.logprowork(log_path, log_context)
        os.system(dataload.storage_l[2] + ' ' + dataload.storage_l[0])

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
