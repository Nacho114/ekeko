FROM docker.io/library/archlinux:latest

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm git which python-pipx

RUN pipx ensurepath

RUN pipx install poetry
