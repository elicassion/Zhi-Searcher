# -*- coding: utf-8 -*-
import os, sys, time, platform, random
import re, json, cookielib
import requests, termcolor, html2text
from bs4 import BeautifulSoup
from login import islogin
from login import Logging

requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    Logging.error(u"你还没有登录知乎哦 ...")
    Logging.info(u"执行 `python auth.py` 即可以完成登录。")
    raise Exception("无权限(403)")


if islogin() != True:
    Logging.error(u"你的身份信息已经失效，请重新生成身份信息( `python auth.py` )。")
    raise Exception("无权限(403)")


reload(sys)
sys.setdefaultencoding('utf8')

class Question:
    url = None
    soup = None

    def __init__(self, url, title=None):

        if not re.compile(r"(http|https)://www.zhihu.com/question/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
        else:
            self.url = url
        if self.soup == None:
            self.parser()

        if title != None: self.title = title

    def parser(self):
        r = requests.get(self.url, timeout=2)
        self.soup = BeautifulSoup(r.content, "html.parser")
        try:
            title = self.soup.find("h2", class_="zm-item-title").string
        except:
            raise ValueError("404 Not Found")

    def get_title(self):
        if hasattr(self, "title"):
            if platform.system() == 'Windows':
                title = self.title.decode('utf-8', 'ignore').encode('gbk', 'ignore')
                return title
            else:
                return self.title
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            title = soup.find("h2", class_="zm-item-title").string.encode("utf-8").replace("\n", "")
            self.title = title
            if platform.system() == 'Windows':
                title = title.decode('utf-8', 'ignore').encode('gbk', 'ignore')
                return title
            else:
                return title

    def get_detail(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        detail = soup.find("div", id="zh-question-detail").div.get_text().encode("utf-8")
        if platform.system() == 'Windows':
            detail = detail.decode('utf-8','ignore').encode('gbk','ignore')
            return detail
        else:
            return detail

    def get_answers_num(self):
        # print '-info-in get ans num'
        if self.soup == None:
            self.parser()
        soup = self.soup
        answers_num = 0
        if soup.find("h3", id="zh-question-answer-num") != None:
            answers_num = int(soup.find("h3", id="zh-question-answer-num")["data-num"])
        # print '-info-out get ans num'
        print answers_num
        return answers_num

    def get_followers_num(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        try:
            followers_num = int(soup.find("div", class_="zg-gray-normal").a.strong.string)
        except:
            followers_num = 0
        return followers_num

    def get_topics(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        topic_list = soup.find_all("a", class_="zm-item-tag")
        topics = []
        for i in topic_list:
            topic = i.contents[0].encode("utf-8",'ignore').replace("\n", "")
            if platform.system() == 'Windows':
                topic = topic.decode('utf-8','ignore').encode('gbk','ignore')
            topics.append(topic)
        return topics

    def get_all_answers(self):
        # print '-info-in get all ans'
        answers_num = self.get_answers_num()
        if answers_num == 0:
            print "No answer."
            return
            yield
        else:
            error_answer_count = 0
            my_answer_count = 0
            for i in xrange((answers_num - 1) / 50 + 1):
                # print '-info-'+str(i)
                if i == 0:
                    for j in xrange(min(answers_num, 50)):
                        print '-info-'+str(j)
                        if self.soup == None:
                            self.parser()
                        soup = BeautifulSoup(self.soup.encode("utf-8","ignore"), "html.parser")

                        is_my_answer = False
                        if soup.find_all("div", class_="zm-item-answer")[j].find("span", class_="count") == None:
                            my_answer_count += 1
                            is_my_answer = True

                        if soup.find_all("div", class_="zm-item-answer")[j].find("div", class_="zm-editable-content clearfix") == None:
                            error_answer_count += 1
                            continue
                        author = None
                        if soup.find_all("div", class_="zm-item-answer-author-info")[j].get_text(strip='\n') == u"匿名用户":
                            author_url = None
                            author = User(author_url)
                        else:
                            author_tag = soup.find_all("div", class_="zm-item-answer-author-info")[j].find_all("a")[1]
                            author_id = author_tag.string.encode("utf-8","ignore")
                            author_url = "http://www.zhihu.com" + author_tag["href"]
                            author = User(author_url, author_id)

                        # print '-info-ismyanswer'

                        if is_my_answer == True:
                            count = soup.find_all("div", class_="zm-item-answer")[j].find("a", class_="zm-item-vote-count").string
                        else:
                            count = soup.find_all("span", class_="count")[j - my_answer_count].string
                        if "K" in count:
                            upvote = int(count.split('K')[0]) * 1000
                        elif "W" in count:
                            upvote = int(count.split('W')[0]) * 10000
                        else:
                            upvote = int(count)

                        answer_url = "http://www.zhihu.com" + soup.find_all("a", class_="answer-date-link")[j]["href"]

                        answer = soup.find_all("div", class_="zm-editable-content clearfix")[j - error_answer_count]
                        # print '-info-extract'
                        soup.body.extract()
                        # print '-info-insafter'
                        soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
                        # print '-info-append'
                        soup.body.append(answer)
                        content = soup
                        answer = Answer(answer_url, self, author, upvote, content)
                        yield answer
                else:
                    print '-info-inot0'
                    post_url = "http://www.zhihu.com/node/QuestionAnswerListV2"
                    _xsrf = self.soup.find("input", attrs={'name': '_xsrf'})["value"]
                    offset = i * 50
                    params = json.dumps(
                        {"url_token": int(self.url[-8:-1] + self.url[-1]), "pagesize": 50, "offset": offset})
                    data = {
                        '_xsrf': _xsrf,
                        'method': "next",
                        'params': params
                    }
                    header = {
                        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                        'Host': "www.zhihu.com",
                        'Referer': self.url
                    }
                    while(1):
                        try:
                            r = requests.post(post_url, data=data, headers=header, timeout=2)
                        except:
                            continue
                        else:
                            break

                    print '-info-req'
                    answer_list = r.json()["msg"]
                    print '-info-anslist '+str(len(answer_list))
                    if len(answer_list) == 0:
                        continue
                    for j in xrange(min(len(answer_list), min(answers_num - i * 50, 50))):
                        print '-info-'+str(j+i*50)
                        soup = BeautifulSoup(self.soup.encode("utf-8","ignore"), "html.parser")

                        answer_soup = BeautifulSoup(answer_list[j], "html.parser")

                        if answer_soup.find("div", class_="zm-editable-content clearfix") == None:
                            continue

                        author = None
                        if answer_soup.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                            author_url = None
                            author = User(author_url)
                        else:
                            author_tag = answer_soup.find("div", class_="zm-item-answer-author-info").find_all("a")[1]
                            author_id = author_tag.string.encode("utf-8","ignore")
                            author_url = "http://www.zhihu.com" + author_tag["href"]
                            author = User(author_url, author_id)

                        if answer_soup.find("span", class_="count") == None:
                            count = answer_soup.find("a", class_="zm-item-vote-count").string
                        else:
                            count = answer_soup.find("span", class_="count").string
                        if count[-1] == "K":
                            upvote = int(count[0:(len(count) - 1)]) * 1000
                        elif count[-1] == "W":
                            upvote = int(count[0:(len(count) - 1)]) * 10000
                        else:
                            upvote = int(count)

                        answer_url = "http://www.zhihu.com" + answer_soup.find("a", class_="answer-date-link")["href"]

                        answer = answer_soup.find("div", class_="zm-editable-content clearfix")
                        soup.body.extract()
                        soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
                        soup.body.append(answer)
                        content = soup
                        answer = Answer(answer_url, self, author, upvote, content)
                        yield answer

    def get_top_i_answers(self, n):
        j = 0
        answers = self.get_all_answers()
        for answer in answers:
            j = j + 1
            if j > n:
                break
            yield answer

    def get_top_answer(self):
        for answer in self.get_top_i_answers(1):
            return answer

    def get_visit_times(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        return int(soup.find("meta", itemprop="visitsCount")["content"])


class User:
    user_url = None
    # session = None
    soup = None

    def __init__(self, user_url, user_id=None):
        if user_url == None:
            self.user_id = "匿名用户"
        elif user_url.startswith('www.zhihu.com/people', user_url.index('//') + 2) == False:
            raise ValueError("\"" + user_url + "\"" + " : it isn't a user url.")
        else:
            self.user_url = user_url
            if user_id != None:
                self.user_id = user_id

    def parser(self):
        r = requests.get(self.user_url, timeout=1)
        soup = BeautifulSoup(r.content, "html.parser")
        self.soup = soup

    def get_user_id(self):
        if self.user_url == None:
            # print "I'm anonymous user."
            if platform.system() == 'Windows':
                return "匿名用户".decode('utf-8','ignore').encode('gbk','ignore')
            else:
                return "匿名用户"
        else:
            if hasattr(self, "user_id"):
                if platform.system() == 'Windows':
                    return self.user_id.decode('utf-8','ignore').encode('gbk','ignore')
                else:
                    return self.user_id
            else:
                if self.soup == None:
                    self.parser()
                soup = self.soup
                user_id = soup.find("div", class_="title-section ellipsis") \
                    .find("span", class_="name").string.encode("utf-8",'ignore')
                self.user_id = user_id
                if platform.system() == 'Windows':
                    return user_id.decode('utf-8','ignore').encode('gbk','ignore')
                else:
                    return user_id

    def get_data_id(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            data_id = soup.find("button", class_="zg-btn zg-btn-follow zm-rich-follow-btn")['data-id']
            return data_id

    def get_gender(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            gender = str(soup.find("span",class_="item gender").i)
            if (gender == '<i class="icon icon-profile-female"></i>'):
                return 'female'
            else:
                return 'male'

    def get_followees_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            followees_num = int(soup.find("div", class_="zm-profile-side-following zg-clear") \
                                .find("a").strong.string)
            return followees_num

    def get_followers_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            followers_num = int(soup.find("div", class_="zm-profile-side-following zg-clear") \
                                .find_all("a")[1].strong.string)
            return followers_num

    def get_agree_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            agree_num = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
            return agree_num

    def get_thanks_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            thanks_num = int(soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
            return thanks_num

    def get_asks_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            asks_num = int(soup.find_all("span", class_="num")[0].string)
            return asks_num

    def get_answers_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            answers_num = int(soup.find_all("span", class_="num")[1].string)
            return answers_num

    def get_collections_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            collections_num = int(soup.find_all("span", class_="num")[3].string)
            return collections_num

    def get_followees(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            followees_num = self.get_followees_num()
            if followees_num == 0:
                return
                yield
            else:
                followee_url = self.user_url + "/followees"
                r = requests.get(followee_url, timeout=1)

                soup = BeautifulSoup(r.content, "html.parser")
                for i in xrange((followees_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("h2", class_="zm-list-content-title")
                        for j in xrange(min(followees_num, 20)):
                            yield User(user_url_list[j].a["href"], user_url_list[j].a.string.encode("utf-8"))
                    else:
                        post_url = "http://www.zhihu.com/node/ProfileFolloweesListV2"
                        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                        offset = i * 20
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r.text)[0]
                        params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        header = {
                            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                            'Host': "www.zhihu.com",
                            'Referer': followee_url
                        }

                        r_post = requests.post(post_url, data=data, headers=header, timeout=1)

                        followee_list = r_post.json()["msg"]
                        for j in xrange(min(followees_num - i * 20, 20)):
                            followee_soup = BeautifulSoup(followee_list[j], "html.parser")
                            user_link = followee_soup.find("h2", class_="zm-list-content-title").a
                            yield User(user_link["href"], user_link.string.encode("utf-8",'ignore'))

    def get_followers(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            followers_num = self.get_followers_num()
            if followers_num == 0:
                return
                yield
            else:
                follower_url = self.user_url + "/followers"
                r = requests.get(follower_url, timeout=1)

                soup = BeautifulSoup(r.content, "html.parser")
                for i in xrange((followers_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("h2", class_="zm-list-content-title")
                        for j in xrange(min(followers_num, 20)):
                            yield User(user_url_list[j].a["href"], user_url_list[j].a.string.encode("utf-8"))
                    else:
                        post_url = "http://www.zhihu.com/node/ProfileFollowersListV2"
                        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                        offset = i * 20
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r.text)[0]
                        params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        header = {
                            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                            'Host': "www.zhihu.com",
                            'Referer': follower_url
                        }
                        r_post = requests.post(post_url, data=data, headers=header, timeout=1)

                        follower_list = r_post.json()["msg"]
                        for j in xrange(min(followers_num - i * 20, 20)):
                            follower_soup = BeautifulSoup(follower_list[j], "html.parser")
                            user_link = follower_soup.find("h2", class_="zm-list-content-title").a
                            yield User(user_link["href"], user_link.string.encode("utf-8",'ignore'))

    def get_asks(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            asks_num = self.get_asks_num()
            if asks_num == 0:
                return
                yield
            else:
                for i in xrange((asks_num - 1) / 20 + 1):
                    ask_url = self.user_url + "/asks?page=" + str(i + 1)
                    r = requests.get(ask_url, timeout=1)

                    soup = BeautifulSoup(r.content, "html.parser")
                    for question in soup.find_all("a", class_="question_link"):
                        url = "http://www.zhihu.com" + question["href"]
                        title = question.string.encode("utf-8",'ignore')
                        yield Question(url, title)

    def get_answers(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            answers_num = self.get_answers_num()
            if answers_num == 0:
                return
                yield
            else:
                for i in xrange((answers_num - 1) / 20 + 1):
                    answer_url = self.user_url + "/answers?page=" + str(i + 1)
                    r = requests.get(answer_url, timeout=1)
                    soup = BeautifulSoup(r.content, "html.parser")
                    for answer in soup.find_all("a", class_="question_link"):
                        question_url = "http://www.zhihu.com" + answer["href"][0:18]
                        question_title = answer.string.encode("utf-8",'ignore')
                        question = Question(question_url, question_title)
                        yield Answer("http://www.zhihu.com" + answer["href"], question, self)

    def get_collections(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            collections_num = self.get_collections_num()
            if collections_num == 0:
                return
                yield
            else:
                for i in xrange((collections_num - 1) / 20 + 1):
                    collection_url = self.user_url + "/collections?page=" + str(i + 1)

                    r = requests.get(collection_url, timeout=1)

                    soup = BeautifulSoup(r.content, "html.parser")
                    for collection in soup.find_all("div", class_="zm-profile-section-item zg-clear"):
                        url = "http://www.zhihu.com" + \
                              collection.find("a", class_="zm-profile-fav-item-title")["href"]
                        name = collection.find("a", class_="zm-profile-fav-item-title").string.encode("utf-8")
                        yield Collection(url, name, self)


    def get_likes(self):
        # This function only handles liked answers, not including zhuanlan articles
        if self.user_url == None:
            print "I'm an anonymous user."
            return
            yield
        else:
            r = requests.get(self.user_url, timeout=1)
            soup = BeautifulSoup(r.content, "html.parser")
            # Handle the first liked item
            first_item = soup.find("div", attrs={'class':'zm-profile-section-item zm-item clearfix'})
            first_item = first_item.find("div", attrs={'class':'zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main'})
            if u"赞同了回答" in str(first_item):
                first_like = first_item.find("a")['href']
                yield Answer("http://www.zhihu.com" + first_like)
            # Handle the rest liked items
            post_url = self.user_url + "/activities"
            start_time = soup.find("div", attrs={'class':'zm-profile-section-item zm-item clearfix'})["data-time"]
            _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
            data = {
                'start': start_time,
                '_xsrf': _xsrf,
            }
            header = {
                'Host': "www.zhihu.com",
                'Referer': self.user_url,
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            }
            r = requests.post(post_url, data=data, headers=header, timeout=1)
            response_size = r.json()["msg"][0]
            response_html = r.json()["msg"][1]
            while response_size > 0:
                all_liked_answers = re.findall(u"\u8d5e\u540c\u4e86\u56de\u7b54\n\n<a class=\"question_link\" target=\"_blank\" href=\"\/question\/\d{8}\/answer\/\d{8}", response_html)
                liked_answers = list(set(all_liked_answers))
                liked_answers.sort(key=all_liked_answers.index)
                for i in xrange(len(liked_answers)):
                    answer_url = "http://www.zhihu.com" + liked_answers[i][54:]
                    yield Answer(answer_url)
                data_times = re.findall(r"data-time=\"\d+\"", response_html)
                if len(data_times) != response_size:
                    print "读取activities栏时间信息时发生错误，可能因为某答案中包含data-time信息"
                    return
                    yield
                latest_data_time = re.search(r"\d+", data_times[response_size - 1]).group()
                data = {
                'start': latest_data_time,
                '_xsrf': _xsrf,
                }
                r = requests.post(post_url, data=data, headers=header, timeout=1)
                response_size = r.json()["msg"][0]
                response_html = r.json()["msg"][1]
            return
            yield



class Answer:
    answer_url = None
    # session = None
    soup = None

    def __init__(self, answer_url, question=None, author=None, upvote=None, content=None):

        self.answer_url = answer_url
        if question != None:
            self.question = question
        if author != None:
            self.author = author
        if upvote != None:
            self.upvote = upvote
        if content != None:
            self.content = content

    def parser(self):
        try:
            r = requests.get(self.answer_url, timeout=1)
        except requests.exceptions.ReadTimeout:
            raise requests.exceptions.ReadTimeout
        soup = BeautifulSoup(r.content, "html.parser")
        self.soup = soup

    def get_question(self):
        if hasattr(self, "question"):
            return self.question
        else:
            if self.soup == None:
                try:
                    self.parser()
                except:
                    raise requests.exceptions.ReadTimeout
            soup = self.soup
            question_link = soup.find("h2", class_="zm-item-title zm-editable-content").a
            url = "http://www.zhihu.com" + question_link["href"]
            title = question_link.string.encode("utf-8")
            question = Question(url, title)
            return question

    def get_author(self):
        if hasattr(self, "author"):
            return self.author
        else:
            if self.soup == None:
                try:
                    self.parser()
                except:
                    raise requests.exceptions.ReadTimeout
            soup = self.soup
            if soup.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                author_url = None
                author = User(author_url)
            else:
                author_tag = soup.find("div", class_="zm-item-answer-author-info").find_all("a")[1]
                author_id = author_tag.string.encode("utf-8")
                author_url = "http://www.zhihu.com" + author_tag["href"]
                author = User(author_url, author_id)
            return author

    def get_upvote(self):
        if hasattr(self, "upvote"):
            return self.upvote
        else:
            if self.soup == None:
                try:
                    self.parser()
                except:
                    raise requests.exceptions.ReadTimeout
            soup = self.soup
            count = soup.find("span", class_="count").string
            if count[-1] == "K":
                upvote = int(count[0:(len(count) - 1)]) * 1000
            elif count[-1] == "W":
                upvote = int(count[0:(len(count) - 1)]) * 10000
            else:
                upvote = int(count)
            return upvote

    def get_content(self):
        if hasattr(self, "content"):
            return self.content
        else:
            if self.soup == None:
                try:
                    self.parser()
                except:
                    raise requests.exceptions.ReadTimeout
            soup = BeautifulSoup(self.soup.encode("utf-8"), "html.parser")
            answer = soup.find("div", class_="zm-editable-content clearfix")
            soup.body.extract()
            soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
            soup.body.append(answer)
            content = soup
            self.content = content
            return content

    def to_txt(self):

        content = self.get_content()
        body = content.find("body")
        br_list = body.find_all("br")
        for br in br_list:
            br.insert_after(content.new_string("\n"))
        li_list = body.find_all("li")
        for li in li_list:
            li.insert_before(content.new_string("\n"))

        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8', 'ignore').encode('gbk', 'ignore')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8', 'ignore').encode('gbk', 'ignore')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "text"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write("\n\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write(self.get_question().get_title() + "\n\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8', 'ignore').encode('gbk', 'ignore')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "wt")
            f.write(self.get_question().get_title() + "\n\n")
        if platform.system() == 'Windows':
            f.write("作者: ".decode('utf-8', 'ignore').encode('gbk', 'ignore') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8', 'ignore').encode('gbk', 'ignore') + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("gbk", 'ignore'))
            link_str = "原链接: ".decode('utf-8', 'ignore').encode('gbk', 'ignore')
            f.write("\n" + link_str + self.answer_url.decode('utf-8', 'ignore').encode('gbk', 'ignore'))
        else:
            f.write("作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("utf-8", 'ignore'))
            f.write("\n" + "原链接: " + self.answer_url)
        f.close()

    def to_md(self):
        content = self.get_content()
        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8').encode('gbk', 'ignore')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8', 'ignore').encode('gbk', 'ignore')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("# " + self.get_question().get_title() + "\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8', 'ignore').encode('gbk', 'ignore')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "wt")
            f.write("# " + self.get_question().get_title() + "\n")
        if platform.system() == 'Windows':
            f.write("### 作者: ".decode('utf-8', 'ignore').encode('gbk', 'ignore') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8', 'ignore').encode('gbk', 'ignore') + str(self.get_upvote()) + "\n")
        else:
            f.write("### 作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n")
        text = html2text.html2text(content.decode('utf-8', 'ignore')).encode("utf-8", 'ignore')

        r = re.findall(r'\*\*(.*?)\*\*', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'_(.*)_', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'!\[\]\((?:.*?)\)', text)
        for i in r:
            text = text.replace(i, i + "\n\n")

        if platform.system() == 'Windows':
            f.write(text.decode('utf-8').encode('gbk', 'ignore'))
            link_str = "\n---\n#### 原链接: ".decode('utf-8', 'ignore').encode('gbk', 'ignore')
            f.write(link_str + self.answer_url.decode('utf-8', 'ignore').encode('gbk', 'ignore'))
        else:
            f.write(text)
            f.write("\n---\n#### 原链接: " + self.answer_url)
        f.close()

    def get_visit_times(self):
        if self.soup == None:
            try:
                self.parser()
            except:
                raise requests.exceptions.ReadTimeout
        soup = self.soup
        for tag_p in soup.find_all("p"):
            if "所属问题被浏览" in tag_p.contents[0].encode('utf-8', 'ignore'):
                return int(tag_p.contents[1].contents[0])

    def get_voters(self):
        if self.soup == None:
            try:
                self.parser()
            except:
                raise requests.exceptions.ReadTimeout
        soup = self.soup
        data_aid = soup.find("div", class_="zm-item-answer ")["data-aid"]
        request_url = 'http://www.zhihu.com/node/AnswerFullVoteInfoV2'
        # if session == None:
        #     create_session()
        # s = session
        # r = s.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)})
        r = requests.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)}, timeout=1)
        soup = BeautifulSoup(r.content, "html.parser")
        voters_info = soup.find_all("span")[1:-1]
        if len(voters_info) == 0:
            return
            yield
        else:
            for voter_info in voters_info:
                if voter_info.string == ( u"匿名用户、" or u"匿名用户"):
                    voter_url = None
                    yield User(voter_url)
                else:
                    voter_url = "http://www.zhihu.com" + str(voter_info.a["href"])
                    voter_id = voter_info.a["title"].encode("utf-8", 'ignore')
                    yield User(voter_url, voter_id)


class Collection:
    url = None
    # session = None
    soup = None

    def __init__(self, url, name=None, creator=None):
        if not re.compile(r"(http|https)://www.zhihu.com/collection/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a collection url.")
        else:
            self.url = url
            # print 'collection url',url
            if name != None:
                self.name = name
            if creator != None:
                self.creator = creator
    def parser(self):
        r = requests.get(self.url, timeout=1)
        soup = BeautifulSoup(r.content, "html.parser")
        self.soup = soup

    def get_name(self):
        if hasattr(self, 'name'):
            if platform.system() == 'Windows':
                return self.name.decode('utf-8', 'ignore').encode('gbk', 'ignore')
            else:
                return self.name
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            self.name = soup.find("h2", id="zh-fav-head-title").string.encode("utf-8").strip()
            if platform.system() == 'Windows':
                return self.name.decode('utf-8', 'ignore').encode('gbk', 'ignore')
            return self.name

    def get_creator(self):
        if hasattr(self, 'creator'):
            return self.creator
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            creator_id = soup.find("h2", class_="zm-list-content-title").a.string.encode("utf-8", 'ignore')
            creator_url = "http://www.zhihu.com" + soup.find("h2", class_="zm-list-content-title").a["href"]
            creator = User(creator_url, creator_id)
            self.creator = creator
            return creator

    def get_all_answers(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        answer_list = soup.find_all("div", class_="zm-item")
        if len(answer_list) == 0:
            print "the collection is empty."
            return
            yield
        else:
            question_url = None
            question_title = None
            for answer in answer_list:
                if not answer.find("p", class_="note"):
                    question_link = answer.find("h2")
                    if question_link != None:
                        question_url = "http://www.zhihu.com" + question_link.a["href"]
                        question_title = question_link.a.string.encode("utf-8", 'ignore')
                    question = Question(question_url, question_title)
                    answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a["href"]
                    author = None

                    if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                        author_url = None
                        author = User(author_url)
                    else:
                        author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
                        author_id = author_tag.string.encode("utf-8", 'ignore')
                        author_url = "http://www.zhihu.com" + author_tag["href"]
                        author = User(author_url, author_id)
                    yield Answer(answer_url, question, author)
            i = 2
            while True:
                r = requests.get(self.url + "?page=" + str(i), timeout=1)
                answer_soup = BeautifulSoup(r.content, "html.parser")
                answer_list = answer_soup.find_all("div", class_="zm-item")
                if len(answer_list) == 0:
                    break
                else:
                    for answer in answer_list:
                        if not answer.find("p", class_="note"):
                            question_link = answer.find("h2")
                            if question_link != None:
                                question_url = "http://www.zhihu.com" + question_link.a["href"]
                                question_title = question_link.a.string.encode("utf-8",'ignore')
                            question = Question(question_url, question_title)
                            answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a[
                                "href"]
                            author = None
                            if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                                # author_id = "匿名用户"
                                author_url = None
                                author = User(author_url)
                            else:
                                author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
                                author_id = author_tag.string.encode("utf-8", 'ignore')
                                author_url = "http://www.zhihu.com" + author_tag["href"]
                                author = User(author_url, author_id)
                            yield Answer(answer_url, question, author)
                i = i + 1

    def get_top_i_answers(self, n):
        j = 0
        answers = self.get_all_answers()
        for answer in answers:
            j = j + 1
            if j > n:
                break
            yield answer