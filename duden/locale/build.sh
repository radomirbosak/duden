#!/bin/sh

for po_file in *.po; do
    echo "Generating $po_file..."
    mo_dir=${po_file%%.*}/LC_MESSAGES
    mkdir -p $mo_dir
    msgfmt -o $mo_dir/duden.mo $po_file
done
