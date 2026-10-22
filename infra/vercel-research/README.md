# Vercel research execution runbook

Environment: `vga-vercel-cpu-v1`. This is a full Linux Vercel Sandbox, not a Vercel Function, Cloudflare Worker or public web application. It uses the existing Pro team; no new subscription, Cloudflare resource, cron job or public application endpoint was created. The sandbox and project IDs below are identifiers, not credentials.

## Exact lookup and lifecycle

- Team: `team_QUlu3mpg38EsnDb9PutdBL1o` / `jmsbooths-projects`
- Project: `prj_yzVr5decl5ft9XD3e2Ls7bq7QHlM` / `vga-pythia-research`
- Named sandbox: `vga-pythia-cpu-v1`
- 4 vCPUs, 8192 MiB RAM, amd64, iad1, CPU only
- 30-minute session timeout; one retained snapshot; the API recorded seven-day snapshot expiration.

Use the authenticated Vercel connector:

1. Call `get_named_sandbox` with name/project/team and `resume=false` to inspect without starting compute.
2. When a bounded task is authorized, call it with `resume=true`. Use the **returned current session ID** for commands; a stopped session ID cannot be restarted.
3. Execute commands with `run_session_command` and the returned ID. Source `/vercel/vga-activate.sh` first. Capture command IDs, exit status, stdout and immutable artifacts.
4. Stop the session explicitly with `stop_session` at the end, including error paths. Verify stopped status and the new snapshot identity. Do not leave compute running while writing documentation.

Persistence was actually tested by stopping, snapshotting, resuming and loading the exact model offline. Snapshot IDs change; resolve the named sandbox rather than hardcoding the historical ID. Snapshots preserve files, not a running training process. Resume a saved training checkpoint only after protocol-approved checkpoint equivalence checks.

The final setup snapshot was `snap_1T8uk8H2wlS6Y2wDac1tZyHwjFgq`, 3,766,465,199 bytes, expiring `2026-10-29T00:15:40.399Z`. This is observed deployment configuration, not a claim about the current default retention advertised in Vercel documentation. An idle environment may need rebuilding after expiry. Store important new artifacts in GitHub or separately approved durable storage before that point.

## Commands in a resumed session

```bash
source /vercel/vga-activate.sh
# Verify cached model identities and an actual offline forward pass; no training:
python /vercel/vga-cloud-kit/prepare.py
# Regression uses the current recorded checkout:
python -m pytest -q tests
```

The qualified source is draft PR #1 head `41d01730ca98430d282a06f089b0617d6351ab6b`. It is not the main-branch model implementation. Do not silently update it or represent this test as a test of later commits. For new code, inspect the PR/head, preserve the current workspace, register the intended new SHA, and explicitly obtain/requalify that source. Normal sessions deny outbound network; only temporarily allow the specific public GitHub hosts needed for an approved source refresh.

The shell is noninteractive and `source` requires bash. The virtualenv is `/vercel/vga-env`, model cache `/vercel/vga-model-cache`, source `/vercel/value-grounded-ai-alignment`, and setup evidence `/vercel/vga-environment-records`.

Read the scientific [master protocol](../../experiments/protocols/vga-master-v1.0.0/protocol.md). Before model training, resolve the run plan, source/data/parameter hashes, generation feasibility, longest structured input memory, time budget and exact expected coverage. Unit-test success does not close those requirements. Use CPU as an explicit environment condition; do not pool these runs with Mac/MPS training as though the backend were identical.

No pretrained fine-tuning, all-arm comparison, locked study or OLMo training ran during setup. The next useful increment is bounded real-tokenizer/gradient/resource diagnostics, then the registered memorization/A1 schedules if they fit measured resources. Checkpoint early enough to stop within the session budget. A longer session or GPU service is a separate budget decision, not automatic retry logic.

## Rebuild after expiration

The kit contains the exact executed bootstrap and verification scripts, plus the 45-package resolved lock. Their versions are pinned, but wheel hashes are not locked; this is not claimed to be a hermetic supply-chain build. Model bytes have independent expected SHA-256 digests; the weight file also matched the official Hugging Face LFS metadata during setup.

Create a new persistent named sandbox (reuse the configured name only if the platform allows recovery; otherwise version it and update the manifest). Use the project above, 4 vCPUs / 8192 MiB, iad1, 30-minute timeout, one retained snapshot, no application ports, and the pinned base image in `environment.json` where supported. Initialize its source at the exact qualified commit or separately copy the public checkout. The existing bootstrap refuses to reset a differing checkout.

Copy this kit's `bootstrap.sh`, `prepare.py`, and `requirements.lock` into `/vercel/vga-cloud-kit` using connector file upload or a verified public GitHub download. If cloning the infrastructure main commit to retrieve this kit, put that clone in a separate directory; the model checkout must still be the exact qualified SHA.

Temporarily allow only these download domains: `github.com`, `api.github.com`, `codeload.github.com`, `raw.githubusercontent.com`, `*.githubusercontent.com`, `pypi.org`, `files.pythonhosted.org`, `download.pytorch.org`, `*.pytorch.org`, `huggingface.co`, `*.huggingface.co`, `*.hf.co`. Do not inject secrets. Clear inherited offline flags only for bootstrap:

```bash
unset HF_HUB_OFFLINE TRANSFORMERS_OFFLINE
bash /vercel/vga-cloud-kit/bootstrap.sh
source /vercel/vga-activate.sh
```

Then replace BOTH the running session policy and the named sandbox's persisted policy with `deny-all`. Persist the offline variables from `environment.json`/activation script. Rerun `prepare.py` without `--download`; archive a new qualification run and stop. The bootstrap was replay-tested on the provisioned environment; the cloud creation itself was executed through the connector, not by this script.

## Cost controls

The existing Pro account incurs metered usage; the new project does not make Sandbox usage automatically free. Official iad1 rates checked during setup: active CPU $0.128/vCPU-hour, provisioned memory $0.0212/GB-hour, snapshot $0.08/GB-month. At continuous full utilization, 4 CPUs plus 8 GB are approximately $0.6816/hour, or $0.3408 for 30 minutes, before account credits, storage, tax and other charges. At lower active CPU use the compute component decreases; allocated memory bills while the session exists. This is an estimate, not a billed amount.

A roughly 3.77 GB snapshot is approximately $0.30 if retained a full month, or $0.07 for seven days at a 30-day prorating illustration. One snapshot is kept and old ones are deleted. Stop compute rather than letting it idle. There is no account-wide dollar hard cap configured by this task; the timeout is a per-session safety bound, not an account spending ceiling. No account-wide billing settings were changed.

Pricing source: https://vercel.com/docs/sandbox/pricing . Persistence source: https://vercel.com/docs/sandbox/concepts/persistence . Recheck rates before a larger study. No Cloudflare service was needed for this bounded CPU environment. Do not add storage/queues/functions/GPU services without a concrete requirement and budget.

## Evidence and security

[Qualification report](../../results/reports/environment-qualification/vga-vercel-cpu-v1/20261022T001540Z/report.md) includes exact source, regression counts, raw evidence archive and checksums. The archive contains no model weights, secret credentials or user data. It is an environment qualification artifact, not an empirical model comparison or a replacement for the study registry.

Application ports are empty; Vercel may expose its own system control route. No GitHub write credential was installed inside the VM. Publish results via the separately authenticated GitHub connector, verify original bytes and identities, and keep the scientific study's raw/analysis/report lineage intact. Avoid commands that regenerate the frozen manuscript.
