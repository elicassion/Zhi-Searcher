import jieba
import init1
import urllib2
import os
from lucene import \
    QueryParser, IndexSearcher, StandardAnalyzer, SimpleFSDirectory, File, \
    VERSION, initVM, Version, BooleanQuery, BooleanClause, Highlighter, \
    SimpleHTMLFormatter, QueryScorer, SimpleFragmenter, WhitespaceAnalyzer
searcher = None
analyzer = None
vm = None

def init():
    global searcher, analyzer, vm
    vm = initVM()
    STORE_DIR = "index_ans"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)

def parseCommand(command):
    allowed_opt = ['qst_name']
    command_dict = {}
    opt = 'ans_contents'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + " ".join(jieba.cut(value))
        else:
            command_dict[opt] = command_dict.get(opt, '') + ' ' + " ".join(jieba.cut(i))
    return command_dict

def storesort(store, prior):
    if prior == "like":
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

            if doc.get("ans_num") in scored:
                continue
            if not doc.get("ans_contents"):
                continue
            scored.append(doc.get("ans_num"))

            contents =  doc.get("ans_contents").replace(' ','')
            returnfile.append(contents)
            name =  doc.get("qst_name").replace(' ','')
            returnfile.append(name)

            returnfile.append(doc.get("ans_author"))
            returnfile.append(int(doc.get("ans_like")))
            returnfile.append(doc.get("qst_num"))
            returnfile.append(doc.get("ans_num"))

            store.append(returnfile)

        store = storesort(store, prior)
        return store


def Searchfile(command, prior, page, RPP):
    STORE_DIR = "index_ans"
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(directory, True)
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    store = run(searcher, analyzer,command, prior)
    searcher.close()
    start = (page - 1) * RPP
    end = start + RPP

    return store[start:end], len(store)

"""if __name__ == '__main__':
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        #prior = raw_input("Prior:")
        command = unicode(command, 'gbk')
        if command == '':
            exit
        print "Searching for:", command
        store = Searchfile(command)

        print "The total results number is:",len(store)
        for i in range(len(store)):
            print "------------------------"
            print 'ans_contents:', store[i][0]
            print 'qst_name:', store[i][1]
            print 'ans_author:', store[i][2]
            print 'ans_like:', store[i][3]
            print 'qst_num:', store[i][4]
            print 'ans_num:', store[i][5]"""
