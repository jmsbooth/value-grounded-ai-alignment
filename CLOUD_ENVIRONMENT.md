# Cloud research environment

The reusable VGA/Pythia execution environment is **Vercel Sandbox `vga-pythia-cpu-v1`**, in the existing `jmsbooths-projects` team and the new sandbox-only `vga-pythia-research` project.

Read [the operating runbook](infra/vercel-research/README.md) and [the exact environment manifest](infra/vercel-research/environment.json) before resuming it. The master scientific protocol remains [TESTING.md](TESTING.md); cloud availability does not authorize a locked study.

The environment was created, loaded with the pinned Pythia checkpoint, tested, stopped, resumed from its snapshot, verified offline again, and stopped. No application endpoint or recurring job was deployed. It has 4 vCPUs, 8 GiB RAM, a 30-minute session limit, one retained snapshot, and deny-all outbound networking after setup. The actual configured snapshot lifetime is seven days; the checked-in bootstrap kit provides a rebuild path after expiry.

The checkout qualified here is PR #1 head `41d01730ca98430d282a06f089b0617d6351ab6b`, not the main-branch model source. Full repository pytest: **135 passed, no failures/errors/skips, one warning**. Actual Pythia loaded offline with finite logits and LoRA initialized; no pretrained-model optimizer update or hypothesis experiment ran.

[Qualification report and original test evidence](results/reports/environment-qualification/vga-vercel-cpu-v1/20261022T001540Z/report.md).

This infrastructure-only commit does not merge PR #1, modify research code, change protocols/datasets, or regenerate the paper. The environment removes the previous missing-dependency/checkpoint blocker for subsequent bounded work; resource profiling, treatment fidelity and study-specific gates still apply.
