# PR 571 review-fix validation — 2026-10-04

Target: [Quittance-Labs/Quittance0#571](https://github.com/Quittance-Labs/Quittance0/pull/571).

Candidate commit: `f634e4f37945d40b0ed4024a88b380f5847fe87a`.

Candidate tree: `cc5b8f56e908f6e60e8bb683211a3d950fd959be`.

Retained candidate ref: `validation/q571-candidate-f634e4f` in this fork. This report and its validation workflow are not part of the product candidate.

## Project checks

[Combined run 37189795925](https://github.com/woahwhattheheck/Quittance0/actions/runs/37189795925), job `111399414070`, assembled and checked the exact candidate. Runtime: Node 24.21.0, npm 11.19.0, Ubuntu hosted runner. Locked frontend and backend dependencies were installed. No live payment or settlement smoke was performed.

| Working directory | Command | Exit | Test result |
| --- | --- | --- | --- |
| frontend | `npm run lint` | 0 | Three anonymous-default-export warnings; no lint error |
| frontend | `npm run typecheck` | 0 | Typecheck passed |
| frontend | `npm test` | 0 | 756 passed, 0 failed |
| backend | `npm run typecheck` | 0 | Typecheck passed |
| backend | `node --import tsx --test tests/invoice-contract.test.ts tests/create-invoice-validation.test.ts tests/shared-verification-contract.test.ts` | 0 | 80 passed, 0 failed |
| repository root | `node --test tests/invoice-contract.test.mjs` | 0 | 2 passed, 0 failed |

All six project commands returned zero: 838 selected tests passed. The backend command is a selected contract check, not the full backend suite. The shared command covers the named file, not every shared test.

**The combined workflow's overall conclusion is failure**, not success. An additional validation-wrapper condition required the tracked worktree to remain unchanged. It was false after the commands. That initial runner did not retain the changed-file list or diff. The raw receipt deliberately retains both `all_checks_passed: true` and `source_worktree_unchanged: false`.

The full command logs and receipt are in [artifact 11298905270](https://github.com/woahwhattheheck/Quittance0/actions/runs/37189795925/artifacts/11298905270). The downloaded ZIP was inspected directly; SHA-256: `8e823cff096f23a31c455f293a5c004324cfdd5bf9a6e427a30b0e250446e0d8`.

## Independent pristine-source typecheck

[Run 37190601163](https://github.com/woahwhattheheck/Quittance0/actions/runs/37190601163), job `111401771842`, checked out the same candidate directly and compared `frontend/next-env.d.ts` byte-for-byte with `git show HEAD:frontend/next-env.d.ts`. The worktree Git blob and committed Git blob matched. No copied expected file digest or generated declaration replacement was used.

- `npm ci --prefix frontend --no-audit --no-fund`: exit 0, no tracked changes.
- `npm --prefix frontend run typecheck`: exit 0 on the original source declaration.
- The only tracked change afterward was `frontend/tsconfig.tsbuildinfo`, the generated TypeScript build-cache file. The exact diff was retained; application files and `next-env.d.ts` were unchanged.

**This workflow also has an overall failure conclusion** because its extra clean-worktree condition rejected the generated cache change. That is not a TypeScript compilation failure. It does not change the successful project-command exit codes. The pristine source typechecks without first regenerating or replacing its declarations.

The actual declaration bytes, install/typecheck logs, receipt and complete cache diff are in [artifact 11298820972](https://github.com/woahwhattheheck/Quittance0/actions/runs/37190601163/artifacts/11298820972). The downloaded ZIP was inspected directly; SHA-256: `0aa3e93795894a7b7121fa2cb141ede1197e3ccd3b7b5dc144cf7d44f61a0654`.

## Earlier diagnostics and limits

Baseline run `37188450363` reproduced six failing frontend tests on original PR head `b223d5798fe68c150a429e652f10990d3f632a7d`: 594 of 600 passed. The candidate also integrates a newer upstream base, so the larger candidate test count is not presented as six new tests alone.

Narrow follow-ups `37189948422` and `37190209233` did not establish the initially proposed declaration-normalization recipe. The latter stopped on an expected-file-hash condition before executing npm. Copied diagnostic hashes from interim notes are not validation authority. The downloadable raw project-command receipt and independently verified pristine-source artifact above are the retained evidence; earlier failed runs remain failed.

No test suites were rerun in the pristine-source check. No product branch was changed by this validation work, and no generated cache or declaration change was committed to the candidate. This report supports review of the candidate; it does not assert upstream CI success, sponsor approval, merge, award or payment.
