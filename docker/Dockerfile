FROM python:3.11-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HERMES_HOME=/home/hermes/.hermes \
    PATH="/opt/venv/bin:${PATH}"

ARG HERMES_REPO=https://github.com/NousResearch/hermes-agent.git
ARG HERMES_BRANCH=main
ARG HERMES_UID=1000
ARG HERMES_GID=1000

ARG INSTALL_BROWSER_TOOLS=true
ARG INSTALL_SEARCH_FALLBACK=false
ARG INSTALL_SPREADSHEET_EXTRAS=false

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    ffmpeg \
    git \
    libffi-dev \
    nodejs \
    npm \
    python3-dev \
    ripgrep \
  && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip && python -m pip install uv

RUN groupadd --gid ${HERMES_GID} hermes \
  && useradd --create-home --uid ${HERMES_UID} --gid ${HERMES_GID} --shell /bin/bash hermes

WORKDIR /srv/hermes-agent
RUN git clone --depth 1 --shallow-submodules --recurse-submodules \
    --branch "${HERMES_BRANCH}" \
    "${HERMES_REPO}" .

RUN /usr/local/bin/uv venv /opt/venv --python 3.11

RUN /usr/local/bin/uv pip install -e ".[all]" \
  && /usr/local/bin/uv pip install -e ./mini-swe-agent

RUN if [ "${INSTALL_BROWSER_TOOLS}" = "true" ]; then \
      npm install; \
      npm cache clean --force; \
    fi

RUN if [ "${INSTALL_SEARCH_FALLBACK}" = "true" ]; then \
      /usr/local/bin/uv pip install ddgs Search-Engines-Scraper trafilatura; \
    fi

RUN if [ "${INSTALL_SPREADSHEET_EXTRAS}" = "true" ]; then \
      /usr/local/bin/uv pip install pandas openpyxl xlsxwriter; \
    fi

RUN mkdir -p /opt/hermes-templates \
  && cp -a /srv/hermes-agent/cli-config.yaml.example /opt/hermes-templates/cli-config.yaml.example \
  && cp -a /srv/hermes-agent/.env.example /opt/hermes-templates/.env.example \
  && ln -s /opt/venv/bin/hermes /usr/local/bin/hermes \
  && ln -s /srv/hermes-agent/setup-hermes.sh /usr/local/bin/setup-hermes.sh \
  && mkdir -p "${HERMES_HOME}"/{cron,sessions,logs,skills,memories,image_cache,audio_cache,pairing,whatsapp/session,output}

COPY docker/entrypoint.sh /usr/local/bin/hermes-entrypoint.sh
RUN chmod +x /usr/local/bin/hermes-entrypoint.sh \
  && chown -R hermes:hermes /srv/hermes-agent "${HERMES_HOME}" /opt/hermes-templates /usr/local/bin/hermes-entrypoint.sh

USER hermes
WORKDIR /home/hermes
VOLUME ["/home/hermes/.hermes", "/home/hermes/.hermes/output"]
ENTRYPOINT ["/usr/local/bin/hermes-entrypoint.sh"]
CMD ["hermes", "gateway"]
