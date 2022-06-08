from pickle import FALSE
import nltk
import sys
import string

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP
NP -> N | AdjP NP | Det NP | N PP
VP -> V | V NP | V NP PP | V PP | AdvP NP | PP Adv | V Adv
AdjP -> Adj | Adj AdjP
AdvP -> Adv | Adv V
PP -> P NP | V P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    words = nltk.word_tokenize(sentence)
    alphabet = list(string.ascii_lowercase)
    lower_words = []
    for word in words:
        lower_word = word.lower()
        chars = [char for char in lower_word]
        alphabetical = False
        for char in chars:
            if char in alphabet:
                alphabetical = True
        if alphabetical == True:
            lower_words.append(lower_word)
    return lower_words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    noun_phrases_subtrees = []
    extra_subtrees = 0
    for subtree in tree.subtrees(lambda tree: tree.label() == "NP"):
        for stree in subtree.subtrees(lambda s: s.label() == "NP"):
            extra_subtrees += 1
        if extra_subtrees == 1:
            noun_phrases_subtrees.append(subtree)
        extra_subtrees = 0
    return noun_phrases_subtrees



if __name__ == "__main__":
    main()
