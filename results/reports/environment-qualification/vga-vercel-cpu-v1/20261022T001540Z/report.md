# Vercel Pythia environment qualification

Environment ID: `vga-vercel-cpu-v1`  
Evidence scope: environment setup, actual pretrained inference/LoRA initialization, repository regression and stop/resume recovery.  
Qualified source: `41d01730ca98430d282a06f089b0617d6351ab6b`, draft PR #1; not merged main research code.  
Model: `EleutherAI/pythia-410m` at `bba6a464f54bbf08fc174cfb351d9794d58af21d`.

## Executed results

- Created a sandbox-only Vercel project on the existing Pro team; no new subscription or Cloudflare service.
- Created persistent sandbox `vga-pythia-cpu-v1`: 4 vCPUs, 8 GiB, Linux amd64, iad1, 30-minute timeout.
- Installed Python 3.13.16, Torch 2.14.0+cpu, Transformers 5.16.1 and PEFT 0.20.0; retained the exact 45-package resolved lock.
- Verified model weight SHA-256 against official LFS metadata; pinned and verified all five model/tokenizer files.
- Loaded the actual checkpoint offline and observed finite logits, shape `[1,8,50304]`.
- Initialized LoRA with 3,145,728 trainable adapter parameters.
- Executed `python -m pytest -q tests` in the full checkout: **135 passed, zero failed, zero errors, zero skipped, one warning**, JUnit time 8.918 seconds. The warning concerns missing vocabulary config in a tiny-model checkpoint fixture.
- Repository working tree remained clean after the test suite.
- Replayed the bootstrap kit successfully on the prepared environment.
- Set session and persistent outbound networking to deny-all.
- Stopped the first session, resumed from its snapshot, verified a saved marker and loaded the actual model offline again.
- Stopped the resumed session. Final platform response: stopped, automatically snapshotted, one retained snapshot.

No optimizer updates on the pretrained Pythia checkpoint were executed. Unit tests include small fixtures; they are not Pythia learning experiments. No alignment benefit, attack robustness, calibration result, completed study or locked-run authorization follows from this setup.

## Runtime identities

Project: `prj_yzVr5decl5ft9XD3e2Ls7bq7QHlM`. Team: `team_QUlu3mpg38EsnDb9PutdBL1o`.

First session: `sbx_tltSJgZniH3x2kb0c2wOxqd9EaLj`; first automatic snapshot: `snap_uNvrrHduUJxdeRZptXYtVcNXQG4m`.

Verified resumed session: `sbx_4ncxQ7YyGABP9B9UguUqfGf5iNxP`. Final snapshot: `snap_1T8uk8H2wlS6Y2wDac1tZyHwjFgq`, 3,766,465,199 bytes; expiry `2026-10-29T00:15:40.399Z`.

The platform recorded aggregate session duration 752,759 ms and active CPU duration 165,014 ms. These are platform counters, not an inspected billing invoice or performance measurement of model training.

## Original evidence

[Original qualification archive](qualification-evidence.tar.gz), 5,638 bytes:

`SHA256 60d9064ed210d727dd762b7570d07009a28ab8576460cab48ed48716e8966b98`

Contents: original `pytest.xml`, `pytest.log`, `test-summary.json`, `qualification.json`, `restore-verification.json`, `model-assets.json`, and the empty `checkout-status-after-tests.txt`.

Important raw-file hashes:

- JUnit XML: `36a6c135a6daa8d8d11afc74056e9f0dab02cf9cedf3681b910ad57e8c22984a`
- pytest stdout: `e30e52b5f677c0202aba3144ca63a744efacee2ae6e297539cc945aa9de430f8`
- initial model qualification: `7da94b64c5a6c5d96be5deae69287ba7be6d3f61bd5d58f4eeb021c39808d255`
- model weight: `1c88b0bf18293fae0e09c1d978b14b1adb08cb6a83154463133982fe460fcea4`
- resolved dependency lock: `359a573805badbebe6088594a24265160dbefdef75de164858f50cf68a1a0751`
- executed bootstrap: `ca86cac331ea253c37151cbabec79deb764d45a3e78fd7d229339e88c1e0a270`
- executed verification script: `7f8442da5d88f2dca10b5291d994533d09d4ff603f68f2328bcc193b2840911f`

Archive export was verified against the remote SHA-256 and Git blob ID `c2b003a1a67ad505dabdacb496cbe31fee24437d`. These original logs are retained, not reconstructed from a pass count. Creation of the infrastructure commit does not retroactively turn the environment qualification into a preregistered scientific experiment.

## Next use

Follow [the operating runbook](../../../../../infra/vercel-research/README.md) and [environment manifest](../../../../../infra/vercel-research/environment.json). Resolve the named sandbox before resume; session/snapshot IDs are historical. Rebuild from the checked-in kit if the seven-day snapshot has expired. Requalify any new source revision, retain per-run evidence, profile actual training costs and keep the master protocol's locked-study boundary intact.
