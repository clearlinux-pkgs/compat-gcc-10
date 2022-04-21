%define keepstatic 1
%define gcc_target x86_64-generic-linux
%define libstdcxx_maj 6
%define libstdcxx_full 6.0.26
%define isl_version 0.16.1
%define gccver 10
%define gccpath gcc-10.3.0
# Highest optimisation ABI we target
%define mtune haswell
# Lowest compatible ABI (must be lowest of current targets & OBS builders)
# avoton (silvermont target) && ivybridge (OBS builders) = westmere
%define march westmere

Name     : compat-gcc-10
Version  : 10.3.0
Release  : 118
URL      : https://gcc.gnu.org
Source0  : https://gcc.gnu.org/pub/gcc/releases/gcc-10.3.0/gcc-10.3.0.tar.xz
Source1  : https://gcc.gnu.org/pub/gcc/infrastructure/isl-0.16.1.tar.bz2
Source2  : DATESTAMP
Source3  : REVISION
Summary  : GNU cc and gcc C compilers
Group    : Development/Tools
License  : BSD-3-Clause BSL-1.0 GFDL-1.2 GFDL-1.3 GPL-2.0 GPL-3.0 LGPL-2.1 LGPL-3.0 MIT
BuildRequires : autogen
BuildRequires : bison
BuildRequires : dejagnu
BuildRequires : docbook-utils
BuildRequires : docbook-xml
BuildRequires : doxygen
BuildRequires : expect
BuildRequires : flex
BuildRequires : gdb-dev
BuildRequires : gmp-dev
BuildRequires : graphviz
BuildRequires : guile
BuildRequires : libstdc++
BuildRequires : libunwind-dev
BuildRequires : libxml2-dev
BuildRequires : libxslt
BuildRequires : mpc-dev
BuildRequires : mpfr-dev
BuildRequires : pkgconfig(zlib)
BuildRequires : procps-ng
BuildRequires : sed
BuildRequires : tcl
BuildRequires : texinfo
BuildRequires : util-linux
BuildRequires : valgrind-dev
Patch1   : gcc-stable-branch.patch
Patch2   : 0001-Fix-stack-protection-issues.patch
Patch3   : openmp-vectorize-v2.patch
Patch4   : fortran-vector-v2.patch
Patch5   : optimize.patch
Patch6   : ipa-cp.patch
Patch7   : optimize-at-least-some.patch
Patch8   : gomp-relax.patch
Patch9   : arch-native-override.patch
Patch10  : 0001-Ignore-Werror-if-GCC_IGNORE_WERROR-environment-varia.patch
Patch11  : 0001-Always-use-z-now-when-linking-with-pie.patch
Patch12  : tune-inline.patch
Patch13  : memcpy.patch

# zero registers on ret to make ROP harder
Patch14  : 0001-x86-Add-mzero-caller.patch

# cves: 1xx

%description
GNU cc and gcc C compilers.


%package dev
Summary: GNU cc and gcc C compilers
Group: devel
License: GPL-3.0-with-GCC-exception and GPL-3.0
Requires: compat-gcc-10 = %{version}-%{release}

%description dev
GNU cc and gcc C compilers dev files


%prep
%setup -q -n %{gccpath}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

%build

# Live in the gcc source tree
tar xf %{SOURCE1} && ln -sf isl-%{isl_version} isl

# Update the DATESTAMP and add a revision
tee $(find -name DATESTAMP) > /dev/null < %{SOURCE2}
cp %{SOURCE3} gcc/

rm -rf ../gcc-build
mkdir ../gcc-build

pushd ../gcc-build

unset CFLAGS
unset CXXFLAGS

export CFLAGS="-march=%{march} -g1 -O3 -fstack-protector -Wl,-z,now,-z,relro,-z,max-page-size=0x1000 -mtune=%{mtune}"
export CXXFLAGS="-march=%{march} -g1 -O3 -Wl,-z,max-page-size=0x1000 -mtune=%{mtune}"
export CFLAGS_FOR_TARGET="$CFLAGS"
export CXXFLAGS_FOR_TARGET="$CXXFLAGS"
export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64

../%{gccpath}/configure \
    --program-suffix="-10" \
    --prefix=/usr \
    --with-pkgversion='Clear Linux OS for Intel Architecture'\
    --libdir=/usr/lib64 \
    --enable-libstdcxx-pch \
    --libexecdir=/usr/lib64 \
    --with-system-zlib \
    --enable-shared \
    --enable-gnu-indirect-function \
    --disable-vtable-verify \
    --enable-threads=posix \
    --enable-__cxa_atexit \
    --enable-plugin \
    --enable-ld=default \
    --enable-clocale=gnu \
    --disable-multiarch \
    --disable-multilib \
    --enable-lto \
    --disable-werror \
    --enable-linker-build-id \
    --build=%{gcc_target} \
    --target=%{gcc_target} \
    --enable-languages="c,c++" \
    --enable-bootstrap \
    --with-ppl=yes \
    --with-isl \
    --includedir=/usr/include \
    --exec-prefix=/usr \
    --with-glibc-version=2.19 \
    --disable-libunwind-exceptions \
    --with-gnu-ld \
    --with-tune=%{mtune} \
    --with-arch=%{march} \
    --enable-cet \
    --disable-libmpx \
    --with-gcc-major-version-only \
    --enable-default-pie

