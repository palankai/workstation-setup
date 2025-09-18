if [ ! -f .installed-once ]; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "" > .installed-once
else
    uv self update
fi
