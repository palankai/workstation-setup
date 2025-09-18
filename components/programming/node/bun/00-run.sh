if [ ! -f .installed-once ]; then
    curl -fsSL https://bun.sh/install | bash
    echo "" > .installed-once
else
    bun upgrade
fi
