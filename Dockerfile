ARG tag=3.10-slim-bullseye

# STEP 1: pull base image
FROM python:${tag}

# STEP 2: create a passwordless sudo user
ARG username=appuser
ENV USER ${username}
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}
USER ${USER}
ENV PATH /home/${USER}/.local/bin:$PATH
ENV HOME /home/${USER}
WORKDIR ${HOME}/app

# STEP 3: install python dependencies
COPY --chown=${USER}:${USER} pyproject.toml poetry.lock ${HOME}/app/
RUN pip install --user poetry && \
    poetry install --no-root

# STEP 4: copy the rest of the application
COPY --chown=${USER}:${USER} . ${HOME}/app/

# STEP 5: run the application
CMD ["poetry", "run", "python", "main.py"]
