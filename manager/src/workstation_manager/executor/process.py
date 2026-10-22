"""Run a command so it shows live in the terminal while every byte is also captured."""

import fcntl
import os
import pty
import select
import subprocess
import sys
import termios
import tty
from pathlib import Path
from typing import BinaryIO


def run(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    """Returns the exit code; negative when killed by a signal."""
    if sys.stdin.isatty() and sys.stdout.isatty():
        return _run_in_pty(argv, cwd, env, output)
    return _run_with_pipe(argv, cwd, env, output)


def _run_with_pipe(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    process = subprocess.Popen(
        argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    assert process.stdout
    while chunk := process.stdout.read1(4096):
        _emit(chunk, output)
    return process.wait()


def _run_in_pty(argv: list[str], cwd: Path, env: dict[str, str], output: BinaryIO) -> int:
    """A pseudo-terminal keeps colours, progress bars and password prompts working."""
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
    try:
        sources = [master, stdin]
        while True:
            readable, _, _ = select.select(sources, [], [])
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
                if typed:
                    os.write(master, typed)
                else:
                    sources.remove(stdin)
    finally:
        termios.tcsetattr(stdin, termios.TCSADRAIN, saved)
        os.close(master)
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status)


def _emit(chunk: bytes, output: BinaryIO) -> None:
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
    output.write(chunk)
    output.flush()
