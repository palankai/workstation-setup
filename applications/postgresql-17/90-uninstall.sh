# Stops the service, then uninstalls the formula (which also unlinks it).
# The data directory ($(brew --prefix)/var/postgresql@17) is left in place.
if brew list --formula postgresql@17 >/dev/null 2>&1; then
  brew services stop postgresql@17 >/dev/null 2>&1 || true
  brew uninstall --formula postgresql@17
fi
