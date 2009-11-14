%define major		17
%define libname         %mklibname %{name} %{major}
%define develname	%mklibname %{name} -d
%define rel 1
# (Abel) making guile require guile-devel means user need to download
# more stuff, which is worse
%define _requires_exceptions devel(.*)

Name:           guile
Version:        1.8.7
Release:        %mkrel %rel 
Summary:        GNU implementation of Scheme for application extensibility
License:        LGPLv2+
Group:          Development/Other
URL:            http://www.gnu.org/software/guile/guile.html
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Source0:        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz
Source1:        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz.sig
Patch0:         guile-1.8.3-64bit-fixes.patch
Patch1:         guile-1.6.4-amd64.patch
Patch2:		guile-1.8.5-drop-ldflags-from-pkgconfig.patch
Requires(post): %{libname} = %{version}-%{release}
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:  chrpath
BuildRequires:  libgmp-devel
BuildRequires:  libltdl-devel
BuildRequires:  libncurses-devel
BuildRequires:  libreadline-devel
BuildRequires:	gettext-devel
# for srfi-19.test
BuildRequires:  timezone

%package -n %{libname}
Summary:        Libraries for Guile %{version}
Group:          System/Libraries
Requires:       %{name} = %{version}

%package -n %{develname}
Summary:        Development headers and static library for libguile
Group:          Development/C
Requires:       %{libname} = %{version}
Provides:       libguile-devel = %{version}-%{release}
Provides:       guile-devel = %{version}-%{release}
Obsoletes:      guile-devel
Obsoletes:	%{mklibname guile 17 -d}
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

%description -n %{develname}
This package contains the development headers and the static library
for libguile. C headers, aclocal macros, the `guile1.4-snarf' and
`guile-config' utilities, and static `libguile' library for Guile, the
GNU Ubiquitous Intelligent Language for Extension

%prep
%setup -q
%patch0 -p1 -b .64bit-fixes
%patch1 -p1 -b .amd64
%patch2 -p0 -b .pkgconfig

%build
autoreconf
%{configure2_5x} \
    --disable-error-on-warning \
    --disable-rpath \
    --enable-dynamic-linking \
    --with-threads
%{make} LIBTOOL=%{_bindir}/libtool

%check
%ifarch ia64
# FAIL: r4rs.test: (6 9): (#<procedure leaf-eq? (x y)> (a (b (c))) ((a) b c))
%{__make} check LIBTOOL=%{_bindir}/libtool -k || :
%else
# all tests must pass
%{__make} check LIBTOOL=%{_bindir}/libtool
%endif

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std} LIBTOOL=%{_bindir}/libtool

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/site

%multiarch_includes %{buildroot}%{_includedir}/lib%{name}/scmconfig.h

%{_bindir}/chrpath -d %{buildroot}{%{_bindir}/%{name},%{_libdir}/*.so.*.*.*}

# create ghost file for packaging
touch %{buildroot}%{_datadir}/%{name}/site/slib %{buildroot}%{_datadir}/%{name}/site/slibcat

%clean
%{__rm} -rf %{buildroot}

%post
%_install_info %{name}-tut.info
%_install_info %{name}.info
%_install_info r5rs.info
%_install_info goops.info

%preun
%_remove_install_info %{name}-tut.info
%_remove_install_info %{name}.info
%_remove_install_info r5rs.info
%_remove_install_info goops.info

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%triggerin -- slib
ln -sfT ../../slib %{_datadir}/%{name}/site/slib
rm -f %{_datadir}/%{name}/site/slibcat
SCHEME_LIBRARY_PATH=%{_datadir}/slib/ \
    %{_bindir}/%{name} -l %{_datadir}/slib/%{name}.init -c "\
    (define (implementation-vicinity) \"%{_datadir}/%{name}/site/\")
    (require 'new-catalog)" &> /dev/null
:

%triggerun -- slib
if [ "$1" = 0 -o "$2" = 0 ]; then
    rm -f %{_datadir}/%{name}/site/slib{,cat}
fi


%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog GUILE-VERSION LICENSE README THANKS
%{_bindir}/%{name}
%{_bindir}/%{name}-tools
%{_datadir}/%{name}
%{_mandir}/man1/guile.1.*
%{_infodir}/*
%{_libdir}/lib%{name}-srfi-srfi-13-14-v-3.so
%{_libdir}/lib%{name}-srfi-srfi-4-v-3.so
%{_libdir}/lib%{name}-srfi-srfi-1-v-3.so
%{_libdir}/lib%{name}-srfi-srfi-60-v-2.so
%{_libdir}/lib%{name}readline-v-%{major}.so
#%ghost %{_datadir}/%{name}/site/slib
#%ghost %{_datadir}/%{name}/site/slibcat

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/lib*.so.%{major}*
%{_libdir}/lib%{name}-srfi-srfi-13-14-v-3.so.3*
%{_libdir}/lib%{name}-srfi-srfi-4-v-3.so.3*
%{_libdir}/lib%{name}-srfi-srfi-1-v-3.so.3*
%{_libdir}/lib%{name}-srfi-srfi-60-v-2.so.2*

%files -n %{develname}
%defattr(-,root,root)
%doc ABOUT-NLS HACKING NEWS INSTALL libguile/ChangeLog*
%multiarch %{multiarch_includedir}/lib%{name}/scmconfig.h
%{_bindir}/%{name}-config
%{_bindir}/%{name}-snarf
%{_datadir}/aclocal/*
%{_includedir}/lib%{name}*
%{_includedir}/%{name}*
%{_libdir}/lib*.*a
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}*.pc

