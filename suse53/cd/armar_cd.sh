#!/bin/bash
# armar_cd.sh - CD complementario de k_retro24 para YaST 0.97 (SuSE Linux 5.3): un ISO que YaST acepta como medio
# de instalación y en el que solo aparece k_retro24 (serie «kret»). No lleva archivos de SuSE: el catálogo es nuestro.
#   bash suse53/cd/armar_cd.sh k_retro24-2.4.37.11-2.i386.rpm DIR_KERNEL [salida.iso]
# DIR_KERNEL: la salida de armar_kernel.sh (vmlinuz, System.map, config, raiz/lib/modules) para la lista de archivos.
# YaST revisa tres cosas: suse/setup/descr/*.pkd (paquetes), *.ser (series) y /.S.u.S.E-disk-001 (sin él: «Wrong CD»).
set -e
RPM=${1:?uso: armar_cd.sh k_retro24.rpm DIR_KERNEL [salida.iso]}; K=${2:?DIR_KERNEL}
OUT=${3:-k_retro24-2.4.37.11-2-cd.iso}
IDENT='S.u.S.E.-Linux-FTP-DE-i386-5.3.0#0'      # el DIST_IDENT de SuSE 5.3 (edición FTP)
VER=2.4.37.11-2
T=$(mktemp -d); D=$T/suse/setup/descr
mkdir -p $D $T/suse/setup/du $T/suse/kret1
cp "$RPM" $T/suse/kret1/k_retro24.rpm
RSIZE=$(wc -c < "$RPM")
printf '%s\n1\n' "$IDENT" > $T/.S.u.S.E-disk-001
cat > $D/info <<EOI
ELF
MIN_YAST_VERSION 0.90
DIST_STRING      S.u.S.E.
DIST_IDENT       $IDENT
MIN_DIST_VERSION 5.3
HAS_LIVE_CD=0
EOI
printf '##\n## k_retro24 add-on CD - series\n##\nSeries: kret\nStatus:\nVersion:\n##\n' > $D/common.ser
for L in english german french; do
    printf '##\n## k_retro24 add-on CD - series\n##\nSeries: kret\nLabel: Linux 2.4 kernel (k_retro24 add-on CD)\nNotify:\nYfiton:\nDescription:\nNoitpircsed:\n##\n' > $D/$L.ser
done
# lista de archivos (KB) para el cálculo de espacio de YaST
FIL=$T/suse/setup/du/k_retro24.fil
{ echo '##'; echo '## k_retro24 add-on CD - files'; echo '##'; echo 'Files:'
  for f in vmlinuz System.map config; do echo "boot/$f-2.4.37.11-retro $(( ($(wc -c < $K/$f-2.4.37.11-retro) + 1023) / 1024 ))"; done
  (cd $K/raiz && find lib/modules -type f -name '*.o' -printf '%p %k\n')
  for f in insmod modinfo depmod despachar; do echo "lib/modutils-2.4/$f 60"; done
  echo 'Selif:'; } > $FIL
ISIZE=$(awk '/ [0-9]+$/ { s += $NF } END { print s * 1024 }' $FIL)
cat > $D/common.pkd <<EOI
##
## k_retro24 add-on CD - packages
##
## -----> k_retro24 <-----
##
Filename:      k_retro24.rpm
Series:        kret
InstPath:      01 /kret1/
Size:          $ISIZE $RSIZE
Buildtime:     907648800
DepAND:        lilo  modules
DepOR:
DepExcl:
Flag:          A(k_retro24 KERNEL ) ELF
Category:
Copyright:     GPL (c) 2026 retroblog
AuthorName:    retroblog
AuthorEmail:
AuthorAddress: canaldelasrecetas.com
Version:       $VER
StartCommand:
EOI
EN="Linux 2.4.37.11-retro for SuSE Linux 5.3: DMA, SATA/AHCI, USB keyboards, GBs of RAM, 541 modules and modutils 2.4.27. Installs next to SuSE's kernel 2.0.35, which stays the default: type linux24 at the LILO prompt. rpm -e k_retro24 undoes everything. https://github.com/madgusmx/suse-retro-kernel"
desc() { printf '##\n## k_retro24 add-on CD - package descriptions\n##\n## -----> k_retro24 <-----\n##\nFilename:      k_retro24.rpm\nLabel:         %s\nNotify:\nYfiton:\nDelnotify:\nYfitonled:\nDescription:\n%s\n\nContains: k_retro24-%s\nNoitpircsed:\n' "$2" "$3" "$VER" > $D/$1; }
desc english.pkd "Linux 2.4.37.11-retro kernel (DMA, SATA, USB)" "$EN"
desc german.pkd "Linux-2.4.37.11-retro-Kernel (DMA, SATA, USB)" "Linux 2.4.37.11-retro fuer SuSE Linux 5.3: DMA, SATA/AHCI, USB-Tastaturen, GBs RAM, 541 Module und modutils 2.4.27. Wird neben dem Kernel 2.0.35 installiert, der Standard bleibt: am LILO-Prompt linux24 eingeben. https://github.com/madgusmx/suse-retro-kernel"
desc french.pkd "Noyau Linux 2.4.37.11-retro (DMA, SATA, USB)" "$EN"
cat > $T/README.TXT <<'EOI'
k_retro24 2.4.37.11-2 - add-on CD for SuSE Linux 5.3 (YaST 0.97)

1. Put this CD in the drive (or attach the ISO to the virtual machine).
2. As root: yast -> Choose/Install packages -> Change/create configuration -> series kret -> mark k_retro24
   -> F10 -> Start installation.  (Or simply: mount the CD and rpm -ivh suse/kret1/k_retro24.rpm)
3. Reboot and type linux24 at the LILO prompt.  To remove it: rpm -e k_retro24.

YaST only sees k_retro24 on this CD; the rest of SuSE stays as installed.
https://github.com/madgusmx/suse-retro-kernel
EOI
MK=$(command -v genisoimage || command -v mkisofs)
$MK -quiet -r -J -V K_RETRO24 -A "k_retro24 2.4.37.11-2 add-on CD for SuSE Linux 5.3" -o "$OUT" $T
rm -rf $T
echo "$OUT"
