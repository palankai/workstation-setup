---
name: working-issues
description: Pick a refined GitHub issue and work it through to a pull request — grounding in the code first, agreeing the approach before touching anything, committing only what the author has reviewed, and handing back a PR that references the issue rather than closing it. Use whenever the user wants to start on an issue, asks what to work on next, names an issue number, or says they want to pick something up from the backlog — including bugs to fix and research tasks, not only features.
---

# Working a GitHub issue

## What this is for

A refined issue is a prompt someone already thought hard about. Refinement settled
*what* and *why*; this skill is about *how*, and about not losing the thread between
"picked it up" and "someone can review it".

Treat the issue as the brief, not as a straitjacket. It will be wrong about some
details — that is normal, and small course corrections are part of doing the work.
What is not part of doing the work is quietly changing what the issue is *for*. That
distinction is the one to keep hold of; the rest of this skill is mechanics.

The author reviews before every commit and before the push. Those gates are not
ceremony — they are the only points where a wrong turn is cheap to undo.

## Before the first issue

Make sure the workflow's labels exist. Creating them is harmless if they are already
there — the command just fails and you carry on:

```bash
gh label create "in progress" --color "1d76db" --description "Picked up and being worked on"
gh label create "ready to test" --color "5319e7" --description "Work delivered; awaiting the author's verdict"
```

## The loop

### 1. Pick the issue

```bash
gh issue list --label "refined" --state open --json number,title,issueType,labels
```

Show them as a numbered list — number, type, and a one-line summary of the outcome —
and let the author choose. If the author already named an issue, skip straight to it.

If nothing is refined, say so and offer the `refining-issues` skill rather than
starting on something raw. Working an unrefined issue is how you end up building the
wrong thing carefully.

Anything already labelled `in progress` is a session someone abandoned. Say so, and
check the branch and any existing commits before assuming you are starting from
nothing.

### 2. Ground yourself before saying anything about approach

Read the issue and all of its comments, then read enough of the repository to know
what you are landing in: README, the Makefile or whatever the project uses as its
entry points, the code the issue touches, related closed issues and their PRs.

Opinions formed before this reading are guesses wearing a confident voice. The
author can tell the difference, and so can the diff.

### 3. Ask only what genuinely blocks you

One question at a time. The test is whether the answer changes what you do: if you
would write the same code either way, decide it yourself and mention the decision.
If you would write something materially different, ask.

Anything material that comes out of those answers belongs on the issue, not only in
the conversation:

```bash
gh issue comment <n> --body-file /tmp/note-<n>.md
```

Sessions end. The issue is what survives them.

### 4. Shape the work, and agree it

Summarise what you are going to do — the approach, the files you expect to touch,
anything the issue left open that you have decided — and get approval before you
touch the repository. Keep it to what the author needs in order to say "no, not like
that"; a long plan invites agreement by exhaustion.

Reach for a process skill only when the issue earns it. The signal is the work, not
the label: several interacting changes, an ordering that is not obvious, or a failure
you cannot yet explain. A one-file change with clear acceptance criteria does not
need a planning document, and producing one wastes the author's attention on
paperwork instead of on the diff.

- **Bug** — reproduce it first, then use `systematic-debugging` before writing any
  fix. A fix for a fault you have not observed is a guess, however plausible. The
  bug is not done until the original failure demonstrably no longer happens, and the
  reproduction is what proves it.
- **Feature** — the deliverable is code, and the acceptance criteria are the
  contract. Where the repository has tests, the feature arrives with them. If the
  work is large or the ordering matters, use `writing-plans` first; otherwise a short
  plan in the conversation is enough.
- **Task** — usually research or a decision, and the deliverable is a document at the
  path the issue names. The prose *is* the work, so the review gate is the author
  reading it, not skimming a diff. Record what was decided and why it beat the
  alternatives; a decision whose reasoning is missing gets relitigated within the
  year. If the task's answer implies implementation work, that is a follow-up issue,
  not an extension of this one.

### 5. Set up

```bash
git switch -c <n>-<short-slug-from-the-title>
gh issue edit <n> --add-assignee @me --remove-label "refined" --add-label "in progress"
```

Branch from the repository's main branch, and check it is current first. Working on
top of a stale main produces a PR whose diff is half other people's work.

### 6. Do the work, one reviewable commit at a time

Several commits is the normal shape, not a failure to be tidy. Commit at points where
the tree makes sense on its own — a refactor that changes no behaviour, then the
behaviour change that needed it, reads far better in review than one commit
containing both.

Before every commit, stage deliberately and show the author exactly what will be
committed:

```bash
git add -p   # or explicit paths — never `git add -A` without looking
git diff --staged
```

Then wait. The author reviews the staged diff and the proposed message; you commit
only once they have. Match the repository's existing commit style — read `git log`
rather than importing a convention from elsewhere.

Do not commit generated output, dependency directories, or files you touched only to
debug. If something needs to be ignored, say so and let the author decide.

### 7. Verify before you claim anything

Run the project's standard checks — `make check`, `make build` and whatever else the
Makefile exposes, or the commands the README documents when there is no Makefile.
Show the output. A check you did not run is not a check that passed.

Then walk the issue's acceptance criteria one at a time and state the evidence for
each: the command, the file, the observed behaviour. Where a criterion cannot be
verified from here — anything needing production, a browser, or the author's own eyes
— say that plainly and say who has to check it. An unmarked "done" against something
you could not test is the most expensive kind of small lie.

If a criterion is not met, it is not met. Report it, with what remains.

### 8. Hand over

Push only after the author has approved it. Then open the pull request:

```bash
git push -u origin HEAD
gh pr create --title "..." --body-file /tmp/pr-<n>.md
```

The PR body says what changed and why, references the issue as `Refs #<n>`, and calls
out anything the reviewer has to verify by hand. Use `Refs`, never `Closes` or
`Fixes`: closing the issue is the author's decision once they have seen the result,
and an auto-closed issue takes the follow-up conversation with it.

Request the Copilot review, then stop — do not poll for it. Tell the author it has
been requested and that they will see it land.

Finally, move the issue to its waiting state:

```bash
gh issue edit <n> --remove-label "in progress" --add-label "ready to test"
```

Then report: the PR link, what was delivered, what still needs the author's eyes, and
anything you noticed that might deserve its own issue. Suggest follow-up issues;
don't create them uninvited.

## When the issue turns out to be wrong

Sometimes the ground shifts under you: the issue is bigger than it looked, it rests
on an assumption the code contradicts, or it is blocked on something nobody spotted
during refinement.

Stop. Do not improvise a smaller version of the issue and deliver that — a
half-answered issue that looks finished is worse than an honest halt, because nobody
knows to come back to it.

Record what you found as a comment on the issue, say what you have already done and
where the branch stands, and hand back to `refining-issues`. Re-refining costs one
conversation. Discovering the mismatch after merge costs considerably more.

## Things to be careful about

- **Don't skip the review gates.** Committing and pushing without the author seeing
  the diff removes the only cheap moment to change direction.
- **Don't close the issue.** The PR references it; the author closes it.
- **Don't widen the scope.** Things you notice along the way — nearby bugs, tempting
  refactors, missing tests elsewhere — go into the report as candidate issues, not
  into the diff. A PR that answers its issue plus three things nobody asked about is
  a PR nobody can review.
- **Don't hide a failing check.** If `make check` fails on something unrelated to
  your change, say so rather than working around it silently.
- **Match the repository's language and conventions.** British English if that is what
  the repository uses, in commits, PR bodies and comments alike.
