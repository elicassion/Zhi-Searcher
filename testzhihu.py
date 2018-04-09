# -*- coding: utf-8 -*-
from zhihu import Question
from zhihu import Answer
from zhihu import User
from zhihu import Collection
import requests

url = "https://www.zhihu.com/question/19550321/answer/14240492"
ans = Answer(url)
print ans.get_content().find('body').get_text()
input()