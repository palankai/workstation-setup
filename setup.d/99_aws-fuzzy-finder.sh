if [ "$ARCH" = "arm64" ]; then
    ensure_repository https://github.com/epoplavskis/aws-fuzzy-finder.git /tmp/aws-fuzzy-finder
    (cd /tmp/aws-fuzzy-finder/; $SYSTEM_PIP install .)
    rm -rf /tmp/aws-fuzzy-finder
else
    $SYSTEM_PIP install aws-fuzzy-finder
fi
