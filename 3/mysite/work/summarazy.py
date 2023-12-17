from rake_nltk import Rake
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize

import math
import string

from summarizer.sbert import SBertSummarizer


def summarize_text_with_rake(text, num_keywords=15):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()[:num_keywords]
    return ','.join(keywords[:4])
rake.extract_keywords_from_text(text)

def summarize_text_advanced(text, num_sentences=2):
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words("german") + list(string.punctuation) + ['was', 'das', 'wer', 'bin', 'in', 'der', 'die', 'und', 'was', 'ist', 'wenn', 'für', 'zu', 'nach', "auf", "um"])
    term_freq_doc = FreqDist([word for word in word_tokenize(text.lower()) if word.isalnum() and word not in stop_words])
    max_freq_doc = term_freq_doc.most_common(1)[0][1]
    num_docs = len(sentences)
    sentence_weights = {}
    for sentence in sentences:
        sentence_weight = 0
        for word in word_tokenize(sentence.lower()):
            if word.isalnum() and word not in stop_words:
                term_freq_sentence = FreqDist([word for word in word_tokenize(sentence.lower()) if word.isalnum() and word not in stop_words])[word]

                # Для каждого слова в предложении вычисляется вес, учитывающей частоту слова в предложении, частоту слова в документе, и логарифм отношения общего числа предложений к числу предложений, содержащих данное слово.
                weight = term_freq_sentence * 0.5 * (1 + term_freq_doc[word] / max_freq_doc) * math.log(num_docs / sum(1 for sent in sentences if word in word_tokenize(sent.lower()) and word.isalnum() and word not in stop_words))
                sentence_weight += weight
        sentence_weights[sentence] = sentence_weight
    top_sentences = sorted(sentence_weights, key=sentence_weights.get, reverse=True)[:num_sentences]
    return ' '.join(top_sentences[:4])


model = SBertSummarizer('paraphrase-MiniLM-L6-v2')
