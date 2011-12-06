%define desktop_file 1
%define fontdir %{_datadir}/x3270/fonts
%define catalogue /etc/X11/fontpath.d
%if %{desktop_file}
%define desktop_file_utils_version 0.2.93
%endif

Summary: An X Window System based IBM 3278/3279 terminal emulator
Name: x3270
Version: 3.3.6
Release: 10.4%{?dist}
License: MIT
Group: Applications/Internet
URL: http://www.geocities.com/SiliconValley/Peaks/7814
Source0: http://x3270.bgp.nu/download/x3270-%{version}.tgz
Source1: http://x3270.bgp.nu/download/c3270-%{version}.tgz
Source2: x3270.png
Source3: x3270.desktop
Patch0: x3270-3.3.6-redhat.patch
Patch1: c3270-332-ncursesw.patch
Patch2: x3270-3.3-syntax.patch
Patch4: x3270-3.3.6-resize.patch
Patch5: x3270-3.3.6-tinfo.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: ncurses-devel readline-devel glibc-devel openssl-devel libtool
BuildRequires: perl fontconfig
%if %{desktop_file}
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
%endif

%package x11
Summary: IBM 3278/3279 terminal emulator for the X Window System
Group: Applications/Internet
BuildRequires: xorg-x11-font-utils imake xorg-x11-xbitmaps
BuildRequires: libXmu-devel libXaw-devel libXt-devel libICE-devel
BuildRequires: libXext-devel libX11-devel libXpm-devel libSM-devel
BuildRequires: libXt-devel
Requires: %{name} = %{version}
Requires: gtk2 >= 2.6
Requires(post): /usr/bin/mkfontdir
Requires(postun): /usr/bin/mkfontdir

%package text
Summary: IBM 3278/3279 terminal emulator for text mode
Group: Applications/Internet
Requires: %{name} = %{version}

%description
The x3270 package contains files needed for emulating the IBM 3278/3279
terminals, commonly used with mainframe applications.

You will also need to install a frontend for %{name}. Available frontends
are %{name}-x11 (for the X Window System) and %{name}-text (for text mode).

%description x11
The x3270 program opens a window in the X Window System which emulates
the actual look of an IBM 3278/3279 terminal, commonly used with
mainframe applications.  x3270 also allows you to telnet to an IBM
host from the x3270 window.

Install the %{name}-x11 package if you need to access IBM hosts using an IBM
3278/3279 terminal emulator from X11.

%description text
The c3270 program opens a 3270 terminal which emulates the actual look of an
IBM 3278/3279 terminal, commonly used with mainframe applications.
x3270 also allows you to telnet to an IBM host from the x3270 window.

Install the %{name}-text package if you need to access IBM hosts using an IBM
3278/3279 terminal emulator without running X.

%prep
%setup -q -n x3270-3.3 -a 1
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch4 -p1
%patch5 -p1

%build
# Set LIBX3270DIR to something we can share with x3270-text
perl -pi -e "s,LIBX3270DIR =.*,LIBX3270DIR = %{_datadir}/x3270,g" Imakefile.in
# use rpmoptflags for x3270if
perl -pi -e 's/ -o x3270if x3270if.c/ \$(CCOPTIONS) -o x3270if x3270if.c/g' Imakefile.in
# Fix end of line encodings
perl -pi -e "s///" html/Keymap.html html/Build.html
libtoolize --copy --force
%configure --prefix=%{_prefix}/ --with-fontdir=%{fontdir} --x-includes=/usr/include/X11 --x-libraries=/%{_libdir}/X11 --enable-app-defaults
xmkmf
make Makefiles
make includes
make depend

make %{?_smp_mflags} CCOPTIONS="$RPM_OPT_FLAGS"
cd c3270-3.3
autoconf
libtoolize --copy --force
%configure --prefix=%{_prefix}
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
mkdir -p $RPM_BUILD_ROOT%{_prefix}/bin
mkdir -p $RPM_BUILD_ROOT%{_datadir}/x3270
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
mkdir -p ${RPM_BUILD_ROOT}%{fontdir}
mkdir -p ${RPM_BUILD_ROOT}/%{_datadir}/icons/hicolor/48x48/apps
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/X11/app-defaults
mkdir -p ${RPM_BUILD_ROOT}%{catalogue}

