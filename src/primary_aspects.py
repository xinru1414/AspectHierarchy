'''
This file contains code for generating primary aspect pairs

Commind line input:
    -p: path to aspect pairs generated from treeparser (see gen_list_of_pairs), default '../rst_results/noun_pairs.pickle2'
Output:
    Most common primary aspects are printed in the console
    The primary aspects in data/resources/primary_aspects are selected from these aspects
'''
from typing import List, Tuple, Set
from collections import Counter
from utils.utils import *
import click
import nltk


def mattress_pairs(l: List) -> List:
    '''
    Selects mattress aspect pairs i.e. 'mattress' in first element but not in the second element
    :param l: a list of aspect pairs
    :return: a list of filtered aspect pairs (mattress pairs)
    '''
    mattress_p = []
    for x, y in l:
        if 'mattress' in x.lower() and 'mattress' not in y.lower():
            mattress_p.append((x, y))
        if 'mattress' in y.lower() and 'mattress' not in x.lower():
            mattress_p.append((x, y))
    return mattress_p


def no_mattress_pairs(l: List) -> List:
    '''
    Selecting pairs that do not contain mattress in either of the elements
    :param l: a list of noun pairs
    :return:
    '''
    mattress_p = []
    for x, y in l:
        if 'mattress' not in x.lower() and 'mattress' not in y.lower() and 'mattresses' not in x.lower() and 'mattresses' not in y.lower():
            mattress_p.append((x, y))
    return mattress_p


def noun_pairs(l: List) -> List:
    '''
    Extracting nouns and noun phrases from a list of pairs
    :param l: a list of aspect pairs (mattress pairs)
    :return: a list of aspect pairs consisting of nouns and noun phrases (noun mattress pairs)
    '''
    np = []
    nountags = ['NN', 'NNS', 'NNP', 'NNPS']
    for x, y in l:
        x = nltk.pos_tag(nltk.word_tokenize(x))
        y = nltk.pos_tag(nltk.word_tokenize(y))
        nx = ' '.join([v[0] for v in x if v[1] in nountags])
        ny = ' '.join([v[0] for v in y if v[1] in nountags])
        if len(nx) > 0 and len(ny) > 0:
            np.append((nx, ny))
    return np


def clean_step(l: List) -> List:
    '''
    Initial cleaning of the candidate noun mattress pairs
    :param l: a list of noun pairs
    :return: a list of cleaned noun pairs
    '''
    nl = list()
    for x, y in l:
        if x != 've' and y != 've' and len(y.split()) <= 4 and len(x.split()) <= 4:
            if x == 'this mattress' or x == 'the mattress' or x == 'This mattress' or x == 'The mattress' or x == 'a mattress':
                x = 'mattress'
            if x == 'reviews':
                x = 'review'
            if y == 'reviews':
                y = 'review'
            if y == 'memory form mattress':
                y = 'memory foam mattress'
            if x == 'memory form mattress':
                x = 'memory foam mattress'
            if x == 'weeks':
                x = 'week'
            if y == 'weeks':
                y = 'week'
            nl.append((x, y))
    return nl


def most_common(l: List) -> List:
    '''
    Selecting the most common 100 second elements in the candidate noun mattress pairs
    :param l: a list of noun mattress pairs
    :return: a list of most common noun mattress pairs
    '''
    first = set([item[0][1] for item in Counter(l).most_common(100)])
    nl = [(x, y) for (x, y) in l if y in first]
    return nl


def keyword_map(keyword: str, relatedwords: List, l: List) -> Tuple[Set, List]:
    '''
    Selecting the most common 40 noun mattress pairs and change the first element of the pairs to 'mattress'
    :param keyword: mattress
    :param relatedwords: [mattress, mattresses]
    :param l: a list of most common noun mattress pairs
    :return:
    '''
    nl = list()
    for x, y in l:
        for item in relatedwords:
            if x == item:
                nl.append((keyword, y))
    first = [item[0][1] for item in Counter(nl).most_common(40)]
    nl = set([(x, y) for (x, y) in nl if y in first])
    return nl, first


def relavant_nmp(l: List, relavant: List, relatedwords: List, not_cared_aspects: List, determiners: List) -> Set:
    n = list()
    for x, y in l:
        if x in relavant and y not in relatedwords and y not in not_cared_aspects and len(y.split()) <= 4 and len(list(set(x.split()) & set(y.split()))) == 0:
            y = ' '.join([i for i in y.lower().split() if i not in determiners])
            n.append((x, y))
    print(len(n))
    first = [item[0][1] for item in Counter(n).most_common(120)]
    n = set([(x, y) for (x, y) in n if y in first])
    return n


@click.command()
@click.option('-p', '--pairs', default='../rst_results/noun_pairs.pickle2')
def main(pairs):
    npairs = read_pickle(pairs)
    new_smp = mattress_pairs(npairs)
    new_snmp = noun_pairs(new_smp)
    cnew_snmp = clean_step(new_snmp)
    most_common_cnew_snmp = most_common(cnew_snmp)
    most_common_mattress_cnew_snmp, _ = keyword_map('mattress', ['mattress', 'mattresses'],
                                                            most_common_cnew_snmp)
    print(f'Most common 40 primary aspects \n{most_common_mattress_cnew_snmp}')


if __name__ == '__main__':
    main()