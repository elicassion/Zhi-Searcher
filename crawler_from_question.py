# -*- coding:utf8 -*-
from bs4 import BeautifulSoup
import os, sys, time, platform, random, shutil
import re, json, cookielib
import requests, termcolor
import codecs
import threading
import urllib
import urllib2
import urlparse
from Queue import Queue

from login import islogin
from login import Logging

from zhihu import Question
from zhihu import Answer

requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    Logging.error("Not Logined")
    raise Exception("403")

if islogin() != True:
    Logging.error("Info Disabled")
    raise Exception("403")

THREAD_NUM = 50

def dealWithPage(page_num):
    page = urlparse.urljoin(url_prefix, str(page_num))

    question_index_filename = 'q_index'
    try:
        question = Question(page)
    except:
        print 'Question Get Error.'
        return
    f = codecs.open(question_index_filename+'.txt', 'a')
    f.write(str(page_num) + '\r\n')
    f.close()
    question_folder = 'Zhihu/Question_'+str(page_num)
    question_filename = 'q'
    if (not os.path.exists(question_folder)):
        os.makedirs(question_folder)
    f = codecs.open(os.path.join(question_folder, question_filename+'.txt'), 'w')
    f.write(question.get_title() + '\r\n|||\r\n')
    f.write(question.get_detail() + '\r\n|||\r\n')
    for topic in question.get_topics():
        f.write(topic + '\t')
    f.write('\r\n|||\r\n')
    f.write(str(question.get_visit_times()) + '\r\n|||\r\n')
    f.write(str(question.get_followers_num()) + '\r\n|||\r\n')
    f.write(str(question.get_answers_num()) + '\r\n|||\r\n')
    f.close()

    answers = question.get_all_answers()
    for answer in answers:
        ansURL = answer.answer_url
        ans = Answer(ansURL)
        answer_folder = os.path.join(question_folder, 'Answer')
        answer_filename = str(ansURL.split('/')[-1])
        answer_index_filename = 'a_index'
        f = codecs.open(answer_index_filename+'.txt', 'a')
        f.write(str(page_num) + '|||' + str(answer_filename) + '\r\n')
        f.close()
        if (not os.path.exists(answer_folder)):
            os.makedirs(answer_folder)
        f = codecs.open(os.path.join(answer_folder, answer_filename+'.txt'), 'w')
        try:
            f.write(ans.get_content().find('body').get_text().strip().encode("gbk", 'ignore') + '\r\n|||\r\n')
            f.write(ans.get_author().get_user_id() + '\r\n|||\r\n')
            f.write(str(ans.get_upvote()) + '\r\n|||\r\n')
        except:
            print 'TimeOut Occurred.'
            f.close()
            f = codecs.open(os.path.join(answer_folder, answer_filename+'.txt'), 'w')
            f.write('None')
            f.close()
            continue
        f.close()

def crawling(page_num):
    global url_prefix
    # page_num = crawlQueue.get()
    # if varLock.acquire():
    print page_num
        # try:
    dealWithPage(page_num)
        # except:
    #         crawlQueue.task_done()
    #     varLock.release()
    # else:
    #     crawlQueue.task_done()
    # crawlQueue.task_done()


url_prefix = 'https://www.zhihu.com/question/'

start = time.clock()
for i in range(33312935,34000000):
    crawling(i)
"""try:
    crawlQueue = Queue()
    for page_num in range(19550226, 19554226):
        crawlQueue.put(page_num)
    varLock = threading.Lock()
    for i in range(THREAD_NUM):
        t = threading.Thread(target = crawling)
        t.setDaemon(True)
        t.start()
    crawlQueue.join()
except:
    print 'Error'"""

print '--------------------END---------------------'
print 'Time: ' + str(time.clock()-start)

