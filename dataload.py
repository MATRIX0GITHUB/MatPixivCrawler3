#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon(LeaderN)
# =====================================================================
# this test script is written to handle datas and some info

# projrct info
PROJECT_NAME        = 'MatPixivCrawler3'
DEVELOPER           = 'Neod Anderjon(LeaderN)'                      # author signature
LABORATORY          = 'T.WKVER'                                     # lab
ORGANIZATION        = '</MATRIX>'
VERSION             = 'v1p5_LTE'

import urllib.request, urllib.parse, urllib.error
import time, os, linecache
import getpass

# define some global variable
SHELLHEAD = PROJECT_NAME + '@' + ORGANIZATION + ':~$ '              # copy linux head symbol
# work directory
storage_l = []
# login datas
login_data_l = []

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
    file_manager = None
    global storage_l
    # linux
    if os.name == 'posix':
        work_dir = '/home/neod-anderjon/Pictures/Crawler/'
        symbol = '/'
        file_manager = 'nautilus'
    # windows
    elif os.name == 'nt':
        work_dir = 'E:\\Workstation_Files\\PictureDatabase\\Crawler\\'
        symbol = '\\'
        file_manager = 'explorer'
    else:
        pass

    # call a global list
    storage_l = [work_dir, symbol, file_manager]
platform_setting()

# real time clock
_rtc = time.localtime()
_ymd = '%d-%d-%d' % (_rtc[0], _rtc[1], _rtc[2])

# universal path
LOG_NAME = storage_l[1] + 'CrawlerWork[%s].log' % _ymd
HTML_NAME = storage_l[1] + 'CrawlerWork[%s].html' % _ymd
RANK_DIR = storage_l[0] + 'rankingtop_%s%s' % (_ymd, storage_l[1])
# rankingtop use path
LOG_PATH = RANK_DIR + LOG_NAME
HTML_PATH = RANK_DIR + HTML_NAME
# illustrepo use path
REPO_DIR = storage_l[0]

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
    global login_data_l
    print("###################################login data check###################################")
    login_file_path = os.getcwd() + storage_l[1] + 'login.cr'           # get local dir path
    is_login_file_existed = os.path.exists(login_file_path)
    if is_login_file_existed:
        user_mailbox = linecache.getline(login_file_path, 2)           # row 2, usernamemail
        user_password = linecache.getline(login_file_path, 3)          # row 3, password
        # empty file
        if user_mailbox == '' or user_password == '':
            print(SHELLHEAD + "login.cr file invaild, please input your login info")
            user_mailbox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
            user_password = getpass.getpass(SHELLHEAD + 'enter your account password: ') # pycharm python console not support
        else:
            check = input(SHELLHEAD + "please check your info:\n"
                                          "[!]    username: %s[!]    password: %s"
                                          "Yes or No?: " % (user_mailbox, user_password))
            # user judge info are error
            if check != 'yes' and check != 'Yes' and check != 'YES' and check != 'y' and check != 'Y':
                print(SHELLHEAD + "you can write new info")
                user_mailbox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
                user_password = getpass.getpass(SHELLHEAD + 'enter your account password: ')
            else:
                pass
    # no login.cr file
    else:
        print(SHELLHEAD + "cannot find login.cr file, please input your login info")
        user_mailbox = input(SHELLHEAD + 'enter your pixiv id(mailbox), must be a R18: ')
        user_password = getpass.getpass(SHELLHEAD + 'enter your account password: ')

    # strip() delete symbol '\n'
    username = user_mailbox.strip()
    passwd = user_password.strip()

    getway_reg_info = [('user', username), ('pass', passwd)]
    getway_data = urllib.parse.urlencode(getway_reg_info).encode(encoding='UTF8')

    # save in a list
    login_data_l = [username, passwd, getway_data]
login_infopreload()

# ========================================some use url address=====================================================
# login request must be https proxy format, request page or image must be http proxy

# login and request image https proxy
WWW_HOST_URL = "www.pixiv.net"
HTTPS_HOST_URL = 'https://www.pixiv.net/'
ACCOUNTS_URL = "accounts.pixiv.net"
LOGIN_POSTKEY_URL = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
LOGIN_POSTDATA_REF = 'wwwtop_accounts_index'
LOGIN_REQUEST_URL = "https://accounts.pixiv.net/api/login?lang=en"
_LOGIN_REQUEST_URL = "https://accounts.pixiv.net"                   # interal build use
# request universal original image constant words
ORIGINAL_IMAGE_HEAD = 'https://i.pximg.net/img-original/img'
ORIGINAL_IMAGE_TAIL = lambda px: '_p%d.png' % px                    # use lambda write picture number
# page request http proxy
PROXYSERVER_URL = 'http://www.xicidaili.com/nn/'
# ranking top url and word
RANKING_URL = 'http://www.pixiv.net/ranking.php?mode='
R18_WORD = '_r18'
DAILY_WORD = 'daily'
WEEKLY_WORD = 'weekly'
MONTHLY_WORD = 'monthly'
DAILY_RANKING_URL = RANKING_URL + DAILY_WORD
WEEKLY_RANKING_URL = RANKING_URL + WEEKLY_WORD
MONTHLY_RANKING_URL = RANKING_URL + MONTHLY_WORD
DAILY_RANKING_R18_URL = DAILY_RANKING_URL + R18_WORD
WEEKLY_RANKING_R18_URL = WEEKLY_RANKING_URL + R18_WORD
BASEPAGE_URL = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='
MEMBER_URL = 'http://www.pixiv.net/member.php?id='
MEMBER_ILLUST_URL = 'http://www.pixiv.net/member_illust.php?id='
TYPE_ALL_WORD = '&type=all'
PAGE_NUM_WORD = '&p='
JUDGE_NOGIF_WORD = '_p0_master1200.jpg'                             # judge gif or jpg/png
PROXYIP_STR_BUILD = lambda ix,list_:'http://' + list_[ix - 1] + ':' + list_[ix]

