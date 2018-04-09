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
        f = open('a_index.txt','r')
        for line in f:
            line_num = line[:-2]
            qst_num = line_num.split('|||')[0]
            ans_num = line_num.split('|||')[1]
            print "adding answer",ans_num
            try:
                path = os.path.join(root, 'Question_'+qst_num,'q.txt')
                file = open(path)
                contents_read = unicode(file.read(), 'gbk')
                file.close()
                contents = contents_read.split('\r\n|||\r\n')
                qst_name = contents[0]

                path = os.path.join(root, 'Question_'+qst_num, 'Answer', ans_num+'.txt')
                file = open(path)
                contents_read = unicode(file.read(), 'gbk')
                file.close()
                contents = contents_read.split('\r\n|||\r\n')

                ans_contents = contents[0]
                if(ans_contents!='None'):
                    ans_author = contents[1]
                    ans_like = contents[2]

                    answer = lucene.Document()
                    answer.add(lucene.Field("qst_name", qst_name,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                    answer.add(lucene.Field("ans_contents", ans_contents,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.ANALYZED))
                    answer.add(lucene.Field("ans_author", ans_author,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.NOT_ANALYZED))
                    answer.add(lucene.Field("ans_like",ans_like,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.NOT_ANALYZED))
                    answer.add(lucene.Field("qst_num",qst_num,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.NOT_ANALYZED))
                    answer.add(lucene.Field("ans_num",ans_num,
                                         lucene.Field.Store.YES,
                                         lucene.Field.Index.NOT_ANALYZED))
                    writer.addDocument(answer)
                else:
                    print "there is no contents in answer", ans_num
            except Exception, e:
                print "Failed in indexDocs:", e
        f.close()



if __name__ == '__main__':

    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        IndexFiles('analyzed_zhihu', "index_ans", lucene.WhitespaceAnalyzer(lucene.Version.LUCENE_CURRENT))
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
