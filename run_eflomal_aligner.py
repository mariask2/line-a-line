#!/usr/bin/env python3

from eflomal import read_text, write_text, align
from cefmaral import ibm_print
from tempfile import NamedTemporaryFile

import sys, argparse, random, pickle, tempfile, io

def do_align(f_name, rev_f_name, seed=None):
    print('Reading source/target sentences from %s...' %
                f_name,
              file=sys.stderr, flush=True)
    with open(f_name, 'r', encoding='utf-8') as f:
        src_sents_text = []
        trg_sents_text = []
        for i, line in enumerate(f):
            fields = line.strip().split(' ||| ')
            if len(fields) != 2:
                print('ERROR: line %d of %s does not contain a single |||'
                      ' separator, or sentence(s) are empty!' % (
                          i+1, args.joint_filename),
                      file=sys.stderr, flush=True)
                sys.exit(1)
            src_sents_text.append(fields[0])
            trg_sents_text.append(fields[1])
        src_text = '\n'.join(src_sents_text) + '\n'
        trg_text = '\n'.join(trg_sents_text) + '\n'
        src_sents_text = None
        trg_sents_text = None

        source_prefix_len = 0
        source_suffix_len = 0
        
        target_prefix_len = 0
        target_suffix_len = 0
        
        with io.StringIO(src_text) as f:
            src_sents, src_index = read_text(
                    f, True, source_prefix_len, source_suffix_len)
            n_src_sents = len(src_sents)
            src_voc_size = len(src_index)
            srcf = NamedTemporaryFile('wb')
            write_text(srcf, tuple(src_sents), src_voc_size)
            src_sents = None
            src_text = None

        with io.StringIO(trg_text) as f:
            trg_sents, trg_index = read_text(
                    f, True, target_prefix_len, target_suffix_len)
            trg_voc_size = len(trg_index)
            n_trg_sents = len(trg_sents)
            trgf = NamedTemporaryFile('wb')
            write_text(trgf, tuple(trg_sents), trg_voc_size)
            trg_sents = None
            trg_text = None
    """
    print("source")
    with open(f_name, 'r', encoding='utf-8') as f:
        src_sents, src_index = read_text(
                f, True, 0, 0)
        n_src_sents = len(src_sents)
        src_voc_size = len(src_index)
        srcf = NamedTemporaryFile('wb')
        write_text(srcf, tuple(src_sents), src_voc_size)
        src_sents = None
    
    print("target")
    with open(rev_f_name, 'r', encoding='utf-8') as f:
        trg_sents, trg_index = read_text(
                f, True, 0, 0)
        trg_voc_size = len(trg_index)
        n_trg_sents = len(trg_sents)
        trgf = NamedTemporaryFile('wb')
        write_text(trgf, tuple(trg_sents), trg_voc_size)
        trg_sents = None
    """
    
    fwd_links_file = NamedTemporaryFile('r+')
    rev_links_file = NamedTemporaryFile('r+')
    stat_file = NamedTemporaryFile('r+')
    print("start align")
    
    
    align(srcf.name, trgf.name, statistics_filename = stat_file.name, quiet=False, links_filename_fwd=fwd_links_file.name, links_filename_rev=rev_links_file.name)
    
    # Not using stat_file at the moment
    result = fwd_links_file.readlines()
    rev_result = rev_links_file.readlines()
                   
    fwd_links_file.close()
    rev_links_file.close()
    stat_file.close()
    srcf.close()
    trgf.close()
    
        
    """
    if discretize:
        ibm_print(aaa, reverse, output.fileno())
    else: # Not used at the moment, but keeping this for the future
        with open(output_prob, 'wb') as f:
            pickle.dump(aaa, f, -1)

    output.seek(0)
    result = []
    for line in output:
        result.append(line.decode('ascii').strip())
    """
    return result, rev_result


if __name__ == '__main__':
    res = do_align("efmaral/3rdparty/data/test.eng", "efmaral/3rdparty/data/test.hin")


