# gensim modules
from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import Doc2Vec

# numpy
import numpy

# shuffle
from random import shuffle

# logging
import logging
import os.path
import sys
# import cPickle as pickle
import pprint

program = os.path.basename(sys.argv[0])
logger = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))

class LabeledLineSentence(object):

    def __init__(self, sources):
        self.sources = sources

        flipped = {}

        # make sure that keys are unique
        for key, value in sources.items():
            if value not in flipped:
                flipped[value] = [key]
            else:
                raise Exception('Non-unique prefix encountered')

    def __iter__(self):
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    yield LabeledSentence(utils.to_unicode(line).split(), [prefix + '_%s' % item_no])

    def to_array(self):
        self.sentences = []
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    self.sentences.append(LabeledSentence(
                        utils.to_unicode(line).split(), [prefix + '_%s' % item_no]))
        return self.sentences

    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences


def d2v_onefile(onefile, outcsv, d2v_dim):
    sources = {onefile: 'SENT'}
    sentences = LabeledLineSentence(sources)
    model = Doc2Vec(min_count=1, window=10, size=d2v_dim, sample=1e-4, negative=5, workers=7)
    model.build_vocab(sentences.to_array())
    for epoch in range(50):
        logger.info('Epoch %d' % epoch)
        model.train(sentences.sentences_perm())
    feat_array = numpy.zeros((418, d2v_dim))
    for i in range(418):
        prefix = 'SENT_' + str(i)
        feat_array[i] = model.docvecs[prefix].tolist()
    numpy.savetxt(outcsv, feat_array, delimiter=",")


d2v_onefile('vword/trans.txt', 'tran_d2v.csv', 50)
d2v_onefile('vword/vword_emotion.txt', 'emotion_d2v.csv', 20)
d2v_onefile('vword/vword_headposee.txt', 'headpose_d2v.csv', 10)
d2v_onefile('vword/vword_gaze.txt', 'gaze_d2v.csv', 10)



