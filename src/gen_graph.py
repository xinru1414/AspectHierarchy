'''
This file contains code for generating aspect hierarchies

Command line input:
    -b: brand name, should be one of ths list: [Casper, Classic, Zinus, Serta, TN, All]
    -o: dir for generated graph

Output:
    generated graph in png format
'''
from aspect_hierarchy import *
from typing import List
import click


def define_brand_pairs(name: str) -> List:
    # Casper
    casper_pri = ['no pain', 'price', 'smell', 'memory foam', 'plastic cover']
    casper_p1 = [('casper', i) for i in casper_pri]
    casper_p2 = [('no pain', i) for i in ['back', 'hip', 'arthritis', 'neck', 'shoulder', 'side', 'difference', 'physical therapy']]
    casper_p2.extend([('price', i) for i in ['loan']])
    casper_p2.extend([('plastic cover', i) for i in ['take time']])
    casper_p2.extend([('smell', i) for i in  ['strong chemical smell', 'typical new mattress smell', 'no gross smell']])
    casper_p2.extend([('memory foam', i) for i in ['comfort']])
    Casper = casper_p1 + casper_p2

    # T&N
    tn_pri = ['pain', 'memory foam topper', 'price']
    tn_p1 = [('tuft&needle', i) for i in tn_pri]
    tn_p2 = [('pain', i) for i in ['lower back pain', 'shoulder pain']]
    tn_p2.extend(('price', i) for i in ['reasonable'])
    TN = tn_p1 + tn_p2

    # Zinus
    zinus_pri = ['price', 'smell', 'topper', 'plastic']
    zinus_p1 = [('zinus', i) for i in zinus_pri]
    zinus_p2 = [('topper', i) for i in ['memory foam', 'medium firm natural latex', 'support foam', 'some cushion', 'latex']]
    zinus_p2.extend(('smell', i) for i in ['light', 'chemical', 'typical', 'no smell', 'not last long', 'box'])
    zinus_p2.extend(('price', i) for i in ['main reason', 'lower', 'prime day', 'great product'])
    zinus_p2.extend(('plastic', i) for i in ['no permanent odor', 'febreze'])
    Zinus = zinus_p1 + zinus_p2

    # Serta
    serta_pri = ['plastic', 'smell','pain', 'memory foam topper', 'price']
    serta_p1 = [('serta', i) for i in serta_pri]
    serta_p2 = [('memory foam topper', i) for i in ['support', 'more memory effect', 'irregular cushioning', 'softness', 'hybrid']]
    serta_p2.extend(('price', i) for i in ['full price'])
    serta_p2.extend(('plastic', i) for i in ['shipment', 'thick'])
    serta_p2.extend(('smell', i) for i in ['long lasting', 'chemical smell', 'migraine'])
    serta_p2.extend(('pain', i) for i in ['second night', 'pressure point pain', 'back pain'])
    Serta = serta_p1 + serta_p2

    # Classic Brands
    classic_pri = ['pain', 'price', 'smell', 'plastic', 'topper']
    classic_p1 = [('classic brands', i) for i in classic_pri]
    classic_p2 = [('price', i) for i in ['reasonable price', 'deal','good quality', 'great investment', 'financing options', 'free delivery', 'warranty']]
    classic_p2.extend(('topper', i ) for i in['deep pockets', 'comfortable', 'firm', 'fewer night sweats', 'deterioration', 'lavender scent'] )
    classic_p2.extend(('plastic', i) for i in ['heavy duty', 'wrap'])
    classic_p2.extend(('pain', i) for i in ['back', 'shoulder', 'hip'])
    classic_p2.extend(('smell', i )for i in ['no off-gassing smell', 'slight', 'minor', 'lingering', 'chemical', 'paint-like', 'unpleasnt', 'strange', 'funny'])
    Classic = classic_p1 + classic_p2

    if name == 'Classic':
        brandpair = Classic
    elif name == 'Capser':
        brandpair = Casper
    elif name == 'Serta':
        brandpair = Serta
    elif name == 'TN':
        brandpair = TN
    elif name == 'Zinus':
        brandpair = Zinus
    elif name == 'All':
        brandpair = read_pickle('../data/resources/all_pairs')
    else:
        raise ValueError("Please enter a valid brand name from: Casper, TN, Classic, Zinus, Serta, All")
    return brandpair


@click.command()
@click.option('-b', '--brand', default='All')
@click.option('-o', '--output', default='../figs/')
def main(brand, output):
    brandpair = define_brand_pairs(brand)
    tree = get_trees(brandpair)
    g = tree[0].asp_graph()
    output_path = output + brand
    g.render(output_path, format='png')


if __name__ == '__main__':
    main()