# XXX Hack around mkfontdir madness on install.
install -m755 x3270 $RPM_BUILD_ROOT%{_prefix}/bin
install -m755 x3270if $RPM_BUILD_ROOT%{_prefix}/bin
install -m644 *pcf.gz $RPM_BUILD_ROOT%{fontdir}
install -m644 ibm_hosts $RPM_BUILD_ROOT%{_sysconfdir}/
install -m755 pr3287/pr3287 $RPM_BUILD_ROOT%{_prefix}/bin
install -m644 pr3287/pr3287.man $RPM_BUILD_ROOT%{_mandir}/man1/pr3287.1x
cd c3270-3.3
install -m755 c3270 $RPM_BUILD_ROOT%{_prefix}/bin
for i in c3270 x3270if x3270-script ibm_hosts; do
    install -m644 $i.man $RPM_BUILD_ROOT%{_mandir}/man1/$i.1
done
cd ..

install -m644 %{SOURCE2} ${RPM_BUILD_ROOT}%{_datadir}/icons/hicolor/48x48/apps
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/Utilities
install -m644 %{SOURCE3} ${RPM_BUILD_ROOT}%{_sysconfdir}/X11/applnk/Utilities
install -m644 X3270.xad ${RPM_BUILD_ROOT}%{_datadir}/X11/app-defaults/X3270
ln -sf %{fontdir} $RPM_BUILD_ROOT%{catalogue}/x3270

%if %{desktop_file}
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications
desktop-file-install --vendor fedora \
        --dir $RPM_BUILD_ROOT/%{_datadir}/applications \
        --add-category "Application;System;X-Fedora-Extra" \
        $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/Utilities/x3270.desktop

# remove x3270.desktop from the buildroot now that we're done with it
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk
%endif


