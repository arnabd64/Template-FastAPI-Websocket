ARG python-tag=3.10-slim-bullseye

# STEP 1: pull base image
FROM python:${python-tag}

# STEP 2: create a passwordless sudo user
ARG username=appuser
ENV USER ${username}
ENV HOME /home/${username}
RUN useradd -m -u 1000 ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}
WORKDIR ${HOME}/app
USER ${USER}

# STEP 3: install python dependencies
COPY --chown=${USER}:${USER} pyproject.toml poetry.lock ${HOME}/app/
RUN pip install --user poetry && \
    poetry install --no-root

# STEP 4: copy the rest of the application
COPY --chown=${USER}:${USER} . ${HOME}/app/

# STEP 5: run the application
CMD ["poetry", "run", "python", "main.py"]
