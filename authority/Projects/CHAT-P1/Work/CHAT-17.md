<!-- lwa:meta
{
  "id": "CHAT-17",
  "kind": "issue",
  "title": "License ChatMD under MIT",
  "authority": "local-native",
  "revision": 1,
  "status": "active",
  "created_at": "2026-09-21T06:55:00Z",
  "updated_at": "2026-09-21T06:55:00Z",
  "owner": {
    "kind": "project",
    "id": "CHAT-P1"
  },
  "relations": []
}
-->
# License ChatMD under MIT

## Outcome

Make ChatMD explicitly open source under the MIT License.

The repository is already public, but current repository inspection shows no root
`LICENSE` file and GitHub reports no detected license. Public visibility alone
does not grant the reuse, modification, redistribution, and commercial-use
permissions that an explicit open-source license provides.

This Work records the human product decision to use MIT.

## Governing authority / source of truth

CHAT-P1 defines ChatMD as a small, local-first conversion tool with a portable
product boundary. This Work does not change that product contract.

The current public GitHub repository `loneborz/chatmd` is the source of truth
for repository visibility and files. Inspection before this Work found:

- repository visibility is public;
- GitHub repository metadata reports `license: null`;
- no root `LICENSE` file exists;
- the current README describes ChatMD as a usable public tool but does not
  establish an explicit software license.

The human owner has explicitly selected the MIT License for ChatMD.

## Scope

Add an explicit MIT License to ChatMD using the standard MIT license text.

Required implementation:

- add a root `LICENSE` file;
- use year `2026`;
- use a human-approved copyright holder attribution;
- preserve the standard MIT grant, copyright notice retention requirement,
  warranty disclaimer, and liability disclaimer;
- ensure GitHub can detect the repository license as MIT after the change;
- if useful for discoverability, add a small factual License section to
  `README.md` stating that ChatMD is licensed under MIT and linking to the
  repository license file.

The exact copyright-holder string is a human decision. Do not invent a legal
name. If the owner has not supplied the desired attribution at execution time,
stop before writing the final license text and ask for it.

## Non-goals

Do not:

- change ChatMD runtime behavior;
- change `chatmd.py`, parser behavior, capture behavior, tests, or bundle
  semantics;
- change CHAT-D1;
- add a Contributor License Agreement;
- add dual licensing;
- add GPL, Apache-2.0, source-available, or custom license terms;
- change package versioning, release automation, distribution, Homebrew, or
  publishing;
- claim rights over third-party software, ChatGPT, OpenAI, user conversations,
  or other material not owned by the ChatMD copyright holder;
- perform unrelated README or website cleanup.

## Evidence requirements

- A root `LICENSE` file exists.
- Its text is the standard MIT License with year `2026` and the
  human-approved copyright holder.
- GitHub repository metadata or the repository UI detects the license as MIT
  after the change has reached the default branch.
- Any README change is limited to a concise factual license reference.
- `git diff --check` passes.
- Local-native render and validate pass for authority changes.
- The intended diff contains no unrelated product changes.

## Acceptance criteria

- [ ] ChatMD has a root `LICENSE` file containing the standard MIT License.
- [ ] The license uses year `2026`.
- [ ] The copyright-holder attribution was explicitly approved by the human
      owner rather than inferred.
- [ ] GitHub detects the repository license as MIT on the default branch.
- [ ] Runtime code, tests, product behavior, and CHAT-D1 are unchanged.
- [ ] Any README edit is limited to a concise MIT license reference.
- [ ] `git diff --check` and local-native render/validate pass.
- [ ] The complete intended diff contains no unrelated changes.
- [ ] A human accepts the resulting license presentation.

## Completion boundary

CHAT-17 is complete when the standard MIT License is present at the repository
root with a human-approved copyright attribution, GitHub detects MIT on the
default branch, required verification passes, and the human owner accepts the
result.

Do not mark this Work done, check human-accepted criteria, reconcile authority,
commit implementation, or push additional implementation unless a later human
decision explicitly authorizes those actions.
