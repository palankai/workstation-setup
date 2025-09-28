#!/bin/bash

# DO NOT EDIT this script by hand, this script is generated!
# Instead, edit the components and fundamentals and re-run compile-targets.py
set -e

source ~/.workstation-setup-config
source "$WORKSTATION_INSTALLATION_PATH/_config.sh"
source "$WORKSTATION_INSTALLATION_PATH/_setup_functions.sh"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ "$(pwd)" != "$SCRIPT_DIR" ]; then
    echo "Please run this script from its own directory: $SCRIPT_DIR"
    exit 1
fi
if [ "$WORKSTATION" != "freetrade" ]; then
    echo "This script is intended for '"freetrade"', but you are running it on '$WORKSTATION'."
    exit 1
fi

function help() {
    echo "Usage: $0 <command>"
    echo "Available commands:"
    echo "  run_upgrade                   Run the full upgrade process"
    echo "  brew_upgrade                  Update Homebrew and upgrade all packages"
    echo "  brew_cleanup                  Cleanup old Homebrew packages and caches"
    echo "  brew_upgrade_and_cleanup      Update Homebrew and upgrade all packages"
    echo "  help                          Show this help message"
    echo ""
    echo "Included feature functions:"
    echo "  install_fundamentals_shell_folders"
    echo "  install_fundamentals_shell_linux_compatibility"
    echo "  install_fundamentals_shell_zsh"
    echo "  install_fundamentals_shell_git"
    echo "  install_fundamentals_essentials_envchain"
    echo "  install_fundamentals_essentials_keyring"
    echo "  install_fundamentals_essentials_tmux"
    echo "  install_fundamentals_essentials_vim_setup"
    echo "  install_components_programming_node_node"
    echo "  install_components_programming_node_nvm"
    echo "  install_components_programming_rust_rustup"
    echo "  install_components_programming_python_uv"
    echo "  install_components_terminal_ghostty"
}

function run_upgrade() {
    mkdir -p .once
    brew_upgrade

    install_fundamentals_shell_folders
    install_fundamentals_shell_linux_compatibility
    install_fundamentals_shell_zsh
    install_fundamentals_shell_git
    install_fundamentals_essentials_envchain
    install_fundamentals_essentials_keyring
    install_fundamentals_essentials_tmux
    install_fundamentals_essentials_vim_setup
    install_components_programming_node_node
    install_components_programming_node_nvm
    install_components_programming_rust_rustup
    install_components_programming_python_uv
    install_components_terminal_ghostty

    brew_cleanup
}
function brew_upgrade_and_cleanup() {
    brew_upgrade
    brew_cleanup
}

function brew_upgrade() {
    brew update
    brew upgrade
}

function brew_cleanup() {
    brew cleanup --prune=all --scrub
}


