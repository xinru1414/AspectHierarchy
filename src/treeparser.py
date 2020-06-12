'''
This file contains the tree parser for parsing RST results and functions to extract aspects (nouns and noun chunks)
'''
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
from pprint import pprint
from graphviz import Digraph
from collections import defaultdict, Counter
from utils.utils import *
import string
import re
import glob
import click
import spacy

'''
Tree Parser
'''
@dataclass
class TreeNode:
    val: str
    sub_nodes: List["TreeNode"] = field(default_factory=list)

    def pstr(self, level=0):
        base_level = '  ' * level
        if self.sub_nodes:
            cs = ",\n".join(n.pstr(level + 1) for n in self.sub_nodes)
            return f'{base_level}TreeNode {{\n{base_level}  "{self.val}",\n{base_level}  [\n{cs}\n{base_level}  ]}}'
        else:
            return f'{base_level}Val: "{self.val}"'

    @property
    def is_good_type(self):
        return '[N]' in self.val and '[S]' in self.val

    @property
    def is_type(self):
        return self.val.endswith('[N]') or self.val.endswith('[S]')

    def get_types(self):
        return re.findall("\[(.)\]", self.val)

    def get_relation(self):
        if "[N]" in self.val:
            return self.val[:-6]
        else:
            return self.val

    def rst_graph(self, name='rst_tree_graph'):
        d = Digraph(name)
        self.__add_to_rst_graph(d)
        return d

    def __add_to_rst_graph(self, g):
        g.node(str(id(self)), self.get_relation())
        for n_type, node in zip(self.get_types(), self.sub_nodes):
            g.edge(str(id(self)), str(id(node)), label=n_type)
            node.__add_to_rst_graph(g)

    def asp_graph(self, name='aspect_tree_graph'):
        d = Digraph(name)
        self.__add_to_asp_graph(d)
        return d

    def __add_to_asp_graph(self, g):
        g.node(str(id(self)), self.val)
        for node in self.sub_nodes:
            g.edge(str(id(self)), str(id(node)))
            node.__add_to_asp_graph(g)

    def to_pairs(self):
        pairs = []
        if self.is_type:
            assert len(self.sub_nodes) == 2, f'I need two sub trees! Val: "{self.val}" only have {len(self.sub_nodes)} sub trees:\n {self.sub_nodes}'
            first, second = self.sub_nodes[0], self.sub_nodes[1]
            if self.val.endswith('[N]'):
                first, second = second, first

            if first.is_type:
                pairs.extend(first.to_pairs())
            if second.is_type:
                pairs.extend(second.to_pairs())

            if not first.is_type and not second.is_type and self.is_good_type:
                pairs.append((first.val, second.val))
        return pairs

    def relation_to_paris(self, relation: str):
        pairs = []
        if self.is_type:
            assert len(self.sub_nodes) == 2, f'I need two sub trees! Val: "{self.val}" only have {len(self.sub_nodes)} sub trees:\n {self.sub_nodes}'
            first, second = self.sub_nodes[0], self.sub_nodes[1]
            if self.val.endswith('[N]'):
                first, second = second, first

            if first.is_type and self.get_relation() == relation:
                pairs.extend(first.to_pairs())
            if second.is_type and self.get_relation() == relation:
                pairs.extend(second.to_pairs())

            if not first.is_type and not second.is_type and self.is_good_type:
                pairs.append((first.val, second.val))
        return pairs

    def find_relations(self):
        relations = []
        if self.is_good_type:
            assert len(self.sub_nodes) == 2, f'I need two sub trees! Val: "{self.val}" only have {len(self.sub_nodes)} sub trees:\n {self.sub_nodes}'
            first, second = self.sub_nodes[0], self.sub_nodes[1]
            relations.extend(first.find_relations())
            relations.extend(second.find_relations())
            relations.append(self.get_relation())
        return relations

    def find_by_value(self, value):
        if self.val == value:
            return self
        for subnode in self.sub_nodes:
            subnode_result = subnode.find_by_value(value)
            if subnode_result is not None:
                return subnode_result
        return None

    def add_subnode(self, node):
        assert isinstance(node, TreeNode), 'only treenode can be added as a child'
        if node not in self.sub_nodes:
            self.sub_nodes.append(node)


