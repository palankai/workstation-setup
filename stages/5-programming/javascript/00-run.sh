if [ ! -f .installed-bun ]; then
    curl -fsSL https://bun.sh/install | bash
    echo "" > .installed-bun
fi
