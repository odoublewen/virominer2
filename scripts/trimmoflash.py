#!/usr/bin/env python3

import sys
import logging
import argparse
import subprocess
import os
import gzip


def fastq_to_tab(fastq):

    if fastq[-3:] == '.gz':
        f = gzip.open(fastq, 'r')
    else:
        f = open(fastq, 'r')

    while True:
        try:
            header = next(f).rstrip()
            seq = next(f).rstrip()
            next(f)
            qual = next(f).rstrip()
            print("{}\t{}\t{}".format(header[1:], seq, qual))
        except StopIteration:
            break

    f.close()


def main(fastq, threads, trimmomatic, single):

    log = logging.getLogger()
    logging_filehandler = logging.FileHandler(filename=fastq + '_trimmoflash.log')
    logging_consolehandler = logging.StreamHandler()
    log.setLevel(logging.INFO)
    logging_filehandler.setLevel(logging.INFO)
    logging_consolehandler.setLevel(logging.ERROR)
    logging_formatter = logging.Formatter('%(asctime)s__%(module)s__%(message)s')
    logging_filehandler.setFormatter(logging_formatter)
    logging_consolehandler.setFormatter(logging_formatter)
    log.addHandler(logging_filehandler)
    log.addHandler(logging_consolehandler)

    # TRIMMOMATIC
    trimmomatic_adapter = os.path.join(os.path.dirname(trimmomatic), 'adapters', 'NexteraPE-Multiplex.fa')

    trimmomatic_outdir = fastq + '_trimmomatic'
    os.mkdir(trimmomatic_outdir)

    trimmomatic_command = 'trimmomatic '

    if single:
        trimmomatic_command += 'SE '.format(fastq)
    else:
        trimmomatic_command += 'PE '

    if threads:
        trimmomatic_command += '-threads {} '.format(threads)

    trimmomatic_command += '-trimlog {0}/trimmomatic.log '.format(trimmomatic_outdir)

    if single:
        trimmomatic_command += '{} '.format(fastq)
        trimmomatic_command += '{}/trimmomatic.fq '.format(trimmomatic_outdir)
    else:
        trimmomatic_command += '-basein {} '.format(fastq)
        trimmomatic_command += '-baseout {}/trimmomatic.fq '.format(trimmomatic_outdir)

    trimmomatic_command += 'ILLUMINACLIP:{1}:2:30:10 ' \
                           'SLIDINGWINDOW:5:25 ' \
                           'MINLEN:30'.format(trimmomatic_outdir, trimmomatic_adapter)

    log.debug(trimmomatic_command)

    p = subprocess.Popen(trimmomatic_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    trimmomatic_output = p.communicate()
    for fop in trimmomatic_output:
        for l in fop.decode().split('\n'):
            log.info(l)

    if not single:
        # FLASH
        flash_command = 'flash -To -M 300 -c {0}/trimmomatic_1P.fq {0}/trimmomatic_2P.fq'.format(trimmomatic_outdir)
        log.debug(flash_command)
        p = subprocess.Popen(flash_command.split(), stderr=subprocess.PIPE)
        flash_output = p.communicate()
        for l in flash_output[1].decode().split('\n'):
            if '[FLASH] Processed' not in l:
                log.info(l)

        fastq_to_tab('{}/trimmomatic_1U.fq'.format(trimmomatic_outdir))
        fastq_to_tab('{}/trimmomatic_2U.fq'.format(trimmomatic_outdir))


def make_arg_parser():
    parser = argparse.ArgumentParser(
        description="Trimmomatic plus FLASH.")

    parser.add_argument('--fastq', required=True,
                        help='FASTQ file (if paired, first in the pair)')

    parser.add_argument('--threads', default=0,
                        help='Number of threads to tell Trimmomatic and FLASH to use. '
                             'If 0, these programs will automatically choose')

    parser.add_argument('--trimmomatic', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Trimmomatic-0.33', 'trimmomatic-0.33.jar'),
                        help='Path to trimmomatic jar file')

    parser.add_argument('--single', action='store_true',
                        help='Single read')

    return parser

if __name__ == '__main__':
    args = make_arg_parser().parse_args()
    main(args.fastq, args.threads, args.trimmomatic, args.single)
