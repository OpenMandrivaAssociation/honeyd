Summary:	A Virtual Honeypot Daemon
Name:		honeyd
Version:	1.5c
Release:	%mkrel 12
License:	BSD
Group:		System/Servers
URL:		http://www.honeyd.org/
Source0:	http://www.citi.umich.edu/u/provos/honeyd/%{name}-%{version}.tar.gz
Source2:	%{name}.conf
Source3:	%{name}.init
Source4:	%{name}.sysconfig
Source5:	%{name}-webserver.sysconfig
Source6:	%{name}.logrotate
Patch0:		%{name}.Makefile.patch
Patch1:		honeyd-1.5a-nmap-prints.diff
Patch2:		honeyd-lib64.diff
Patch3:		%{name}-1.5c-pidsock.patch
Patch4:		%{name}-1.0-tmpdir.diff
Patch5:		honeyd-mkinstalldirs.diff
Patch6:		honeyd-pypcap_DESTDIR.diff
Patch7:		honeyd-1.5a-python_x86_64.diff
Patch8:		honeyd-pcre_includes.diff
Patch9:		honeyd-external_python_packages.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	rrdtool
BuildRequires:	libevent-devel >= 1.0
BuildRequires:	libdnet-devel
BuildRequires:	libpcap-devel
BuildRequires:	libpcre-devel
BuildRequires:	flex bison
BuildRequires:	automake
BuildRequires:	python-devel
BuildRequires:	readline-devel
BuildRequires:	ncurses-devel
BuildRequires:	rrdtool
BuildRequires:	zlib-devel
BuildRequires:	python-dpkt
BuildRequires:	python-pypcap
BuildRequires:	python
BuildRequires:	python-devel
# it's either readline or libedit. it seems almost each time libedit is preferred.
BuildConflicts:	edit-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Honeyd is a small daemon that creates virtual hosts on a network.
The hosts can be configured to run arbitrary services, and their
personality can be adapted so that they appear to be running
certain operating systems. Honeyd enables a single host to claim
multiple addresses - I have tested up to 65536 - on a LAN for
network simulation. Honeyd improves cyber security by providing
mechanisms for threat detection and assessment. It also deters
adversaries by hiding real systems in the middle of virtual
systems. 

It is possible to ping the virtual machines, or to traceroute 
them. Any type of service on the virtual machine can be simulated
according to a simple configuration file. Instead of simulating a
service, it is also possible to proxy it to another machine. 

%package	webserver
Summary:	A simple Python based webserver for honeyd
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	python-dnet
Requires:	python-dpkt
Requires:	python-pypcap
Requires:	%{name} = %{version}-%{release}

%description	webserver
This package contains a simple Python based webserver for honeyd.

%package	devel
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{name} = %{version}-%{release}

%description	devel
This package contains development files for %{name}

%prep

%setup -q -n %{name}-%{version}
# (misc) this patch correct the soname of the bundled library
%patch0 -p1 -b .Makefile
# (misc) this patch remove a error message, it seems that the file
# contains two non standard value.
%patch1 -p0 -b .nmap-prints
%patch2 -p0 -b .lib64
%patch3 -p1 -b .pidsock
%patch4 -p1 -b .tmpdir
%patch5 -p0 -b .mkinstalldirs
%patch6 -p0 -b .DESTDIR
%patch7 -p0 
%patch8 -p0 
%patch9 -p0 

cp %{SOURCE2} %{name}.conf
cp %{SOURCE3} %{name}.init
cp %{SOURCE4} %{name}.sysconfig
cp %{SOURCE5} %{name}-webserver.sysconfig
cp %{SOURCE6} %{name}.logrotate

%build
autoreconf -fi
%configure2_5x \
    --enable-shared \
    --enable-static \
    --bindir=%{_sbindir} \
    --with-python
		
# parallell build's broken
make

cat <<EOF >README.Mandriva
This package was build with python support.

The file with /usr/share/honeyd/nmap.prints was
tweaked to remove two bogus values 
( search Mandriva in the comment ).

If you want to simulated large network, you will need
arpd, avaliable from contribs.
Use 'urpmi arpd' to install it.
EOF

%install
rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_datadir}/%{name}/scripts
install -d %{buildroot}%{_localstatedir}/lib/%{name}/tmp
install -d %{buildroot}/var/run/%{name}
install -d %{buildroot}/var/log/%{name}

%makeinstall_std

cp -R scripts/* %{buildroot}%{_datadir}/%{name}/scripts

install -m0755 %{name}.init %{buildroot}%{_initrddir}/%{name}
install -m0644 %{name}.conf %{buildroot}%{_sysconfdir}/
install -m0644 %{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -m0644 %{name}-webserver.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}-webserver
install -m0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

mv %{buildroot}%{_datadir}/%{name}/webserver/htdocs %{buildroot}%{_localstatedir}/lib/%{name}/html

# cleanup
rm -f %{buildroot}%{_datadir}/%{name}/README
rm -f %{buildroot}%{_datadir}/%{name}/config.ethernet
rm -f %{buildroot}%{_datadir}/%{name}/config.sample

# we use the stand alone python-pypcap package instead
rm -rf %{buildroot}%{py_platsitedir}

# create ghostfiles
touch %{buildroot}/var/log/honeyd/honeyd.log
touch %{buildroot}/var/log/honeyd/servicelog.log

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%postun
%_postun_userdel %{name}

%post
%create_ghostfile /var/log/honeyd/honeyd.log %{name} %{name} 0644
%create_ghostfile /var/log/honeyd/servicelog.log %{name} %{name} 0644
%_post_service %{name}

%preun
%_preun_service %{name}

%post webserver
%{_initrddir}/%{name} restart

%preun webserver
%{_initrddir}/%{name} restart

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README* config.sample config.ethernet
%attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/%{name}.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %{_sbindir}/*
%attr(0644,root,root) %{_mandir}/man?/*
#
%dir %{_libdir}/%{name}
%attr(0755,root,root) %{_libdir}/%{name}/lib%{name}.so
#
%dir %{_datadir}/%{name}
%attr(0644,root,root) %{_datadir}/%{name}/nmap.assoc
%attr(0644,root,root) %{_datadir}/%{name}/nmap.prints
%attr(0644,root,root) %{_datadir}/%{name}/xprobe2.conf
%attr(0644,root,root) %{_datadir}/%{name}/pf.os
%attr(0755,root,root) %{_datadir}/%{name}/proxy
%attr(0755,root,root) %{_datadir}/%{name}/smtp
#
%dir %{_datadir}/%{name}/scripts
%attr(0755,root,root) %{_datadir}/%{name}/scripts/*
#
%dir %attr(0755,%{name},%{name}) /var/run/%{name}
%dir %attr(0755,%{name},%{name}) /var/log/%{name}
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/tmp
#
%attr(0644,%{name},%{name}) %ghost %config(noreplace) /var/log/honeyd/honeyd.log
%attr(0644,%{name},%{name}) %ghost %config(noreplace) /var/log/honeyd/servicelog.log

%files webserver
%defattr(-,root,root)
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/%{name}-webserver
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/graphs
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/images
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/styles
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/templates
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/templates/inc
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/graphs/*.gif
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/images/*.gif
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/styles/*.css
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/templates/inc/*.tmpl
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/templates/*.tmpl
%attr(0644,%{name},%{name}) %{_localstatedir}/lib/%{name}/html/*.py
%attr(0644,root,root) %{_datadir}/%{name}/webserver/*.py

%files devel
%defattr(-,root,root)
%dir %{_includedir}/%{name}
%attr(0644,root,root) %{_includedir}/%{name}/*.h
