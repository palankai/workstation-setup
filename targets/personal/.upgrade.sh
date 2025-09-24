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
if [ "$WORKSTATION" != "personal" ]; then
    echo "This script is intended for '"personal"', but you are running it on '$WORKSTATION'."
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
    echo "  install_components_chat_discord"
    echo "  install_components_chat_signal"
    echo "  install_components_chat_slack"
    echo "  install_components_cloud_aws"
    echo "  install_components_cloud_aws_cli"
    echo "  install_components_cloud_google"
    echo "  install_components_cloud_google_drive"
    echo "  install_components_cloud_synology_drive"
    echo "  install_components_creative_adobe"
    echo "  install_components_creative_obs"
    echo "  install_components_database_postgresql"
    echo "  install_components_desktop_brave_browser"
    echo "  install_components_desktop_grammarly_desktop"
    echo "  install_components_desktop_obsidian"
    echo "  install_components_desktop_vlc"
    echo "  install_components_dev_dbeaver_community"
    echo "  install_components_dev_sqlite_browser"
    echo "  install_components_dev_sublime"
    echo "  install_components_dev_vscode"
    echo "  install_components_dev_zed"
    echo "  install_components_programming_node_bun"
    echo "  install_components_programming_node_node"
    echo "  install_components_programming_node_nvm"
    echo "  install_components_programming_node_yarn"
    echo "  install_components_programming_python_pip"
    echo "  install_components_programming_python_pipx"
    echo "  install_components_programming_python_pyenv"
    echo "  install_components_programming_rust_rustup"
    echo "  install_components_programming_python_uv"
    echo "  install_components_programming_terraform"
    echo "  install_components_secrets_1password_latest"
    echo "  install_components_secrets_keepassium_pro"
    echo "  install_components_secrets_keepassxc"
    echo "  install_components_secrets_ledger_live"
    echo "  install_components_system_FruitJuice"
    echo "  install_components_system_TheUnarchiver"
    echo "  install_components_system_bartender"
    echo "  install_components_system_iStatMenus"
    echo "  install_components_system_karabiner_elements"
    echo "  install_components_system_settings"
    echo "  install_components_system_surfshark"
    echo "  install_components_terminal_ghostty"
    echo "  install_components_terminal_iterm2"
    echo "  install_components_tools_bat"
    echo "  install_components_tools_btop"
    echo "  install_components_tools_cmake"
    echo "  install_components_tools_docker"
    echo "  install_components_tools_jq"
    echo "  install_components_tools_watchman"
    echo "  install_components_tools_websocat"
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
    install_components_chat_discord
    install_components_chat_signal
    install_components_chat_slack
    install_components_cloud_aws
    install_components_cloud_aws_cli
    install_components_cloud_google
    install_components_cloud_google_drive
    install_components_cloud_synology_drive
    install_components_creative_adobe
    install_components_creative_obs
    install_components_database_postgresql
    install_components_desktop_brave_browser
    install_components_desktop_grammarly_desktop
    install_components_desktop_obsidian
    install_components_desktop_vlc
    install_components_dev_dbeaver_community
    install_components_dev_sqlite_browser
    install_components_dev_sublime
    install_components_dev_vscode
    install_components_dev_zed
    install_components_programming_node_bun
    install_components_programming_node_node
    install_components_programming_node_nvm
    install_components_programming_node_yarn
    install_components_programming_python_pip
    install_components_programming_python_pipx
    install_components_programming_python_pyenv
    install_components_programming_rust_rustup
    install_components_programming_python_uv
    install_components_programming_terraform
    install_components_secrets_1password_latest
    install_components_secrets_keepassium_pro
    install_components_secrets_keepassxc
    install_components_secrets_ledger_live
    install_components_system_FruitJuice
    install_components_system_TheUnarchiver
    install_components_system_bartender
    install_components_system_iStatMenus
    install_components_system_karabiner_elements
    install_components_system_settings
    install_components_system_surfshark
    install_components_terminal_ghostty
    install_components_terminal_iterm2
    install_components_tools_bat
    install_components_tools_btop
    install_components_tools_cmake
    install_components_tools_docker
    install_components_tools_jq
    install_components_tools_watchman
    install_components_tools_websocat

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

