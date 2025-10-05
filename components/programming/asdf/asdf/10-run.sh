asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin add yarn https://github.com/twuni/asdf-yarn
asdf plugin add pnpm https://github.com/jonathanmorley/asdf-pnpm
asdf plugin add gcloud https://github.com/jthegedus/asdf-gcloud
asdf plugin add github-cli https://github.com/bartlomiejdanek/asdf-github-cli.git
asdf plugin add terraform https://github.com/asdf-community/asdf-hashicorp.git


asdf install nodejs lts
asdf install pnpm latest
asdf install yarn latest
asdf install gcloud latest
# asdf install github-cli latest
asdf install terraform latest

asdf set -u nodejs lts
asdf set -u pnpm latest
asdf set -u yarn latest
asdf set -u gcloud latest
# asdf global github-cli latest
asdf set -u terraform latest
