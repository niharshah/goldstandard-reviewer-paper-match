# This Python file uses the following encoding: utf-8
import re
import unicodedata


###############################################################
# Helper file for TPMS
# The code is adapted from the original code by Laurent Charlin
###############################################################

def isUIWord(word):
    """
        Returns true if the word is un-informative
        (for now either a stopword or a single character word)
    """

    if len(word) <= 1:
        return True

    # List provided by Amit Gruber
    l = set(['a', 'about', 'above', 'accordingly', 'across', 'after', 'afterwards', 'again', \
             'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', \
             'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', \
             'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', \
             'around', 'as', 'aside', 'at', 'away', 'back', 'be', 'became', 'because', \
             'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', \
             'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', \
             'bottom', 'briefly', 'but', 'by', 'call', 'came', 'can', 'cannot', 'cant', \
             'certain', 'certainly', 'co', 'computer', 'con', 'could', 'couldnt', 'cry', \
             'de', 'describe', 'detail', 'do', 'does', 'done', 'down', 'due', 'during', \
             'each', 'edit', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', \
             'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', \
             'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', \
             'first', 'five', 'following', 'for', 'former', 'formerly', 'forty', 'found', \
             'four', 'from', 'front', 'full', 'further', 'gave', 'get', 'gets', 'give', \
             'given', 'giving', 'go', 'gone', 'got', 'had', 'hardly', 'has', 'hasnt', 'have', \
             'having', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', \
             'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', \
             'hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', \
             'it', 'its', 'itself', 'just', 'keep', 'kept', 'kg', 'knowledge', 'largely', \
             'last', 'latter', 'latterly', 'least', 'less', 'like', 'ltd', 'made', 'mainly', \
             'make', 'many', 'may', 'me', 'meanwhile', 'mg', 'might', 'mill', 'mine', 'ml', \
             'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', \
             'name', 'namely', 'nearly', 'necessarily', 'neither', 'never', 'nevertheless', \
             'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'normally', 'not', \
             'noted', 'nothing', 'now', 'nowhere', 'obtain', 'obtained', 'of', 'off', \
             'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', \
             'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'owing', 'own', 'part', \
             'particularly', 'past', 'per', 'perhaps', 'please', 'poorly', 'possible', \
             'possibly', 'potentially', 'predominantly', 'present', 'previously', \
             'primarily', 'probably', 'prompt', 'promptly', 'put', 'quickly', 'quite', \
             'rather', 're', 'readily', 'really', 'recently', 'refs', 'regarding', \
             'regardless', 'relatively', 'respectively', 'resulted', 'resulting', 'results', 'rst', \
             'said', 'same', 'second', 'see', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'serious', \
             'several', 'shall', 'she', 'should', 'show', 'showed', 'shown', 'shows', 'side', \
             'significantly', 'similar', 'similarly', 'since', 'sincere', 'six', 'sixty', \
             'slightly', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', \
             'sometimes', 'somewhat', 'somewhere', 'soon', 'specifically', 'state', 'states', \
             'still', 'strongly', 'substantially', 'successfully', 'such', 'sufficiently', \
             'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'theirs', 'them', \
             'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', \
             'therein', 'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', \
             'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', \
             'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', \
             'under', 'unless', 'until', 'up', 'upon', 'us', 'use', 'used', 'usefully', \
             'usefulness', 'using', 'usually', 'various', 'very', 'via', 'was', 'we', 'well', \
             'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', \
             'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', \
             'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'widely', \
             'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', \
             'yourself', 'yourselves'])

    if word in l:
        return True

        # if re.match('[0-9]*$', word):
    # return True

    return False


def tokenize(line):
    # space_regexp = re.compile('\s', re.U)
    # space_regexp_full = re.compile('\W', re.U)

    space_regexp = re.compile('[^a-zA-Z]')  # üñèéóãàáíøö¨úïäýâåìçôêßëîÁÅÇÉÑÖØÜ]')
    line = sanitize(line)  # sanitize returns unicode
    words = re.split(space_regexp, line)
    words = [x for x in words if len(x) > 0]

    return words


def sanitize(w):
    """
      sanitize (remove accents and standardizes)
    """

    # print w

    map = {'æ': 'ae',
           'ø': 'o',
           '¨': 'o',
           'ß': 'ss',
           'Ø': 'o',
           '\xef\xac\x80': 'ff',
           '\xef\xac\x81': 'fi',
           '\xef\xac\x82': 'fl'}

    # This replaces funny chars in map
    for char, replace_char in map.items():
        w = re.sub(char, replace_char, w)

    # w = unicode(w, encoding='latin-1')
    # w = str(w, encoding="utf-8")

    # This gets rite of accents
    w = ''.join((c for c in unicodedata.normalize('NFD', w) if unicodedata.category(c) != 'Mn'))

    return w
