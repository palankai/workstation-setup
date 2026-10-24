---
name: refining-issues
description: Turn rough GitHub issues labelled "to refine" into issues someone can actually pick up — asking the clarifying questions first, framing research and decision work so its deliverable is a document, and splitting oversized issues into sub-issues. Use this whenever the user asks to refine issues, groom or triage a backlog, work through the "to refine" label, flesh out an issue they jotted down, or turn a one-line request into a proper spec — even if they don't say the word "refine".
---

# Refining GitHub issues

## What refinement is for

People write issues fast and rough — a sentence or two to catch the want before it
escapes. That is the right way to capture work, and the wrong state to start work
from. Refinement closes the gap: it turns a note-to-self into something the author,
or you six months later, can act on without reconstructing the intent from memory.

Almost all of the value comes from the questions you ask, not the headings you
apply. A beautifully formatted issue that dodged the hard question is worse than a
scruffy one, because it looks finished. Aim your effort at the ambiguity.

**The output of a refinement session is the issue.** That boundary is what keeps
refinement from quietly turning into the work itself. Light research is welcome
and often necessary — enough to know the option space exists, name the plausible
candidates, use the field's vocabulary, and set criteria that will actually decide
something. That is the difference between "look into analytics" and an issue naming
four candidates and the three criteria that separate them. But the moment a question
needs real evaluation — trade-offs weighed, evidence gathered, something worth
re-reading in a year — that evaluation *is* the issue's deliverable, not yours.

The test: if you find yourself producing the answer rather than sharpening the
question, stop. What you gathered goes into the issue as starting material for
whoever picks it up, clearly marked as input rather than verdict.

## Before the first issue

Make sure the workflow's labels exist. Creating them is harmless if they are
already there — the command just fails and you carry on:

```bash
gh label create "refined" --color "0e8a16" --description "Refined and ready to pick up"
gh label create "needs answers" --color "d93f0b" --description "Refinement is waiting on the author's answers"
```

## The loop

### 1. Pick the issue

```bash
gh issue list --label "to refine" --state open
gh issue list --label "needs answers" --state open
```

Show them as a numbered list with a one-line summary of each, and let the author
choose. If they say "all", still work through them one at a time — after each one
is done, show what remains and confirm which to continue with. Refinement is
tiring in a way that writing issues is not; a session that can be stopped cleanly
after any issue is a session that gets finished.

Anything already carrying `needs answers` starts from the open questions in its
comments rather than from scratch.

### 2. Ground yourself before asking anything

Read the issue and all its comments, then read enough of the repository to know
what the issue is landing in — README, existing docs, the code or config the issue
touches, related closed issues. Questions the repository already answers are the
fastest way to make refinement feel like an interrogation, and they burn the
author's patience before you reach the questions that matter.

### 3. Ask

One question at a time. Multiple choice where the options are genuinely
enumerable, open where they are not.

Ask only what changes the issue. For each candidate question: if the author
answered either way, would the issue read differently? If not, drop it, or make
your assumption and mark it in the issue for them to strike out. Good territory
is usually scope boundaries, what "done" looks like, constraints they hold
implicitly, and the thing they'd be annoyed to receive.

### 4. Decide the shape

Most issues are one of three shapes. Recognising which one you have is most of
the work, because each has a different notion of "done".

**Building something.** The deliverable is code or configuration. Acceptance
criteria are checkable statements — a reader must be able to look at the result
and say yes or no without a judgement call. "Analytics works" fails that test;
"page views and referrers visible in a dashboard" passes it.

**Deciding something.** The deliverable is a document, not a change. The issue's
job is to answer a question well enough that nobody has to reopen it. Write:
the question, the candidate options, the criteria that will separate them, and
the exact path where the answer will be recorded — `docs/decisions/YYYY-MM-DD-<topic>.md`
in ADR style is a sensible default, but agree the location with the author
during refinement rather than assuming it; some answers belong in a notes vault
or elsewhere in the docs. "Done" for such an issue includes recording the
decision and opening the follow-up implementation issue.

