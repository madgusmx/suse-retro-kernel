#!/usr/bin/env python3
"""preparar_config.py ARBOL FRAGMENTO: arch/i386/defconfig + fragmento -> ARBOL/.config (después: make ARCH=i386 oldconfig)."""
import re, sys
arbol, fragf = sys.argv[1], sys.argv[2]
frag = {}
for l in open(fragf):
    m = re.match(r'(CONFIG_\w+)=(.*)', l)
    if m: frag[m.group(1)] = m.group(2); continue
    m = re.match(r'# (CONFIG_\w+) is not set', l)
    if m: frag[m.group(1)] = 'n'
def key(l):
    m = re.match(r'(CONFIG_\w+)=', l) or re.match(r'# (CONFIG_\w+) is not set', l)
    return m.group(1) if m else None
out = [l for l in open(arbol + '/arch/i386/defconfig') if key(l) not in frag]
out += ['# %s is not set\n' % k if v == 'n' else '%s=%s\n' % (k, v) for k, v in frag.items()]
open(arbol + '/.config', 'w').writelines(out)
