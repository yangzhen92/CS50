from nltk.tokenize import TweetTokenizer

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        self.positives = []                                 #正能量list
        self.negatives = []                                 #负能量list
                                             
        with open(positives) as lines:                      #以行的形式打开文档    
            for line in lines:
                if not line.startswith(';'):                #观察文档，若不以“;”开通则为单词
                    self.positives.append(line.strip())     #除去空格并录入list
        with open(negatives) as lines:
            for line in lines:
                if not line.startswith(';'):
                    self.positives.append(line.strip())
        # TODO

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        tokens = TweetTokenizer()                           #创建一个推特分词器的实例
        self.score = 0                                      #每条推特的分数 
        for word in tokens.tokenize(text):                  #对一条推特(str)进行分词后遍历
            if word.lower() in self.positives:              
                self.score += 1
            elif word.lower() in self.negatives:
                self.score -= 1
        # TODO
        return self.score
