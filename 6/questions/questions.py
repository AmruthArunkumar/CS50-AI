import nltk
import sys
import pathlib
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 3


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {}
    for path in pathlib.Path(directory).iterdir():
        if path.is_file():
            current_file = open(path, "r")
            name = pathlib.Path(path).stem + ".txt"
            files[name] = current_file.read()
            current_file.close()
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    punctuation = [punc for punc in string.punctuation]
    stopwords = nltk.corpus.stopwords.words("english")
    words = nltk.word_tokenize(document)
    lower_words = []
    for word in words:
        lower = word.lower()
        if lower not in stopwords and lower not in punctuation:
            lower_words.append(lower)
    return lower_words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = {}
    for document in documents:
        for word in documents[document]:
            if word not in words:
                words[word] = 0

    for word in words:
        ndcw = 0
        nd = 0
        for document in documents:
            nd += 1
            if word in documents[document]:
                ndcw += 1
        words[word] = math.log(nd/ndcw)

    return words


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    top_n_files = []
    files_with_tfidf_sums = {file: 0 for file in files.keys()}
    for file_name in files_with_tfidf_sums:
        for word in query:
            tf = files[file_name].count(word)
            idf = idfs[word]
            files_with_tfidf_sums[file_name] += (tf * idf)
    files_with_tfidf_sums = sorted(files_with_tfidf_sums.items(), key=lambda x: x[1], reverse=True)
    top_n_files = list(dict(files_with_tfidf_sums).keys())[:n]
    return top_n_files


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    top_n_sentences = []
    sentences_with_idf_sums = {sentence: 0 for sentence in sentences.keys()}
    for sentence_name in sentences_with_idf_sums:
        for word in query:
            idf = idfs[word]
            if word in sentences[sentence_name]:
                sentences_with_idf_sums[sentence_name] += idf
    sentences_with_idf_sums = sorted(sentences_with_idf_sums.items(), key=lambda x: x[1], reverse=True)
    x = sentences_with_idf_sums[0][1]
    top_sentences = {}
    for sentence in sentences_with_idf_sums:
        if sentence[0][-1] in ('.', '?', '!', '"'):
            if sentence[1] == x:
                top_sentences[sentence[0]] = sentence[1]*100
            elif len(top_sentences) < n:
                top_sentences[sentence[0]] = sentence[1]*100
    for sentence_name in top_sentences:
        qtd = 0
        for word in query:
            if word in sentences[sentence_name]:
                qtd += sentences[sentence_name].count(word)
        qtd = qtd/len(sentences[sentence_name])
        top_sentences[sentence_name] += qtd
    top_n_sentences = sorted(top_sentences.items(), key=lambda x: x[1], reverse=True)[:n]
    top_n_sentences = list(dict(top_n_sentences).keys())
    return top_n_sentences


if __name__ == "__main__":
    main()