rm -f Examples/*.rh Examples/*.orig
chmod -x Examples/* html/*

%clean
rm -rf $RPM_BUILD_ROOT

%post x11
cd %{fontdir} && %{_prefix}/bin/mkfontdir
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%postun x11
if [ "$1" = "0" ]; then
  cd %{fontdir} && %{_prefix}/bin/mkfontdir
fi
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%files
%defattr(-,root,root)
%doc README LICENSE Examples html
%{_prefix}/bin/pr3287
%{_prefix}/bin/x3270if
%exclude %{_mandir}/man1/c3270*
%{_mandir}/man1/*
%dir %{_datadir}/x3270
%config(noreplace) %{_sysconfdir}/ibm_hosts

%files x11
%defattr(-,root,root)
%doc LICENSE
%{_prefix}/bin/x3270
%dir %{fontdir}
%{fontdir}/*
%{catalogue}/x3270
%{_datadir}/icons/hicolor/48x48/apps/x3270.png
%{_datadir}/X11/app-defaults/X3270
%if %{desktop_file}
%{_datadir}/applications/*
%else
%config(missingok) %{_sysconfdir}/X12/applnk/Utilities/*
%endif

%files text
%defattr(-,root,root)
%doc LICENSE
%{_prefix}/bin/c3270
%{_mandir}/man1/c3270*

%changelog
* Wed Jun 30 2010 Karsten Hopp <karsten@redhat.com> 3.3.6-10.4
- add buildrequirement fontconfig

* Wed Jun 23 2010 Karsten Hopp <karsten@redhat.com> 3.3.6-10.3
- bump release

* Wed Jun 16 2010 Karsten Hopp <karsten@redhat.com> 3.3.6-10.2.el6
- fix release

* Fri Feb 26 2010 Karsten Hopp <karsten@redhat.com> 3.3.6-10.el6.2
- link with libtinfo

* Wed Jan 27 2010 Karsten Hopp <karsten@redhat.com> 3.3.6-10.1
- drop prereq, fix macro usage in changelog, drop obsolete patch

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 3.3.6-10
- rebuilt with new openssl

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.6-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 18 2009 Tomas Mraz <tmraz@redhat.com> 3.3.6-7
- rebuild with new openssl

* Thu Oct 02 2008 Karsten Hopp <karsten@redhat.com> 3.3.6-6
- update redhat patch for fuzz=0 (#465087)

* Thu Mar 20 2008 Karsten Hopp <karsten@redhat.com> 3.3.6-5
- fix compiler flags for FORTIFY_SOURCE

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.3.6-4
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Karsten Hopp <karsten@redhat.com> 3.3.6-3
- rebuild with new openssl libs

* Tue Aug 21 2007 Karsten Hopp <karsten@redhat.com> 3.3.6-2
- drop chkfontpath dependency (#252274)

* Wed Aug 08 2007 Karsten Hopp <karsten@redhat.com> 3.3.6-1
- version 3.3.6
- fix font resize issue
- enable app-defaults

* Sun Aug 27 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p7-5
- rebuild

* Tue Aug 15 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p7-4
- fix requirements of -X11 subpackage

* Wed Jul 12 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p7-3
- fix fileconflicts in subpackages

* Wed Jul 05 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p7-2
- silence chkconfig
- rpmlint fixes:
 - replace PreReq/BuildPrereq with Requires/BuildRequires
 - move ibm_hosts to %%{_sysconfdir}
 - fix end of line encodings in docs

* Tue Jun 13 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p6-6
- update to 3.3.4p7
- buildrequire libtool

* Fri Feb 17 2006 Karsten Hopp <karsten@redhat.de> 3.3.4p6-5
- rebuild

* Mon Dec 19 2005 Karsten Hopp <karsten@redhat.de> 3.3.4p6-4
- test build without modular-X patch

* Wed Nov 23 2005 Karsten Hopp <karsten@redhat.de> 3.3.4p6-3
- update release again

* Wed Nov 23 2005 Karsten Hopp <karsten@redhat.de> 3.3.4p6-2
- update release

* Thu Nov 17 2005 Karsten Hopp <karsten@redhat.de> 3.3.4p6-1
- update to patchlevel 6
- drop obsolete segfault patch
- build with modular X
- build with current openssl
- gccmakedep is gone, use makedepend wrapper instead

* Wed Oct 19 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-6
- move x3270-x11 files from /usr/X11R6 to /usr (#170938)
  
* Thu Sep 08 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-5
- add missing buildrequires so that x3270 will be built with SSL support
  (#159527)

* Wed Jul 20 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-4
- buildrequires xorg-x11-font-utils (#160737)
- add disttag

* Wed Apr 27 2005 Jeremy Katz <katzj@redhat.com>
- silence gtk-update-icon-cache in %%post

* Wed Apr 20 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-3
- more fixes, enable StartupNotify

* Wed Apr 20 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-2
- spec file cleanups from Chris Ricker <kaboom@oobleck.net>
- remove backup files from rpm patch process

* Mon Apr 18 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-1
- rpmlint fix
- buildroot fix
- use _smp_mflags

* Tue Apr 12 2005 Karsten Hopp <karsten@redhat.de> 3.3.4-1
- Version 3.3.4, fixes mouse selection and timing problems with scripted
  logins in ~/.ibm_hosts

* Mon Mar 28 2005 Christopher Aillon <caillon@redhat.com>
- rebuilt

* Fri Mar 25 2005 Christopher Aillon <caillon@redhat.com> 3.3.3.b2-2
- Update the GTK+ theme icon cache on (un)install

* Tue Mar 08 2005 Karsten Hopp <karsten@redhat.de> 3.3.3.b2-1
- update to b2, which fixes a segfault when login is done with 
  an entry in .ibm_hosts (via emulate_input)

* Wed Mar 02 2005 Karsten Hopp <karsten@redhat.de> 3.3.3.b1-2
- build with gcc-4

* Thu Jan 13 2005 Karsten Hopp <karsten@redhat.de> 3.3.3.b1-1 
- update to fix ibm_hosts file parsing and c3270 color support

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 3.3.2.p1-10
- Rebuilt for new readline.

* Wed Dec 08 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-9
- add icon (#141599, #125577)
- fix variable usage (local variable overwrite) (#116660)

* Wed Dec 08 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-8
- rebuild 

* Thu Oct 21 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-7
- enable builds on ppc(64) again (#136703)

* Wed Jul 07 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-6
- rebuild with new gcc

* Mon Jul 05 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-5 
- update c3270 package to patchlevel2
- fix buildrequires (#124280)
- fix compiler warnings (#106312, #78479)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 17 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-3 
- include license file

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jan 15 2004 Karsten Hopp <karsten@redhat.de> 3.3.2.p1-1
- update to 3.3.2.p1

* Wed Dec 03 2003 Karsten Hopp <karsten@redhat.de> 3.3.2-1
- update to latest stable release, now with SSL and DBCS support

* Tue Aug 12 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-4.2
- check for libncursesw and use it if available

* Wed Jul 09 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-4.1
- rebuilt

* Wed Jul 09 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-4
- fix segfault when ~/.x3270connect isn't writable by the user

* Tue Jun 17 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-3.1
- rebuilt

* Tue Jun 17 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-3
- rebuild 

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 05 2003 Karsten Hopp <karsten@redhat.de> 3.2.20-1
- update to 3.2.20

* Tue Apr  1 2003 Thomas Woerner <twoerner@redhat.com>
- fixed inclusion of time header file (sys/time.h -> time.h)

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Nov 19 2002 Karsten Hopp <karsten@redhat.de> 3.2.19-3
- update to patchlevel 4:
  Re-enable the automatic font switching when the
  x3270 window is resized

* Tue Nov 19 2002 Tim Powers <timp@redhat.com>
- rebuild for all arches
- remove cruft from the buildroot we aren't shipping

* Wed Jul 24 2002 Karsten Hopp <karsten@redhat.de>
- 3.2.19
- use desktop-file-utils

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Mar  4 2002 Bernhard Rosenkraenzer <bero@redhat.com> 3.2.18-2
- Update to 3.2.18 patchlevel 14

* Wed Jan 16 2002 Bernhard Rosenkraenzer <bero@redhat.com> 3.2.18-1
- 3.2.18
- Don't ship x3270-tcl anymore

* Mon Jul 16 2001 Bernhard Rosenkraenzer <bero@redhat.com> 3.2.16-4
- Add build dependencies (#48930)

* Sat Jun 09 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- remove all provides/requires for x3270-frontend

* Sun May 13 2001 Bernhard Rosenkraenzer <bero@redhat.com> 3.2.16-2
- Rebuild with new readline

* Thu May 10 2001 Bernhard Rosenkraenzer <bero@redhat.com> 3.2.16-1
- 3.2.16
- adapt patches
- get rid of the **** pdksh requirement
- split the tcl version into a different package, no need to require tcl for
  normal use
- split the x11 frontend into a separate package.
  We don't necessarily have X on a machine where we want to run
  3270 sessions (e.g. s390...)

* Fri Dec 22 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 3.2.14
- Add c3270 (textmode x3270) in x3270-text package
- Fix build
- Make ibm_hosts a %%config(noreplace)

* Tue Oct 24 2000 Jeff Johnson <jbj@redhat.com>
- remove /usr/local paths in Examples.

* Sun Oct 22 2000 Jeff Johnson <jbj@redhat.com>
- update to 3.2.13.

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Fri Jun  2 2000 Jeff Johnson <jbj@redhat.com>
- rebuild for 7.0

* Mon Feb 07 2000 Preston Brown <pbrown@redhat.com>
- wmconfig -> desktop

* Mon Feb  7 2000 Jeff Johnson <jbj@redhat.com>
- compress man pages.

* Fri Jan 14 2000 Jeff Johnson <jbj@redhat.com>
- update to 3.1.1.9 (see URL for pending 3.2alpha version).

* Fri Sep 24 1999 Preston Brown <pbrown@redhat.com>
- change to directory before doing a mkfontdir

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 7)

* Tue Jan 12 1999 Jeff Johnson <jbj@redhat.com>
- ibm_hosts needed %%config (#788)

* Fri Aug  7 1998 Jeff Johnson <jbj@redhat.com>
- build root

* Fri May 01 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Wed Oct 22 1997 Marc Ewing <marc@redhat.com>
- new version
- added wmconfig entry

* Mon Jul 21 1997 Erik Troan <ewt@redhat.com>
- built against glibc
