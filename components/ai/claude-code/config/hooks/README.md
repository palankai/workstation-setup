# Claude Code hooks

Hooks wired into `~/.claude/settings.json`. The harness runs these — not Claude —
so they hold even if the agent decides otherwise.

| File | Event | Wired in? |
|---|---|---|
| `block_terraform_mutations.py` | `PreToolUse` (matcher `Bash`) | yes |
| `notification.py` | `Notification` | yes |
| `stop.py` | `Stop` | yes |
| `subagent_stop.py` | `SubagentStop` | yes |
| `pre_tool_use.py` | — | **no** (`.env` + `rm -rf` blocking, currently unused) |
| `post_tool_use.py` | — | **no** |

## Terraform policy

The rule: **Claude reads plans, Csaba applies them.**

| Command | Treatment | Enforced by |
|---|---|---|
| `terraform plan` / `validate` / `show` / `output` | runs, no prompt | `permissions.allow` |
| `terraform init` | prompts first | `permissions.ask` |
| `terraform apply` | blocked | `permissions.deny` **and** the hook |
| `terraform destroy` | blocked | `permissions.deny` **and** the hook |
| `terraform fmt`, `state`, `import`, `taint`, … | normal prompt | — |

Two layers, deliberately. The `deny` rules give a clean refusal on the plain
form; the hook catches everything prefix-matching misses — `cd infra &&
terraform apply`, `terraform -chdir=infra destroy`, `sh -c "terraform apply"`,
the `tf` alias, and `tofu`.

### The hook is broad on purpose

`block_terraform_mutations.py` regex-matches the raw Bash command string. A false
positive costs one retry; a false negative costs real infrastructure. So it also
fires on commands that merely *contain* the phrase without running it:

```
python3 -c 'print("terraform apply")'     # blocked, harmless
echo "next: terraform destroy"            # blocked, harmless
```

This is the intended trade. It does **not** stop the agent documenting these
commands, because the hook only inspects `tool_name == "Bash"`:

- **Write / Edit tools** — pass through untouched. Writing this README, a
  runbook, or a commit message containing `terraform apply` works fine.
- **Chat responses** — not tool calls at all. Handing over commands to run is
  never affected.

The only thing that breaks is piping such text through the *shell* — heredocs,
`sed`, `echo >>`. The workaround, used to write this file: put the content in a
file with the Write tool, or the script in a file and invoke it by name, so the
command line itself stays clean.

### Changing the policy

Blocked subcommands are the `BLOCKED` tuple at the top of
`block_terraform_mutations.py`. Adding one there covers every invocation form;
add a matching `"Bash(terraform <cmd>:*)"` line to `permissions.deny` in
`settings.json` for the clean-refusal path.

To check a change without touching real infrastructure, feed the hook a payload
on stdin and read the exit code — `2` blocks, `0` allows:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"terraform refresh"}}' | ~/.claude/hooks/block_terraform_mutations.py; echo "exit $?"
```

To disable temporarily, remove the `PreToolUse` block from `settings.json`.
`/hooks` in an interactive terminal shows what is currently live.

## What Claude hands over

When infrastructure changes are ready, the agent stops at the plan and gives you
the commands in order, with what the plan should show — so a surprising diff is
obvious before anything is applied:

```bash
terraform -chdir=infrastructure plan -out=tfplan
```

Expect e.g. `2 to add, 0 to change, 0 to destroy`. If the counts differ, stop and
say so. Then:

```bash
terraform -chdir=infrastructure apply tfplan
```

Report the result back — the agent does not assume the state of the
infrastructure until you do.