def find_part_end(inp, start):
    end = start
    in_quote = False
    quote_type = None
    while in_quote or inp[end] not in {',', ']'}:
        if inp[end] in {"'", '"'}:
            if in_quote and inp[end] == quote_type:
                in_quote = not in_quote
            elif not in_quote:
                quote_type = inp[end]
                in_quote = True
        end += 1
        if inp[end] == '(' and not in_quote:
            end = find_matching_paren(inp, end)
    return end


def parse_list(inp):
    assert inp[0] == '[' and inp[-1] == ']'
    cur = 1

    parts = []

    while cur < len(inp) and inp[cur] != ']':
        end = find_part_end(inp, cur)
        parts.append(parse(inp[cur:end].strip()))
        cur = end + 1

    return parts


def find_matching_paren(inp, pos, openp='(', closep=')'):
    assert inp[pos] == openp
    count = 1
    cur = pos + 1
    while count != 0:
        if inp[cur] == openp:
            count += 1
        if inp[cur] == closep:
            count -= 1
        if count == 0:
            return cur
        cur += 1
    raise ValueError('Invalid string')


def parse(inp):
    if inp[0] == "'" or inp[0] == '"':
        return TreeNode(inp[1:-1])
    assert inp.startswith('ParseTree'), inp
    val, rest = inp.split(',', 1)
    assert rest[-1] == ')'
    rest = rest[:-1]
    return TreeNode(val[11:-1], parse_list(rest.strip()))


def generate_list(tree):
    if tree.sub_nodes:
        tree_nodes = tree.sub_nodes
    while tree_nodes:
        cur_node = tree_nodes.pop()
        if '[N]' in cur_node.val and '[S]' in cur_node.val:
            # print(cur_node.val)
            if cur_node.sub_nodes:
                tree_nodes.extend(cur_node.sub_nodes)

'''
Aspect Extraction
'''


def read_files(files, output_dir) -> List:
    '''
    Parses RST results and creates RST visualization (graph) for each Amazon review
    :param files: a list of RST parsed files
    :param output_dir: the output dir for created graphs
    :return: pairs:
    '''
    pairs = []
    for file in files:
        with open(file, 'r') as f:
            p = f.readline().strip()
            try:
                try:
                    tree = parse(p)
                except IndexError:
                    continue
                pairs.extend(tree.to_pairs())
                g = tree.rst_graph()
                output_file = output_dir + '/' + 'graphs/' + file[-20:-10]
                g.render(output_file, format='png')
            except AssertionError:
                # RST parser incorrect results
                continue
    return pairs


def read_relevant_parse_files_for_all_relations(files, relevant: Set, relations: List) -> Dict:
    '''
    Parses RST results and extracts clause pairs from relevant RST relations
    :param files: a list of RST parsed files
    :param relevant: a set of review ids
    :param relations: a list of relevant relations (see data/resources/relations)
    :return: a dictionary {key: review_id, value: List[Tuple[str, str]]}
    '''
    pairs = defaultdict(list)
    for file in files:
        for review in relevant:
            if str(review) in file:
                with open(file, 'r') as f:
                    p = f.readline().strip()
                    try:
                        try:
                            tree = parse(p)
                        except IndexError:
                            continue
                        for relation in relations:
                            if len(tree.relation_to_paris(relation)) > 0:
                                pairs[str(review)].extend(tree.relation_to_paris(relation))
                    except AssertionError:
                        continue
    return pairs


