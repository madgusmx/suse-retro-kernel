Name: k_retro24
Version: 2.4.37.11
Release: 2
Copyright: GPL
Group: Kernel
Summary: Linux 2.4.37.11-retro para SuSE Linux 5.3: DMA, SATA/AHCI, USB, 541 modulos y modutils 2.4.27
Source0: k_retro24-bin-2.4.37.11.tar.gz
Source1: modutils-2.4.27.tar.gz
Source2: despachar
Source3: README.k_retro24
Source4: kernel-retro24-fuentes.tar.gz
Packager: retroblog <canaldelasrecetas.com>
BuildRoot: /var/tmp/k_retro24-root

%description
Linux 2.4.37.11 (el ultimo 2.4) configurado para SuSE Linux 5.3 y compilado para 486: arranca en PCs retro
y en PCs con GBs de RAM. Dentro del kernel: IDE con DMA (PIIX, VIA, AMD, SiS, ALi, Promise, HPT...),
SATA por libata (AHCI con cualquier controlador por clase PCI, PIIX/ICH, VIA, SiS, NVIDIA, Promise, SiI),
ide-scsi y sg (para grabar CDs con cdrecord), ext2/ext3, iso9660, red (NE2000, RTL8139, e100, e1000, PCnet,
tulip, 3c59x), USB con teclado y raton, a.out, SysV IPC (ADABAS). 541 modulos: sonido OSS, AppleTalk, IPX,
mas redes, SCSI, sistemas de archivos, I2C/bttv...

Instala modutils 2.4.27 (compilado aqui, con la libc5 de SuSE 5.3) junto al modules 2.1.85 de SuSE:
/sbin/insmod, modprobe, etc. eligen segun el kernel que corre. Agrega la entrada linux24 a /etc/lilo.conf
y corre lilo; el kernel 2.0.35 de SuSE queda como estaba.

El kernel se compila con gcc 3.3 (Debian sarge): el gcc 2.7.2.1 de SuSE 5.3 no compila Linux 2.4.
Las fuentes, el parche, la configuracion y los guiones van en kernel-retro24-fuentes.tar.gz.
https://github.com/madgusmx/xf86vesa

%prep
%setup -c -n k_retro24 -T -a 0
%setup -c -n k_retro24 -T -D -a 1
find modutils-2.4.27 -print | xargs touch
# /etc/conf.modules queda como enlace a /etc/modules.conf (para el modules 2.1.85 de SuSE): sin avisos
( echo '#define NO_WARN_ON_OLD_LINK 1'; cat modutils-2.4.27/util/config.c ) > config.c.tmp && mv config.c.tmp modutils-2.4.27/util/config.c

%build
cd modutils-2.4.27
# el bash 1.14 de SuSE 5.3 se cae con «unset MAIL» (lo hace el configure de autoconf 2.57): entorno limpio
env - PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/root /bin/sh ./configure --prefix=/
# genksyms no hace falta (solo sirve para compilar kernels)
for d in util obj insmod depmod; do make -C $d all; done

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/lib/modutils-2.4 $RPM_BUILD_ROOT/usr/doc/packages/k_retro24
cp -a boot lib $RPM_BUILD_ROOT/
M=$RPM_BUILD_ROOT/lib/modutils-2.4
install -m 755 -s modutils-2.4.27/insmod/insmod modutils-2.4.27/insmod/modinfo modutils-2.4.27/depmod/depmod $M/
for p in modprobe rmmod lsmod ksyms kallsyms; do ln -s insmod $M/$p; done
install -m 755 $RPM_SOURCE_DIR/despachar $M/despachar
cp $RPM_SOURCE_DIR/README.k_retro24 $RPM_SOURCE_DIR/kernel-retro24-fuentes.tar.gz $RPM_BUILD_ROOT/usr/doc/packages/k_retro24/
cp modutils-2.4.27/COPYING $RPM_BUILD_ROOT/usr/doc/packages/k_retro24/COPYING
( cd $RPM_BUILD_ROOT && find lib/modules -type f -print -o -type l -print | sed 's,^,/,' | sort ) > ../modulos.files

