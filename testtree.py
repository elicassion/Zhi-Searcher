# -*- coding: utf-8 -*-
import os, codecs
def tree(cur_node):
    tree_folder = 'Tree'
    # cur_node = unicode('「根话题」', 'gbk' ,'ignore')
    # userData = web.input()
    # if userData.has_key('Node'):
    #     cur_node = userData.Query

    node_folder = cur_node
    info_folder = os.path.join(tree_folder, node_folder)

    itself_filename = unicode(os.path.join(info_folder, 'itself.txt'), 'gbk')
    children_filename = unicode(os.path.join(info_folder, 'children.txt'), 'gbk')
    parent_filename = unicode(os.path.join(info_folder, 'parent.txt'), 'gbk')

    itself_file = open(itself_filename, 'r')
    children_file = open(children_filename, 'r')
    parent_file = open(parent_filename, 'r')


    itself_info = {}
    children_info = {}
    parent_info = {}

    itself_list = itself_file.read().split('\r\n')
    itself_num = itself_list[1].split('/')[4]
    itself_info[itself_num] = [itself_list[0], itself_list[1]]
    print "/".join(itself_list[1].split('/')[:5])

    children_list = children_file.read().split('\r\n')
    # print children_list[0].decode('utf8').encode('gbk')
    # print children_list[1]
    if not children_list[0] == 'None':
        i = 0
        while i < len(children_list) - 1:
            children_num = children_list[i+1].split('/')[4]
            children_info[children_num] = [children_list[i], children_list[i+1]]
            i = i + 2


    parent_list = parent_file.read().split('\r\n')
    if not parent_list[0] == 'None':
        i = 0
        while i < len(parent_list) - 1:
            parent_num = parent_list[i+1].split('/')[4]
            parent_info[parent_num] = [parent_list[i], parent_list[i+1]]
            i = i + 2
    # print str(itself_info)
    # print str(children_info)
    # for k in children_info:
        # print children_info[k][0].decode('utf8').encode('gbk')
    # print str(parent_info)
    # return render.topic_tree(itself_info, children_info, parent_info)

tree('19776749')