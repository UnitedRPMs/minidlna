%global _lto_cflags %{nil}
%define _legacy_common_support 1

Name:           minidlna
Version:        1.3.0
Release:        8%{?dist}
Summary:        Lightweight DLNA/UPnP-AV server targeted at embedded systems

Group:          System Environment/Daemons
License:        GPLv2 
URL:            http://sourceforge.net/projects/minidlna/
Source0:	https://sourceforge.net/projects/minidlna/files/minidlna/%{version}/minidlna-%{version}.tar.gz
# Systemd unit file
Source1:        %{name}.service
# tmpfiles configuration for the /run directory
Source2:        %{name}-tmpfiles.conf 

Patch:		select_use_after_free.patch

BuildRequires:  ffmpeg-devel >= 5.0
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  avahi-devel
BuildRequires:  libuuid-devel
BuildRequires:  sqlite-devel
BuildRequires:  libvorbis-devel
BuildRequires:  flac-devel
BuildRequires:  libid3tag-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libexif-devel
BuildRequires:  zlib-devel
BuildRequires:  gettext
BuildRequires:  systemd
Requires(pre):  shadow-utils
%{?systemd_requires}


%description
MiniDLNA (aka ReadyDLNA) is server software with the aim of being fully 
compliant with DLNA/UPnP-AV clients.

The minidlna daemon serves media files (music, pictures, and video) to 
clients on your network.  Example clients include applications such as 
Totem and XBMC, and devices such as portable media players, smartphones, 
and televisions.


%prep
%autosetup -n %{name}-%{version} -p1   

%build

[ -x configure ] || ./autogen.sh

# Edit the default config file 
sed -i 's/#log_dir=\/var\/log/#log_dir=\/var\/log\/minidlna/' \
  %{name}.conf

# I am not sure it the macro works...
%ifarch x86_64
sed -i 's|LDFLAGS="$LDFLAGS -L$dir/lib"|LDFLAGS="$LDFLAGS -L$dir/lib64"|g' configure
%endif
sed -i 's|/usr/local|/usr|g' configure


%configure \
  --disable-silent-rules \
  --with-db-path=%{_localstatedir}/cache/%{name} \
  --with-log-path=%{_localstatedir}/log/%{name} \
  --enable-tivo

%make_build 


%install
%make_install

# Install config file
mkdir -p %{buildroot}%{_sysconfdir}
install -m 644 minidlna.conf %{buildroot}%{_sysconfdir}

# Install systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{S:1} %{buildroot}%{_unitdir}

# Install man pages
mkdir -p %{buildroot}%{_mandir}/man5
install -m 644 minidlna.conf.5 %{buildroot}%{_mandir}/man5/
mkdir -p %{buildroot}%{_mandir}/man8
install -m 644 minidlnad.8 %{buildroot}%{_mandir}/man8/

# Install tmpfiles configuration
mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 %{S:2} %{buildroot}%{_tmpfilesdir}/%{name}.conf
mkdir -p %{buildroot}/run/
install -d -m 0755 %{buildroot}/run/%{name}/

# Create cache and log directories
mkdir -p %{buildroot}%{_localstatedir}/cache
install -d -m 0755 %{buildroot}%{_localstatedir}/cache/%{name}/
mkdir -p %{buildroot}%{_localstatedir}/log
install -d -m 0755 %{buildroot}%{_localstatedir}/log/%{name}/


%find_lang %{name}


%pre
getent group minidlna >/dev/null || groupadd -r minidlna
getent passwd minidlna >/dev/null || \
useradd -r -g minidlna -d /dev/null -s /sbin/nologin \
  -c "minidlna service account" minidlna
exit 0


%post
%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service
echo "-- needs manual intervention in /var/cache/minidlna and /run/minidlna!"


%files -f %{name}.lang
%attr(-,minidlna,minidlna) %config(noreplace) %{_sysconfdir}/minidlna.conf
%{_sbindir}/minidlnad
%{_unitdir}/minidlna.service
%{_mandir}/man5/%{name}.conf.5*
%{_mandir}/man8/minidlnad.8*
%dir %attr(-,minidlna,minidlna) /run/%{name}
%{_tmpfilesdir}/%{name}.conf
%dir %attr(-,minidlna,minidlna) %{_localstatedir}/cache/%{name}/
%dir %attr(-,minidlna,minidlna) %{_localstatedir}/log/%{name}/
%doc AUTHORS COPYING LICENCE.miniupnpd NEWS README TODO


%changelog

* Wed Feb 02 2022 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.3.0-8
- Rebuilt for ffmpeg

* Sat Mar 20 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.3.0-7
- Fix thanks to Dominik Hassler https://sourceforge.net/p/minidlna/bugs/333/

