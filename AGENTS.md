# Working on DSH Skills

This repository distributes skills through cc-switch. Edit the source under `dsh-plugin/`; do not edit a cc-switch installed copy or its database. Keep the skill directory self-contained and discoverable through `dsh-plugin/SKILL.md`.

For DSH API changes, inspect the target version's source or installed declarations. Record the runtime version and commit in `docs/validation.md`; do not expand compatibility based on documentation alone. The default local checkout is `/home/vesoft/deepseek-harness`, but helpers and generated plugins must accept paths rather than embed it.

Run `python3 scripts/check_skill.py` and `python3 -m unittest discover -s dsh-plugin/tests -v`. If changing templates or DSH integration, generate into a new temporary directory, run `scripts/smoke.mjs` against built DSH, and test the packed bundle in an isolated DSH_HOME. UI changes require the real host page; record any unavailable verification. Do not modify DSH core or existing user profile data to make a test pass.

Keep source references, scripts and usage examples aligned. Generated integration examples are not complete business applications. Preserve this distinction in docs and test reports. Do not publish test profiles, credentials, temporary bundles or browser state.
