# Hermes Agent container deployment (safe secrets + persistent `.hermes`)

This folder contains a rebuild-safe container setup:
- `Dockerfile` installs Hermes + node/browser + `rg` + optional research/tooling extras
- `docker-compose.example.yml` shows Docker Compose with secret mounts
- `entrypoint.sh` bootstraps `~/.hermes` from mounted secrets on first run
- secrets are never baked into the image

## 1) Create secret files

From `docker/` create two files:

- `secrets/hermes.env` for `~/.hermes/.env`
- `secrets/hermes.config.yaml` for `~/.hermes/config.yaml`

Example:

```bash
mkdir -p docker/secrets
cat > docker/secrets/hermes.env <<'EOF'
OPENROUTER_API_KEY=...
MINIMAX_API_KEY=...
GROQ_API_KEY=...
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...
EOF

cp docker/config.yaml.example docker/secrets/hermes.config.yaml
```

## 2) Build and run

```bash
cd docker
cp docker-compose.example.yml docker-compose.yml
docker compose build
docker compose up -d
```

## 3) Rebuild strategy

If you update base dependencies, node modules, or `.env` mount behavior:

- rebuild image: `docker compose build --no-cache`
- restart: `docker compose up -d --force-recreate`

Persistent data and credentials stay in:
- named volume: `hermes-home`
- mounted artifacts folder: `./artifacts` (host-mounted output)
- secret files: `./secrets/*`

## 4) Run tasks interactively

```bash
docker compose run --rm hermes hermes chat --toolsets "skills,web" -q "run deep research on topic X"
```

## 5) Gateway + email workflow

- Configure email variables in `secrets/hermes.env` and keep gateway running (`hermes gateway`).
- Put outputs in `/home/hermes/.hermes/output` so they survive across container restarts.
- For very large table/report outputs, write CSV/XLSX to that folder and attach via reply text using:
  `MEDIA:/home/hermes/.hermes/output/filename.xlsx`

## 6) Launch a test deep-research + table task

Use this exact prompt in CLI or email:

```text
Create a detailed Hungarian robotics ecosystem table in Hungarian and English.
Include every organization or individual in Hungary connected to robotics: integrators, developers, startups, distributors, educational entities, universities, labs, associations, and heavy users. Save results as:
- /home/hermes/.hermes/output/hungarian-robotics-ecosystem.xlsx
- /home/hermes/.hermes/output/hungarian-robotics-ecosystem.csv

Columns:
organization/people name,
type or category,
main profile,
website,
contact email (one or more),
how Hungarian Robotics Association can add value to this entity

Use the web tool to gather evidence links and validate emails from official pages.
When finished, reply with:
MEDIA:/home/hermes/.hermes/output/hungarian-robotics-ecosystem.xlsx
plus a brief summary.
```

Model preference for this run:
1) Use OpenRouter `hunter-alpha` as primary
2) if it fails, retry once with OpenRouter `healer-alpha`
3) `fallback_model` is hard fallback to `minimax MiniMax-M2.5`.

## Notes

- `hermes.config.yaml` is copied only when the secret file is present.
- Existing runtime values in the persistent `${HERMES_HOME}` volume are preserved.
- If you do not want spreadsheet extras, set `INSTALL_SPREADSHEET_EXTRAS=false` in the compose args.
