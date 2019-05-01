FROM debian:stretch

RUN useradd -ms /bin/bash pi
COPY . /opt/iotd/
WORKDIR /opt/iotd/

RUN echo 'debconf debconf/frontend select teletype' | debconf-set-selections
RUN apt-get -qq update -y && apt-get -qq install -y --no-install-recommends \
    anacron      \
    cron         \
    git          \
    python3      \
    sudo         \
    systemd      \
    systemd-sysv \
    wbritish     \
    whiptail     \
    && rm -rf /var/lib/apt/lists/*

RUN bash install.sh --demo

ENV container docker

STOPSIGNAL SIGRTMIN+3
VOLUME [ "/sys/fs/cgroup", "/run", "/run/lock", "/tmp" ]

CMD [ "/sbin/init" ]
