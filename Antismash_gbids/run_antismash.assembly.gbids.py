#!/usr/bin/env python
import subprocess
import os
import os.path
import tqdm
from Bio import Entrez
from Bio import SeqIO
from multiprocessing import Pool

TEMP_ANTISMASH_OUTPUT = "/home/gvandova/antismash_output_assemblies_2018/"
FINAL_ANTISMASH_OUTPUT = "/mnt/gnpn/gnpn/projects/orphanpks/TargetMining/Antismash_gbids/antismash_output_assemblies"
GB_FOLDER = "/home/gvandova/gbdir_assemblies"

import signal, os


def f(gbid):
#    if gbid == "CP033141":
#        print "CP033141 required, not in gbfolder"
#        return
    print "Start %s" % gbid
    temp_dir = os.path.join(TEMP_ANTISMASH_OUTPUT)
    final_dir = os.path.join(FINAL_ANTISMASH_OUTPUT, gbid)

    local_filename = os.path.join(GB_FOLDER, gbid + ".gbff")
    
    # Nov-27-2018 Run antismash for sequences smaller than 100000 bp
    for record in SeqIO.parse(open(local_filename, "rU"), "genbank"):
        if len(record.seq) < 1000:
            print "Sequence %s smaller than 1000; SKIP" % gbid
            return
#        if len(record.seq) > 1000000:
#            print "Sequence %s larget than 1M; SKIP" % gbid
#            return
    
    geneclusters_filename = os.path.join(final_dir, "geneclusters.js")
    print "checking if %s exists" % geneclusters_filename
    if os.path.exists(geneclusters_filename) == True:
        print geneclusters_filename, " exist"
        return
    
    #if os.path.exists(final_dir):
    #    print final_dir, "exists"
    #	return

    antismash = "/home/gvandova/bin/run_antismash" + " " + local_filename + " " + temp_dir
    print antismash
    os.system(antismash)
    print "done %s" % gbid
    subprocess.call(["rm", "-rf", final_dir])
    subprocess.call(["mv", "-f", os.path.join(temp_dir, gbid), FINAL_ANTISMASH_OUTPUT])
    print " ".join(["mv", "-f", os.path.join(temp_dir, gbid), FINAL_ANTISMASH_OUTPUT])

if __name__ == "__main__":
    gbids = []
    gbidfile = "/mnt/gnpn/gnpn/projects/orphanpks/TargetMining/Genbank/gbids.assembly.unique.txt"
    ff = open(gbidfile, "r")
    for line in ff:
        gbid = line.strip()
        #if gbid.startswith("AZW"):
       	gbids.append(gbid)

    total = len(gbids)
    print "Total %s" % total
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    p = Pool(processes=2)
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        for _ in tqdm.tqdm(p.imap_unordered(f, gbids), total=len(gbids)):
            pass

    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        p.terminate()
    else:
        print("Normal termination")
        p.close()
    p.join()

    print "Done, exiting"