function install_components_chat_discord() {
    echo "Installing feature: chat/discord"
    function run_00_Brewfile() {
        # Source: targets/personal/chat/discord/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "discord"
EOF
        echo "  [✓] Brewfile (targets/personal/chat/discord/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (chat/discord) installed successfully."
}

function install_components_chat_signal() {
    echo "Installing feature: chat/signal"
    function run_00_Brewfile() {
        # Source: targets/personal/chat/signal/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "signal"
EOF
        echo "  [✓] Brewfile (targets/personal/chat/signal/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (chat/signal) installed successfully."
}

function install_components_chat_slack() {
    echo "Installing feature: chat/slack"
    function run_00_Brewfile() {
        # Source: targets/personal/chat/slack/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "slack"
EOF
        echo "  [✓] Brewfile (targets/personal/chat/slack/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (chat/slack) installed successfully."
}

function install_components_cloud_aws() {
    echo "Installing feature: cloud/aws"
    function run_00_Brewfile() {
        # Source: targets/personal/cloud/aws/00-Brewfile
        brew bundle -q --file=- <<EOF
            tap "aws/tap"
            tap "xen0l/homebrew-taps" # for aws-gate
            cask "aws-vault-binary"
            # cask "aws-gate"
            cask "session-manager-plugin"
EOF
        echo "  [✓] Brewfile (targets/personal/cloud/aws/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/aws) installed successfully."
}

function install_components_cloud_aws_cli() {
    echo "Installing feature: cloud/aws-cli"
    function run_00_Brewfile() {
        # Source: targets/personal/cloud/aws-cli/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "awscli"
EOF
        echo "  [✓] Brewfile (targets/personal/cloud/aws-cli/00-Brewfile) applied successfully."
    }
    function run_00_run_sh() {
        # Source: targets/personal/cloud/aws-cli/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/cloud/aws-cli"
        mkdir -p $HOME/.aws
        chmod 1755 $HOME/.aws
        ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/aws.conf $HOME/.aws/config
        # pipx install aws-sam-cli-local
        # pipx install awscli-local
        echo "  [✓] Script (targets/personal/cloud/aws-cli/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_00_run_sh
    echo "  Feature (cloud/aws-cli) installed successfully."
}

function install_components_cloud_google() {
    echo "Installing feature: cloud/google"
    function run_00_Brewfile() {
        # Source: targets/personal/cloud/google/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "gcloud-cli"
EOF
        echo "  [✓] Brewfile (targets/personal/cloud/google/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/google) installed successfully."
}

function install_components_cloud_google_drive() {
    echo "Installing feature: cloud/google-drive"
    function run_00_Brewfile() {
        # Source: targets/personal/cloud/google-drive/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "google-drive"
EOF
        echo "  [✓] Brewfile (targets/personal/cloud/google-drive/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/google-drive) installed successfully."
}

function install_components_cloud_synology_drive() {
    echo "Installing feature: cloud/synology-drive"
    function run_00_Brewfile() {
        # Source: targets/personal/cloud/synology-drive/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "synology-drive"
EOF
        echo "  [✓] Brewfile (targets/personal/cloud/synology-drive/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/synology-drive) installed successfully."
}

function install_components_creative_adobe() {
    echo "Installing feature: creative/adobe"
    function run_00_Brewfile() {
        # Source: targets/personal/creative/adobe/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "adobe-creative-cloud"
EOF
        echo "  [✓] Brewfile (targets/personal/creative/adobe/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (creative/adobe) installed successfully."
}

function install_components_creative_obs() {
    echo "Installing feature: creative/obs"
    function run_00_Brewfile() {
        # Source: targets/personal/creative/obs/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "obs"
EOF
        echo "  [✓] Brewfile (targets/personal/creative/obs/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (creative/obs) installed successfully."
}

function install_components_database_postgresql() {
    echo "Installing feature: database/postgresql"
    function run_00_Brewfile() {
        # Source: targets/personal/database/postgresql/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "postgresql@17"
EOF
        echo "  [✓] Brewfile (targets/personal/database/postgresql/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (database/postgresql) installed successfully."
}

function install_components_desktop_brave_browser() {
    echo "Installing feature: desktop/brave-browser"
    function run_00_Brewfile() {
        # Source: targets/personal/desktop/brave-browser/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "brave-browser"
EOF
        echo "  [✓] Brewfile (targets/personal/desktop/brave-browser/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (desktop/brave-browser) installed successfully."
}

function install_components_desktop_grammarly_desktop() {
    echo "Installing feature: desktop/grammarly-desktop"
    function run_00_Brewfile() {
        # Source: targets/personal/desktop/grammarly-desktop/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "grammarly-desktop"
EOF
        echo "  [✓] Brewfile (targets/personal/desktop/grammarly-desktop/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (desktop/grammarly-desktop) installed successfully."
}

function install_components_desktop_obsidian() {
    echo "Installing feature: desktop/obsidian"
    function run_00_Brewfile() {
        # Source: targets/personal/desktop/obsidian/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "obsidian"
EOF
        echo "  [✓] Brewfile (targets/personal/desktop/obsidian/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (desktop/obsidian) installed successfully."
}

function install_components_desktop_vlc() {
    echo "Installing feature: desktop/vlc"
    function run_00_Brewfile() {
        # Source: targets/personal/desktop/vlc/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "vlc"
EOF
        echo "  [✓] Brewfile (targets/personal/desktop/vlc/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (desktop/vlc) installed successfully."
}

function install_components_dev_dbeaver_community() {
    echo "Installing feature: dev/dbeaver-community"
    function run_00_Brewfile() {
        # Source: targets/personal/dev/dbeaver-community/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "dbeaver-community"
EOF
        echo "  [✓] Brewfile (targets/personal/dev/dbeaver-community/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/dbeaver-community) installed successfully."
}

function install_components_dev_sqlite_browser() {
    echo "Installing feature: dev/sqlite-browser"
    function run_00_Brewfile() {
        # Source: targets/personal/dev/sqlite-browser/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "db-browser-for-sqlite"
EOF
        echo "  [✓] Brewfile (targets/personal/dev/sqlite-browser/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/sqlite-browser) installed successfully."
}

function install_components_dev_sublime() {
    echo "Installing feature: dev/sublime"
    function run_00_Brewfile() {
        # Source: targets/personal/dev/sublime/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "sublime-text"
EOF
        echo "  [✓] Brewfile (targets/personal/dev/sublime/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/sublime) installed successfully."
}

function install_components_dev_vscode() {
    echo "Installing feature: dev/vscode"
    function run_00_Brewfile() {
        # Source: targets/personal/dev/vscode/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "visual-studio-code"
EOF
        echo "  [✓] Brewfile (targets/personal/dev/vscode/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/vscode) installed successfully."
}

function install_components_dev_zed() {
    echo "Installing feature: dev/zed"
    function run_00_Brewfile() {
        # Source: targets/personal/dev/zed/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "zed"
EOF
        echo "  [✓] Brewfile (targets/personal/dev/zed/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/zed) installed successfully."
}

function install_components_programming_node_bun() {
    echo "Installing feature: programming/node/bun"
    function run_00_run_sh() {
        # Source: targets/personal/programming/node/bun/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/node/bun"
        if [ ! -f .installed-once ]; then
            curl -fsSL https://bun.sh/install | bash
            echo "" > .installed-once
        else
            bun upgrade
        fi
        echo "  [✓] Script (targets/personal/programming/node/bun/00-run.sh) executed successfully."
        popd > /dev/null
    }
    function run_after_sh() {
        # Source: targets/personal/programming/node/bun/after.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/node/bun"
        bun upgrade
        echo "  [✓] Script (targets/personal/programming/node/bun/after.sh) executed successfully."
        popd > /dev/null
    }
    function run_runonce_sh() {
        # Source: targets/personal/programming/node/bun/runonce.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/node/bun"
        curl -fsSL https://bun.sh/install | bash
        echo "  [✓] Script (targets/personal/programming/node/bun/runonce.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    run_after_sh
    _run_once "install_programming_node_bun_runonce_sh" run_runonce_sh
    echo "  Feature (programming/node/bun) installed successfully."
}

function install_components_programming_node_node() {
    echo "Installing feature: programming/node/node"
    function run_00_Brewfile() {
        # Source: targets/personal/programming/node/node/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "node"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/node/node/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/node/node) installed successfully."
}

function install_components_programming_node_nvm() {
    echo "Installing feature: programming/node/nvm"
    function run_00_run_sh() {
        # Source: targets/personal/programming/node/nvm/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/node/nvm"
        mkdir -p ~/.nvm
        echo "  [✓] Script (targets/personal/programming/node/nvm/00-run.sh) executed successfully."
        popd > /dev/null
    }
    function run_01_Brewfile() {
        # Source: targets/personal/programming/node/nvm/01-Brewfile
        brew bundle -q --file=- <<EOF
            brew "nvm"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/node/nvm/01-Brewfile) applied successfully."
    }

    run_00_run_sh
    run_01_Brewfile
    echo "  Feature (programming/node/nvm) installed successfully."
}

function install_components_programming_node_yarn() {
    echo "Installing feature: programming/node/yarn"
    function run_00_Brewfile() {
        # Source: targets/personal/programming/node/yarn/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "yarn"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/node/yarn/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/node/yarn) installed successfully."
}

function install_components_programming_python_pip() {
    echo "Installing feature: programming/python/pip"
    function run_00_run_sh() {
        # Source: targets/personal/programming/python/pip/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/python/pip"
        $SYSTEM_PYTHON -m pip install --upgrade pip
        echo "  [✓] Script (targets/personal/programming/python/pip/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (programming/python/pip) installed successfully."
}

function install_components_programming_python_pipx() {
    echo "Installing feature: programming/python/pipx"
    function run_00_Brewfile() {
        # Source: targets/personal/programming/python/pipx/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "pipx"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/python/pipx/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/python/pipx) installed successfully."
}

function install_components_programming_python_pyenv() {
    echo "Installing feature: programming/python/pyenv"
    function run_00_Brewfile() {
        # Source: targets/personal/programming/python/pyenv/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "pyenv"
            brew "pyenv-virtualenv"
            brew "pyenv-virtualenvwrapper"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/python/pyenv/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/python/pyenv) installed successfully."
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
        # Source: targets/personal/programming/python/uv/00-runonce.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/python/uv"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "  [✓] Script (targets/personal/programming/python/uv/00-runonce.sh) executed successfully."
        popd > /dev/null
    }
    function run_10_run_sh() {
        # Source: targets/personal/programming/python/uv/10-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/programming/python/uv"
        uv self update
        echo "  [✓] Script (targets/personal/programming/python/uv/10-run.sh) executed successfully."
        popd > /dev/null
    }

    _run_once "install_programming_python_uv_00_runonce_sh" run_00_runonce_sh
    run_10_run_sh
    echo "  Feature (programming/python/uv) installed successfully."
}

function install_components_programming_terraform() {
    echo "Installing feature: programming/terraform"
    function run_00_Brewfile() {
        # Source: targets/personal/programming/terraform/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "terraform"
EOF
        echo "  [✓] Brewfile (targets/personal/programming/terraform/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/terraform) installed successfully."
}

function install_components_secrets_1password_latest() {
    echo "Installing feature: secrets/1password-latest"
    function run_00_Brewfile() {
        # Source: targets/personal/secrets/1password-latest/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "1password"
EOF
        echo "  [✓] Brewfile (targets/personal/secrets/1password-latest/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (secrets/1password-latest) installed successfully."
}

function install_components_secrets_keepassium_pro() {
    echo "Installing feature: secrets/keepassium-pro"
    function run_00_Brewfile() {
        # Source: targets/personal/secrets/keepassium-pro/00-Brewfile
        brew bundle -q --file=- <<EOF
            mas "KeePassium Pro", id: 1481781647
EOF
        echo "  [✓] Brewfile (targets/personal/secrets/keepassium-pro/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (secrets/keepassium-pro) installed successfully."
}

function install_components_secrets_keepassxc() {
    echo "Installing feature: secrets/keepassxc"
    function run_00_Brewfile() {
        # Source: targets/personal/secrets/keepassxc/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "keepassxc"
EOF
        echo "  [✓] Brewfile (targets/personal/secrets/keepassxc/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (secrets/keepassxc) installed successfully."
}

function install_components_secrets_ledger_live() {
    echo "Installing feature: secrets/ledger-live"
    function run_00_Brewfile() {
        # Source: targets/personal/secrets/ledger-live/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "ledger-live"
EOF
        echo "  [✓] Brewfile (targets/personal/secrets/ledger-live/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (secrets/ledger-live) installed successfully."
}

function install_components_system_FruitJuice() {
    echo "Installing feature: system/FruitJuice"
    function run_00_Brewfile() {
        # Source: targets/personal/system/FruitJuice/00-Brewfile
        brew bundle -q --file=- <<EOF
            mas "FruitJuice", id: 671736912
EOF
        echo "  [✓] Brewfile (targets/personal/system/FruitJuice/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/FruitJuice) installed successfully."
}

function install_components_system_TheUnarchiver() {
    echo "Installing feature: system/TheUnarchiver"
    function run_00_Brewfile() {
        # Source: targets/personal/system/TheUnarchiver/00-Brewfile
        brew bundle -q --file=- <<EOF
            mas "The Unarchiver", id: 425424353
EOF
        echo "  [✓] Brewfile (targets/personal/system/TheUnarchiver/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/TheUnarchiver) installed successfully."
}

function install_components_system_bartender() {
    echo "Installing feature: system/bartender"
    function run_00_Brewfile() {
        # Source: targets/personal/system/bartender/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "bartender"
EOF
        echo "  [✓] Brewfile (targets/personal/system/bartender/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/bartender) installed successfully."
}

function install_components_system_iStatMenus() {
    echo "Installing feature: system/iStatMenus"
    function run_00_Brewfile() {
        # Source: targets/personal/system/iStatMenus/00-Brewfile
        brew bundle -q --file=- <<EOF
            mas "iStat Menus", id: 1319778037
EOF
        echo "  [✓] Brewfile (targets/personal/system/iStatMenus/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/iStatMenus) installed successfully."
}

function install_components_system_karabiner_elements() {
    echo "Installing feature: system/karabiner-elements"
    function run_00_Brewfile() {
        # Source: targets/personal/system/karabiner-elements/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "karabiner-elements"
EOF
        echo "  [✓] Brewfile (targets/personal/system/karabiner-elements/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/karabiner-elements) installed successfully."
}

function install_components_system_settings() {
    echo "Installing feature: system/settings"
    function run_00_run_sh() {
        # Source: targets/personal/system/settings/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/system/settings"
        # Enable or disable press and hold for keys in favor of key repeat
        defaults write -g ApplePressAndHoldEnabled -bool true || true
        # Don't store quick time history
        defaults write com.apple.QuickTimePlayerX NSRecentDocumentsLimit 0  || true
        defaults delete com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments || true
        defaults write com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments -dict-add MaxAmount 0 || true
        echo "  [✓] Script (targets/personal/system/settings/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (system/settings) installed successfully."
}

function install_components_system_surfshark() {
    echo "Installing feature: system/surfshark"
    function run_00_Brewfile() {
        # Source: targets/personal/system/surfshark/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "surfshark"
EOF
        echo "  [✓] Brewfile (targets/personal/system/surfshark/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (system/surfshark) installed successfully."
}

function install_components_terminal_ghostty() {
    echo "Installing feature: terminal/ghostty"
    function run_00_Brewfile() {
        # Source: targets/personal/terminal/ghostty/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "ghostty"
EOF
        echo "  [✓] Brewfile (targets/personal/terminal/ghostty/00-Brewfile) applied successfully."
    }
    function run_00_run_sh() {
        # Source: targets/personal/terminal/ghostty/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/terminal/ghostty"
        # TODO: Ensure ghostty config link
        echo "  [✓] Script (targets/personal/terminal/ghostty/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_00_run_sh
    echo "  Feature (terminal/ghostty) installed successfully."
}

function install_components_terminal_iterm2() {
    echo "Installing feature: terminal/iterm2"
    function run_00_Brewfile() {
        # Source: targets/personal/terminal/iterm2/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "iterm2"
EOF
        echo "  [✓] Brewfile (targets/personal/terminal/iterm2/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (terminal/iterm2) installed successfully."
}

function install_components_tools_bat() {
    echo "Installing feature: tools/bat"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/bat/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "bat"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/bat/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/bat) installed successfully."
}

function install_components_tools_btop() {
    echo "Installing feature: tools/btop"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/btop/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "btop"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/btop/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/btop) installed successfully."
}

function install_components_tools_cmake() {
    echo "Installing feature: tools/cmake"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/cmake/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "cmake"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/cmake/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/cmake) installed successfully."
}

function install_components_tools_docker() {
    echo "Installing feature: tools/docker"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/docker/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "docker", overwrite: true, link: true
            brew "docker-credential-helper-ecr"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/docker/00-Brewfile) applied successfully."
    }
    function run_00_run_sh() {
        # Source: targets/personal/tools/docker/00-run.sh
        pushd . > /dev/null
        cd "/Users/csaba/opt/workstation-setup/components/tools/docker"
        mkdir -p $HOME/.docker
        ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/docker-config.json $HOME/.docker/config.json
        echo "  [✓] Script (targets/personal/tools/docker/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_00_run_sh
    echo "  Feature (tools/docker) installed successfully."
}

function install_components_tools_jq() {
    echo "Installing feature: tools/jq"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/jq/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "jq"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/jq/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/jq) installed successfully."
}

function install_components_tools_watchman() {
    echo "Installing feature: tools/watchman"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/watchman/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "watchman"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/watchman/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/watchman) installed successfully."
}

function install_components_tools_websocat() {
    echo "Installing feature: tools/websocat"
    function run_00_Brewfile() {
        # Source: targets/personal/tools/websocat/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "websocat"
EOF
        echo "  [✓] Brewfile (targets/personal/tools/websocat/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/websocat) installed successfully."
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

