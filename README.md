# virominer2


Dependencies
------------
* Trimmomatic
* FLASH
* Bowtie2
* BLAST
* Trinity
* Krona

Set up
------
Use conda to easily satisify all dependencies.  After installing [miniconda](http://conda.pydata.org/miniconda.html), issue these commands:
```conda config --add channels bioconda
conda config --add channels r
conda env create --file environment_generic.yml
```

Then, use `source activate virominer2` to enter your conda environment.

