#!/bin/sh

for hook in git-hooks/*;do
    echo "Setting up git hook for $hook"
    basename=$(basename $hook)
    chmod +x $hook
    ln -sf ../../${hook} .git/hooks/$basename
done
echo "Git hooks setup complete"