def get_noun_chunks(doc: spacy.tokens.doc.Doc) -> List:
    '''
    Extracts nouns and noun_chunks while filtering out pronouns
    :param doc: spacy.tokens.doc.Doc object
    :return: List of nouns and noun chunks
    '''
    chunks = []
    for chunk in doc.noun_chunks:
        if len(chunk) > 1:
            chunks.append(str(chunk))
        else:
            if str(chunk) not in ['I', 'i', 'Me', 'me', 'You', 'you', 'They', 'they', 'He', 'he', 'She', 'she', 'her', 'him', 'It', 'it', 'We', 'we', 'us']:
                chunks.append(str(chunk))
    return chunks


def get_noun_chunk_pairs(tree_pairs: List) -> List[Tuple[List]]:
    '''
    Extracts noun and noun chunk pairs
    :param tree_pairs: a list of RST clause pairs (see tree.to_pairs()). For example: [('This mattress is very comfortable ,', 'been sleeping great with no pain .'), ('I am waiting for hip replacement , could not sleep on my old mattress , to much pain .', 'First night with this mattress , no pain .')]
    :return: a list of noun and noun chunk pairs. eg: [(['This mattress'], ['no pain']), (['hip replacement', 'my old mattress', 'much pain'], ['First night', 'this mattress', 'no pain'])]
    '''
    noun_chunk_pairs = []
    nlp = spacy.load("en_core_web_sm")
    for n, s in tree_pairs:
        doc_n, doc_s = nlp(n), nlp(s)
        chunks_n, chunks_s = get_noun_chunks(doc_n), get_noun_chunks(doc_s)
        if len(chunks_n) > 0 and len(chunks_s) > 0:
            noun_chunk_pairs.append((chunks_n, chunks_s))
    return noun_chunk_pairs


def get_noun_chunk_pairs_with_meta(tree_pairs: Dict) -> Dict:
    '''
    Extracts noun and noun chunk pairs while also keeps track of meta data (such as review id, the RST clause pair that the noun pair is generated from)
    :param tree_pairs: a dictionary {key: review_id, value: clause pairs}
    :return: a dictionary {key: review_id, value:
                                            {key: 'clause_pairs', value: clause_pairs}
                                            {key: 'noun_pairs', value: noun_pairs}}
    '''
    noun_chunk_pairs = defaultdict(lambda: defaultdict(list))
    nlp = spacy.load("en_core_web_sm")
    for review_id, pair in tree_pairs.items():
        for n, s in pair:
            if 'Tuft & Needle' in n:
                n = n.replace('Tuft & Needle', 'T&N')
            if 'Tuft & Needle' in s:
                s = s.replace('Tuft & Needle', 'T&N')
            doc_n, doc_s = nlp(n), nlp(s)
            chunks_n, chunks_s = get_noun_chunks(doc_n), get_noun_chunks(doc_s)
            if len(chunks_n) > 0 and len(chunks_s) > 0:
                noun_chunk_pairs[review_id]['clause_pairs'].append((n,s))
                noun_chunk_pairs[review_id]['noun_pairs'].append((chunks_n, chunks_s))
                assert len(noun_chunk_pairs[review_id]['clause_pairs']) == len(noun_chunk_pairs[review_id]['noun_pairs'])
    return noun_chunk_pairs


def gen_list_of_pairs(pairs: List[Tuple[List]]) -> List[Tuple]:
    '''
    Extracts a list of pairs from the list of noun and noun chunk pairs generated by get_noun_chunk_pairs
    :param pairs: list of noun and noun chunk pairs (see get_noun_chunk_pairs)
    :return: a list of pairs. eg:[('This mattress', 'no pain'), ('hip replacement', 'First night'), ('hip replacement', 'this mattress'), ('hip replacement', 'no pain'), ('my old mattress', 'First night')]
    '''
    new_pairs = []
    for p in pairs:
        h = [(x, y) for x in p[0] for y in p[1]]
        new_pairs.extend(h)
    return new_pairs


