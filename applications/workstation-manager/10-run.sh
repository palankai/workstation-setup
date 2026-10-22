repo="$(git rev-parse --show-toplevel)"

mkdir -p ~/.local/bin
ln -sf "$repo/bin/ws" ~/.local/bin/ws

uv sync --project "$repo/manager" --no-dev --extra server --inexact
