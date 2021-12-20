from nltk import tokenize
from operator import itemgetter
import math
from stop_words import get_stop_words
from collections import Counter

# global
# add here further words to be excluded
custom = ["!","'","£","$","%","&","(",")","?","^","*","+","/","-","ciò", "così", "c’è", "sé", "dopo", "quando", "mentre"]  
stop_words = get_stop_words("italian") + get_stop_words ("english") + custom

with open ("text.txt", "r", encoding = "UTF-8") as text:
    doc = text.read().lower()
    
def check_sent(word, sentences):
    final = [all([w in x for w in word]) for x in sentences] 
    sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    return int(len(sent_len))

def get_top_n(dict_elem, n):
    result = dict(sorted(dict_elem.items(), key = itemgetter(1), reverse = True)[:n])
    return result

def kw_sentiment(doc):
    
    total_sentences = tokenize.sent_tokenize(doc)
    
    doc = doc.replace(",", "").replace(".","")
    
    words = doc.split()
    
    for word in reversed(words):
        if word in stop_words:
            words.remove(word)
        
    total_word_length = len(words)
    
    total_sent_len = len(total_sentences)

    tf_score = dict(Counter(words))
    
    idf_score = dict(Counter(words))
        
    for k,v in idf_score.items():
        if v > 1:
            idf_score[k] =  check_sent(k, total_sentences)
        else:
            idf_score[k] = 1

    # dividing by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())

    # performing a log and divide
    idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())

    tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}

    end_result = get_top_n(tf_idf_score, 10)
    
    return end_result

if __name__ == '__main__':
    kw_sentiment(doc)
    
