if [ -z "$QT_QPA_PLATFORM" ]; then
    set -a
    for i in /var/lib/environment/nemo/*.conf; do
        . $i
    done
    set +a
fi
