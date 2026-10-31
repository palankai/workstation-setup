# Stops the service, then uninstalls the formula; the tap stays.
# The data directory ($(brew --prefix)/var/surreal.db) is left in place.
if brew list --formula surrealdb/tap/surreal-db >/dev/null 2>&1; then
  brew services stop surrealdb/tap/surreal-db >/dev/null 2>&1 || true
  brew uninstall --formula surrealdb/tap/surreal-db
fi
