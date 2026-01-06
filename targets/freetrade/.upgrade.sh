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
    echo "  install_components_ai_gemini"
    echo "  install_components_cloud_google_cloud_proxy"
    echo "  install_components_cloud_google_firebase"
    echo "  install_components_cloud_google_gcloud"
    echo "  install_components_database_postgresql@18"
    echo "  install_components_desktop_obsidian"
    echo "  install_components_dev_github_desktop"
    echo "  install_components_dev_grpc_curl"
    echo "  install_components_dev_grpc_ui"
    echo "  install_components_dev_postman"
    echo "  install_components_dev_proto"
    echo "  install_components_dev_vscode"
    echo "  install_components_dev_zed"
    echo "  install_components_programming_asdf_asdf"
    echo "  install_components_programming_java_openjdk"
    echo "  install_components_programming_node_node"
    echo "  install_components_programming_node_nvm"
    echo "  install_components_programming_node_pnpm"
    echo "  install_components_programming_node_yarn"
    echo "  install_components_programming_python_pip"
    echo "  install_components_programming_python_pipx"
    echo "  install_components_programming_python_pyenv"
    echo "  install_components_programming_rust_rustup"
    echo "  install_components_programming_python_uv"
    echo "  install_components_programming_terraform_tfenv"
    echo "  install_components_secrets_1password_cli"
    echo "  install_components_secrets_berglas"
    echo "  install_components_terminal_ghostty"
    echo "  install_components_tools_ag"
    echo "  install_components_tools_bat"
    echo "  install_components_tools_btop"
    echo "  install_components_tools_bzip2"
    echo "  install_components_tools_colima_docker"
    echo "  install_components_tools_containerisation_lima_guest_agaent"
    echo "  install_components_tools_csvkit"
    echo "  install_components_tools_docker_cli"
    echo "  install_components_tools_fzf"
    echo "  install_components_tools_jq"
    echo "  install_components_tools_miller_csv"
    echo "  install_components_tools_quemu"
    echo "  install_components_tools_zlib"
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
    install_components_ai_gemini
    install_components_cloud_google_cloud_proxy
    install_components_cloud_google_firebase
    install_components_cloud_google_gcloud
    install_components_database_postgresql@18
    install_components_desktop_obsidian
    install_components_dev_github_desktop
    install_components_dev_grpc_curl
    install_components_dev_grpc_ui
    install_components_dev_postman
    install_components_dev_proto
    install_components_dev_vscode
    install_components_dev_zed
    install_components_programming_asdf_asdf
    install_components_programming_java_openjdk
    install_components_programming_node_node
    install_components_programming_node_nvm
    install_components_programming_node_pnpm
    install_components_programming_node_yarn
    install_components_programming_python_pip
    install_components_programming_python_pipx
    install_components_programming_python_pyenv
    install_components_programming_rust_rustup
    install_components_programming_python_uv
    install_components_programming_terraform_tfenv
    install_components_secrets_1password_cli
    install_components_secrets_berglas
    install_components_terminal_ghostty
    install_components_tools_ag
    install_components_tools_bat
    install_components_tools_btop
    install_components_tools_bzip2
    install_components_tools_colima_docker
    install_components_tools_containerisation_lima_guest_agaent
    install_components_tools_csvkit
    install_components_tools_docker_cli
    install_components_tools_fzf
    install_components_tools_jq
    install_components_tools_miller_csv
    install_components_tools_quemu
    install_components_tools_zlib

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
        cd $HOME/opt/workstation-setup/fundamentals/00-shell/10-folders
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
        cd $HOME/opt/workstation-setup/fundamentals/00-shell/20-linux-compatibility
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
        cd $HOME/opt/workstation-setup/fundamentals/00-shell/40-zsh
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
        cd $HOME/opt/workstation-setup/fundamentals/00-shell/50-git
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
        cd $HOME/opt/workstation-setup/fundamentals/30-essentials/tmux
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
        cd $HOME/opt/workstation-setup/fundamentals/30-essentials/vim-setup
        mkdir -p $HOME/.vim
        mkdir -p $HOME/.vim-tmp
        ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/vimrc.vim $HOME/.vimrc
        echo "  [✓] Script (fundamentals/30-essentials/vim-setup/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (30-essentials/vim-setup) installed successfully."
}

