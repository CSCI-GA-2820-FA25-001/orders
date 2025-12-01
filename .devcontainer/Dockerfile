# This image has selenium and chrome driver already installed
FROM rofrano/pipeline-selenium:latest

# Become a regular user for development
ARG USERNAME=vscode
USER $USERNAME

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp; bash ./install-tools.sh

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --dev


#Image for a TDD
#FROM rofrano/nyu-devops-base:su25

# Set up the Python development environment
#WORKDIR /app
#COPY Pipfile Pipfile.lock ./
#RUN sudo python -m pip install --upgrade pip pipenv && \
    #sudo pipenv install --system --dev

# Install user mode tools
#COPY .devcontainer/scripts/install-tools.sh /tmp/
#RUN cd /tmp && bash ./install-tools.sh
