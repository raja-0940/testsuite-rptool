FROM fedora

WORKDIR /rp

RUN dnf -y install uv python make
RUN uv tool install junitparser

COPY src /rp/src
COPY rptool /rp/
COPY pyproject.toml /rp/
COPY Makefile /rp/
COPY README.md /rp/

ENV PATH=/root/.local/bin:/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN uv tool install .

CMD ["bash"]