%post
# 1. modutils: los de SuSE (2.1.85) a /lib/modutils-2.0, el despachador en /sbin
if [ ! -d /lib/modutils-2.0 ]; then
    mkdir -p /lib/modutils-2.0
    for p in insmod rmmod lsmod modprobe depmod ksyms; do
        if [ -f /sbin/$p -o -L /sbin/$p ]; then mv /sbin/$p /lib/modutils-2.0/$p; fi
    done
fi
for p in insmod rmmod lsmod modprobe depmod ksyms modinfo kallsyms; do
    ln -sf /lib/modutils-2.4/despachar /sbin/$p
done
# /etc/modules.conf es el nombre de modutils 2.4; el modules 2.1.85 de SuSE lee /etc/conf.modules por el enlace
if [ -f /etc/conf.modules -a ! -L /etc/conf.modules -a ! -e /etc/modules.conf ]; then
    mv /etc/conf.modules /etc/modules.conf && ln -s modules.conf /etc/conf.modules
fi
/lib/modutils-2.4/depmod -a -F /boot/System.map-2.4.37.11-retro 2.4.37.11-retro
# 2. LILO: entrada linux24 con la misma raiz que el sistema
if ! grep -q "vmlinuz-2.4.37.11-retro" /etc/lilo.conf 2>/dev/null; then
    RAIZ=`awk '$2 == "/" { print $1 }' /etc/fstab`
    # nopentium: con mas de 896 MB (highmem) este kernel para 486 entra en panico con paginas de 4 MB
    printf "image = /boot/vmlinuz-2.4.37.11-retro\n    root = %s\n    label = linux24\n    append = \"nopentium\"\n    read-only\n" $RAIZ >> /etc/lilo.conf
fi
# actualizacion desde 2.4.37.11-1: su entrada no traia nopentium
if ! grep -q "nopentium" /etc/lilo.conf; then
    awk '{ print } /label[ \t]*=[ \t]*linux24/ { print "    append = \"nopentium\"" }' /etc/lilo.conf > /etc/lilo.conf.k24 && \
        mv /etc/lilo.conf.k24 /etc/lilo.conf
fi
/sbin/lilo || echo "k_retro24: lilo fallo; revisa /etc/lilo.conf (el kernel esta en /boot/vmlinuz-2.4.37.11-retro)"
echo "k_retro24: en el prompt de LILO escribe linux24 (o pon esa imagen primera en /etc/lilo.conf). Leeme: /usr/doc/packages/k_retro24"

%preun
if [ "$1" = 0 ]; then
    # quitar la entrada linux24 y devolver los modutils de SuSE
    awk '/^[ \t]*image[ \t]*=/ { saltar = ($0 ~ /vmlinuz-2\.4\.37\.11-retro/) } !saltar' /etc/lilo.conf > /etc/lilo.conf.k24 && \
        mv /etc/lilo.conf.k24 /etc/lilo.conf && /sbin/lilo
    for p in insmod rmmod lsmod modprobe depmod ksyms modinfo kallsyms; do
        if [ -L /sbin/$p ]; then rm -f /sbin/$p; fi
        if [ -f /lib/modutils-2.0/$p -o -L /lib/modutils-2.0/$p ]; then mv /lib/modutils-2.0/$p /sbin/$p; fi
    done
    rmdir /lib/modutils-2.0 2>/dev/null
    if [ -L /etc/conf.modules -a -f /etc/modules.conf ]; then rm -f /etc/conf.modules && mv /etc/modules.conf /etc/conf.modules; fi
    rm -f /lib/modules/2.4.37.11-retro/modules.*
fi

%files -f ../modulos.files
/boot/vmlinuz-2.4.37.11-retro
/boot/System.map-2.4.37.11-retro
/boot/config-2.4.37.11-retro
/lib/modutils-2.4
%doc /usr/doc/packages/k_retro24
