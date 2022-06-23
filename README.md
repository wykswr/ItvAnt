# ItvAnt
Interval annotator (ItvAnt) is a UNIX style command line tool to automatically obtain various epigenetics' data of
certain given genes interval.

## Characterizing the genomic regions with repeat expansions
The epigenetics' data, including CTCF binding sites, DNase-seq and histone modification data, were obtained from the [ENCODE project](https://www.encodeproject.org/). Accession IDs are: ENCFF618DDO (CTCF ChIP-seq, narrowPeak); ENCFF021YPR (H3K27me3 ChIP-seq, bigWig); ENCFF388WCD (H3K36me3 ChIP-seq, bigWig); ENCFF481BLF (H3K4me1 ChIP-seq, bigWig); ENCFF780JKM (H3K3me3 ChIP-seq, bigWig); ENCFF411VJD (H3K9me3 ChIP-seq, bigWig).

phastCons conservation scores were downloaded from [UCSC](https://hgdownload.cse.ucsc.edu/goldenpath/hg19/phastCons100way/hg19.100way.phastCons.bw).

The pre-computed MMSplice scores were obtained from the annotation of [CADD (offline version)](https://cadd.gs.washington.edu/download).

Non-B DNA structure annotation (hg19): https://ncifrederick.cancer.gov/bids/ftp/?non\#, https://ncifrederick.cancer.gov/bids/ftp/actions/download/?resource=/bioinfo/static/nonb_dwnld/human_hg19/human_hg19.gff.tar.gz.

The file named “hg19.rloop.filtered.mergedRegion.bed” for Rloop annotation is from the publication of Piroon Jenjaroenpun et.al., “R-loopDB: a database for R-loop forming sequences (RLFS) and R-loops” (PMID: 27899586)

The DNA repair binding signal intensity files (the four .bw files) for [BER annotation](https://de.cyverse.org/data/ds/iplant/home/abacolla/bigwig?selectedOrder=asc&selectedOrderBy=name&selectedPage=0&selectedRowsPerPage=100)


## Using guideline
* prepare for the environment
    * make sure the python's version is not less than 3.8. 
    * use virtualenv to create a new environment (optional but recommended).
    * type in: `install -r requirement.txt`, make sure you are in the same path of this project.

* config epigenetic data resources in manifest.txt.
    * It should contain your sample file and epigenetic data file (in various formats can be found in the sample.).
    * If you want to add new property, add new line following.
    * To remove property, use '%' to comment out that line.

* set configuration in config.json.
* organise your input file in BED3 format.
* type in `python main.py input.bed -o theOutputPath`
* find the result named annotated.csv in the output path.

## Input file format
The input file should be organised following the BED3 format, in which the columns are seperated with tab:<br>
The columns are chromosome, start and end, without header.

Here are some examples:<br>
chr1 12252260 12252264<br>
chr3 187388896 187388910<br>
chr4 1019055 1019075<br>

For a certain repeat, the repeat interval is [start, end), with start and end in hg19 coordinate system<br>
See example.bed for example.