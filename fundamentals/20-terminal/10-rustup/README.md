# Installs Rust

Alternative way would be:

```shell
if [ ! -f .installed ]; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    echo "" > .installed
fi
```
