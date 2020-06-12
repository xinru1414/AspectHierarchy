'''
This file contains utility functions
'''
from typing import List
import pickle


def save_pickle(filename: str, l: List):
    '''
    Saves a list into a pickle file
    :param filename: output file
    :param l: input list
    :return: None
    '''
    with open(filename, 'wb') as f:
        pickle.dump(l, f)


def read_pickle(filename: str) -> List:
    '''
    Reads from a pickle file and turn it into a list
    :param filename: input file
    :return: a list
    '''
    with open(filename, 'rb') as f:
        l = pickle.load(f)
    return l


def read_txt(filename: str) -> List:
    '''
    Read a txt file into a list
    The txt file should contain one word per line without any seperaters
    :param filename: input file
    :return: a list
    '''
    with open(filename, 'r') as f:
        l = f.read().splitlines()
    return l