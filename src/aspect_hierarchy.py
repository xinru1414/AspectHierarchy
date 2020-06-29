'''
This file contains code for generating secondary aspect pairs

Command line input:
    -b: brand name, one of ths list of brands: [Casper, Classic, Zinus, Serta, TN, All]
    -p: path to RST parser results
    -d: path to Amazon Review data
    -ca: path to cared_aspects file
    -na: path to not_cared_aspects file
    -rl: path to relations file
    -dt: path to determines file

Output
'''
import pandas as pd
from typing import Tuple, Set
import click
from collections import Counter
from treeparser import *
from utils.utils import *


def get_data(name: str, d: pd.DataFrame) -> Set:
    if name == 'All':
        review_ids = set(d['Id'].tolist())
    else:
        data = d.loc[(d['Brand'] == name) & (d['ReviewRating'] >= 80)]
        review_ids = set(data['Id'].tolist())
    return review_ids


@click.command()
@click.option('-b', '--brand', default='All')
@click.option('-p', '--path', default='../feng-hirst-rst-parser/results')
@click.option('-d', '--datafile', default='../data/review/sample_data.csv')
@click.option('-ca', '--resrouce_ca', default='../data/resources/primary_aspects')
@click.option('-na', '--resrouce_na', default='../data/resources/not_cared_aspects')
@click.option('-rl', '--resrouce_rl', default='../data/resources/relations')
@click.option('-dt', '--resrouce_dt', default='../data/resources/determiners')
@click.option('-k', '--keyword', default='mattress')
def main(brand, path, datafile, resrouce_ca, resrouce_na, resrouce_rl, resrouce_dt, keyword):
    path = path + '/*.parse'
    files = glob.glob(path)
    data = pd.read_csv(datafile)

    brand_full_review = get_data(brand, data)
    cared_aspects = read_txt(resrouce_ca)
    not_cared_aspects = read_txt(resrouce_na)
    determiners = read_txt(resrouce_dt)
    relations = read_txt(resrouce_rl)

    brand_pairs = read_relevant_parse_files_for_all_relations(files, brand_full_review, relations)
    brand_pairlist = gen_list_of_pairs_with_meta(get_noun_chunk_pairs_with_meta(brand_pairs))
    brand_relation_based_pairs_with_meta = relation_based_pairs_with_meta(brand_pairlist, cared_aspects, keyword)
    if brand == 'All':
        first = {(keyword, i) for i in cared_aspects}
        second = get_all_pairs(brand_relation_based_pairs_with_meta, cared_aspects, not_cared_aspects, determiners)
        total = first.union(second)
        save_pickle(f'../data/brand/{brand}_pairs', total)
        print_brand_pairs_only(d=brand_relation_based_pairs_with_meta, not_cared_aspects=not_cared_aspects, determiners=determiners)
    else:
        first = {(brand, i) for i in cared_aspects}
        second = get_brand_pairs(d=brand_relation_based_pairs_with_meta, primary_aspects=cared_aspects, not_cared_aspects=not_cared_aspects, determiners=determiners)
        total = first.union(second)
        save_pickle(f'../data/brand/{brand}_pairs', total)
        # print out brand specific aspects for analysis purpose
        print_brand_pairs_only(d=brand_relation_based_pairs_with_meta, not_cared_aspects=not_cared_aspects, determiners=determiners)


if __name__ == '__main__':
    main()
