'''
This file contains preprocessing code for Amazon reviews. It generates a txt file for each review for the RST parser
'''
import click
import string
import pandas as pd
from utils.utils import *


def update_brand_name(data: pd.DataFrame) -> pd.DataFrame:
    '''
    Detects brand name that has more than one word and replaces it with a new one-word brand name for parsing purpose.
    For example, Classic Brands would be CB, Tuft & Needles would be TN
    :param data: pandas dataframe containing product reviews
    :return: updated pandas dataframe
    '''
    for index, row in data.iterrows():
        if len(row['Brand'].split()) > 1:
            newbrand = ''.join([w[0] for w in row['Brand'].split() if w not in string.punctuation])
            replace = row['Brand']
            new_row = row['Text'].replace(replace, newbrand)
            data.at[index, 'Text'] = new_row
    return data


def write_df(data: pd.DataFrame, od: str):
    for index, row in data.iterrows():
        output_file_name = od + str(row['Id']) + '.txt'
        write_txt(output_file_name, row['Text'])


@click.command()
@click.option('-r', '--review', type=str, default='../data/preprocessed/brand_data_new.csv')
@click.option('-o', '--output_dir', type=str, default='../feng-2/feng-hirst-rst-parser/tmp2/')
def main(review, output_dir):
    reviews = pd.read_csv(review)
    new_reviews = update_brand_name(reviews)
    write_df(new_reviews, output_dir)


if __name__ == '__main__':
    main()




