Name:       lbs-server
Summary:    lbs server for Tizen
Version:    0.6.5
Release:    1
Group:		Framework/Location
License:	Apache-2.0
Source0:    %{name}-%{version}.tar.gz
Source1:    lbs-server.service
BuildRequires:  cmake
BuildRequires:  model-build-features
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(network)
BuildRequires:  pkgconfig(tapi)
BuildRequires:  pkgconfig(vconf)
BuildRequires:  pkgconfig(dlog)
BuildRequires:  pkgconfig(location)
BuildRequires:  pkgconfig(lbs-dbus)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(capi-network-wifi)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(vconf-internal-keys)
BuildRequires:  pkgconfig(gthread-2.0)
BuildRequires:  pkgconfig(gmodule-2.0)
Requires:  sys-assert

%description
lbs server for Tizen


%package -n location-lbs-server
Summary:    lbs server for Tizen
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description -n location-lbs-server
lbs server for Tizen


%package -n lbs-server-plugin-devel
Summary:    lbs server for Tizen (development files)
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description -n lbs-server-plugin-devel
lbs server for Tizen (development files)


%prep
%setup -q

%ifarch %{arm}
%define ARCH armel
%else
%define ARCH x86
%endif

%build
%define _prefix /usr

export CFLAGS="$CFLAGS -DTIZEN_DEBUG_ENABLE"
export CXXFLAGS="$CXXFLAGS -DTIZEN_DEBUG_ENABLE"
export FFLAGS="$FFLAGS -DTIZEN_DEBUG_ENABLE"

MAJORVER=`echo %{version} | awk 'BEGIN {FS="."}{print $1}'`
cmake . -DCMAKE_INSTALL_PREFIX=%{_prefix} -DFULLVER=%{version} -DMAJORVER=${MAJORVER} \
%if 0%{?model_build_feature_location_position_wps}
    -DENABLE_WPS=YES \
%endif

make %{?jobs:-j%jobs}

%install
rm -rf %{buildroot}
%make_install

mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/lbs-server.service
ln -s ../lbs-server.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/lbs-server.service

chmod 755 %{buildroot}/etc/rc.d/init.d/lbs-server
mkdir -p %{buildroot}/etc/rc.d/rc5.d
ln -sf ../init.d/lbs-server %{buildroot}/etc/rc.d/rc5.d/S90lbs-server

%define GPS_DUMP_DIR /opt/etc/dump.d/module.d
%define libexecdir /usr/libexec

mkdir -p %{buildroot}/%{GPS_DUMP_DIR}
cp -a lbs-server/script/dump_gps.sh %{buildroot}/%{GPS_DUMP_DIR}/dump_gps.sh

%clean
rm -rf %{buildroot}


%post
#GPS Indicator value
vconftool set -t int memory/location/position/state "0" -i -s location_fw::vconf -u 200 -g 5000
vconftool set -t int memory/location/gps/state "0" -i -s location_fw::vconf -u 200 -g 5000
vconftool set -t int memory/location/wps/state "0" -i -s location_fw::vconf -u 200 -g 5000

#NMEA_SETTING
vconftool set -t int db/location/nmea/LoggingEnabled "0" -f -s location_fw::vconf -u 200 -g 5000

#REPLAY_SETTING
vconftool set -t string db/location/replay/FileName "nmea_replay.log" -f -s location_fw::vconf -u 200 -g 5000
%ifarch %arm
	vconftool set -t int db/location/replay/ReplayEnabled "0" -f -s location_fw::vconf -u 200 -g 5000
	vconftool set -t int db/location/replay/ReplayMode "1" -f -s location_fw::vconf -u 200 -g 5000
%else
	vconftool set -t int db/location/replay/ReplayEnabled "1" -f -s location_fw::vconf -u 200 -g 5000
	vconftool set -t int db/location/replay/ReplayMode "0" -f -s location_fw::vconf -u 200 -g 5000
%endif
vconftool set -t double db/location/replay/ManualLatitude "0.0" -f -s location_fw::vconf -u 200 -g 5000
vconftool set -t double db/location/replay/ManualLongitude "0.0" -f -s location_fw::vconf -u 200 -g 5000
vconftool set -t double db/location/replay/ManualAltitude "0.0" -f -s location_fw::vconf -u 200 -g 5000
vconftool set -t double db/location/replay/ManualHAccuracy "0.0" -f -s location_fw::vconf -u 200 -g 5000

%post -n location-lbs-server
#%ifnarch %arm
#	cp -f /usr/lib/location/module/libgps.so /usr/lib/location/module/libwps0.so
#%endif

%postun -p /sbin/ldconfig

%files
%manifest lbs-server.manifest
%defattr(-,system,system,-)
%{libexecdir}/lbs-server
/usr/share/dbus-1/services/org.tizen.lbs.Providers.LbsServer.service
/usr/share/lbs/lbs-server.provider
/etc/rc.d/init.d/lbs-server
/etc/rc.d/rc5.d/S90lbs-server
#/etc/rc.d/*
/usr/lib/systemd/system/lbs-server.service
/usr/lib/systemd/system/multi-user.target.wants/lbs-server.service
/opt/etc/dump.d/module.d/dump_gps.sh

%files -n location-lbs-server
%manifest location-lbs-server.manifest
%defattr(-,system,system,-)
%{_libdir}/location/module/libgps.so*

%if 0%{?model_build_feature_location_position_wps}
%{_libdir}/location/module/libwps.so*
%endif

%files -n lbs-server-plugin-devel
%defattr(-,system,system,-)
%{_libdir}/pkgconfig/lbs-server-plugin.pc
%{_includedir}/lbs-server-plugin/*.h