# Install function implementations
function install_fundamentals_shell_folders() {
    echo "Installing feature: 00-shell/10-folders"
    function run_00_run_sh() {
        # Source: fundamentals/00-shell/10-folders/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/00-shell/10-folders"
        mkdir -p $HOME/opt/Applications
        mkdir -p $HOME/opt/src
        mkdir -p $HOME/Local
        mkdir -p $HOME/Git
        mkdir -p $HOME/.local/bin
        echo "  [✓] Script (fundamentals/00-shell/10-folders/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (00-shell/10-folders) installed successfully."
}

function install_fundamentals_shell_linux_compatibility() {
    echo "Installing feature: 00-shell/20-linux-compatibility"
    function run_00_Brewfile() {
        # Source: fundamentals/00-shell/20-linux-compatibility/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "ack"
            brew "autoconf"
            brew "binutils"
            brew "coreutils"
            brew "curl"
            brew "diffutils"
            brew "dnsmasq"
            brew "findutils"
            brew "gawk"
            brew "gettext"
            brew "gnu-getopt"
            brew "gnu-indent"
            brew "gnu-sed"
            brew "gnu-tar"
            brew "gnu-which"
            brew "gnutls"
            brew "gpatch"
            brew "grep"
            brew "gzip"
            brew "htop"
            brew "iproute2mac"
            brew "less"
            brew "lsof"
            brew "make"
            brew "midnight-commander"
            brew "openssl"
            brew "pwgen"
            brew "screen"
            brew "tree"
            brew "vim"
            brew "watch"
            brew "wdiff"
            brew "wget"
            brew "lsusb"
EOF
        echo "  [✓] Brewfile (fundamentals/00-shell/20-linux-compatibility/00-Brewfile) applied successfully."
    }
    function run_01_run_sh() {
        # Source: fundamentals/00-shell/20-linux-compatibility/01-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/00-shell/20-linux-compatibility"
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
        echo "  [✓] Script (fundamentals/00-shell/20-linux-compatibility/01-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_01_run_sh
    echo "  Feature (00-shell/20-linux-compatibility) installed successfully."
}

function install_fundamentals_shell_zsh() {
    echo "Installing feature: 00-shell/40-zsh"
    function run_00_Brewfile() {
        # Source: fundamentals/00-shell/40-zsh/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "font-meslo-for-powerlevel10k"
            cask "font-hack-nerd-font"
EOF
        echo "  [✓] Brewfile (fundamentals/00-shell/40-zsh/00-Brewfile) applied successfully."
    }
    function run_01_run_sh() {
        # Source: fundamentals/00-shell/40-zsh/01-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/00-shell/40-zsh"
        ensure_repository https://github.com/robbyrussell/oh-my-zsh ~/.oh-my-zsh
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zshenv $HOME/.zshenv
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zshrc $HOME/.zshrc
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/p10k.zsh $HOME/.p10k.zsh
        echo "  [✓] Script (fundamentals/00-shell/40-zsh/01-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_01_run_sh
    echo "  Feature (00-shell/40-zsh) installed successfully."
}

function install_fundamentals_shell_git() {
    echo "Installing feature: 00-shell/50-git"
    function run_00_Brewfile() {
        # Source: fundamentals/00-shell/50-git/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "git"
            brew "git-extras"
            brew "git-lfs"      # git large file support
            brew "gh"           # github cli
EOF
        echo "  [✓] Brewfile (fundamentals/00-shell/50-git/00-Brewfile) applied successfully."
    }
    function run_01_run_sh() {
        # Source: fundamentals/00-shell/50-git/01-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/00-shell/50-git"
        git lfs install
        echo "  [✓] Script (fundamentals/00-shell/50-git/01-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_01_run_sh
    echo "  Feature (00-shell/50-git) installed successfully."
}

function install_fundamentals_essentials_envchain() {
    echo "Installing feature: 30-essentials/envchain"
    function run_00_Brewfile() {
        # Source: fundamentals/30-essentials/envchain/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "envchain"
EOF
        echo "  [✓] Brewfile (fundamentals/30-essentials/envchain/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (30-essentials/envchain) installed successfully."
}

function install_fundamentals_essentials_keyring() {
    echo "Installing feature: 30-essentials/keyring"
    function run_00_Brewfile() {
        # Source: fundamentals/30-essentials/keyring/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "keyring"
EOF
        echo "  [✓] Brewfile (fundamentals/30-essentials/keyring/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (30-essentials/keyring) installed successfully."
}

function install_fundamentals_essentials_tmux() {
    echo "Installing feature: 30-essentials/tmux"
    function run_00_Brewfile() {
        # Source: fundamentals/30-essentials/tmux/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "tmux"
EOF
        echo "  [✓] Brewfile (fundamentals/30-essentials/tmux/00-Brewfile) applied successfully."
    }
    function run_00_run_sh() {
        # Source: fundamentals/30-essentials/tmux/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/30-essentials/tmux"
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/tmux.conf $HOME/.tmux.conf
        echo "  [✓] Script (fundamentals/30-essentials/tmux/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_00_run_sh
    echo "  Feature (30-essentials/tmux) installed successfully."
}

function install_fundamentals_essentials_vim_setup() {
    echo "Installing feature: 30-essentials/vim-setup"
    function run_00_run_sh() {
        # Source: fundamentals/30-essentials/vim-setup/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/fundamentals/30-essentials/vim-setup"
        mkdir -p $HOME/.vim
        mkdir -p $HOME/.vim-tmp
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/vimrc.vim $HOME/.vimrc
        echo "  [✓] Script (fundamentals/30-essentials/vim-setup/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (30-essentials/vim-setup) installed successfully."
}

function install_components_programming_node_node() {
    echo "Installing feature: programming/node/node"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/node/node/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "node"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/node/node/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/node/node) installed successfully."
}

function install_components_programming_node_nvm() {
    echo "Installing feature: programming/node/nvm"
    function run_00_run_sh() {
        # Source: targets/freetrade/programming/node/nvm/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/node/nvm"
        mkdir -p ~/.nvm
        echo "  [✓] Script (targets/freetrade/programming/node/nvm/00-run.sh) executed successfully."
        popd > /dev/null
    }
    function run_01_Brewfile() {
        # Source: targets/freetrade/programming/node/nvm/01-Brewfile
        brew bundle -q --file=- <<EOF
            brew "nvm"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/node/nvm/01-Brewfile) applied successfully."
    }

    run_00_run_sh
    run_01_Brewfile
    echo "  Feature (programming/node/nvm) installed successfully."
}

function install_components_programming_rust_rustup() {
    echo "Installing feature: programming/rust/rustup"
    function run_00_run_sh() {
        # Source: components/programming/rust/rustup/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/rust/rustup"
        mkdir -p $HOME/.cargo
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/cargo/env $HOME/.cargo/env
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/cargo/config.toml $HOME/.cargo/config.toml
        echo "  [✓] Script (components/programming/rust/rustup/00-run.sh) executed successfully."
        popd > /dev/null
    }
    function run_10_Brewfile() {
        # Source: components/programming/rust/rustup/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "rustup-init"
EOF
        echo "  [✓] Brewfile (components/programming/rust/rustup/10-Brewfile) applied successfully."
    }
    function run_20_runonce_sh() {
        # Source: components/programming/rust/rustup/20-runonce.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/rust/rustup"
        rustup-init --no-modify-path -y
        echo "  [✓] Script (components/programming/rust/rustup/20-runonce.sh) executed successfully."
        popd > /dev/null
    }
    function run_30_run_sh() {
        # Source: components/programming/rust/rustup/30-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/rust/rustup"
        rustup update
        echo "  [✓] Script (components/programming/rust/rustup/30-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    run_10_Brewfile
    _run_once "install_programming_rust_rustup_20_runonce_sh" run_20_runonce_sh
    run_30_run_sh
    echo "  Feature (programming/rust/rustup) installed successfully."
}

function install_components_programming_python_uv() {
    echo "Installing feature: programming/python/uv"
    function run_00_runonce_sh() {
        # Source: targets/freetrade/programming/python/uv/00-runonce.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/python/uv"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "  [✓] Script (targets/freetrade/programming/python/uv/00-runonce.sh) executed successfully."
        popd > /dev/null
    }
    function run_10_run_sh() {
        # Source: targets/freetrade/programming/python/uv/10-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/python/uv"
        uv self update
        echo "  [✓] Script (targets/freetrade/programming/python/uv/10-run.sh) executed successfully."
        popd > /dev/null
    }

    _run_once "install_programming_python_uv_00_runonce_sh" run_00_runonce_sh
    run_10_run_sh
    echo "  Feature (programming/python/uv) installed successfully."
}

function install_components_terminal_ghostty() {
    echo "Installing feature: terminal/ghostty"
    function run_10_run_sh() {
        # Source: targets/freetrade/terminal/ghostty/10-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/terminal/ghostty"
        # TODO: Ensure ghostty config link
        mkdir -p ~/.config/ghostty
        ln -sf $(pwd)/config/config ~/.config/ghostty/config
        echo "  [✓] Script (targets/freetrade/terminal/ghostty/10-run.sh) executed successfully."
        popd > /dev/null
    }
    function run_20_Brewfile() {
        # Source: targets/freetrade/terminal/ghostty/20-Brewfile
        brew bundle -q --file=- <<EOF
            cask "ghostty"
EOF
        echo "  [✓] Brewfile (targets/freetrade/terminal/ghostty/20-Brewfile) applied successfully."
    }

    run_10_run_sh
    run_20_Brewfile
    echo "  Feature (terminal/ghostty) installed successfully."
}


# Internal functions
function _run_once() {
    LOCK=$1
    shift
    if [ ! -f .once/installed-$LOCK-once ]; then
        $@
        touch .once/installed-$LOCK-once
    fi
}

if [ $# -eq 0 ]; then
    help
    exit 0
fi

COMMAND="$1"
if declare -F "$COMMAND" > /dev/null; then
    "$@"
else
    echo "❌ Error: Unknown command '$COMMAND'" >&2
    echo >&2 # Print a blank line for spacing
    help
    exit 1 # Exit with an error code
fi

