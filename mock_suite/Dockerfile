FROM fedora:latest

WORKDIR /testsuite

RUN dnf install -y python uv make
RUN uv pip install --system pytest pytest-xdist

COPY sut /testsuite/sut
COPY tests /testsuite/tests
COPY Makefile /testsuite
COPY pyproject.toml /testsuite
COPY pytest.ini /testsuite/


CMD [ "bash" ]

