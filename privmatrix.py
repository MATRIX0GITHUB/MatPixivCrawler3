#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this python script is built to collect all use lib into a class

import urllib.request, urllib.parse, urllib.error, http.cookiejar
from retrying import retry
import threading
from PIL import Image
from collections import OrderedDict
import time, random, re, os, getpass, linecache
import dataload

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
    #    Version: 2.0.0 LTE                                                                                                             #
    #    Code by </MATRIX>@Neod Anderjon(LeaderN)                                                                                       #
    #    MatPixivCrawler3 Help Page                                                                                                     #
    #    1.rtn  ---     RankingTopN, crawl Pixiv daily/weekly/month ranking top artworks                                                #
    #    2.ira  ---     illustRepoAll, crawl Pixiv any illustrator all repertory artworks                                               #
    #    3.help ---     print this help page                                                                                            #
    #####################################################################################################################################
    """

    # init class variable
    login_bias = []                 # login data: username, passwd, getway_data, agree public call
    _proxy_hasrun_flag = False      # create proxy handler once flag, only class internal call
    _datastream_pool = 0            # download data-stream(KB) whole pool, only class internal call
    _alivethread_counter = 0        # multi-thread alive sub-threads count, only class internal call

    def __init__(self):
        """Create a class public call webpage opener with cookie

        From first login save cookie and continue call
        Call this global opener must write parameter name
        Cookie, cookiehandler, opener all can inherit and call
        """
        self.cookie = http.cookiejar.LWPCookieJar()
        self.cookieHandler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.cookieHandler)
        urllib.request.install_opener(self.opener)

    @staticmethod
    def _login_preload(logincr_path):
        """Get user input username and password

        login.cr file example:
        =================================
        [login]
        <mail>
        <passwd>
        =================================
        :param logincr_path:    login.cr file path
        :return:                username, password, get data
        """
        is_login_file_existed = os.path.exists(logincr_path)
        if is_login_file_existed:
            # read two row content
            user_mailbox = linecache.getline(logincr_path, 2)
            user_password = linecache.getline(logincr_path, 3)
            # empty file
            if user_mailbox == '' or user_password == '':
                dataload.SBH_PRINT(
                    "login.cr file invaild, please input your login info")
                user_mailbox = dataload.SBH_INPUT(
                    'enter your pixiv id(mailbox), must be a R18: ')
                # pycharm python console not support getpass input
                user_password = getpass.getpass(
                    dataload.SHELL_BASHHEAD + 'enter your account password: ')
            else:
                check = dataload.SBH_INPUT(
                    "please check your info:\n"
                    "[!]    username: %s[!]    password: %s"
                    "Yes or No?: "
                    % (user_mailbox, user_password))
                # user judge info are error
                if (check != 'yes' and check != 'Yes'
                    and check != 'YES' and check != 'y' and check != 'Y'):
                    dataload.SBH_PRINT(
                        "you can write new info")
                    user_mailbox = dataload.SBH_INPUT(
                        'enter your pixiv id(mailbox), must be a R18: ')
                    user_password = getpass.getpass(
                        dataload.SHELL_BASHHEAD + 'enter your account password: ')
                else:
                    pass
        # no login.cr file
        else:
            dataload.SBH_PRINT(
                "cannot find login.cr file, please input your login info")
            user_mailbox = dataload.SBH_INPUT(
                'enter your pixiv id(mailbox), must be a R18: ')
            user_password = getpass.getpass(
                dataload.SHELL_BASHHEAD + 'enter your account password: ')

        # strip() delete symbol '\n'
        username = user_mailbox.strip()
        passwd = user_password.strip()

        getway_reg_info = [('user', username), ('pass', passwd)]
        getway_data \
            = urllib.parse.urlencode(getway_reg_info).encode(encoding='UTF8')

        # return login need 3 elements
        return username, passwd, getway_data

    @staticmethod
    def logprowork(log_path, log_content):
        """Universal work log save

        :param log_path:    log save path
        :param log_content: log save content
        :return:            none
        """
        # add context to file option 'a+'
        log_filepath = open(log_path, 'a+', encoding='utf-8')
        dataload.SBH_PRINT(log_content)
        print(dataload.SHELL_BASHHEAD + log_content, file=log_filepath)

    def mkworkdir(self, log_path, folder):
        """Create a crawler work directory

        :param self:    self class
        :param log_path: log save path
        :param folder:  folder create path
        :return:        folder create path
        """
        # create a folder to save picture
        dataload.SBH_PRINT(
            'crawler work directory setting: ' + folder)
        is_folder_existed = os.path.exists(folder)
        if not is_folder_existed:
            os.makedirs(folder)
            log_context = 'folder create successed'
        else:
            log_context = 'the folder has already existed'
        # remove old log file
        if os.path.exists(log_path):
            os.remove(log_path)
        # this step will create a new log file and write the first line
        self.logprowork(log_path, log_context)

    def _getproxyserver(self, log_path):
        """Catch a proxy server

        when crwaler crawl many times website forbidden host ip
        :param log_path: log save path
        :return:        proxy server, add to opener
        """
        req_ps_url = dataload.PROXYSERVER_URL
        ps_headers = dataload.uc_user_agent()
        request = urllib.request.Request(
            url=req_ps_url,
            headers=ps_headers)
        try:
            response = urllib.request.urlopen(
                request,
                timeout=30)
        except Exception as e:
            log_context = str(e) + " request proxy website failed"
            self.logprowork(log_path, log_context)
            response = None
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'crawl proxy successed'
        else:
            log_context = 'crawl proxy failed, return code: %d' \
                          % response.getcode()
        self.logprowork(log_path, log_context)

        web_src = response.read().decode("UTF-8", "ignore")
        proxy_pattern = re.compile(dataload.PROXYIP_REGEX, re.S)
        proxy_rawwords = re.findall(proxy_pattern, web_src)

        # catch key words in web source
        proxy_iplist = []
        for i in range(len(proxy_rawwords)):
            if i % 5 == 0 and proxy_rawwords[i].isdigit():
                # build proxy ip string
                proxy_ip = dataload.PROXYIP_STR_BUILD(i, proxy_rawwords)
                proxy_iplist.append(proxy_ip)
            else:
                pass
        # random choose a proxy ip and port
        proxy_choose = random.choice(proxy_iplist)
        proxyserver_d = {'http': proxy_choose}

        log_context = 'choose proxy server: ' + proxy_choose
        self.logprowork(log_path, log_context)

        return proxyserver_d

    def _gatherpostkey(self, log_path):
        """POST way login need post-key

        :param log_path:    log save path
        :return:            post way request data
        """
        Matrix.login_bias = self._login_preload(dataload.LOGINCR_PATH)
        # request a post key
        try:
            response = self.opener.open(
                dataload.LOGIN_POSTKEY_URL,
                timeout=30)
        except Exception as e:
            log_context = str(e) + " request post-key failed"
            self.logprowork(log_path, log_context)
            response = None
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'post-key response successed'
        else:
            log_context = 'post-key response failed, return code: %d' \
                          % response.getcode()
        self.logprowork(log_path, log_context)

        # cookie check
        for item in self.cookie:
            log_context = \
                'cookie: [name:' + item.name + '-value:' + item.value + ']'
            self.logprowork(log_path, log_context)

        # mate post key
        web_src = response.read().decode("UTF-8", "ignore")
        post_pattern = re.compile(dataload.POSTKEY_REGEX, re.S)
        postkey = re.findall(post_pattern, web_src)[0]
        log_context = 'get post-key: ' + postkey
        self.logprowork(log_path, log_context)

        # build post-way data order dict
        post_orderdict = OrderedDict()
        post_orderdict['pixiv_id'] = Matrix.login_bias[0]
        post_orderdict['password'] = Matrix.login_bias[1]
        post_orderdict['captcha'] = ""
        post_orderdict['g_recaptcha_response'] = ""
        post_orderdict['post_key'] = postkey
        post_orderdict['source'] = "pc"
        post_orderdict['ref'] = dataload.LOGIN_POSTDATA_REF
        post_orderdict['return_to'] = dataload.HTTPS_HOST_URL

        # transfer to json data format
        postway_data = urllib.parse.urlencode(post_orderdict).encode("UTF-8")

        return postway_data

    def camouflage_login(self, log_path):
        """Camouflage browser to login

        :param log_path: log save path
        :return:        none
        """
        # login init need to commit post data to Pixiv
        postway_data = self._gatherpostkey(log_path)
        # the most important step
        try:
            response = self.opener.open(
                fullurl=dataload.LOGIN_REQUEST_URL,
                data=postway_data,
                timeout=30)
        except Exception as e:
            log_context = str(e) + " login timeout failed"
            self.logprowork(log_path, log_context)
            response = None
            exit()
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            log_context = 'login response successed'
        else:
            log_context = 'login response fatal, return code %d' \
                          % response.getcode()
            exit()
        self.logprowork(log_path, log_context)

    def save_test_html(self, workdir, content, log_path):
        """Save request web source page in a html file, test use

        :param workdir:     work directory
        :param content:     save content
        :param log_path:    log save path
        :return:            none
        """
        htmlfile = open(workdir + dataload.fs_operation[1] + 'test.html', "w")
        htmlfile.write(content)
        htmlfile.close()
        log_context = 'save request html page ok'
        self.logprowork(log_path, log_context)

    @staticmethod
    def commit_spansizer(whole_pattern, info_pattern, web_src):
        """A sizer for all of images in a page

        :param whole_pattern:   whole info data regex compile pattern
        :param info_pattern:    image info regex compile pattern
        :param web_src:         webpage source
        :return:                original target urls, image infos
        """
        gather_info = []
        gather_url = []
        datasrc_pattern = re.compile(dataload.DATASRC_REGEX, re.S)
        span_pattern = re.compile(dataload.SPAN_REGEX, re.S)
        img_whole_info = re.findall(whole_pattern, web_src)
        # image have 3 format: jpg/png/gif
        # this crawler will give gif format up and crawl png or jpg
        # pixiv one repo maybe have multi-images
        for item in img_whole_info:
            # get judge key word
            thumbnail = re.findall(datasrc_pattern, item)[0]
            judge_word = thumbnail[-18:]

            # check jpg/png or gif
            if judge_word == dataload.JUDGE_NOGIF_WORD:
                span_nbr = re.findall(span_pattern, item)
                # get vaild word
                vaild_word = thumbnail[44:-18]

                # try to check multi-span images
                if len(span_nbr) != 0:
                    # one commit artwork has more pages, iter it
                    for _px in range(int(span_nbr[0])):
                        # set same info
                        info = re.findall(info_pattern, item)[0]
                        gather_info.append(info)
                        # more pages point
                        target_url = dataload.ORIGINAL_IMAGE_HEAD + vaild_word \
                                     + dataload.ORIGINAL_IMAGE_TAIL(_px)
                        gather_url.append(target_url)
                # just only one picture in a commit
                else:
                    info = re.findall(info_pattern, item)[0]
                    gather_info.append(info)
                    # only _p0 page
                    target_url = dataload.ORIGINAL_IMAGE_HEAD + vaild_word \
                                 + dataload.ORIGINAL_IMAGE_TAIL(0)
                    gather_url.append(target_url)
            # give up gif format
            else:
                pass

        return gather_url, gather_info

    @retry
    def _save_oneimage(self, index, url, basepages, img_savepath, log_path):
        """Download one target image, then multi-process will call here

        Add retry decorator, if first try failed, it will auto-retry
        :param index:           image index
        :param url:             one image url
        :param basepages:       referer basic pages list
        :param img_savepath:    image save path
        :param log_path:        log save path
        :return:                none
        """
        proxy_handler = None
        timeout = 30
        img_datatype = 'png'
        # name artwork_id + _px
        image_name = url[57:-4]

        # setting new headers
        headers = dataload.build_original_headers(basepages[index])
        list_headers = dataload.dict_transto_list(headers)
        self.opener.addheaders = list_headers
        # update install opener
        urllib.request.install_opener(self.opener)

        # this request image step will delay much time
        response = None
        try:
            response = self.opener.open(
                fullurl=url,
                timeout=timeout)
        except urllib.error.HTTPError as e:
            ## log_context = str(e.code)
            ## self.logprowork(logpath, log_context)

            # http error 404, change image type
            if e.code == dataload.HTTP_NOTFOUND_CODE_404:
                # change data type
                img_datatype = 'jpg'
                jpg_img_url = url[0:-3] + img_datatype
                try:
                    response = self.opener.open(
                        fullurl=jpg_img_url,
                        timeout=timeout)
                except urllib.error.HTTPError as e:
                    ## log_context = str(e.code)
                    ## self.logprowork(logpath, log_context)

                    # not 404 change proxy, cause request server forbidden
                    if e.code != dataload.HTTP_NOTFOUND_CODE_404:
                        # if timeout, use proxy reset request
                        log_context = "change proxy server"
                        self.logprowork(log_path, log_context)

                        # preload a proxy handler, just run once
                        if Matrix._proxy_hasrun_flag is False:
                            Matrix._proxy_hasrun_flag = True
                            proxy = self._getproxyserver(log_path)
                            proxy_handler = urllib.request.ProxyHandler(proxy)
                        else:
                            pass

                        # add proxy handler
                        self.opener = urllib.request.build_opener(proxy_handler)
                        # re-request
                        response = self.opener.open(
                            fullurl=jpg_img_url,
                            timeout=timeout)
                    else:
                        pass
            # if timeout, use proxy reset request
            else:
                log_context = "change proxy server"
                self.logprowork(log_path, log_context)
                self.opener = urllib.request.build_opener(proxy_handler)
                response = self.opener.open(
                    fullurl=url,
                    timeout=timeout)

        # save image bin data to files
        if response.getcode() == dataload.HTTP_OK_CODE_200:
            img_bindata = response.read()

            # calcus download source whole size
            source_size = float(len(img_bindata) / 1024)
            Matrix._datastream_pool += source_size

            with open(img_savepath + dataload.fs_operation[1]
                      + image_name + '.' + img_datatype, 'wb') as img:
                img.write(img_bindata)
            log_context = 'target no.%d image download finished,' \
                          ' image size: %dKB' % (index + 1, source_size)
            self.logprowork(log_path, log_context)

    class _MultiThreading(threading.Thread):
        """Overrides its run method by inheriting the Thread class

        This class can be placed outside the main class, you can also put inside
        threads are the smallest unit of program execution flow
        that is less burdensome than process creation
        Internal call
        """
        def __init__(self, lock, i, img_url, basepages, img_savepath, log_path):
            """Provide class arguments

            :param lock:            object lock
            :param i:               image index
            :param img_url:         image url
            :param basepages:       referer basic page
            :param img_savepath:    image save path
            :param log_path:        log save path
            """
            # callable class init
            threading.Thread.__init__(self)
            self.lock = lock
            self.i = i
            self.img_url = img_url
            self.base_pages = basepages
            self.imgPath = img_savepath
            self.logPath = log_path

        def run(self):
            """Overwrite threading.thread run() method

            :return:    none
            """
            # cancel lock release will let multi-process change to easy process
            ## self.lock.acquire()
            Matrix()._save_oneimage(self.i, self.img_url, self.base_pages,
                                    self.imgPath, self.logPath)
            ## self.lock.release()

    def download_alltarget(self, urls, basepages, workdir, log_path):
        """Multi-process download all image

        :param urls:        all original images urls
        :param basepages:   all referer basic pages
        :param workdir:     work directory
        :param log_path:    log save path
        :return:            none
        """
        queueLength = len(urls)

        log_context = 'start to download %d target(s)======>' % queueLength
        self.logprowork(log_path, log_context)

        lock = threading.Lock()
        # here init var alive thread count
        aliveThreadCnt = queueLength

        # log download elapsed time
        starttime = time.time()

        # create overwrite threading.Thread object
        for i, one_url in enumerate(urls):
            sub_thread = self._MultiThreading(lock, i, one_url, basepages,
                                              workdir, log_path)
            # set every download sub-process is non-daemon process
            sub_thread.setDaemon(False)
            sub_thread.start()
            # confirm thread has been created, delay cannot too long
            ## time.sleep(0.1)

        # parent thread wait all sub-thread end
        while aliveThreadCnt > 1:
            # global variable update
            Matrix._alivethread_counter = threading.active_count()

            # when alive thread count change, print its value
            if aliveThreadCnt != Matrix._alivethread_counter:
                # update alive thread count
                aliveThreadCnt = Matrix._alivethread_counter
                log_context = ('currently remaining sub-thread(s): %d/%d' 
                              % (aliveThreadCnt - 1, queueLength))
                self.logprowork(log_path, log_context)

        # calcus average download speed and whole elapesd time
        endtime = time.time()
        elapesd_time = endtime - starttime
        average_download_speed = float(Matrix._datastream_pool / elapesd_time)

        log_context = ("all of threads reclaim, elapsed time: %0.2fs, " 
                     "average download speed: %0.2fKB/s"
                      % (elapesd_time, average_download_speed))
        self.logprowork(log_path, log_context)

    def htmlpreview_build(self, workdir, html_path, log_path):
        """Build a html file to browse image

        :param self:        class self
        :param workdir:     work directory
        :param html_path:   html file save path
        :param log_path:    log save path
        :return:            none
        """
        html_file = open(html_path, "w")
        # build html background page text
        # write a title
        html_file.writelines(
            "<html>\r\n"
            "<head>\r\n"
            "<title>MatPixivCrawler3 ResultPage</title>\r\n"
            "</head>\r\n"
            "<body>\r\n")
        # put all crawl images into html source code
        html_file.writelines(
            "<script>window.onload = function(){"
                "var imgs = document.getElementsByTagName('img');"
                "for(var i = 0; i < imgs.length; i++){"
                    "imgs[i].onclick = function(){"
                        "if(this.width == this.attributes['oriWidth'].value "
                            "&& this.height == this.attributes['oriHeight'].value){"
                            "this.width = this.attributes['oriWidth'].value * 1.0 "
                            "/ this.attributes['oriHeight'].value * 200;"
                            "this.height = 200;"
                        "}else{this.width = this.attributes['oriWidth'].value ;"
                        "this.height = this.attributes['oriHeight'].value;}}}};"
            "</script>")
        for i in os.listdir(workdir):
            if i[-4:len(i)] in [".png", ".jpg", ".bmp"]:
                width, height = Image.open(
                    workdir + dataload.fs_operation[1] + i).size
                i = i.replace("#", "%23")
                ## html_file.writelines("<a href = \"%s\">"%("./" + filename))
                # set image size
                html_file.writelines(
                    "<img src = \"%s\" width = \"%dpx\" height = \"%dpx\" "
                    "oriWidth = %d oriHeight = %d />\r\n"
                    % ("./" + i, width * 1.0 / height * 200, 200, width, height))
                ## html_file.writelines("</a>\r\n")

        # end of htmlfile
        html_file.writelines(
            "</body>\r\n"
            "</html>")
        html_file.close()

        log_context = 'image browse html generate finished'
        self.logprowork(log_path, log_context)

    def work_finished(self, log_path):
        """Work finished log

        :param log_path:    log save path
        :return:            none
        """
        # end time log
        rtc = time.localtime()
        ymdhms = '%d-%d-%d %d:%d:%d' \
                 % (rtc[0], rtc[1], rtc[2], rtc[3], rtc[4], rtc[5])
        log_context = "crawler work finished, log time: " + ymdhms
        self.logprowork(log_path, log_context)

        # logo display
        log_context =(
            dataload.LABORATORY + ' ' + dataload.ORGANIZATION
            + ' technology support\n'                                   
            'Code by ' + dataload.ORGANIZATION + '@' + dataload.DEVELOPER)

        # open work directory, check result
        self.logprowork(log_path, log_context)
        os.system(dataload.fs_operation[2] + ' ' + dataload.fs_operation[0])

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
