#!/usr/bin/perl

$filename = $ARGV[0];
if(length $filename == 0){
    $filename="Concentration";
}

system ('pdflatex ' . $filename . '.tex' );
system ('bibtex ' . $filename );
system ('pdflatex ' . $filename . '.tex' );
system ('pdflatex ' . $filename . '.tex' );
#system ('dvipdfm ' . $filename );#. 'tex' );
system ('open ' . $filename . '.pdf');