* Mon Feb 15 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.3.0-6
- Updated to 1.3.0

* Tue Jun 23 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-6
- Rebuilt for ffmpeg

* Sun May 03 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-5
- Rebuilt   

* Thu Dec 06 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-4
- Rebuilt for ffmpeg  

* Thu Apr 26 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-3  
- Automatic Mass Rebuild

* Wed Oct 18 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-2  
- Automatic Mass Rebuild

* Fri Sep 22 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.2.1-1
- Updated to 1.2.1-1

* Sat May 27 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.2.0-1
- Updated to 1.2.0-1

* Mon Apr 24 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.6-2
- Reverted service changed

* Fri Apr 21 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.6-1
- Updated to 1.1.6-1

* Tue Apr 18 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 1.1.5-6  
- Automatic Mass Rebuild

* Sat Mar 18 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.5-5
- Rebuilt for libbluray

* Thu Jun 30 2016 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.5-3
- Massive rebuild F25

* Sun Jun 26 2016 The UnitedRPMs Project (Key for UnitedRPMs infrastructure) <unitedrpms@protonmail.com> - 1.1.5-2
- Rebuild with new ffmpeg

* Sun Oct 04 2015 Andrea Musuruane <musuruan@gmail.com> - 1.1.5-1
- Updated to upstream 1.1.5

* Mon Oct 20 2014 Sérgio Basto <sergio@serjux.com> - 1.1.4-3
- Rebuilt for FFmpeg 2.4.3

* Fri Sep 26 2014 Nicolas Chauvet <kwizart@gmail.com> - 1.1.4-2
- Rebuilt for FFmpeg 2.4.x

* Sat Aug 30 2014 Andrea Musuruane <musuruan@gmail.com> - 1.1.4-1
- Updated to upstream 1.1.4

* Thu Aug 07 2014 Sérgio Basto <sergio@serjux.com> - 1.1.3-2
- Rebuilt for ffmpeg-2.3

* Sat Jun 07 2014 Andrea Musuruane <musuruan@gmail.com> - 1.1.3-1
- Updated to upstream 1.1.3

* Sat Mar 29 2014 Andrea Musuruane <musuruan@gmail.com> - 1.1.2-2
- Rebuilt for new ffmpeg

* Sat Mar 08 2014 Andrea Musuruane <musuruan@gmail.com> - 1.1.2-1
- Updated to upstream 1.1.2

* Sun Jan 12 2014 Nicolas Chauvet <kwizart@gmail.com> - 1.1.1-1
- Update to 1.1.1

* Mon Sep 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 1.1.0-2
- Rebuilt

* Sun Sep 15 2013 Andrea Musuruane <musuruan@gmail.com> - 1.1.0-1
- Updated to upstream 1.1.0
- Better systemd integration

* Thu Aug 15 2013 Nicolas Chauvet <kwizart@gmail.com> - 1.0.26-3
- Rebuilt for FFmpeg 2.0.x

* Sun May 26 2013 Nicolas Chauvet <kwizart@gmail.com> - 1.0.26-2
- Rebuilt for x264/FFmpeg

* Wed May 08 2013 Andrea Musuruane <musuruan@gmail.com> - 1.0.26-1
- Updated to upstream 1.0.26

* Wed Jan 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 1.0.25-4
- Rebuilt for ffmpeg

* Sat Nov 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.0.25-3
- Rebuilt for FFmpeg 1.0

* Sat Nov 03 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.25-2
- Fixed FTBFS caused by ffmpeg 1.0
- Updated minidlna.service I forgot to commit (BZ #2294)

* Sat Jul 14 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.25-1
- Updated to upstream 1.0.25

* Tue Jun 26 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.0.24-3
- Rebuilt for FFmpeg

* Wed Apr 25 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.24-2
- Run the daemon with the minidlna user (BZ #2294)
- Updated Debian man pages

* Sun Feb 19 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.24-1
- Updated to upstream 1.0.24

* Sat Jan 28 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.23-1
- Updated to upstream 1.0.23

* Sun Jan 22 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.22-2
- Fixed systemd unit file

* Sun Jan 15 2012 Andrea Musuruane <musuruan@gmail.com> 1.0.22-1
- Updated to upstream 1.0.22
- Removed default Fedora RPM features (defattr, BuildRoot, clean section)
- Better consistent macro usage

* Sat Jul 23 2011 Andrea Musuruane <musuruan@gmail.com> 1.0.21-1
- Updated to upstream 1.0.21

* Sat Jun 18 2011 Andrea Musuruane <musuruan@gmail.com> 1.0.20-1
- First release
- Used Debian man pages