# ==================================http request headers include data============================================
# request use data, from browser javascript or fiddler

HTTP_OK_CODE_200 = 200
HTTP_REQUESTFAILED_CODE_403 = 403
HTTP_NOTFOUND_CODE_404 = 404
# login headers info dict
_USERAGENT_LINUX = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                           "Chrome/56.0.2924.87 Safari/537.36"
_USERAGENT_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                            " Chrome/60.0.3112.90 Safari/537.36"
_HEADERS_ACCEPT = "application/json, text/javascript, */*; q=0.01"
_HEADERS_ACCEPT2 = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
_HEADERS_ACCEPT_ENCODING = "gzip, deflate, br"
_HEADERS_ACCEPT_ENCODING2 = "br"                                    # no use gzip, transfer speed down, but will no error
_HEADERS_ACCEPT_LANGUAGE = "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4,zh-CN;q=0.2"
_HEADERS_CACHE_CONTROL = "no-cache"
_HEADERS_CONNECTION = "keep-alive"
_HEADERS_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
_HEADERS_XMLHTTPREQUEST = "XMLHttpRequest"

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

def uc_user_agent():
    """
    choose platform user-agent headers
    :return:    headers
    """
    # build dict word
    ua_headers_linux = {'User-Agent': _USERAGENT_LINUX}
    ua_headers_windows = {'User-Agent': _USERAGENT_WIN}
    # platform choose
    headers = None
    if os.name == 'posix':
        headers = ua_headers_linux
    elif os.name == 'nt':
        headers = ua_headers_windows
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
    base_headers = {
        'Accept': _HEADERS_ACCEPT,
        'Accept-Encoding': _HEADERS_ACCEPT_ENCODING,
        'Accept-Language': _HEADERS_ACCEPT_LANGUAGE,
        'Cache-Control': _HEADERS_CACHE_CONTROL,
        'Connection': _HEADERS_CONNECTION,
        'Content-Length': "207",
        'Content-Type': _HEADERS_CONTENT_TYPE,
        'Cookie': cookie,
        'DNT': "1",
        'Host': ACCOUNTS_URL,
        'Origin': _LOGIN_REQUEST_URL,
        'Referer': LOGIN_POSTKEY_URL,
        'X-Requested-With': _HEADERS_XMLHTTPREQUEST,
    }
    # dict merge, longth-change argument
    build_headers = dict(base_headers, **uc_user_agent())

    return build_headers

def build_original_headers(referer):
    """
    original image request headers
    :param referer: headers need a last page referer
    :return:        build headers
    """
    base_headers = {
        'Accept': "image/webp,image/*,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, sdch",
        'Accept-Language': _HEADERS_ACCEPT_LANGUAGE,
        'Connection': _HEADERS_CONNECTION,
        # must add referer, or server will return a damn http error 403, 404
        # copy from javascript console network request headers of image
        'Referer': referer,  # request basic page
    }
    build_headers = dict(base_headers, **uc_user_agent())

    return build_headers

# =======================================regex collection==========================================================
# mate web src need word strip

POSTKEY_REGEX = 'key".*?"(.*?)"'
RANKING_INFO_REGEX = 'data-rank-text="(.*?)" data-title="(.*?)" data-user-name="(.*?)" data-date="(.*?)".*?data-id="(.*?)"'
NUMBER_REGEX = '\d+\.?\d*'
IMAGEITEM_REGEX = '<li class="image-item">(.*?)</li>'               # catch <li class="image-item">...</li>
DATASRC_REGEX = 'data-src="(.*?)"'
ILLUST_NAME_REGEX = 'me"title="(.*?)"'
IMAGE_NAME_REGEX = 'e" title="(.*?)"'
REPO_WHOLE_NUMBER_REGEX = 'dge">(.*?)<'                             # illust artwork count mate
SPAN_REGEX = '<span>(.*?)</span>'                                   # gather one span image count
RANKING_SECTION_REGEX = '<section id=(.*?)</section>'
PROXYIP_REGEX = '<td>(.*?)</td>'                                    # proxy website data mate

# =====================================================================
# code by </MATRIX>@Neod Anderjon(LeaderN)
