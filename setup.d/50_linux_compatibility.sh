# https://apple.stackexchange.com/questions/69223/how-to-replace-mac-os-x-utilities-with-gnu-core-utilities
# https://dev.to/dnsmichi/use-homebrew-bundle-to-manage-software-installation-on-macos-1223

mkdir -p $HOME/opt/gnubin
mkdir -p $HOME/opt/gnuman
mkdir -p $HOME/opt/gnuman/man1
mkdir -p $HOME/opt/gnuman/man2
mkdir -p $HOME/opt/gnuman/man3
mkdir -p $HOME/opt/gnuman/man4
mkdir -p $HOME/opt/gnuman/man5
mkdir -p $HOME/opt/gnuman/man6
mkdir -p $HOME/opt/gnuman/man7
mkdir -p $HOME/opt/gnuman/man8
mkdir -p $HOME/opt/gnuman/man9
mkdir -p $HOME/opt/gnuman/mann

for i in $HOMEBREW_CELLAR/*/*/libexec/gnubin; do
    for j in $i/*; do
        ln -sf $j $HOME/opt/gnubin/$(basename $j)
    done
done
log_result "$HOME/opt/gnubin/ updated"

mans=("man1" "man2" "man3" "man4" "man5" "man6" "man7" "man8" "man9" "mann")

for i in $HOMEBREW_CELLAR/*/*/libexec/gnuman; do
    for j in "${mans[@]}"; do
        for k in $i/$j/*; do
            bn=$(basename $k)
            if [ "$bn" != "*" ]; then
                ln -sf $i/$j/$bn $HOME/opt/gnuman/$j/$bn
            fi
        done
    done
done
log_result "$HOME/opt/gnuman/ updated"
