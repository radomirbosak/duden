#!/bin/sh

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
for po_file in $SCRIPT_DIR/*.po; do
    echo "Generating $po_file..."
    mo_dir="${po_file%%.*}/LC_MESSAGES"
    mkdir -p "$mo_dir"
    msgfmt -o "$mo_dir/duden.mo" "$po_file"
done
