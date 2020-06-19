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


@click.command()
@click.option('-b', '--brand', default='All')
@click.option('-o', '--output', default='../figs/')
def main(brand, output):
    brandpair = read_pickle(f'../data/resources/{brand}_pairs')
    tree = get_trees(brandpair)
    g = tree[0].asp_graph()
    output_path = output + brand
    g.render(output_path, format='png')


if __name__ == '__main__':
    main()

