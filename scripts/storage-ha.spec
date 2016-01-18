%define major_version 0
%define minor_version 7
%define release 1%{?dist}

Name: storage-ha
Summary: High-Availability Storage Server Add-on
Version: %{major_version}.%{minor_version}
Release: %{release}
License: GPLv2+
Group: Applications/System
URL: http://www.redhat.com
Vendor: Red Hat, Inc.
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-root

Source0: %{name}-%{version}.tar.gz

Requires: glusterfs-server
%if %{defined rhel} && %{rhel} < 7
Requires: cman
Requires: pacemaker
%else
Requires: fence-agents-all
%endif
Requires: pcs

%description
High-Availability add-on for storage servers

### NFS (GANESHA)
%package nfs
Summary: STORAGE-HA NFS module
Group: Applications/System
Requires: storage-ha = %{version}-%{release}
Requires: nfs-ganesha

%description nfs
High-Availability NFS add-on for storage servers

### SMB (SAMBA)
%package smb
Summary: STORAGE-HA SMB module
Group: Applications/System
Requires: storage-ha = %{version}-%{release}
Requires: ctdb >= 2.5
Requires: samba
Requires: samba-client

%description smb
High-Availability SMB add-on for storage servers


%prep
%setup -q -n %{name}

%install
%{__rm} -rf %{buildroot}

install -d -m 0755 %{buildroot}%{_sbindir}
install -m 0700 storage-ha %{buildroot}%{_sbindir}/storage-ha

sed -i 's/\%CONFDIR/\%{_sysconfdir}/' "%{buildroot}%{_sbindir}/storage-ha"

install -d -m 0700 %{buildroot}%{_sysconfdir}/sysconfig/storage-ha.d
install -m 0600 storage-ha.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storage-ha.conf
install -m 0600 nfs-ha.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storage-ha.d/nfs-ha.conf
install -m 0600 smb-ha.conf.sample %{buildroot}%{_sysconfdir}/sysconfig/storage-ha.d/smb-ha.conf

install -d -m 0755 %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat
install -m 0755 ganesha %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha
install -m 0755 ganesha_trigger %{buildroot}%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha_trigger

%post
%if %{defined rhel} && %{rhel} < 7
chkconfig corosync off
chkconfig pacemaker on
chkconfig pcsd on
service pcsd start
%else
systemctl start pcsd.service
systemctl enable pcsd.service
%endif


%post smb
%if %{defined rhel} && %{rhel} < 7
chkconfig ctdb off
chkconfig smb off
chkconfig nmb off
chkconfig winbind off
service ctdb stop
service smb stop
service nmb stop
service winbind stop
%else
systemctl stop ctdb smb nmb winbind
systemctl disable ctdb smb nmb winbind
%endif

%post nfs
%if %{defined rhel} && %{rhel} < 7
chkconfig nfs-server off
chkconfig nfs-lock off
service nfs-server stop
service nfs-lock stop
%else
systemctl stop nfs-server nfs-lock
systemctl disable nfs-server nfs-lock
%endif

[ -d /var/lib/nfs.backup ] || mv /var/lib/nfs /var/lib/nfs.backup
[ -d /var/lib/nfs ] && rm -rf /var/lib/nfs
ln -s /gluster/state/`hostname`/nfs /var/lib/nfs

if [[ ! -f /etc/dbus-1/system.d/org.ganesha.nfsd.conf ]]; then
	cp /etc/glusterfs-ganesha/org.ganesha.nfsd.conf /etc/dbus-1/system.d/
%if %{defined rhel} && %{rhel} < 7
	service messagebus restart
%else
	systemctl restart messagebus
%endif
fi

%postun nfs
if [ -d /var/lib/nfs.backup ]; then
	rm -rf /var/lib/nfs
	mv /var/lib/nfs.backup /var/lib/nfs
fi

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storage-ha.conf
%attr(755,root,root) %dir %{_sysconfdir}/sysconfig/storage-ha.d/
%{_sbindir}/storage-ha

%files nfs
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storage-ha.d/nfs-ha.conf
%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha
%{_prefix}/lib/ocf/resource.d/heartbeat/ganesha_trigger

%files smb
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/storage-ha.d/smb-ha.conf


%changelog
* Mon Jan 18 2016 Jose A. Rivera <jarrpa@redhat.com> - 0.7-1
- Force cluster creation
- Allow for definition of which nodes will be storage nodes
- Enable direct-io for GlusterFS backend volumes
- Temporarily comment out NFS functionality

* Thu Nov 19 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.6-2
- Add functionality for EL7

* Thu Apr 23 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.6-1
- Properly update CIB file during cluster creation
- Better tempfile handling
- Improve ganesha statedir creation

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.5-1
- Remove extraneous cleanup commands

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.4-1
- Add missing service
- Add missing requires

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-3
- Fix installation config bug

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-2
- Don't install custom CTDB RA, update it in
  resource-agents package

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.3-1
- Add storage-ha script
- Additional post-installation prep work

* Wed Apr 15 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.2-2
- Add Ganesha symlink

* Mon Apr 13 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.2-1
- Add config files

* Wed Apr 08 2015 Jose A. Rivera <jarrpa@redhat.com> - 0.1-1
- Initial version