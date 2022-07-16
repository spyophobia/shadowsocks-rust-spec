%global debug_package %{nil}
%global _unitdir %{_prefix}/lib/systemd/system

Name:    shadowsocks-rust
Version: 1.14.3
Release: 1%{?dist}
Summary: A Rust port of shadowsocks
License: MIT
URL: https://github.com/shadowsocks/shadowsocks-rust
Source0: %{url}/archive/v%{version}.tar.gz
BuildRequires: gcc

%description
This is a Rust port of shadowsocks: https://shadowsocks.org/

shadowsocks is a fast tunnel proxy that helps you bypass firewalls.

%prep
%autosetup

%build
# use latest stable rust version from rustup
curl -Lfo rustup https://sh.rustup.rs
chmod +x rustup
./rustup -y
source ~/.cargo/env

RUSTFLAGS="-C strip=symbols" cargo build --release --features local-dns,local-http-rustls,local-redir,local-tun

%check
source ~/.cargo/env
cargo test

%install
# bin
for BIN_NAME in sslocal ssserver ssurl ssmanager ssservice; do
    install -Dpm 755 target/release/${BIN_NAME} %{buildroot}%{_bindir}/${BIN_NAME}
done

# units
install -Dpm 644 debian/%{name}-local@.service %{buildroot}%{_unitdir}/%{name}-local@.service
install -Dpm 644 debian/%{name}-server@.service %{buildroot}%{_unitdir}/%{name}-server@.service

# configs
install -Dpm 644 examples/config.json %{buildroot}%{_sysconfdir}/%{name}/config.json.example
install -Dpm 644 examples/config_ext.json %{buildroot}%{_sysconfdir}/%{name}/config_ext.json.example

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
* Sat Jul 16 2022 spyophobia - 1.43.3-1
- Release 1.43.3
