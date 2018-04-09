#!/usr/bin/env python

import jieba
import sys, os, lucene, threading, time, re, urlparse
from datetime import datetime
from BeautifulSoup import BeautifulSoup


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        store = lucene.SimpleFSDirectory(lucene.File(storeDir))
        writer = lucene.IndexWriter(store, analyzer, True,
                                    lucene.IndexWriter.MaxFieldLength.LIMITED)
        writer.setMaxFieldLength(1048576)
        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'optimizing index',
        threading.Thread(target=ticker.run).start()
        writer.optimize()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):
        f = open('q_index.txt','r')
        for line in f:
            qst_num = line[:-2]
#        for root, dirnames, filenames in os.walk(root):
#            for filename in filenames:
#                if not filename.endswith('.txt'):
#                    continue
            print "adding question",qst_num
            try:
                path = os.path.join(root, 'Question_'+qst_num,'q.txt')
                file = open(path)
                contents_read = unicode(file.read(), 'gbk')
                file.close()

                contents = contents_read.split('\r\n|||\r\n')
                qst_name = contents[0]
                qst_detail = contents[1]
                qst_topic_blur = contents[2]
                qst_topic_accu = contents[3]
                qst_browse = contents[4]
                qst_follow = contents[5]
                qst_ans = contents[6]

                qestion = lucene.Document()
                qestion.add(lucene.Field("qst_name", qst_name,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                qestion.add(lucene.Field("qst_detail", qst_detail,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                qestion.add(lucene.Field("qst_topic_blur", qst_topic_blur,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                qestion.add(lucene.Field("qst_topic_accu", qst_topic_accu,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.ANALYZED))
                qestion.add(lucene.Field("qst_browse",qst_browse,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.NOT_ANALYZED))
                qestion.add(lucene.Field("qst_follow", qst_follow,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.NOT_ANALYZED))
                qestion.add(lucene.Field("qst_ans", qst_ans,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.NOT_ANALYZED))
                qestion.add(lucene.Field("qst_num", qst_num,
                                     lucene.Field.Store.YES,
                                     lucene.Field.Index.NOT_ANALYZED))
                writer.addDocument(qestion)
            except Exception, e:
                print "Failed in indexDocs:", e
        f.close()



if __name__ == '__main__':

    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        IndexFiles('analyzed_zhihu', "index_qst", lucene.WhitespaceAnalyzer(lucene.Version.LUCENE_CURRENT))
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
