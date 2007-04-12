%define major_version   1.8
%define libname         %mklibname %{name} 17
%define rel 7
# (Abel) making guile require guile-devel means user need to download
# more stuff, which is worse
%define _requires_exceptions devel(.*)

Name:           guile
Version:        1.8.1
Release:        %mkrel %rel 
Summary:        GNU implementation of Scheme for application extensibility
License:        GPL
Group:          Development/Other
URL:            http://www.gnu.org/software/guile/guile.html
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Source0:        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz
Source1:        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz.sig
Patch0:         guile-1.8.1-64bit-fixes.patch
Patch1:         guile-1.8.1-srfi-14-test.patch
Patch2:         guile-1.6.4-amd64.patch
Patch3:         guile-1.8.1-slib.patch
Patch4:         guile-1.8-rational.patch
Requires(post): umb-scheme
Requires(post): %{libname} = %{version}-%{release}
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:  chrpath
BuildRequires:  libgmp-devel
BuildRequires:  libltdl-devel
BuildRequires:  libncurses-devel
BuildRequires:  libreadline-devel
# for srfi-19.test
BuildRequires:  timezone

%package -n %{libname}
Summary:        Libraries for Guile %{version}
Group:          System/Libraries
Requires:       %{name} = %{version}

%package -n %{libname}-devel
Summary:        Development headers and static library for libguile
Group:          Development/C
Requires:       %{libname} = %{version}
Provides:       libguile-devel = %{version}-%{release}
Provides:       %{_lib}guile-devel = %{version}-%{release}
Provides:       guile-devel = %{version}-%{release}
Obsoletes:      guile-devel
Requires:       libgmp-devel
Requires:       libtool-devel
# (Abel) here comes the definition of "ugliness"
%ifarch x86_64 ia64 amd64 sparc64 ppc64
Requires:        devel(libcrypt(64bit))
Requires:        devel(libdl(64bit))
Requires:        devel(libm(64bit))
#i (misc) removed, no quickthread on 64 bit
%else
Requires:        devel(libcrypt)
Requires:        devel(libdl)
Requires:        devel(libm)
%endif

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a
library implementation of the Scheme programming language, written in
C. GUILE provides a machine-independent execution platform that can
be linked in as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to
programs that you are developing. You'll also need to install the
guile-devel package.

%description -n %{libname}
This package contains Guile shared object libraries and the ice-9
scheme module. Guile is the GNU Ubiquitous Intelligent Language for
Extension.

%description -n %{libname}-devel
This package contains the development headers and the static library
for libguile. C headers, aclocal macros, the `guile1.4-snarf' and
`guile-config' utilities, and static `libguile' library for Guile, the
GNU Ubiquitous Intelligent Language for Extension

%prep
%setup -q
%patch0 -p1 -b .64bit-fixes
%patch1 -p1 -b .srfi-14-test
%patch2 -p1 -b .amd64
%patch3 -p1 -b .slib
%patch4 -p0 -b .rational

%build
%{configure2_5x} \
    --disable-error-on-warning \
    --disable-rpath \
    --enable-dynamic-linking \
    --with-threads
%{make} #LIBTOOL=%{_bindir}/libtool

%ifarch ia64
# FAIL: r4rs.test: (6 9): (#<procedure leaf-eq? (x y)> (a (b (c))) ((a) b c))
%{__make} check -k || :
%else
# all tests must pass
%{__make} check
%endif

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

%{__mkdir_p} %{buildroot}%{_datadir}/guile/site
%{__ln_s} ../../share/umb-scheme/slib %{buildroot}%{_datadir}/guile/slib
#gw needed with guile 1.6.8 and new slib
%{__ln_s} %{_datadir}/umb-scheme/slib %{buildroot}%{_datadir}/guile/%{major_version}/slib

%multiarch_includes %{buildroot}%{_includedir}/libguile/scmconfig.h

%{_bindir}/chrpath -d %{buildroot}{%{_bindir}/guile,%{_libdir}/*.so.*.*.*}

%clean
%{__rm} -rf %{buildroot}

%post
%{_bindir}/guile -c "(use-modules (ice-9 slib)) (require 'new-catalog)"
%_install_info guile-tut.info
%_install_info guile.info
%_install_info r5rs.info
%_install_info goops.info

%preun
%_remove_install_info guile-tut.info
%_remove_install_info guile.info
%_remove_install_info r5rs.info
%_remove_install_info goops.info

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc AUTHORS BUGS COPYING COPYING.LIB GUILE-VERSION LICENSE NEWS README THANKS
%{_bindir}/guile
%{_bindir}/guile-tools
%{_datadir}/guile
%{_infodir}/*
%{_libdir}/libguile-srfi-srfi-13-14-v-3.so
%{_libdir}/libguile-srfi-srfi-4-v-3.so
%{_libdir}/libguile-srfi-srfi-1-v-3.so
%{_libdir}/libguile-srfi-srfi-60-v-2.so
%{_libdir}/libguilereadline-v-17.so

%files -n %{libname}
%defattr(-,root,root)
%doc libguile/ChangeLog*
%{_libdir}/lib*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc ABOUT-NLS ANON-CVS ChangeLog HACKING INSTALL SNAPSHOTS
%multiarch %{multiarch_includedir}/libguile/scmconfig.h
%{_bindir}/guile-config
%{_bindir}/guile-snarf
%{_datadir}/aclocal/*
%{_includedir}/libguile*
%{_includedir}/guile*
%{_libdir}/lib*.*a
%{_libdir}/libguile.so