function install_components_ai_gemini() {
    echo "Installing feature: ai/gemini"
    function run_10_Brewfile() {
        # Source: targets/freetrade/ai/gemini/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "gemini-cli"
EOF
        echo "  [✓] Brewfile (targets/freetrade/ai/gemini/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (ai/gemini) installed successfully."
}

function install_components_cloud_google_cloud_proxy() {
    echo "Installing feature: cloud/google/cloud-proxy"
    function run_10_Brewfile() {
        # Source: targets/freetrade/cloud/google/cloud-proxy/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "cloud-sql-proxy"
EOF
        echo "  [✓] Brewfile (targets/freetrade/cloud/google/cloud-proxy/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (cloud/google/cloud-proxy) installed successfully."
}

function install_components_cloud_google_firebase() {
    echo "Installing feature: cloud/google/firebase"
    function run_00_Brewfile() {
        # Source: targets/freetrade/cloud/google/firebase/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "firebase-cli"
EOF
        echo "  [✓] Brewfile (targets/freetrade/cloud/google/firebase/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/google/firebase) installed successfully."
}

function install_components_cloud_google_gcloud() {
    echo "Installing feature: cloud/google/gcloud"
    function run_00_Brewfile() {
        # Source: targets/freetrade/cloud/google/gcloud/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "gcloud-cli"
EOF
        echo "  [✓] Brewfile (targets/freetrade/cloud/google/gcloud/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (cloud/google/gcloud) installed successfully."
}

function install_components_database_postgresql@18() {
    echo "Installing feature: database/postgresql@18"
    function run_00_Brewfile() {
        # Source: targets/freetrade/database/postgresql@18/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "postgresql@18"
EOF
        echo "  [✓] Brewfile (targets/freetrade/database/postgresql@18/00-Brewfile) applied successfully."
    }
    function run_10_run_sh() {
        # Source: targets/freetrade/database/postgresql@18/10-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/database/postgresql@18
        brew link postgresql@18
        echo "  [✓] Script (targets/freetrade/database/postgresql@18/10-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_10_run_sh
    echo "  Feature (database/postgresql@18) installed successfully."
}

function install_components_desktop_obsidian() {
    echo "Installing feature: desktop/obsidian"
    function run_00_Brewfile() {
        # Source: targets/freetrade/desktop/obsidian/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "obsidian"
EOF
        echo "  [✓] Brewfile (targets/freetrade/desktop/obsidian/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (desktop/obsidian) installed successfully."
}

function install_components_dev_github_desktop() {
    echo "Installing feature: dev/github-desktop"
    function run_10_Brewfile() {
        # Source: targets/freetrade/dev/github-desktop/10-Brewfile
        brew bundle -q --file=- <<EOF
            cask "github"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/github-desktop/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (dev/github-desktop) installed successfully."
}

function install_components_dev_grpc_curl() {
    echo "Installing feature: dev/grpc-curl"
    function run_10_Brewfile() {
        # Source: targets/freetrade/dev/grpc-curl/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "grpcurl"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/grpc-curl/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (dev/grpc-curl) installed successfully."
}

function install_components_dev_grpc_ui() {
    echo "Installing feature: dev/grpc-ui"
    function run_10_Brewfile() {
        # Source: targets/freetrade/dev/grpc-ui/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "grpcui"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/grpc-ui/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (dev/grpc-ui) installed successfully."
}

function install_components_dev_postman() {
    echo "Installing feature: dev/postman"
    function run_00_Brewfile() {
        # Source: targets/freetrade/dev/postman/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "postman"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/postman/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/postman) installed successfully."
}

function install_components_dev_proto() {
    echo "Installing feature: dev/proto"
    function run_10_Brewfile() {
        # Source: targets/freetrade/dev/proto/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "proto"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/proto/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (dev/proto) installed successfully."
}

function install_components_dev_vscode() {
    echo "Installing feature: dev/vscode"
    function run_00_Brewfile() {
        # Source: targets/freetrade/dev/vscode/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "visual-studio-code"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/vscode/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/vscode) installed successfully."
}

function install_components_dev_zed() {
    echo "Installing feature: dev/zed"
    function run_00_Brewfile() {
        # Source: targets/freetrade/dev/zed/00-Brewfile
        brew bundle -q --file=- <<EOF
            cask "zed"
EOF
        echo "  [✓] Brewfile (targets/freetrade/dev/zed/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (dev/zed) installed successfully."
}

function install_components_programming_asdf_asdf() {
    echo "Installing feature: programming/asdf/asdf"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/asdf/asdf/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "asdf"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/asdf/asdf/00-Brewfile) applied successfully."
    }
    function run_10_run_sh() {
        # Source: targets/freetrade/programming/asdf/asdf/10-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/asdf/asdf
        asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
        asdf plugin add yarn https://github.com/twuni/asdf-yarn
        # asdf plugin add pnpm https://github.com/jonathanmorley/asdf-pnpm
        asdf plugin add gcloud https://github.com/jthegedus/asdf-gcloud
        asdf plugin add github-cli https://github.com/bartlomiejdanek/asdf-github-cli.git
        asdf plugin add terraform https://github.com/asdf-community/asdf-hashicorp.git
        asdf install nodejs lts
        # asdf install pnpm latest
        asdf install yarn latest
        asdf install gcloud latest
        # asdf install github-cli latest
        asdf install terraform latest
        asdf set -u nodejs lts
        # asdf set -u pnpm latest
        asdf set -u yarn latest
        asdf set -u gcloud latest
        # asdf global github-cli latest
        asdf set -u terraform latest
        echo "  [✓] Script (targets/freetrade/programming/asdf/asdf/10-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_10_run_sh
    echo "  Feature (programming/asdf/asdf) installed successfully."
}

function install_components_programming_java_openjdk() {
    echo "Installing feature: programming/java/openjdk"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/java/openjdk/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "openjdk"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/java/openjdk/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/java/openjdk) installed successfully."
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
        cd $HOME/opt/workstation-setup/components/programming/node/nvm
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

function install_components_programming_node_pnpm() {
    echo "Installing feature: programming/node/pnpm"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/node/pnpm/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "pnpm"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/node/pnpm/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/node/pnpm) installed successfully."
}

function install_components_programming_node_yarn() {
    echo "Installing feature: programming/node/yarn"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/node/yarn/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "yarn"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/node/yarn/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/node/yarn) installed successfully."
}

function install_components_programming_python_pip() {
    echo "Installing feature: programming/python/pip"
    function run_00_run_sh() {
        # Source: targets/freetrade/programming/python/pip/00-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/python/pip
        $SYSTEM_PYTHON -m pip install --upgrade pip
        echo "  [✓] Script (targets/freetrade/programming/python/pip/00-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_run_sh
    echo "  Feature (programming/python/pip) installed successfully."
}

function install_components_programming_python_pipx() {
    echo "Installing feature: programming/python/pipx"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/python/pipx/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "pipx"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/python/pipx/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/python/pipx) installed successfully."
}

function install_components_programming_python_pyenv() {
    echo "Installing feature: programming/python/pyenv"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/python/pyenv/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "pyenv"
            brew "pyenv-virtualenv"
            brew "pyenv-virtualenvwrapper"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/python/pyenv/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (programming/python/pyenv) installed successfully."
}

function install_components_programming_rust_rustup() {
    echo "Installing feature: programming/rust/rustup"
    function run_00_run_sh() {
        # Source: components/programming/rust/rustup/00-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/rust/rustup
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
        cd $HOME/opt/workstation-setup/components/programming/rust/rustup
        rustup-init --no-modify-path -y
        echo "  [✓] Script (components/programming/rust/rustup/20-runonce.sh) executed successfully."
        popd > /dev/null
    }
    function run_30_run_sh() {
        # Source: components/programming/rust/rustup/30-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/rust/rustup
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
        cd $HOME/opt/workstation-setup/components/programming/python/uv
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "  [✓] Script (targets/freetrade/programming/python/uv/00-runonce.sh) executed successfully."
        popd > /dev/null
    }
    function run_10_run_sh() {
        # Source: targets/freetrade/programming/python/uv/10-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/python/uv
        uv self update
        echo "  [✓] Script (targets/freetrade/programming/python/uv/10-run.sh) executed successfully."
        popd > /dev/null
    }

    _run_once "install_programming_python_uv_00_runonce_sh" run_00_runonce_sh
    run_10_run_sh
    echo "  Feature (programming/python/uv) installed successfully."
}

function install_components_programming_terraform_tfenv() {
    echo "Installing feature: programming/terraform/tfenv"
    function run_00_Brewfile() {
        # Source: targets/freetrade/programming/terraform/tfenv/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "tfenv"
EOF
        echo "  [✓] Brewfile (targets/freetrade/programming/terraform/tfenv/00-Brewfile) applied successfully."
    }
    function run_10_run_sh() {
        # Source: targets/freetrade/programming/terraform/tfenv/10-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/programming/terraform/tfenv
        tfenv install
        echo "  [✓] Script (targets/freetrade/programming/terraform/tfenv/10-run.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    run_10_run_sh
    echo "  Feature (programming/terraform/tfenv) installed successfully."
}

function install_components_secrets_1password_cli() {
    echo "Installing feature: secrets/1password-cli"
    function run_10_Brewfile() {
        # Source: targets/freetrade/secrets/1password-cli/10-Brewfile
        brew bundle -q --file=- <<EOF
            cask "1password-cli"
EOF
        echo "  [✓] Brewfile (targets/freetrade/secrets/1password-cli/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (secrets/1password-cli) installed successfully."
}

function install_components_secrets_berglas() {
    echo "Installing feature: secrets/berglas"
    function run_10_Brewfile() {
        # Source: targets/freetrade/secrets/berglas/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "berglas"
EOF
        echo "  [✓] Brewfile (targets/freetrade/secrets/berglas/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (secrets/berglas) installed successfully."
}

function install_components_terminal_ghostty() {
    echo "Installing feature: terminal/ghostty"
    function run_10_run_sh() {
        # Source: targets/freetrade/terminal/ghostty/10-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/terminal/ghostty
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

function install_components_tools_ag() {
    echo "Installing feature: tools/ag"
    function run_Brewfile() {
        # Source: targets/freetrade/tools/ag/Brewfile
        brew bundle -q --file=- <<EOF
            brew "ag"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/ag/Brewfile) applied successfully."
    }

    run_Brewfile
    echo "  Feature (tools/ag) installed successfully."
}

function install_components_tools_bat() {
    echo "Installing feature: tools/bat"
    function run_00_Brewfile() {
        # Source: targets/freetrade/tools/bat/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "bat"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/bat/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/bat) installed successfully."
}

function install_components_tools_btop() {
    echo "Installing feature: tools/btop"
    function run_00_Brewfile() {
        # Source: targets/freetrade/tools/btop/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "btop"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/btop/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/btop) installed successfully."
}

function install_components_tools_bzip2() {
    echo "Installing feature: tools/bzip2"
    function run_10_Brewfile() {
        # Source: targets/freetrade/tools/bzip2/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "bzip2"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/bzip2/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (tools/bzip2) installed successfully."
}

function install_components_tools_colima_docker() {
    echo "Installing feature: tools/colima-docker"
    function run_00_Brewfile() {
        # Source: targets/freetrade/tools/colima-docker/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "colima"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/colima-docker/00-Brewfile) applied successfully."
    }
    function run_10_runonce_sh() {
        # Source: targets/freetrade/tools/colima-docker/10-runonce.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/tools/colima-docker
        colima start
        docker context use colima
        docker context ls
        echo "  [✓] Script (targets/freetrade/tools/colima-docker/10-runonce.sh) executed successfully."
        popd > /dev/null
    }

    run_00_Brewfile
    _run_once "install_tools_colima_docker_10_runonce_sh" run_10_runonce_sh
    echo "  Feature (tools/colima-docker) installed successfully."
}

function install_components_tools_containerisation_lima_guest_agaent() {
    echo "Installing feature: tools/containerisation/lima-guest-agaent"
    function run_10_Brewfile() {
        # Source: targets/freetrade/tools/containerisation/lima-guest-agaent/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "lima-additional-guestagents"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/containerisation/lima-guest-agaent/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (tools/containerisation/lima-guest-agaent) installed successfully."
}

function install_components_tools_csvkit() {
    echo "Installing feature: tools/csvkit"
    function run_Brewfile() {
        # Source: targets/freetrade/tools/csvkit/Brewfile
        brew bundle -q --file=- <<EOF
            brew "csvkit"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/csvkit/Brewfile) applied successfully."
    }

    run_Brewfile
    echo "  Feature (tools/csvkit) installed successfully."
}

function install_components_tools_docker_cli() {
    echo "Installing feature: tools/docker-cli"
    function run_10_Brewfile() {
        # Source: targets/freetrade/tools/docker-cli/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "docker"
            brew "docker-buildx"
            brew "docker-compose"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/docker-cli/10-Brewfile) applied successfully."
    }
    function run_20_run_sh() {
        # Source: targets/freetrade/tools/docker-cli/20-run.sh
        pushd . > /dev/null
        cd $HOME/opt/workstation-setup/components/tools/docker-cli
        mkdir -p ~/.docker/cli-plugins
        ln -sfn $(which docker-buildx) ~/.docker/cli-plugins/docker-buildx
        ln -sfn $(which docker-compose) ~/.docker/cli-plugins/docker-compose
        echo "  [✓] Script (targets/freetrade/tools/docker-cli/20-run.sh) executed successfully."
        popd > /dev/null
    }

    run_10_Brewfile
    run_20_run_sh
    echo "  Feature (tools/docker-cli) installed successfully."
}

function install_components_tools_fzf() {
    echo "Installing feature: tools/fzf"
    function run_Brewfile() {
        # Source: targets/freetrade/tools/fzf/Brewfile
        brew bundle -q --file=- <<EOF
            brew "fzf"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/fzf/Brewfile) applied successfully."
    }

    run_Brewfile
    echo "  Feature (tools/fzf) installed successfully."
}

function install_components_tools_jq() {
    echo "Installing feature: tools/jq"
    function run_00_Brewfile() {
        # Source: targets/freetrade/tools/jq/00-Brewfile
        brew bundle -q --file=- <<EOF
            brew "jq"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/jq/00-Brewfile) applied successfully."
    }

    run_00_Brewfile
    echo "  Feature (tools/jq) installed successfully."
}

function install_components_tools_miller_csv() {
    echo "Installing feature: tools/miller-csv"
    function run_Brewfile() {
        # Source: targets/freetrade/tools/miller-csv/Brewfile
        brew bundle -q --file=- <<EOF
            brew "miller"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/miller-csv/Brewfile) applied successfully."
    }

    run_Brewfile
    echo "  Feature (tools/miller-csv) installed successfully."
}

function install_components_tools_quemu() {
    echo "Installing feature: tools/quemu"
    function run_Brewfile() {
        # Source: targets/freetrade/tools/quemu/Brewfile
        brew bundle -q --file=- <<EOF
            brew "qemu"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/quemu/Brewfile) applied successfully."
    }

    run_Brewfile
    echo "  Feature (tools/quemu) installed successfully."
}

function install_components_tools_zlib() {
    echo "Installing feature: tools/zlib"
    function run_10_Brewfile() {
        # Source: targets/freetrade/tools/zlib/10-Brewfile
        brew bundle -q --file=- <<EOF
            brew "zlib"
EOF
        echo "  [✓] Brewfile (targets/freetrade/tools/zlib/10-Brewfile) applied successfully."
    }

    run_10_Brewfile
    echo "  Feature (tools/zlib) installed successfully."
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

