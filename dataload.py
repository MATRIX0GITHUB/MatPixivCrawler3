#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this test script is written to handle datas and some info

# projrct info
__author__          = 'Neod Anderjon(LeaderN)'                      # author signature
__laboratory__      = 'T.WKVER'                                     # lab
__organization__    = '</MATRIX>'
__version__         = 'v1p2_LTE'

import urllib.request, urllib.parse, urllib.error
import time, os, linecache
import getpass

# define some global variable
SHELLHEAD = 'MatPixivCrawler@' + __organization__ + ':~$ '          # copy linux head symbol
# work directory
storage = []
# login datas
loginData = []

# ======================get format time, and get year-month-date to be a folder name===============================
# work directory

def platform_setting():
    """
    set os platform to set folder format
    folder must with directory symbol '/' or '\\'
    :return:    platform work directory
    """
    # call global variables
    work_dir = None
    symbol = None
    fileManager = None
    global storage
    # linux
    if os.name == 'posix':
        work_dir = '/home/neod-anderjon/Pictures/Crawler/'
        symbol = '/'
        fileManager = 'nautilus'
    # windows
    elif os.name == 'nt':
        work_dir = 'E:\\Workstation_Files\\PictureDatabase\\Crawler\\'
        symbol = '\\'
        fileManager = 'explorer'
    else:
        pass

    # call a global list
    storage = [work_dir, symbol, fileManager]
platform_setting()

# real time clock
rtc = time.localtime()
ymd = '%d-%d-%d' % (rtc[0], rtc[1], rtc[2])

# universal path
logfile_name = storage[1] + 'CrawlerWork[%s].log' % ymd
htmlfile_name = storage[1] + 'CrawlerWork[%s].html' % ymd
ranking_folder = storage[0] + 'rankingtop_%s%s' % (ymd, storage[1])
# rankingtop use path
logfile_path = ranking_folder + logfile_name
htmlfile_path = ranking_folder + htmlfile_name
# illustrepo use path
repo_folder = storage[0]

# ==============================================pixiv login info====================================================

def login_infopreload():
    """
    get user input username and password
    login.cr file example:
    =================================
    [login]
    <mail>
    <passwd>
    =================================
    :return:    username, password, get data
    """
    global loginData
    print("###################################login data check###################################")
    loginFilePath = os.getcwd() + storage[1] + 'login.cr'           # get local dir path
    isLoginCrExisted = os.path.exists(loginFilePath)
    if isLoginCrExisted:
        userMailBox = linecache.getline(loginFilePath, 2)           # row 2, usernamemail
        userPassword = linecache.getline(loginFilePath, 3)          # row 3, password
        # empty file
        if userMailBox == '' or userPassword == '':
            print(SHELLHEAD + "login.cr file invaild, please input your login info")
            userMailBox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
            userPassword = getpass.getpass(SHELLHEAD + 'enter your account password: ') # pycharm python console not support
        else:
            check = input(SHELLHEAD + "please check your info:\n"
                                          "[!]    username: %s[!]    password: %s"
                                          "Yes or No?: " % (userMailBox, userPassword))
            # user judge info are error
            if check != 'yes' and check != 'Yes' and check != 'YES' and check != 'y' and check != 'Y':
                print(SHELLHEAD + "you can write new info")
                userMailBox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
                userPassword = getpass.getpass(SHELLHEAD + 'enter your account password: ')
            else:
                pass
    # no login.cr file
    else:
        print(SHELLHEAD + "cannot find login.cr file, please input your login info")
        userMailBox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
        userPassword = getpass.getpass(SHELLHEAD + 'enter your account password: ')

    # strip() delete symbol '\n'
    username = userMailBox.strip()
    passwd = userPassword.strip()

    getwayRegInfo = [('user', username), ('pass', passwd)]
    getData = urllib.parse.urlencode(getwayRegInfo).encode(encoding='UTF8')

    # save in a list
    loginData = [username, passwd, getData]
login_infopreload()

# ========================================some use url address=====================================================
# login request must be https proxy format, request page or image must be http proxy

