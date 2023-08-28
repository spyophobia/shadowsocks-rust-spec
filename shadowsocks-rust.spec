%global debug_package %{nil}
%global _features dns-over-https,dns-over-tls,local-dns,local-http-rustls,local-redir,local-tun

Name:    shadowsocks-rust
Version: 1.16.0
Release: 1%{?dist}
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
for BIN_NAME in sslocal ssserver ssurl ssmanager ssservice; do
    install -Dpm 755 target/release/${BIN_NAME} %{buildroot}%{_bindir}/${BIN_NAME}
done

# systemd
mkdir -p %{buildroot}%{_unitdir}
install -Dpm 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}-local@.service
install -Dpm 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-server@.service
mkdir -p %{buildroot}%{_userunitdir}
install -Dpm 644 %{SOURCE3} %{buildroot}%{_userunitdir}/%{name}-local@.service
install -Dpm 644 %{SOURCE4} %{buildroot}%{_userunitdir}/%{name}-server@.service
mkdir -p %{buildroot}%{_sysusersdir}
install -Dpm 644 %{SOURCE5} %{buildroot}%{_sysusersdir}/%{name}.conf

# empty config dirs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/{local,server}

# example configs
install -Dpm 644 examples/config.json %{buildroot}%{_sysconfdir}/%{name}/example/config.json5
install -Dpm 644 examples/config_ext.json %{buildroot}%{_sysconfdir}/%{name}/example/config_ext.json5

%files
%license LICENSE
%doc README.md
%{_bindir}/sslocal
%{_bindir}/ssserver
%{_bindir}/ssurl
%{_bindir}/ssmanager
%{_bindir}/ssservice
%{_unitdir}/%{name}-local@.service
%{_unitdir}/%{name}-server@.service
%{_userunitdir}/%{name}-local@.service
%{_userunitdir}/%{name}-server@.service
%{_sysusersdir}/%{name}.conf
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
* Mon Aug 28 2023 spyophobia - 1.16.0-1
- Release 1.16.0

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
