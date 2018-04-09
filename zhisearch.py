# -*- coding: gbk -*-
import web
from web import form
import urllib2
import os
import searcher_ans
import searcher_qst
import codecs
from lucene import initVM

RESULT_PER_PAGE = 30
searchResult = []
lastQuery = ''
lastQueryType ='qst'
lastPage = -1

urls = (
    '/', 'index_qst',
    '/ans', 'index_ans',
    '/qstres', 'qst_res',
    '/ansres', 'ans_res',
    '/topictree', 'topic_tree'
)


render = web.template.render('templates/') # your templates


def qstSearch(command, prior, page, RPP):
    if searcher_qst.vm == None:
        searcher_qst.vm = initVM()
    searcher_qst.vm.attachCurrentThread()
    return searcher_qst.Searchfile(command, prior, page, RPP)

def ansSearch(command, prior, page, RPP):
    if searcher_ans.vm == None:
        searcher_ans.vm = initVM()
    searcher_ans.vm.attachCurrentThread()
    return searcher_ans.Searchfile(command, prior, page, RPP)

class topic_tree:
    def GET(self):
        tree_folder = 'Tree'
        cur_node = '19776749'
        userData = web.input()
        if userData.has_key('Node'):
            cur_node = userData.Node

        node_folder = cur_node
        info_folder = os.path.join(tree_folder, node_folder)

        itself_filename = os.path.join(info_folder, 'itself.txt')
        children_filename = os.path.join(info_folder, 'children.txt')
        parent_filename = os.path.join(info_folder, 'parent.txt')

        itself_file = open(itself_filename, 'r')
        children_file = open(children_filename, 'r')
        parent_file = open(parent_filename, 'r')


        itself_info = {}
        children_info = {}
        parent_info = {}

        itself_list = unicode(itself_file.read(),'gbk').split('\r\n')

        # l1 = itself_list[0].decode('utf8').encode('gbk')
        # l2 = itself_list[0].decode('utf8').encode('gbk')
        itself_num = itself_list[1].split('/')[4]
        itself_info[itself_num] = [itself_list[0], itself_list[1]]

        children_list = children_file.read().split('\r\n')
        if not children_list[0] == 'None':
            i = 0
            while i < len(children_list) - 1:
                children_num = children_list[i+1].split('/')[4]
                children_info[children_num] = [children_list[i], children_list[i+1]]
                i = i + 2



        parent_list = unicode(parent_file.read(),'gbk').split('\r\n')
        if not parent_list[0] == 'None':
            i = 0
            while i < len(parent_list) - 1:
                parent_num = parent_list[i+1].split('/')[4]
                parent_info[parent_num] = [parent_list[i], parent_list[i+1]]
                i = i + 2
        return render.topic_tree(itself_info, children_info, parent_info)

class index_qst:
    def GET(self):
        return render.index_qst()

class index_ans:
    def GET(self):
        return render.index_ans()

class qst_res:
    def GET(self):
        global lastQuery, searchResult, RESULT_PER_PAGE, lastPage
        userData = web.input()
        if not userData.has_key('Query'):
            return render.qst_result('', [], 0, 1, RESULT_PER_PAGE)
        else:
            if not userData.Query:
                return render.qst_result('', [], 0, 1, RESULT_PER_PAGE)
        if userData.has_key('pg'):
            page = int(userData.pg)
        else:
            page = 1
        if not userData.has_key('select_prior'):
            prior = 'None'
        else:
            prior = userData.select_prior
        searchResult, totalResults = qstSearch(userData.Query, prior, page, RESULT_PER_PAGE)
        lastQuery = userData.Query
        lastQueryType = 'qst'
        lastPage = page
        
        return render.qst_res(lastQuery, searchResult, totalResults, lastPage, RESULT_PER_PAGE, prior)

class ans_res:
    def GET(self):
        global lastQuery, searchResult, RESULT_PER_PAGE, lastPage
        userData = web.input()
        if userData.has_key('pg'):
            page = int(userData.pg)
        else:
            page = 1
        if not userData.has_key('select_prior'):
            prior = 'None'
        else:
            prior = userData.select_prior
        searchResult, totalResults = ansSearch(userData.Query, prior, page, RESULT_PER_PAGE)
        lastQuery = userData.Query
        lastQueryType = 'ans'
        lastPage = page
        
        return render.ans_res(lastQuery, searchResult, totalResults, lastPage, RESULT_PER_PAGE, prior)

if __name__ == "__main__":
    searcher_qst.init()
    searcher_ans.init()
    app = web.application(urls, globals())
    app.run()
