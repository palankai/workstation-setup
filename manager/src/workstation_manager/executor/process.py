"""Run a command so it shows live in the terminal while every byte is also captured."""

import fcntl
import os
import pty
import select
import signal
import subprocess
import sys
import termios
import time
import tty
from pathlib import Path
from typing import BinaryIO

CTRL_C = b"\x03"
# After Ctrl-C: SIGINT goes to the step at once, then SIGTERM and SIGKILL if it's still running;
# every further Ctrl-C sends the next one straight away
ESCALATION = ((2.0, signal.SIGTERM), (4.0, signal.SIGKILL))
NOTICES = {
    signal.SIGINT: "Interrupting; Ctrl-C again to terminate",
    signal.SIGTERM: "Terminating; Ctrl-C again to kill",
    signal.SIGKILL: "Killed",
}


def run(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    """Returns the exit code; negative when killed by a signal.

    Raises KeyboardInterrupt once the command is gone if the user pressed Ctrl-C.
    """
    if sys.stdin.isatty() and sys.stdout.isatty():
        return _run_in_pty(argv, cwd, env, output)
    return _run_with_pipe(argv, cwd, env, output)


def _run_with_pipe(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    process = subprocess.Popen(
        argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    assert process.stdout
    try:
        while chunk := process.stdout.read1(4096):
            _emit(chunk, output)
    except KeyboardInterrupt:
        process.kill()
        process.wait()
        raise
    return process.wait()


def _run_in_pty(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    """A pseudo-terminal keeps colours, progress bars and password prompts working.

    The terminal is raw meanwhile, so Ctrl-C arrives here as a byte rather than a signal.
    """
    stdin = sys.stdin.fileno()
    pid, master = pty.fork()
    if pid == 0:
        try:
            os.chdir(cwd)
            os.execvpe(argv[0], argv, env)
        except OSError as e:
            os.write(2, f"{argv[0]}: {e}\n".encode())
        os._exit(127)

    size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
    fcntl.ioctl(master, termios.TIOCSWINSZ, size)
    saved = termios.tcgetattr(stdin)
    tty.setraw(stdin)
    interrupted_at: float | None = None
    escalation = list(ESCALATION)
    try:
        sources = [master, stdin]
        while True:
            timeout = None
            if interrupted_at is not None:
                if escalation and time.monotonic() - interrupted_at >= escalation[0][0]:
                    _interrupt(pid, escalation.pop(0)[1], output)
                if not escalation:
                    break
                timeout = 0.2
            readable, _, _ = select.select(sources, [], [], timeout)
            if master in readable:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                _emit(chunk, output)
            if stdin in readable:
                typed = os.read(stdin, 1024)
                if not typed:
                    sources.remove(stdin)
                    continue
                os.write(master, typed)
                for _ in range(typed.count(CTRL_C)):
                    if interrupted_at is None:
                        interrupted_at = time.monotonic()
                        _interrupt(pid, signal.SIGINT, output)
                    elif escalation:
                        _interrupt(pid, escalation.pop(0)[1], output)
    finally:
        termios.tcsetattr(stdin, termios.TCSADRAIN, saved)
        os.close(master)
    if interrupted_at is not None:
        _signal(pid, signal.SIGKILL)
    _, status = os.waitpid(pid, 0)
    if interrupted_at is not None:
        raise KeyboardInterrupt
    return os.waitstatus_to_exitcode(status)


def _interrupt(pid: int, sig: signal.Signals, output: BinaryIO) -> None:
    _emit(f"\r\n[ws] {NOTICES[sig]}\r\n".encode(), output)
    _signal(pid, sig)


def _signal(pid: int, sig: signal.Signals) -> None:
    """The step is a session leader, so this reaches everything it started."""
    try:
        os.killpg(pid, sig)
    except (ProcessLookupError, PermissionError):
        # Already gone; macOS answers EPERM when only the unreaped step itself is left
        pass


def _emit(chunk: bytes, output: BinaryIO) -> None:
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
    output.write(chunk)
    output.flush()
