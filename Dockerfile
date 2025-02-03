# Build Python package and dependencies
FROM python:3.11-alpine3.16 AS python-build

RUN apk add --no-cache \
        git \
        libffi-dev \
        musl-dev \
        gcc \
        g++ \
        make \
        zlib-dev \
        tiff-dev \
        freetype-dev \
        libpng-dev \
        libjpeg-turbo-dev \
        lcms2-dev \
        libwebp-dev \
        openssl-dev

RUN mkdir -p /opt/venv
WORKDIR /opt/venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /src
WORKDIR /src


COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM python:3.11-alpine3.16 AS final

RUN apk update

RUN apk add --no-cache \
        curl \
        git \
        nss \
        libffi \
        musl \
        gcc \
        g++ \
        make \
        tiff \
        freetype \
        libpng \
        libjpeg-turbo \
        lcms2 \
        libwebp \
        openssl \
        zlib \
        busybox \
        sqlite \
        libxml2 \
        libssh2 \
        ca-certificates \
        ffmpeg \
        libvpx \
        x264-libs \
        x265 \
        libvorbis \
        opus \
        libass \
        xvidcore \
        lame

RUN curl -LO https://github.com/dylanaraps/neofetch/archive/refs/tags/7.1.0.tar.gz && \
    tar -xzf 7.1.0.tar.gz && \
    cd neofetch-7.1.0 && \
    install -Dm755 neofetch /usr/local/bin/neofetch && \
    cd .. && rm -rf neofetch-7.1.0 7.1.0.tar.gz

RUN mkdir -p /caligo
WORKDIR /caligo
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
COPY --from=python-build /opt/venv /opt/venv

CMD ["python3", "-m", "caligo"]
