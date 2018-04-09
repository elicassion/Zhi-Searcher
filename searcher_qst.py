import jieba
import init1
import urllib2
import os
from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, BooleanQuery, BooleanClause, Highlighter, \
    SimpleHTMLFormatter, QueryScorer, SimpleFragmenter, WhitespaceAnalyzer, \
    Term, WildcardQuery
searcher = None
analyzer = None
vm = None

def init():
    global searcher, analyzer, vm
    vm = initVM()
    STORE_DIR = "index_qst"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)


def parseCommand(command):
    allowed_opt = ['qst_detail','qst_topic_blur','qst_topic_accu']
    command_dict = {}
    opt = 'qst_name'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            if opt in allowed_opt and value != '':
                if opt =="qst_topic_accu":
                    command_dict[opt] = value
                else:
                    command_dict[opt] = " ".join(jieba.cut(value))
        else:
            command_dict[opt] = " ".join(jieba.cut(i))
    print command_dict
    return command_dict

def storesort(store, prior):
    if prior == "answer":
        store_sorted = sorted(store, key=lambda s: s[5], reverse=True)
    elif prior == "follow":
        store_sorted = sorted(store, key=lambda s: s[4], reverse=True)
    elif prior == "browse":
        store_sorted = sorted(store, key=lambda s: s[3], reverse=True)
    else:
        store_sorted = store
    return store_sorted

def run(searcher, analyzer, command, prior):
        if command == '':
            return

        store = []

        command_dict = parseCommand(command)
        querys = BooleanQuery()
        for k,v in command_dict.iteritems():
            query = QueryParser(Version.LUCENE_CURRENT, k,
                                    analyzer).parse(v)
            querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = searcher.search(querys, 500000).scoreDocs

        scored = []

        for scoreDoc in scoreDocs:
            returnfile = []
            doc = searcher.doc(scoreDoc.doc)

            if doc.get("qst_num") in scored:
                continue
            if not doc.get("qst_name"):
                continue
            scored.append(doc.get("qst_num"))

            name =  doc.get("qst_name").replace(' ','')
            returnfile.append(name)
            detail = doc.get("qst_detail").replace(' ','')
            returnfile.append(detail)

            returnfile.append(doc.get("qst_topic_accu"))
            returnfile.append(int(doc.get("qst_browse")))
            returnfile.append(int(doc.get("qst_follow")))
            returnfile.append(int(doc.get("qst_ans")))
            returnfile.append(int(doc.get("qst_num")))

            store.append(returnfile)

        store = storesort(store, prior)
        return store


def Searchfile(command, prior, page, RPP):

    STORE_DIR = "index_qst"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    store = run(searcher, analyzer, command, prior)
    searcher.close()
    start = (page - 1) * RPP
    end = start + RPP

    return store[start:end], len(store)

"""if __name__ == '__main__':
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        prior = raw_input("Prior:")
        if prior == "":
            prior = "browse"
        command = unicode(command, 'gbk')
        if command == '':
            exit
        print "Searching for:", command
        store = Searchfile(command, prior)

        print "The total results number is:",len(store)
        for i in range(len(store)):
            print "------------------------"
            print 'qst_name:', store[i][0]
            print 'qst_detail:', store[i][1]
            print 'qst_topic:', store[i][2]
            print 'qst_browse:', store[i][3]
            print 'qst_follow:', store[i][4]
            print 'qst_ans:', store[i][5]
            print 'qst_num:', store[i][6]"""
