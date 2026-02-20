import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
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
    # if page has no outgoing links, then do probability 1-d
    if not corpus[page]:
        return {p: 1/len(corpus.keys()) for p in corpus}
    else: # if the page has outgoing links
        # everything has a baseline probability
        links = corpus[page]
        baseline = (1-damping_factor) / len(corpus.keys())
        prob = damping_factor / len(links)
        new_dist = {}
        for p in corpus:
            if p in links:
                new_dist[p] = baseline + prob
            else:
                new_dist[p] = baseline

        return new_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # random sample
    counts = {p: 0 for p in corpus.keys()}
    current_page = random.choice(list(corpus.keys()))
    for i in range(n):
        counts[current_page] +=1
        dist = transition_model(corpus, current_page, damping_factor)
        pages = list(dist.keys())
        weights = list(dist.values())
        current_page = random.choices(pages, weights = weights, k = 1)[0]

    proportions = {k: v / n for k, v in counts.items()}
    return proportions



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    ranks = {p: 1/n for p in corpus}
    while True:
        new_ranks = {}
        for page in corpus:
            total = (1- damping_factor) / n

            iteration_sum = 0
            for possible_linker in corpus:
                if page in corpus[possible_linker]:
                    iteration_sum += ranks[possible_linker] / len(corpus[possible_linker])
                elif len(corpus[possible_linker]) == 0:
                    iteration_sum += ranks[possible_linker] / n

            total += damping_factor * iteration_sum
            new_ranks[page] = total

        differences = [abs(new_ranks[p] - ranks[p]) for p in corpus]
        if max(differences) < 0.001:
            break
        ranks = new_ranks.copy()
    return ranks


if __name__ == "__main__":
    main()
