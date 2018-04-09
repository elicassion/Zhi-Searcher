import jieba
import sys, os, lucene, threading, time, re, urlparse
from datetime import datetime
from BeautifulSoup import BeautifulSoup

def analyze_con(root,num):
    a_index = open('a_index.txt','r')
    qst_ans={}
    for line in a_index:
        line_num = line[:-2]
        qst_num = line_num.split('|||')[0]
        ans_num = line_num.split('|||')[1]
        if qst_ans.has_key(qst_num):
            qst_ans[qst_num].append(ans_num)
        else:
            qst_ans[qst_num]=[ans_num]

    f = open('q_index.txt','r')
    folder = 'analyzed_zhihu'
    if not os.path.exists(folder):
        os.mkdir(folder)
    count = 0

    for line in f:
        qst_num = line[:-2]


        folder_qst = os.path.join(folder, 'Question_' + qst_num)
        if not os.path.exists(folder_qst):
            os.mkdir(folder_qst)
        else:
            continue
        print "analyzing", qst_num
        folder_ans = os.path.join(folder_qst, 'Answer')
        root_ans = os.path.join(root, 'Question_' + qst_num, 'Answer')
        if os.path.exists(root_ans) and not os.path.exists(folder_ans):
            os.mkdir(folder_ans)

        path = os.path.join(root, 'Question_' + qst_num, 'q.txt')
        file = open(path)
        contents_read = unicode(file.read(), 'gbk')
        file.close()

        contents = contents_read.split('\r\n|||\r\n')
        contents_ana = ""
        for i in range(6):
            try:
                if i<2:
                    seg_list = jieba.cut(contents[i])
                    contents_ana = contents_ana + " ".join(seg_list)
                elif i==2:
                    contents_tmp = ""
                    label_list = contents[i].split('\t')
                    for element in label_list:
                        seg_list = jieba.cut(element)
                        contents_tmp = contents_tmp+" ".join(seg_list)+' | '
                    contents_ana = contents_ana + contents_tmp
                    contents_ana = contents_ana + '\r\n|||\r\n' + " ".join(contents[i].split('\t'))
                elif i==5:
                    if qst_ans.has_key(qst_num):
                        num_tmp = str(len(qst_ans[qst_num]))
                    else:
                        num_tmp = "0"
                    contents_ana = contents_ana + num_tmp
                else:
                    contents_ana = contents_ana + contents[i]
                contents_ana = contents_ana+'\r\n|||\r\n'
            except:
                continue
        savename = 'q.txt'
        sub_f = open(os.path.join(folder_qst, savename), 'w')
        sub_f.write(contents_ana.encode('gbk'))
        sub_f.close()

        if qst_ans.has_key(qst_num):
            for ans_num in qst_ans[qst_num]:
                path = os.path.join(root_ans, ans_num+'.txt')
                file = open(path)
                contents_read = unicode(file.read(), 'gbk')
                file.close()

                contents = contents_read.split('\r\n|||\r\n')
                contents_ana = ""
                for i in range(3):
                    try:
                        if i==0:
                            seg_list = jieba.cut(contents[i])
                            contents_ana = contents_ana + " ".join(seg_list)
                        else:
                            contents_ana = contents_ana + contents[i]
                        contents_ana = contents_ana+'\r\n|||\r\n'
                    except:
                        continue
                savename = ans_num+'.txt'
                sub_f = open(os.path.join(folder_ans, savename), 'w')
                sub_f.write(contents_ana.encode('gbk'))
                sub_f.close()

        count=count+1
        if(count>=num):
            break

    f.close()

start = time.clock()
analyze_con('Zhihu',100000)
end = time.clock()-start
print end
