if [ ! -f .installed-once ]; then
    rustup-init --no-modify-path -y
    echo "" > .installed
else
    rustup update
fi
