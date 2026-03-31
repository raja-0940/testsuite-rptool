FROM fedora:latest

WORKDIR /rp

RUN dnf -y install uv python make
RUN uv tool install junitparser

COPY src /rp/src
COPY rptool /rp/
COPY pyproject.toml /rp/
COPY Makefile /rp/
COPY README.md /rp/

ENV PATH=/root/.local/bin:/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Use build arg to pass version (defaults to 0.0.0+unknown if not provided)
ARG VERSION=0.0.0+unknown
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

RUN uv tool install .

CMD ["bash"]