def gen_list_of_pairs_with_meta(pairs: Dict) -> Dict:
    '''
    Extracts a list of pairs from the dictionary generated by get_noun_chunk_pairs_with_meta
    :param pairs: a dictionary (see get_noun_chunk_pairs_with_meta)
    :return: a dictionary {key: review_id, value:
                                            {key: 'clause_pairs', value: clause_pairs  <- List[Tuple[str, str]]}
                                            {key: 'noun_pair_candidate': value: noun_pairs <- List[Tuple[List[str], List[str]]]}
                                            {key: 'noun_pairs', value: a list of noun pairs <- List[List[Tuple[str, str]]}
    '''
    noun_chunk_pairs = defaultdict(lambda: defaultdict(list))
    for review_id, value in pairs.items():
        for p in value['noun_pairs']:
            h = [(x, y) for x in p[0] for y in p[1]]
            noun_chunk_pairs[review_id]['clause_pairs'] = value['clause_pairs']
            noun_chunk_pairs[review_id]['noun_pair_candidates'] = value['noun_pairs']
            noun_chunk_pairs[review_id]['noun_pairs'].append(h)
        assert (len(value['clause_pairs']) == len(value['noun_pairs']))
    return noun_chunk_pairs


def relation_based_pairs_with_meta(d: Dict, primary_aspects: List) -> Dict:
    '''
    Extracts the final list of valid aspect pairs from the dictionary generated by gen_list_of_pairs_with_meta
    A valid aspect pair satisfies the following conditions: 1) the first element of the aspect pair contains words in cared aspects
                                                            2) the second element of the aspect pair does not contain word 'mattress'
                                                            3) the first element and the second element do not contain the same word
    :param d: a dictionary (see gen_list_of_pairs_with_meta)
    :param primary_aspects: a list of cared aspects
    :return: a dictionary {key: review_id, value:
                                            {key: 'clause_pairs', value: List[str]}
                                            {key: 'relation_based_pairs, value: List[Tuple[str]]}}
    '''
    noun_chunk_pairs = defaultdict(lambda: defaultdict(list))
    for review_id, values in d.items():
        for j, item in enumerate(values['noun_pairs']):
            clause_set = False
            for value in item:
                if ((value[0] in primary_aspects) or (len([i for i in value[0].lower().split() if i in primary_aspects]) == 1)) and (
                        'mattress' not in value[1].lower().split()) and len(list(set(value[0].lower().split()) & set(value[1].lower().split()))) == 0:
                #if (value[0] in cared_aspects or len([i for i in value[0].lower().split() if i in cared_aspects]) > 0) and ('mattress' not in value[1].lower().split()):
                    if clause_set is False:
                        noun_chunk_pairs[review_id]['clause_pairs'].extend(values['clause_pairs'][j])
                        clause_set = True
                    noun_chunk_pairs[review_id]['relation_based_pairs'].append((value[0].lower(), value[1].lower()))
    return noun_chunk_pairs


def get_pairs_only(d: Dict, not_cared_aspects: List, determiners: List):
    '''
    Outputs the review ids, the aspect pairs and the clause pairs which the aspect pairs are extracted from
    Currently only used for a specific brand
    :param d: a dictionary (see relation_based_pairs_with_meta)
    :param not_cared_aspects: a list of generic words to filter out (see data/resources/not_cared_aspects)
    :param determiners: a list of determiners to filter out (see data/resources/determiners)
    :return:
    '''
    for key, item in d.items():
        clauses = item['clause_pairs']
        print(f'review id: {key} \nclauses: {clauses}')
        for x, y in item['relation_based_pairs']:
            x = ' '.join([i for i in x.split() if (i not in determiners) and (i not in not_cared_aspects)])
            y = ' '.join([i for i in y.split() if (i not in determiners) and (i not in not_cared_aspects)])
            if len(x) > 0 and len(y) > 0 and len(list(set(x.split()) & set(y.split()))) == 0:
                print(f'review id: {key} \n')
                print(f'aspect pairs: {(x, y)}')
                print(f'clauses: {clauses}')