# login and request image https proxy
wwwHost = "www.pixiv.net"                                           # only can set into host
hostWebURL = 'https://www.pixiv.net/'
accountHost = "accounts.pixiv.net"                                  # account login
postKeyGeturl = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
login_ref = 'wwwtop_accounts_index'                                 # post data include
originHost = "https://accounts.pixiv.net/api/login?lang=en"         # login request url
originHost2 = "https://accounts.pixiv.net"                          # login origin
# request universal original image constant words
imgOriginalheader = 'https://i.pximg.net/img-original/img'          # original image https url header
imgOriginaltail = lambda num:'_p%d.png' % num                       # original image https url tail, default set to png
# page request http proxy
proxyServerRequestURL = 'http://www.xicidaili.com/nn/'              # proxy server get website
ucRankURL = 'http://www.pixiv.net/ranking.php?mode='                # rank top universal word header
r18RankWordTail = '_r18'                                            # r18 rank word tail
dailyRankURL = ucRankURL + 'daily'                                  # daily-rank
weeklyRankURL = ucRankURL + 'weekly'                                # weekly-rank
monthlyRankURL = ucRankURL + 'monthly'                              # monthly-rank
dailyRankURL_R18 = dailyRankURL + r18RankWordTail                   # r18 daily-rank
weeklyRankURL_R18 = weeklyRankURL + r18RankWordTail                 # r18 weekly-rank
baseWebURL = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id=' # basic format
illustHomeURL = 'http://www.pixiv.net/member.php?id='               # illust home page
mainPage = 'http://www.pixiv.net/member_illust.php?id='             # illust main page
mainPagemiddle = '&type=all'                                        # url middle word
mainPagetail = '&p='                                                # url tail word
judgeWord = '_p0_master1200.jpg'                                    # judge gif or jpg/png

# ==================================http request headers include data============================================
# request use data, from browser javascript or fiddler

reqSuccessCode = 200
reqNotFound = 404
# login headers info dict
userAgentLinux = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                           "Chrome/56.0.2924.87 Safari/537.36"
userAgentWindows = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                            " Chrome/60.0.3112.90 Safari/537.36"
accept = "application/json, text/javascript, */*; q=0.01"
accept2 = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
acceptEncoding = "gzip, deflate, br"
acceptEncoding2 = "br"                                              # no use gzip, transfer speed down, but will not error
acceptLanguage = "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4,zh-CN;q=0.2"
cacheControl = "no-cache"
connection = "keep-alive"
contentType = "application/x-www-form-urlencoded; charset=UTF-8"
xRequestwith = "XMLHttpRequest"

def dict_transto_list (input_dict):
    """
    change dict data-type to list
    :param input_dict:      dict
    :return:                list
    """
    result_list = []
    for key, value in list(input_dict.items()):
        item = (key, value)
        result_list.append(item)

    return result_list

def ucUserAgent():
    """
    choose platform user-agent headers
    :return:    headers
    """
    uaHeadersLinux = {'User-Agent': userAgentLinux}                 # build dict word
    uaHeadersWindows = {'User-Agent': userAgentWindows}             # build dict word
    # platform choose
    headers = None
    if os.name == 'posix':
        headers = uaHeadersLinux
    elif os.name == 'nt':
        headers = uaHeadersWindows
    else:
        pass

    return headers

def build_login_headers(cookie):
    """
    build the first request login headers
    :param cookie:  cookie
    :return:        login headers
    """
    # this build headers key-word is referer and user-agent
    baseHeaders = {
        'Accept': accept,
        'Accept-Encoding': acceptEncoding,
        'Accept-Language': acceptLanguage,
        'Cache-Control': cacheControl,
        'Connection': connection,
        'Content-Length': "207",
        'Content-Type': contentType,
        'Cookie': cookie,
        'DNT': "1",
        'Host': accountHost,
        'Origin': originHost2,
        'Referer': postKeyGeturl,                                   # last page is request post-key page
        'X-Requested-With': xRequestwith,
    }
    # dict merge
    buildHeaders = dict(baseHeaders, **ucUserAgent())               # longth-change argument

    return buildHeaders

def build_original_headers(referer):
    """
    original image request headers
    :param referer: headers need a last page referer
    :return:        build headers
    """
    baseHeaders = {
        'Accept': "image/webp,image/*,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, sdch",
        'Accept-Language': acceptLanguage,
        'Connection': connection,
        # must add referer, or server will return a damn http error 403, 404
        # copy from javascript console network request headers of image
        'Referer': referer,  # request basic page
    }
    # dict merge
    buildHeaders = dict(baseHeaders, **ucUserAgent())               # longth-change argument

    return buildHeaders

# =======================================regex collection==========================================================
# mate web src need word strip

postKeyRegex = 'key".*?"(.*?)"'                                     # mate post key
rankTitleRegex = 'data-rank-text="(.*?)" data-title="(.*?)" data-user-name="(.*?)" data-date="(.*?)".*?data-id="(.*?)"'
nbrRegex = '\d+\.?\d*'                                              # mate any number
imgWholeInfoRegex = '<li class="image-item">(.*?)</li>'             # catch <li class="image-item">...</li>
datasrcRegex = 'data-src="(.*?)"'                                   # thumbnail mate
illustNameRegex = 'me"title="(.*?)"'                                # mate illust name
imagesNameRegex = 'e" title="(.*?)"'                                # mate mainpage images name
illustAWCntRegex = 'dge">(.*?)<'                                    # illust artwork count mate
imgSpancnt = '<span>(.*?)</span>'                                   # gather one span image count
rankSectionRegex = '<section id=(.*?)</section>'                    # ranking top whole info

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
