---
name: experiment
description: Start or continue an experiment in the person's Experiments folder, whatever folder the session is in. Invoked by hand only, as /experiment followed by the idea.
disable-model-invocation: true
---

# Experiment

The person wants to try out an idea as an experiment. Experiments always live in the
Experiments folder, even when the session started somewhere else.

## Find the folder

1. Run `printenv WORK_HOME`. The Experiments folder is `$WORK_HOME/Experiments`.
2. If `WORK_HOME` is empty, or that folder doesn't exist, stop and tell the person. Don't
   guess a path.
3. Read `$WORK_HOME/CLAUDE.md` and `$WORK_HOME/Experiments/CLAUDE.md` and follow them. They
   hold the rules; this skill only gets the experiment set up.

## Start or continue

- Each experiment is its own subfolder of Experiments. List the existing ones first.
- If the idea matches an existing experiment, ask whether to continue that one. If so, read
  its `CLAUDE.md` or `AGENTS.md` and its notes before doing anything else.
- For a new one, propose a short folder name in the style of the existing ones (words joined
  by hyphens, such as `DB-explorer`) and agree it with the person. Then create the folder,
  run `git init` in it, and add a `CLAUDE.md` with what the experiment is trying to find out.
  Commit that as the first commit.

## While working

- Every file for the experiment goes in its folder. Work from that folder (change into it)
  rather than from wherever the session started, and don't touch the starting folder.
- Commit often, in small steps, inside the experiment's repository.
- Never add a remote or push. These repositories stay local.
- Keep the experiment's `CLAUDE.md` current with what was learnt and any decisions the person
  made, so a later session can pick it up.
