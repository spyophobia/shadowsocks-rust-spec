%global debug_package %{nil}
%global _unitdir %{_prefix}/lib/systemd/system
%global _features dns-over-https,dns-over-tls,local-dns,local-http-rustls,local-redir,local-tun

Name:    shadowsocks-rust
Version: 1.14.3
Release: 4%{?dist}
Summary: A Rust port of shadowsocks
License: MIT
URL: https://github.com/shadowsocks/shadowsocks-rust
Source0: %{url}/archive/v%{version}.tar.gz
Source1: %{name}-local@.service
Source2: %{name}-server@.service
BuildRequires: gcc

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
cargo test --release --features %{_features}

%install
# bin
for BIN_NAME in sslocal ssserver ssurl ssmanager ssservice; do
    install -Dpm 755 target/release/${BIN_NAME} %{buildroot}%{_bindir}/${BIN_NAME}
done

# units
mkdir -p %{buildroot}%{_unitdir}
install -Dpm 644 -t %{buildroot}%{_unitdir} %{SOURCE1} %{SOURCE2}

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
%{_sysconfdir}/%{name}/*

%changelog
* Mon Aug 01 2022 spyophobia - 1.43.3-4
- Add autorestart to systemd unit files

* Sun Jul 31 2022 spyophobia - 1.43.3-3
- Use modified unit files to facilitate better organisation of config files

* Sat Jul 16 2022 spyophobia - 1.43.3-2
- Enable dns-over-https & dns-over-tls features

* Sat Jul 16 2022 spyophobia - 1.43.3-1
- Release 1.43.3