make -O %{?_smp_mflags} profiledbootstrap

popd # ../gcc-build


%install
export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64

pushd ../gcc-build
%make_install
popd # ../gcc-build

find %{buildroot}/usr/ -name libiberty.a | xargs rm -vf
find %{buildroot}/usr/ -name libiberty.h | xargs rm -vf

chmod a+x %{buildroot}/usr/bin
chmod a+x %{buildroot}/usr/lib64
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.so*' -print0 | xargs -r0 chmod 755
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.o' -print0 | xargs -r0 chmod 644


%files
/usr/bin/%{gcc_target}-c++-%{gccver}
/usr/bin/%{gcc_target}-g++-%{gccver}
/usr/bin/%{gcc_target}-gcc-%{gccver}
/usr/bin/%{gcc_target}-gcc-ar-%{gccver}
/usr/bin/%{gcc_target}-gcc-nm-%{gccver}
/usr/bin/%{gcc_target}-gcc-ranlib-%{gccver}
/usr/bin/c++-%{gccver}
/usr/bin/cpp-%{gccver}
/usr/bin/g++-%{gccver}
/usr/bin/gcc-%{gccver}
/usr/bin/gcc-ar-%{gccver}
/usr/bin/gcc-nm-%{gccver}
/usr/bin/gcc-ranlib-%{gccver}
/usr/bin/gcov-%{gccver}
/usr/bin/gcov-dump-%{gccver}
/usr/bin/gcov-tool-%{gccver}
/usr/bin/lto-dump-%{gccver}
/usr/lib64/gcc/%{gcc_target}/%{gccver}/cc1
/usr/lib64/gcc/%{gcc_target}/%{gccver}/cc1plus
/usr/lib64/gcc/%{gcc_target}/%{gccver}/collect2
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include-fixed/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/install-tools/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/liblto_plugin.so
/usr/lib64/gcc/%{gcc_target}/%{gccver}/liblto_plugin.so.0
/usr/lib64/gcc/%{gcc_target}/%{gccver}/liblto_plugin.so.0.0.0
/usr/lib64/gcc/%{gcc_target}/%{gccver}/lto-wrapper
/usr/lib64/gcc/%{gcc_target}/%{gccver}/lto1
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/*.so
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/*.so.*
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/gtype.state
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/include/
/usr/share/gcc-%{gccver}
%exclude /usr/bin/x86_64-generic-linux-gcc-tmp
%exclude /usr/lib64/*.o
%exclude /usr/lib64/libasan.so.*
%exclude /usr/lib64/libatomic.so.*
%exclude /usr/lib64/libcc1.so.*
%exclude /usr/lib64/libgcc_s.so.*
%exclude /usr/lib64/libgomp.so.*
%exclude /usr/lib64/libitm.so.*
%exclude /usr/lib64/liblsan.so.*
%exclude /usr/lib64/libquadmath.so.*
%exclude /usr/lib64/libssp.so.*
%exclude /usr/lib64/libstdc++.so.*
%exclude /usr/lib64/libtsan.so.*
%exclude /usr/lib64/libubsan.so.*
%exclude /usr/share/info
%exclude /usr/share/locale
%exclude /usr/share/man/man1
%exclude /usr/share/man/man7

%files dev
/usr/include/c++/*
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include/ssp
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/gengtype
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbegin.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbeginS.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbeginT.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtend.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtendS.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtfastmath.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec32.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec64.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec80.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcc.a
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcc_eh.a
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcov.a
%exclude /usr/lib64/*.a
%exclude /usr/lib64/*.spec
%exclude /usr/lib64/libasan.so
%exclude /usr/lib64/libatomic.so
%exclude /usr/lib64/libcc1.so
%exclude /usr/lib64/libgcc_s.so
%exclude /usr/lib64/libgomp.so
%exclude /usr/lib64/libitm.so
%exclude /usr/lib64/liblsan.so
%exclude /usr/lib64/libquadmath.so
%exclude /usr/lib64/libssp.so
%exclude /usr/lib64/libstdc++.so
%exclude /usr/lib64/libtsan.so
%exclude /usr/lib64/libubsan.so
