#!/usr/bin/env python3

import argparse
import os
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def main(args):

    if args.virominerdb:
        dbpath = args.virominerdb
    else:
        try:
            dbpath = os.environ['VIROMINERDB']
        except KeyError:
            raise RuntimeError('You must either set VIROMINERDB env variable or '
                               'else specify --virominerdb on command line.')

    if not os.path.exists(dbpath):
        raise FileNotFoundError('Virominer db path {} does not exist.'.format(dbpath))

    if os.path.exists(args.output):
        raise FileExistsError('Output directory {} already exists.'.format(args.output))
    os.makedirs(args.output)

    with open(os.path.join(PROJECT_ROOT, 'Snakefile'), 'r') as snake_template:
        with open(os.path.join(args.output, 'Snakefile'), 'w') as snake_job:
            snake_job.write(snake_template.read().format(FILTEROUT=args.filterout,
                                                         FILTERIN=args.filterin,
                                                         DATA=args.input,
                                                         THREADS=args.threads))


def make_arg_parser():
    parser = argparse.ArgumentParser(
        description="Trimmomatic plus FLASH.")

    parser.add_argument('--filterout', required=True,
                        help='Comma-delimited list of taxa (either txid30420 or corvus,gallus')

    parser.add_argument('--filterin', required=True,
                        help='FASTQ file (if paired, first in the pair)')

    parser.add_argument('--virominerdb',
                        help='path to virominer database files (required if VIROMINERDB not set in enviornment)')

    parser.add_argument('--threads', default=1, type=int,
                        help='Number of threads to use (especially during alignment & assembly)')

    parser.add_argument('input',
                        help='Sequence data in BAM or FASTQ format (if paired, first in the pair)')

    parser.add_argument('output',
                        help='name for directory containing all output')

    return parser

if __name__ == '__main__':
    args = make_arg_parser().parse_args()
    main(args)