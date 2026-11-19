#!/bin/bash
# armar_kernel.sh - Linux 2.4.37.11-retro para SuSE Linux 5.3 (retroblog): bzImage + módulos.
# Necesita un gcc de la época (gcc 3.3 / 2.95, p. ej. Debian sarge i386): el gcc moderno no compila 2.4.
#   bash armar_kernel.sh linux-2.4.37.11.tar CONFIG SALIDA_DIR
# CONFIG: config-2.4.37.11-retro-mod (sale de preparar_config.py + modularizar.py + make ARCH=i386 oldconfig)
# Deja en SALIDA_DIR: vmlinuz, System.map, config y raiz/lib/modules/2.4.37.11-retro; los módulos que no
# compilan quedan en modulos-fallidos.txt (se agregan a modulos-no.txt y se vuelve a correr).
set -e
mkdir -p "${3:?salida}"   # el readlink -f de sarge falla si no existe
TAR=$(readlink -f ${1:?tarball}); CONF=$(readlink -f ${2:?config}); OUT=$(readlink -f $3); AQUI=$(cd "$(dirname "$0")" && pwd)
CC=${CC:-gcc-3.3}; J=${J:-12}
M="make ARCH=i386 CC=$CC HOSTCC=$CC"
W=$(mktemp -d); cd $W
tar xf "$TAR"
cd linux-2.4.37.11
patch -p1 < $AQUI/ahci-clase.diff
sed -i 's/^EXTRAVERSION =.*/EXTRAVERSION = .11-retro/' Makefile
cp $CONF .config
yes "" | $M oldconfig > /dev/null
$M dep > dep.log 2>&1 || { tail -30 dep.log; exit 1; }
$M -j$J bzImage > bzImage.log 2>&1 || { tail -30 bzImage.log; exit 1; }
$M -k -j$J modules > modules.log 2>&1 || true
grep -E "^make\[[0-9]+\]: \*\*\* \[[^]]*\.o\]" modules.log | sed 's/.*\[\(.*\.o\)\].*/\1/' | sort -u > $OUT/modulos-fallidos.txt || true
rm -rf $OUT/raiz; $M INSTALL_MOD_PATH=$OUT/raiz DEPMOD=/bin/true modules_install > modules_install.log 2>&1 || tail -20 modules_install.log
cp arch/i386/boot/bzImage $OUT/vmlinuz-2.4.37.11-retro
cp System.map $OUT/System.map-2.4.37.11-retro
cp .config $OUT/config-2.4.37.11-retro
echo "módulos: $(find $OUT/raiz -name '*.o' | wc -l)   fallidos: $(wc -l < $OUT/modulos-fallidos.txt)"
ls -la $OUT
