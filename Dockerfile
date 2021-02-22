#:
FROM ubuntu:18.04 AS hon-base

ENV CHECKOUT_DIR=/usr/src/hon \
    TZ=UTC \
    POETRY_VERSION=1.1.4

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && apt-get update \
 && apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    checkinstall \
    curl \
    git \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \ 
    libxmlsec1-dev \ 
    llvm \
    make \
    openssl \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev \
 && curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
 && ln -s /root/.pyenv/bin/pyenv /usr/local/bin/pyenv \
 && echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc \
 && echo 'eval "$(pyenv init -)"' >> ~/.bashrc \
 && echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc \
 && exec $SHELL

ARG PYTHON_VERSION
RUN pyenv install ${PYTHON_VERSION} \
    && pyenv global ${PYTHON_VERSION}

COPY . $CHECKOUT_DIR
COPY ./infrastructure/github-build.sh /github-build.sh
RUN chmod +x /github-build.sh
WORKDIR $CHECKOUT_DIR
ENTRYPOINT [ "/github-build.sh" ]
