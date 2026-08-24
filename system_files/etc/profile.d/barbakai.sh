# Barbakaï OS identity
export BARBAKAI_OS=1
if [ -z "${PS1:-}" ]; then
    return 0 2>/dev/null || exit 0
fi
# Interactive shells only: a short banner the first time per tty session
if [ -z "${BARBAKAI_BANNER_SHOWN:-}" ] && [ -t 1 ]; then
    export BARBAKAI_BANNER_SHOWN=1
    printf '\n  Barbakaï OS  ·  The Game Control  ·  barbakai-info\n\n'
fi
