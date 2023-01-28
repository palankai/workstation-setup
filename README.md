# Secretless Idempotent macOS setup

Yet another migration from my previous setup.
It seems Ansible isn't a viable option anymore.

This repository contains my macOS configuration.
Most of the steps are automated. The script might ask for the sudo password.
There are some manual steps after the installation.
The goal is not to fully automate but ensure the smoothest possible start on a new installation.

It also helps me to keep more or less the same environment both on my personal and work machine, which helps me to reduce the context switching.

I don't recommend using it as it is. Get inspired, copy part of it.

This repository is kept up-to-date with my current needs; it includes workarounds. I update them if necessary when I find an obstacle.

The repository doesn't contain any secrets.

## Full setup steps

### 0. Insert Yubikey

### 1. Initialise the machine

Idempotent, but needed only once.

Download and execute the `initial-setup.sh` file.

Simplified install:
```
sh -c "$(curl -H 'Cache-Control: no-cache, no-store' -sSL https://raw.githubusercontent.com/palankai/workstation-setup/master/initial-setup.sh)"
```

That script does the following:
- Environment setup, so my machine setups can be slightly different
- Install requirements: homebrew and GPG
- sets up GPG & ssh
- Clones the repository

### 2. Start the setup process

This can and should be repeated frequently

In the `~/opt/workstation-setup` exectue:

```
sh setup.sh
```

### 3. Manual steps

Most of these steps need to be done once.


### 4. Manual applications

- [Surfshark](https://surfshark.com/)
- [Freecad Realthunder](https://github.com/realthunder/FreeCAD)
- [Blender](https://www.blender.org/)
- [SuperSlicer](https://github.com/supermerill/SuperSlicer)
- [Bartender](https://www.macbartender.com/)
