#!/bin/sh

# runs ipython3 and loads a word from duden (by default 'Hase')
WORD=${1:-Hase}
ipython3 -i -c "import duden; word = duden.get('$WORD'); soup = word.soup; print('\nPrepared objects: \'word\', \'soup\'')"