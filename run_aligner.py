#!/usr/bin/env python3

from efmaral import align
from cefmaral import ibm_print

import sys, argparse, random, pickle, tempfile

# Adapted from efmaral's align.py
def do_align(f_name, rev_f_name, seed):
    verbose = True
    no_lower_case = False
    reverse = False
    null_prior = 0.2
    lex_alpha = 1e-3
    null_alpha = 1e-3
    n_samplers = 2
    model = 3
    prefix_len = 0
    suffix_len = 0
    length = 1.0
    output_prob = None
    
    seed = random.randint(0, 0x7ffffff) if seed is None else seed

    # One direction
    inputs = [f_name]
    discretize = output_prob is None

    aaa = align(inputs, n_samplers, len(inputs),
                    null_prior, lex_alpha, null_alpha,
                    reverse, model, prefix_len, suffix_len,
                    seed, discretize, True, lower=not no_lower_case)

    output = tempfile.TemporaryFile()

    print('Writing alignments...', file=sys.stderr)
    if discretize:
        ibm_print(aaa, reverse, output.fileno())
    else: # Not used at the moment, but keeping this for the future
        with open(output_prob, 'wb') as f:
            pickle.dump(aaa, f, -1)

    output.seek(0)
    result = []
    for line in output:
        result.append(line.decode('ascii').strip())
        
    # The other direction
    
    rev_inputs = [rev_f_name]
    reversed = align(rev_inputs, n_samplers, len(rev_inputs),
        null_prior, lex_alpha, null_alpha,
        reverse, model, prefix_len, suffix_len,
        seed, discretize, True, lower=not no_lower_case)
    
    rev_output = tempfile.TemporaryFile()
    ibm_print(reversed, reverse, rev_output.fileno())
    
    rev_output.seek(0)
    rev_result = []
    for line in rev_output:
        rev_result.append(line.decode('ascii').strip())

    return result, rev_result


if __name__ == '__main__':
    inputs = ["efmaral/3rdparty/data/test.eng",  "efmaral/3rdparty/data/test.hin"]
    res = do_align(inputs, seed=None)
    print("result ", res)

    #inputs_2 = ["fast_align_format_test.txt"]
    #res_2 = do_align(inputs_2, seed=None)
    #print("result ", res_2)