def get_all_pairs(d: Dict, primary_aspects: List, not_cared_aspects: List, determiners: List) -> Set:
    '''
    Creates consise aspect pairs for aspect hierarchy generation from dictionary generated by relation_based_pairs_with_meta
    Currently only used for All, not specific brands
    :param d: a dictionary
    :param primary_aspects: a list of cared aspects (see data/resources/primary_aspects)
    :param not_cared_aspects: a list of not cared aspects to filter out (see data/resources/not_cared_aspects)
    :param determiners: a list of determiners to filter out (see data/resources/determiners)
    :return: a set of aspect pairs
    '''
    pairs = []
    ignore = not_cared_aspects + [i for i in string.punctuation]
    for key, value in d.items():
        for item in value['relation_based_pairs']:
            if item[0] in primary_aspects:
                x = item[0]
            else:
                x = [i for i in item[0].lower().split() if i in primary_aspects][0]
            y = ' '.join([i for i in item[1].lower().split() if (i not in determiners and i not in ignore)])
            if len(y) > 0 and y not in primary_aspects and y not in ignore:
                pairs.append((x, y))
    first = [item[0][1] for item in Counter(pairs).most_common(20)]
    n = set([(x, y) for (x, y) in pairs if y in first])
    return n


def get_trees(s: List) -> List[TreeNode]:
    '''
    Creates aspect hierarchy tree from a list of aspect pairs
    :param s: a list of aspect pairs
    :return: a list of TreeNodes
    '''
    nodes = {}
    is_not_root = set()
    for x, y in s:
        if x not in nodes:
            nodes[x] = TreeNode(x)
        if y not in nodes:
            nodes[y] = TreeNode(y)
        node_x = nodes[x]
        node_y = nodes[y]
        if node_y.find_by_value(x) is not None:
            print(f'We have a cycle at {y}!!!')
        else:
            node_x.add_subnode(node_y)
        is_not_root.add(y)
    return [x for x in nodes.values() if x.val not in is_not_root]


@click.command()
@click.option('-i', '--inputdir', 'input_dir', type=str, default='../feng-2/feng-hirst-rst-parser/results2')
@click.option('-o', '--outputdir', 'output_dir', type=str, default='../rst_results')
def main(input_dir, output_dir):
    path = input_dir + '/*.parse'
    files = glob.glob(path)
    pairs = read_files(files, output_dir)

    noun_chunk_pairs = get_noun_chunk_pairs(pairs)
    pairs = gen_list_of_pairs(noun_chunk_pairs)

    save_pickle(f'{output_dir}/noun_pairs.pickle2', pairs)


def tests():
    s = """ParseTree('Elaboration[N][S]', [ParseTree('Elaboration[N][S]', [ParseTree('Elaboration[N][S]', [ParseTree('Elaboration[N][S]', ['This mattress is very comfortable ,', 'been sleeping great with no pain .']), ParseTree('Elaboration[N][S]', ['I am waiting for hip replacement , could not sleep on my old mattress , to much pain .', 'First night with this mattress , no pain .'])]), ParseTree('Elaboration[N][S]', [ParseTree('Joint[N][N]', ['Had the mattress for a couple weeks', 'and all is good .']), ParseTree('Contrast[S][N]', [ParseTree('Elaboration[N][S]', ['It took the mattress along time to get to the size', 'that it was supposed to be ,']), 'but it got there .'])])]), 'No complaints about this mattress , hopefully this will continue .'])"""
    tree = parse(s)
    pprint(f'RST tree {tree.pstr()}')
    pprint(f'RST relations {tree.find_relations()}')
    print(f"Contrast relation pairs \n{tree.relation_to_paris('Contrast')}")
    print(f'All pairs \n{tree.to_pairs()}')
    pairs = tree.to_pairs()
    noun_chunk_pairs = get_noun_chunk_pairs(pairs)
    print(f'Noun and Noun chunk pairs \n{noun_chunk_pairs}')
    new_pairs = gen_list_of_pairs(noun_chunk_pairs)
    print(f'List of Noun and Noun chunk pairs {new_pairs}')


if __name__ == '__main__':
    tests()
    #main()
