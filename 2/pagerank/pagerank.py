import os
import random
import re
import sys
from decimal import *
from numpy.random import choice

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    #print(transition_model(corpus, "3.html", DAMPING))
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus.keys())
    model = dict((page, 0) for page in pages)
    getcontext().prec = 4

    links = list(corpus[page])
    if (len(links)) == 0:
        links = pages

    link_prob = float(Decimal(damping_factor) / Decimal(len(links)))
    for link in links:
        model[link] = link_prob

    random_prob = float(Decimal(1 - damping_factor) / Decimal(len(pages)))
    for page in pages:
        model[page] += random_prob

    for page in pages:
        model[page] = round(model[page], 4)

    sum = 0
    for value in list(model.values()):
        sum += value

    if sum < 1:
        while int(sum) != 1:
            model[random.choice(list(model.keys()))] += 0.0001
            sum += 0.0001
            sum = round(sum, 4)
    if sum > 1:
        while sum != 1:
            model[random.choice(list(model.keys()))] -= 0.0001
            sum -= 0.0001
            sum = round(sum, 4)

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    weights = []
    current_page = random.choice(pages)
    page_rank = dict((page, 0) for page in pages)
    total = 1
    page_rank[current_page] += 1
    getcontext().prec = 4

    for i in range(n):
        weights = list((transition_model(corpus, current_page, damping_factor)).values())
        current_page = choice(pages, p=weights)
        page_rank[current_page] += 1
        total += 1

    for page in pages:
        page_rank[page] = round(float(Decimal(page_rank[page]) / Decimal(total)), 4)

    sum = 0
    for value in list(page_rank.values()):
        sum += value
        sum = round(sum, 4)

    if sum < 1:
        while int(sum) != 1:
            page_rank[random.choice(list(page_rank.keys()))] += 0.0001
            sum += 0.0001
            sum = round(sum, 4)
    else:
        while sum != 1:
            page_rank[random.choice(list(page_rank.keys()))] -= 0.0001
            sum -= 0.0001
            sum = round(sum, 4)

    return page_rank


def linksTo(corpus, target):
    pages = []
    key_list = list(corpus.keys())
    val_list = list(corpus.values())
    i = 0
    for value in val_list:
        if target in value:
            pages.append(key_list[i])
        i += 1

    return pages


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    page_rank = dict((page, round(1/len(pages), 4)) for page in pages)

    while True:
        old_rank = page_rank.copy()

        for page in page_rank.keys():
            rank = round(((1 - damping_factor) / len(pages)), 4)
            summation = 0
            links = linksTo(corpus, page)
            for link in links:
                summation += round((old_rank[link] / len(corpus[link])), 4)

            rank += damping_factor * round(summation, 4)
            page_rank[page] = round(rank, 4)

        i = 0
        for page in pages:
            if abs(page_rank[page] - old_rank[page]) <= 0.001:
                i += 1

        if i == len(pages):
            break

    return page_rank


if __name__ == "__main__":
    main()