**Too big.** See splitting, below.

An issue can start as one shape and turn out to be another — "implement X" often
becomes "decide which X" plus "implement the chosen X". That reframing is one of
the more valuable things refinement produces.

If the repository uses issue types, set the right one with
`gh issue edit <n> --type Feature|Bug|Task`. Don't invent type names; if the
command fails the repository has no types configured, so mention it once and
move on.

### 5. Write

Rewrite the body. The issue becomes the single source of truth, so a reader
should get the whole picture from the body without digging through comments.

Tighten the title to an imperative summary of the actual outcome — "Choose an
analytics provider" says more than "Implement analytics" when the real first
step is a decision.

Keep the body lean and adaptive. A short paragraph of context, then acceptance
criteria, then only the sections this particular issue needs. Empty headings are
noise; omit any section you'd have to pad. Preserve the author's original words
verbatim at the bottom, so the request that started it survives your
interpretation of it:

```markdown
Analytics on palankai.dev so I can see which pages people read and where
visitors come from.

## Acceptance criteria

- [ ] Page views and referrers visible in a dashboard
- [ ] No cookie banner required
- [ ] Script adds under 5 kB to the page

## Out of scope

- Per-user session recording
- A/B testing

<details><summary>Original request</summary>

Implement analytics so I can understand what people do on my page.
check Google Analytics but also competitors
</details>
```

Sections worth reaching for when they earn their place: **Out of scope** when
you can name something a reader would reasonably assume is included;
**Dependencies** when another issue must land first; **Open questions** for
things deliberately left to the implementer; **Assumptions** for anything you
inferred rather than got from the author, so they can see and strike it.

Write the body to a temporary file and pass it with `--body-file` — multi-line
markdown does not survive being shoved through `--body` on a command line:

```bash
gh issue edit <n> --title "..." --body-file /tmp/issue-<n>.md
```

### 6. Label and confirm

```bash
gh issue edit <n> --remove-label "to refine" --add-label "refined"
```

Then show the author what changed — the new title, the criteria, anything you
assumed — and move on to the next issue only once they've seen it.

## Splitting an oversized issue

When an issue holds more than one outcome, propose the split before creating
anything: each piece as a title plus a one-line scope, so the author can drop,
merge or rename them cheaply. Creating issues first and fixing them afterwards
leaves debris in the repository.

Choose the structure by asking whether the parent is still worth tracking:

- **Sub-issues** when the parent is a coherent umbrella whose completion means
  something — the parent becomes a tracking issue and the pieces hang under it
  (`gh issue create --parent <n>`, or `gh issue edit <n> --add-sub-issue 12,13`
  for issues that already exist).
- **Siblings** when the original was really several unrelated wants that happened
  to be written in one go. Ask before closing the original; it is the author's
  issue to close.

Pieces you refine properly in the same session are born `refined`. Pieces you
only got as far as a title for get `to refine` — that is honest, and it means
they surface again next session instead of looking finished.

Resist splitting for its own sake. Two issues that will always be worked
together are one issue with two acceptance criteria.

## When the session ends mid-refinement

If you've asked questions the author can't answer now, don't leave the state in
your context where it dies. Post the open questions as a comment on the issue and
move it to the waiting state:

```bash
gh issue comment <n> --body-file /tmp/questions-<n>.md
gh issue edit <n> --remove-label "to refine" --add-label "needs answers"
```

Next session picks up from those questions. Once they're all answered, the issue
finishes refinement and moves to `refined`.

## Things to be careful about

- **Don't invent acceptance criteria.** Anything material should come from the
  author's answers. Where you inferred something, say so in the issue rather than
  presenting it as agreed — an unmarked assumption is indistinguishable from a
  requirement once the issue is a few weeks old.
- **Don't close, delete or reassign** an issue without asking.
- **Don't refine the same issue twice.** If the body already has structure, you're
  probably looking at something already refined that was relabelled for a reason.
  Ask what changed.
- **Match the author's language.** British English if that's what the repository
  uses. The issue should read as though they wrote it on a good day, not as
  though a tool processed it.
