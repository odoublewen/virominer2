#!/usr/bin/env python3
#

import sys
import argparse
import logging
import gzip
import re
from Bio import SeqIO


class Filter:
    def __init__(self, query, filterfile, grep, reverse, length):

        self.filters = []
        self.grep = grep
        self.reverse = reverse

        if query:
            self.queryset = [query.split(' ')[0]]
            self.filters.append('querymatch')
        elif filterfile:
            with open(args.filterfile, 'r') as qf:
                self.queryset = [line.split(' ')[0] for line in qf.read().splitlines()]
            self.queryset = set(self.queryset)
            self.filters.append('querymatch')

        if length:
            relen = re.match(r'([0-9]*)-([0-9]*)', length)
            try:
                self.minlen = int(relen.group(1))
            except ValueError:
                self.minlen = 0
            try:
                self.maxlen = int(relen.group(2))
            except ValueError:
                self.maxlen = float('inf')
            self.filters.append('lengthmatch')

        if not self.filters:
            raise RuntimeError('You must specify a query and/or a length filter!')

    def querymatch(self, seq):
        hit = False
        if self.grep:
            for q in self.queryset:
                if re.search(q, seq.id):
                    hit = True
                    break
        else:
            if seq.id in self.queryset:
                hit = True

        if args.reverse:
            hit = not hit

        return hit

    def lengthmatch(self, seq):
        if self.minlen <= len(seq) <= self.maxlen:
            return True
        else:
            return False

    def filter(self, seq):

        results = [getattr(self, method)(seq) for method in self.filters]

        return all(results)



def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    myfilter = Filter(args.query, args.filterfile, args.grep, args.reverse, args.length)

    if args.file[-3:] == '.gz':
        fh = gzip.GzipFile(args.file, 'r')
    else:
        fh = open(args.file, 'r')

    for line in fh:
        if line[0] == '>':
            filetype = 'fasta'
        elif line[0] == '@':
            filetype = 'fastq'
        else:
            raise RuntimeError("Cannot guess file type for %s" % args.file)
        break

    logging.debug("Reading file %s as filetype %s" % (args.file, filetype))
    fh.seek(0)

    if args.fasta:
        outformat = 'fasta'
    else:
        outformat = filetype

    try:
        for seq in SeqIO.parse(fh, format=filetype):
            if myfilter.filter(seq):
                SeqIO.write(seq, sys.stdout, format=outformat)
    except IOError:
        try:
            sys.stdout.close()
        except IOError:
            pass
        try:
            sys.stderr.close()
        except IOError:
            pass





if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Filters sequences (inclusive or exclusive) from a file (fasta or fastq) using either pattern "
                    "matching of the ID line or sequence lengths.")
    parser.add_argument(
        "file",
        help="fasta or fastq file to search (may be gzipped if suffix = .gz)",
        metavar="FILE")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-q",
        "--query",
        help="search term"
    )
    group.add_argument(
        "-f",
        "--filterfile",
        help="file with list of query terms"
    )
    parser.add_argument(
        "-r",
        "--reverse",
        help="removes records with given terms (reverse of default behavior)",
        action="store_true")
    parser.add_argument(
        "-g",
        "--grep",
        help="grep matching of query term (default is exact match)",
        action="store_true")

    parser.add_argument(
        "-l",
        "--length",
        help="length range, specified like 100-200 or -200 or 200-")

    parser.add_argument(
        "--fasta",
        help="output sequences as fasta (even if fastq input)",
        action="store_true")

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
