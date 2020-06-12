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


def get_brand_name(name: str) -> str:
    if name == 'Classic':
        brand_name = 'Classic Brands'
    elif name == 'TN':
        brand_name = 'Tuft & Needle'
    elif name == 'Serta':
        brand_name = 'Serta'
    elif name == 'Casper':
        brand_name = 'Casper'
    elif name == 'Zinus':
        brand_name = 'Zinus'
    elif name == 'All':
        brand_name = 'All'
    else:
        raise ValueError("Please enter a valid brand name from: Casper, TN, Classic, Zinus, Serta, All")
    return brand_name


@click.command()
@click.option('-b', '--brand', default='TN')
@click.option('-p', '--path', default='../feng-2/feng-hirst-rst-parser/results2')
@click.option('-d', '--datafile', default='../data/preprocessed/brand_data_new.csv')
@click.option('-ca', '--resrouce_ca', default='../data/resources/cared_aspects')
@click.option('-na', '--resrouce_na', default='../data/resources/not_cared_aspects')
@click.option('-rl', '--resrouce_rl', default='../data/resources/relations')
@click.option('-dt', '--resrouce_dt', default='../data/resources/determiners')
def main(brand, path, datafile, resrouce_ca, resrouce_na, resrouce_rl, resrouce_dt):
    path = path + '/*.parse'
    files = glob.glob(path)
    data = pd.read_csv(datafile)

    brand = get_brand_name(brand)
    brand_full_review = get_data(brand, data)
    cared_aspects = read_txt(resrouce_ca)
    not_cared_aspects = read_txt(resrouce_na)
    determiners = read_txt(resrouce_dt)
    relations = read_txt(resrouce_rl)

    brand_pairs = read_relevant_parse_files_for_all_relations(files, brand_full_review, relations)
    brand_pairlist = gen_list_of_pairs_with_meta(get_noun_chunk_pairs_with_meta(brand_pairs))
    brand_relation_based_pairs_with_meta = relation_based_pairs_with_meta(brand_pairlist, cared_aspects)

    if brand == 'All':
        first = {('mattress', i) for i in cared_aspects}
        second = get_all_pairs(brand_relation_based_pairs_with_meta, cared_aspects, not_cared_aspects, determiners)
        total = first.union(second)
        save_pickle('../data/resources/all_pairs', total)
    else:
        get_pairs_only(brand_relation_based_pairs_with_meta)


if __name__ == '__main__':
    main()
