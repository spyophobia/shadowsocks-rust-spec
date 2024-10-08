%global debug_package %{nil}
%global _features dns-over-https,dns-over-tls,local-dns,local-http-rustls,local-redir,local-tun

Name:    shadowsocks-rust
Version: 1.21.0
Release: 3%{?dist}
Summary: A Rust port of shadowsocks
License: MIT
URL: https://github.com/shadowsocks/shadowsocks-rust
Source0: %{url}/archive/v%{version}.tar.gz
Source1: shadowsocks-rust-local@.service.system
Source2: shadowsocks-rust-server@.service.system
Source3: shadowsocks-rust-local@.service.user
Source4: shadowsocks-rust-server@.service.user
Source5: shadowsocks-rust.conf.sysusers
BuildRequires: gcc systemd-rpm-macros

%description
This is a Rust port of shadowsocks: https://shadowsocks.org/

shadowsocks is a fast tunnel proxy that helps you bypass firewalls.

%prep
%autosetup

# use latest stable rust version from rustup
curl -Lf https://sh.rustup.rs | sh -s -- -y --profile minimal

%build
source ~/.cargo/env
RUSTFLAGS="-C strip=symbols" cargo build --release --features %{_features}

%check
source ~/.cargo/env
cargo test --features %{_features}

%install
# bin
install -Dpm 755 -t %{buildroot}%{_bindir}/ \
    target/release/{sslocal,ssserver,ssurl,ssmanager,ssservice}

# systemd
install -Dpm 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}-local@.service
install -Dpm 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-server@.service
install -Dpm 644 %{SOURCE3} %{buildroot}%{_userunitdir}/%{name}-local@.service
install -Dpm 644 %{SOURCE4} %{buildroot}%{_userunitdir}/%{name}-server@.service
install -Dpm 644 %{SOURCE5} %{buildroot}%{_sysusersdir}/%{name}.conf

# empty config dirs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/{local,server}/

# example configs
install -Dpm 644 -t %{buildroot}%{_sysconfdir}/%{name}/example/ \
    examples/{config.json,config_ext.json}

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_unitdir}/*
%{_userunitdir}/*
%{_sysusersdir}/*
%config %{_sysconfdir}/%{name}/*

%post
# 1: install 2: update
if [[ "$1" -gt 1 ]]; then
    systemctl daemon-reload
    ACTIVE_SERVICES=$(systemctl list-units --full --quiet --no-legend --plain --state=active \
        %{name}-{local,server}@\*.service | cut -d " " -f 1)
    for SERVICE in ${ACTIVE_SERVICES}; do
        echo "Restarting ${SERVICE} ..."
        systemctl restart ${SERVICE}
    done
fi

systemd-sysusers

%preun
# 1: update 0: uninstall
if [[ "$1" -lt 1 ]]; then
    SERVICES=$(systemctl list-units --full --quiet --no-legend --plain \
        %{name}-{local,server}@\*.service | cut -d " " -f 1)
    for SERVICE in ${SERVICES}; do
        echo "Stopping and disabling ${SERVICE} ..."
        systemctl disable --now ${SERVICE}
    done
fi

%changelog
* Wed Oct 09 2024 spyophobia - 1.21.0-3
- Fix incorrect binary file mode

* Mon Sep 23 2024 spyophobia - 1.21.0-2
- Simplify install section
    - EL7 is now EOL, so we can finally `install -t` without `mkdir` first

* Mon Sep 23 2024 spyophobia - 1.21.0-1
- Release 1.21.0

* Thu Aug 29 2024 spyophobia - 1.20.4-1
- Release 1.20.4

* Thu Aug 01 2024 spyophobia - 1.20.3-1
- Release 1.20.3

* Thu Jul 25 2024 spyophobia - 1.20.2-2
- Fix capability issues in user services

* Sat Jul 13 2024 spyophobia - 1.20.2-1
- Release 1.20.2

* Fri Jun 21 2024 spyophobia - 1.20.1-1
- Release 1.20.1

* Tue Jun 18 2024 spyophobia - 1.20.0-1
- Release 1.20.0

* Sun Jun 02 2024 spyophobia - 1.19.2-1
- Release 1.19.2

* Sun May 26 2024 spyophobia - 1.19.0-1
- Release 1.19.0

* Sun May 12 2024 spyophobia - 1.18.4-1
- Release 1.18.4

* Tue Apr 23 2024 spyophobia - 1.18.3-1
- Release 1.18.3

* Sun Mar 17 2024 spyophobia - 1.18.2-1
- Release 1.18.2

* Tue Feb 20 2024 spyophobia - 1.18.1-1
- Release 1.18.1

* Sat Feb 10 2024 spyophobia - 1.18.0-1
- Release 1.18.0

* Fri Feb 02 2024 spyophobia - 1.17.2-1
- Release 1.17.2

* Fri Dec 08 2023 spyophobia - 1.17.1-2
- Unit hardening

* Mon Nov 27 2023 spyophobia - 1.17.1-1
- Release 1.17.1

* Sun Oct 15 2023 spyophobia - 1.17.0-1
- Release 1.17.0

* Sun Sep 24 2023 spyophobia - 1.16.2-1
- Release 1.16.2

* Fri Sep 01 2023 spyophobia - 1.16.1-1
- Release 1.16.1
- Reenable fixed test

* Mon Aug 28 2023 spyophobia - 1.16.0-1
- Release 1.16.0
- Temporarily skipping failing test `dns_relay`

* Sat Jul 08 2023 spyophobia - 1.15.4-1
- Release 1.15.4

* Tue May 09 2023 spyophobia - 1.15.3-3
- Use sysusers instead of systemd's DynamicUser

* Tue May 09 2023 spyophobia - 1.15.3-2
- Define explicit user and group for system units

* Mon Mar 13 2023 spyophobia - 1.15.3-1
- Release 1.15.3
- Use `ssservice` in favor of deprecated `sslocal` & `ssserver`

* Wed Jan 04 2023 spyophobia - 1.15.2-1
- Release 1.15.2
- Remove unfitting capability declarations from unit files

* Sun Dec 18 2022 spyophobia - 1.15.1-1
- Release 1.15.1
- Fixed version errors in older changelog

* Wed Aug 31 2022 spyophobia - 1.14.3-9
- Improve user instructions in systemd units

* Thu Aug 25 2022 spyophobia - 1.14.3-8
- Set DynamicUser=yes in systemd units
- Add user units

* Wed Aug 17 2022 spyophobia - 1.14.3-7
- Fix scriptlets

* Wed Aug 17 2022 spyophobia - 1.14.3-6
- Added scriptlets for systemd
- Mark config files properly
- Fix changelog version fuckups

* Tue Aug 16 2022 spyophobia - 1.14.3-5
- Set Restart=always in systemd unit files

* Mon Aug 01 2022 spyophobia - 1.14.3-4
- Add autorestart to systemd unit files

* Sun Jul 31 2022 spyophobia - 1.14.3-3
- Use modified unit files to facilitate better organisation of config files

* Sat Jul 16 2022 spyophobia - 1.14.3-2
- Enable dns-over-https & dns-over-tls features

* Sat Jul 16 2022 spyophobia - 1.14.3-1
- Release 1.14.3
