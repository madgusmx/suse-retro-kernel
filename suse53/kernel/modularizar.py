#!/usr/bin/env python3
"""modularizar.py ARBOL: sobre el .config ya preparado, pone como módulo (=m) todo tristate de las áreas de
"extras" que no esté compilado dentro. Lo esencial para arrancar (IDE, SATA, ext2, red común, consola) sigue en =y.
Las listas NO y SACAR son drivers que no compilan con gcc 3.3 en 2.4.37.11 o que estorban (DRM/AGP)."""
import re, sys, glob, os
arbol = sys.argv[1]
AREAS = ['net', 'fs', 'drivers/sound', 'drivers/usb', 'drivers/scsi', 'drivers/parport', 'drivers/net',
         'drivers/char', 'drivers/block', 'drivers/cdrom', 'drivers/input', 'drivers/pnp', 'drivers/media',
         'drivers/ieee1394', 'drivers/i2c', 'lib', 'crypto']
NO = set(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modulos-no.txt')).read().split())
SACAR = {'CONFIG_DRM', 'CONFIG_AGP'}
FORZAR_M = {'CONFIG_SOUND_SB', 'CONFIG_SOUND_MPU401', 'CONFIG_SOUND_ES1370', 'CONFIG_SOUND_ES1371', 'CONFIG_SOUND_ICH'}  # sin parámetros, dentro del kernel solo se quejan
sims = set()
for a in AREAS:
    for f in glob.glob(f'{arbol}/{a}/**/Config.in', recursive=True):
        for l in open(f, errors='replace'):
            m = re.match(r"\s*(?:dep_)?tristate\s+'[^']*'\s+(CONFIG_\w+)", l)
            if m: sims.add(m.group(1))
cfg = open(f'{arbol}/.config').read().splitlines()
estado = {}
for l in cfg:
    m = re.match(r'(CONFIG_\w+)=(.*)', l) or re.match(r'# (CONFIG_\w+) is not set', l)
    if m: estado[m.group(1)] = m.group(2) if m.lastindex == 2 else 'n'
fuera = []
for l in cfg:
    k = re.match(r'#? ?(CONFIG_\w+)', l)
    if k and (k.group(1) in sims or k.group(1) in SACAR): continue
    fuera.append(l)
for s in sorted(sims | SACAR):
    v = estado.get(s, 'n')
    if s in SACAR or s in NO: fuera.append(f'# {s} is not set')
    elif v == 'y' and s not in FORZAR_M: fuera.append(f'{s}=y')
    else: fuera.append(f'{s}=m')
fuera += ['CONFIG_MODULES=y', 'CONFIG_KMOD=y']
fuera = [l for l in fuera if l not in ('# CONFIG_MODULES is not set', '# CONFIG_KMOD is not set')]
open(f'{arbol}/.config', 'w').write('\n'.join(fuera) + '\n')
print(len(sims), 'tristates;', sum(1 for s in sims if estado.get(s) == 'y'), 'quedan =y')
