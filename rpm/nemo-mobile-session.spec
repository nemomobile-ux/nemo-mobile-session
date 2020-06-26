Name:       nemo-mobile-session
Summary:    Target for nemo systemd user session
Version:    13
Release:    0
Group:      System/Libraries
License:    Public Domain
URL:        https://github.com/nemomobile/nemo-mobile-session
Source0:    %{name}-%{version}.tar.gz
BuildArch:  noarch

%description
Target for nemo systemd user session

%package common
Summary:    Nemo-mobile-session configs files
Group:      Configs
Requires:   systemd >= 187
Requires:   systemd-user-session-targets
Requires:   systemd-config-mer
Requires:   maliit-plugins
Obsoletes:  uxlaunch
# mer release 0.20130605.1 changed login.defs
Requires: setup >= 2.8.56
Requires(post): /bin/chgrp, /usr/sbin/groupmod

%description common
%{summary}
 
%package wayland
Summary:    Wayland configs for nemo-mobile-session
Group:      Configs
Requires:   nemo-mobile-session-common
Requires:   qt5-qtwayland-wayland_egl

Conflicts:  nemo-mobile-session-render2d

%description wayland
%{summary}

%package render2d
Summary:   Nemo session config for device with software render
Group:     Configs
Requires:  nemo-mobile-session-common
Requires:  qtdeclarative-render2d

Conflicts: nemo-mobile-session-wayland

%description render2d
%{summary}

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d
mkdir -p %{buildroot}/lib/systemd/system/graphical.target.wants/
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/
mkdir -p %{buildroot}/var/lib/environment/nemo
mkdir -p %{buildroot}%{_sysconfdir}/systemd/system/
mkdir -p %{buildroot}%{_libdir}/systemd/user/pre-user-session.target.wants/
mkdir -p %{buildroot}/lib/udev/rules.d/
mkdir -p %{buildroot}/etc/profile.d/

# Root services
install -D -m 0644 services/user@.service.d/nemo.conf \
           %{buildroot}/lib/systemd/system/user@.service.d/nemo.conf
install -m 0644 services/set-boot-state@.service %{buildroot}/lib/systemd/system/
install -m 0644 services/start-user-session.service %{buildroot}/lib/systemd/system/
install -m 0644 services/init-done.service %{buildroot}/lib/systemd/system/

# conf
install -m 0644 conf/50-nemo-mobile-ui.conf %{buildroot}/var/lib/environment/nemo/
install -D -m 0644 conf/nemo-session-tmp.conf %{buildroot}%{_libdir}/tmpfiles.d/nemo-session-tmp.conf
install -m 0644 conf/50-nemo-mobile-wayland.conf %{buildroot}/var/lib/environment/nemo/
install -m 0644 conf/50-nemo-mobile-render2d.conf %{buildroot}/var/lib/environment/nemo/

#udev rules
install -m 0644 conf/01-input.rules %{buildroot}/lib/udev/rules.d/
install -m 0644 conf/01-fbdev.rules %{buildroot}/lib/udev/rules.d/

#dbus rules
install -m 0644 conf/glacier-user.conf %{buildroot}/etc/dbus-1/system.d/

# shell environment
install -m 0644 conf/load-nemo.sh %{buildroot}/etc/profile.d/

# bin
install -D -m 0744 bin/set-boot-state %{buildroot}%{_libdir}/startup/set-boot-state
install -D -m 0755 bin/start-user-session %{buildroot}%{_libdir}/startup/start-user-session
install -D -m 0744 bin/init-done %{buildroot}/%{_libdir}/startup/init-done

ln -sf ../set-boot-state@.service %{buildroot}/lib/systemd/system/graphical.target.wants/set-boot-state@USER.service
ln -sf ../start-user-session.service %{buildroot}/lib/systemd/system/graphical.target.wants/start-user-session.service
ln -sf ../init-done.service %{buildroot}/lib/systemd/system/graphical.target.wants/
# In nemo actdead is not (yet) supported. We define actdead (runlevel4) to poweroff
ln -sf /lib/systemd/system/poweroff.target %{buildroot}%{_sysconfdir}/systemd/system/runlevel4.target

# nemo-mobile-session dependencies

# systemd --user is called with '--unit=%I.target' in nemo.conf,
# so default.target is never used. User target is setup at runtime
# by set-boot-state according to the current boot state
#ln -sf post-user-session.target %{buildroot}%{_libdir}/systemd/user/default.target

%post
if [ $1 -gt 1 ] ; then
  # known changes
  if [ ! "$(grep audio %{_sysconfdir}/group | cut -d: -f3)" -eq 1005 ]; then
    groupmod -g 1005 audio
  fi
  if [ ! "$(grep nobody %{_sysconfdir}/group | cut -d: -f3)" -eq 9999 ]; then
    groupmod -g 9999 nobody
  fi

  [ -f /usr/bin/ssh-agent ] && chgrp nobody %{_bindir}/ssh-agent

  # Add these users for dbus like droid-hal-device does
  /usr/sbin/useradd -r -d / -s /sbin/nologin nfc
  /usr/sbin/useradd -r -d / -s /sbin/nologin radio

  # backup group and passwd
  mkdir -p %{_sharedstatedir}/misc
  [ ! -f %{_sharedstatedir}/misc/passwd.old ] && cp %{_sysconfdir}/passwd %{_sharedstatedir}/misc/passwd.old
  [ ! -f %{_sharedstatedir}/misc/group.old ] && cp %{_sysconfdir}/group %{_sharedstatedir}/misc/group.old

fi

%files common
%defattr(-,root,root,-)
%config /var/lib/environment/nemo/50-nemo-mobile-ui.conf
%{_libdir}/tmpfiles.d/nemo-session-tmp.conf
/lib/systemd/system/graphical.target.wants/set-boot-state@USER.service
/lib/systemd/system/graphical.target.wants/start-user-session.service
/lib/systemd/system/graphical.target.wants/init-done.service
/lib/systemd/system/user@.service.d/*
/lib/systemd/system/set-boot-state@.service
/lib/systemd/system/start-user-session.service
/lib/systemd/system/init-done.service
/lib/udev/rules.d/01-input.rules
/lib/udev/rules.d/01-fbdev.rules
%{_libdir}/startup/start-user-session
%{_libdir}/startup/set-boot-state
%{_libdir}/startup/init-done
%{_sysconfdir}/systemd/system/runlevel4.target
%{_sysconfdir}/dbus-1/system.d/glacier-user.conf

%files wayland
%defattr(-,root,root,-)
%config /var/lib/environment/nemo/50-nemo-mobile-wayland.conf

%files render2d
%defattr(-,root,root,-)
%config /var/lib/environment/nemo/50-nemo-mobile-render2d.conf


