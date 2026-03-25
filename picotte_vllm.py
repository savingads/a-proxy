#!/usr/bin/env python3
"""Manage vLLM on Drexel's Picotte HPC cluster for use with a-proxy.

Usage:
    python picotte_vllm.py start    # Submit job, wait for ready, open tunnel, update .env
    python picotte_vllm.py status   # Check if a vLLM job is running
    python picotte_vllm.py stop     # Cancel the job and close the tunnel
    python picotte_vllm.py logs     # Tail the vLLM server logs

Options:
    --ssh-host HOST   SSH host alias (default: picotte, or PICOTTE_SSH_HOST env var)
    --no-env-update   Don't modify the .env file
    --timeout SECS    Max seconds to wait for vLLM to be ready (default: 600)
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_SSH_HOST = os.environ.get("PICOTTE_SSH_HOST", "picotte")
DEFAULT_TIMEOUT = 600
VLLM_PORT = 8000
SLURM_SCRIPT = "~/vllm-serve.slurm"
ENV_FILE = Path(__file__).parent / ".env"

# .env blocks — the script swaps between these two states
OLLAMA_BLOCK = """\
# Local Ollama (for development/testing)
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
OPENAI_COMPATIBLE_API_KEY=none

# Picotte vLLM (uncomment and comment out Ollama lines above)
# Start tunnel: ssh -L 8000:<gpu-node>:8000 picotte -N
# Or use: python picotte_vllm.py start
# OPENAI_COMPATIBLE_URL=http://localhost:8000/v1
# OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-7B-Instruct"""

PICOTTE_BLOCK = """\
# Local Ollama (comment out Picotte lines below to switch back)
# LLM_PROVIDER=openai_compatible
# OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
# OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
# OPENAI_COMPATIBLE_API_KEY=none

# Picotte vLLM (active — managed by picotte_vllm.py)
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:{port}/v1
OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-7B-Instruct
OPENAI_COMPATIBLE_API_KEY=none""".format(port=VLLM_PORT)


def ssh(host, command, timeout=30):
    """Run a command on the remote host via SSH. Returns (stdout, returncode)."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", host, command],
            capture_output=True, text=True, timeout=timeout,
        )
        return (result.stdout or "").strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", 1


def ssh_check(host):
    """Verify SSH connectivity."""
    try:
        out, rc = ssh(host, "echo ok")
        return rc == 0 and "ok" in out
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_running_job(host):
    """Find a running vllm-server SLURM job. Returns (job_id, node) or (None, None)."""
    out, rc = ssh(host, "squeue -u $USER -n vllm-server -h -o '%i %N %T'")
    if rc != 0 or not out.strip():
        return None, None
    for line in out.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "RUNNING":
            return parts[0], parts[1]
        if len(parts) >= 2:
            return parts[0], parts[1] if parts[1] != "(None)" else None
    return None, None


def get_job_log_file(host, job_id):
    """Get the stdout log path for a job."""
    return f"~/vllm-server-{job_id}.out"


def submit_job(host):
    """Submit the vLLM SLURM job. Returns job_id."""
    out, rc = ssh(host, f"sbatch {SLURM_SCRIPT}")
    if rc != 0:
        print(f"Error submitting job: {out}")
        sys.exit(1)
    match = re.search(r"(\d+)", out)
    if not match:
        print(f"Could not parse job ID from: {out}")
        sys.exit(1)
    return match.group(1)


def wait_for_job_running(host, job_id, timeout=120):
    """Wait for a SLURM job to enter RUNNING state. Returns the node name."""
    start = time.time()
    while time.time() - start < timeout:
        out, _ = ssh(host, f"squeue -j {job_id} -h -o '%T %N'")
        if not out.strip():
            print(f"\rJob {job_id} no longer in queue (failed or completed)")
            sys.exit(1)
        parts = out.strip().split()
        state = parts[0]
        node = parts[1] if len(parts) > 1 else None
        if state == "RUNNING" and node:
            return node
        print(f"\rJob {job_id}: {state}... ", end="", flush=True)
        time.sleep(5)
    print(f"\nTimed out waiting for job {job_id} to start")
    sys.exit(1)


def wait_for_vllm_ready(host, job_id, timeout=DEFAULT_TIMEOUT):
    """Wait for vLLM to finish loading and report 'Application startup complete'."""
    log_file = get_job_log_file(host, job_id)
    start = time.time()
    last_status = ""
    err_file = f"~/vllm-server-{job_id}.err"
    while time.time() - start < timeout:
        out, _ = ssh(host, f"tail -3 {log_file} 2>/dev/null")
        err_out, _ = ssh(host, f"tail -5 {err_file} 2>/dev/null")

        # The startup message may appear in either stdout or stderr
        if "Application startup complete" in out or "Application startup complete" in err_out:
            return True

        # Show loading progress from both stdout and stderr
        combined = out + "\n" + err_out
        status = ""
        if "Loading safetensors" in combined:
            match = re.search(r"(\d+)%", combined)
            if match:
                status = f"Loading model weights: {match.group(1)}%"
        elif "Starting to load model" in combined:
            status = "Loading model..."
        elif "Using TRITON_ATTN" in combined or "Using FLASH_ATTN" in combined:
            status = "Compiling CUDA kernels..."
        elif "Starting vLLM API server" in combined:
            status = "Starting API server..."
        elif "Initializing" in combined:
            status = "Initializing engine..."

        if status and status != last_status:
            elapsed = int(time.time() - start)
            print(f"\r[{elapsed}s] {status}            ", end="", flush=True)
            last_status = status

        # Check job hasn't died
        job_out, _ = ssh(host, f"squeue -j {job_id} -h -o '%T'")
        if not job_out.strip():
            print(f"\nJob {job_id} is no longer running. Check logs:")
            print(f"  ssh {host} 'tail -20 {log_file}'")
            sys.exit(1)

        time.sleep(10)

    print(f"\nTimed out after {timeout}s waiting for vLLM to be ready")
    sys.exit(1)


def open_tunnel(host, node, port=VLLM_PORT):
    """Open an SSH tunnel in the background. Returns the subprocess."""
    proc = subprocess.Popen(
        ["ssh", "-L", f"{port}:{node}:{port}", host, "-N", "-o", "ExitOnForwardFailure=yes"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    # Give it a moment to establish or fail
    time.sleep(2)
    if proc.poll() is not None:
        err = proc.stderr.read().decode().strip()
        print(f"SSH tunnel failed: {err}")
        print(f"Is port {port} already in use? Check with: netstat -an | grep {port}")
        sys.exit(1)
    return proc


def close_tunnel(port=VLLM_PORT):
    """Kill any SSH tunnel processes forwarding the given port."""
    # Find and kill ssh processes with the tunnel port
    if sys.platform == "win32":
        # On Windows, find ssh processes with our port in the command line
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ssh.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True,
        )
        for line in result.stdout.strip().splitlines():
            # Get PID from CSV output
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                pid = parts[1].strip('"')
                # Check if this ssh process is our tunnel
                try:
                    cmd_result = subprocess.run(
                        ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/format:list"],
                        capture_output=True, text=True, timeout=5,
                    )
                    if f"-L {port}" in cmd_result.stdout or f"-L{port}" in cmd_result.stdout:
                        subprocess.run(["taskkill", "/F", "/PID", pid],
                                       capture_output=True, timeout=5)
                        print(f"Closed SSH tunnel (PID {pid})")
                except (subprocess.TimeoutExpired, OSError):
                    pass
    else:
        subprocess.run(
            ["pkill", "-f", f"ssh.*-L.*{port}.*-N"],
            capture_output=True,
        )


def update_env_file(target):
    """Swap the LLM config block in .env between Ollama and Picotte.

    target: "picotte" or "ollama"
    """
    if not ENV_FILE.exists():
        print(f"Warning: {ENV_FILE} not found, skipping .env update")
        return

    content = ENV_FILE.read_text()

    if target == "picotte":
        if OLLAMA_BLOCK in content:
            content = content.replace(OLLAMA_BLOCK, PICOTTE_BLOCK)
        elif PICOTTE_BLOCK not in content:
            print("Warning: could not find LLM config block in .env, skipping update")
            return
    else:
        if PICOTTE_BLOCK in content:
            content = content.replace(PICOTTE_BLOCK, OLLAMA_BLOCK)
        elif OLLAMA_BLOCK not in content:
            print("Warning: could not find LLM config block in .env, skipping update")
            return

    ENV_FILE.write_text(content)


def cmd_start(args):
    host = args.ssh_host

    print(f"Connecting to {host}...")
    if not ssh_check(host):
        print(f"Cannot reach {host}. Check your VPN connection and SSH config.")
        sys.exit(1)

    # Check for existing job
    job_id, node = get_running_job(host)
    if job_id and node:
        print(f"Found existing vLLM job {job_id} on {node}")
    elif job_id:
        print(f"Found existing job {job_id} (waiting to start)...")
        node = wait_for_job_running(host, job_id)
        print(f"\rJob {job_id} running on {node}          ")
    else:
        # Submit new job
        print("Submitting SLURM job...")
        job_id = submit_job(host)
        print(f"Job {job_id} submitted. Waiting for a GPU node...")
        node = wait_for_job_running(host, job_id)
        print(f"\rJob {job_id} running on {node}          ")

    # Wait for vLLM to be ready
    print("Waiting for vLLM to load the model...")
    wait_for_vllm_ready(host, job_id, timeout=args.timeout)
    print(f"\rvLLM is ready on {node}:{VLLM_PORT}                    ")

    # Open tunnel
    print(f"Opening SSH tunnel (localhost:{VLLM_PORT} -> {node}:{VLLM_PORT})...")
    tunnel = open_tunnel(host, node)
    print("Tunnel established.")

    # Update .env
    if not args.no_env_update:
        update_env_file("picotte")
        print(f"Updated {ENV_FILE} for Picotte backend.")

    print()
    print("=" * 50)
    print("  vLLM is running and a-proxy is configured.")
    print(f"  Model: Qwen/Qwen2.5-7B-Instruct")
    print(f"  Endpoint: http://localhost:{VLLM_PORT}/v1")
    print(f"  SLURM job: {job_id} on {node}")
    print()
    print("  Start a-proxy:  python app.py --port 5002")
    print()
    print("  Press Ctrl+C to close the tunnel.")
    print("=" * 50)

    # Keep the tunnel alive until Ctrl+C
    try:
        tunnel.wait()
    except KeyboardInterrupt:
        print("\nShutting down tunnel...")
        tunnel.terminate()
        tunnel.wait(timeout=5)

        if not args.no_env_update:
            update_env_file("ollama")
            print(f"Reverted {ENV_FILE} to Ollama backend.")

        print(f"Tunnel closed. SLURM job {job_id} is still running on Picotte.")
        print(f"To cancel it: ssh {host} 'scancel {job_id}'")


def cmd_status(args):
    host = args.ssh_host

    if not ssh_check(host):
        print(f"Cannot reach {host}. Check your VPN and SSH config.")
        sys.exit(1)

    job_id, node = get_running_job(host)
    if not job_id:
        print("No vLLM job running on Picotte.")
        return

    out, _ = ssh(host, f"squeue -j {job_id} -h -o '%T %M %l %N'")
    parts = out.split()
    state = parts[0] if parts else "UNKNOWN"
    elapsed = parts[1] if len(parts) > 1 else "?"
    limit = parts[2] if len(parts) > 2 else "?"
    node_name = parts[3] if len(parts) > 3 else "?"

    print(f"Job {job_id}: {state}")
    print(f"  Node: {node_name}")
    print(f"  Elapsed: {elapsed} / {limit}")

    if state == "RUNNING" and node:
        log_file = get_job_log_file(host, job_id)
        err_file = log_file.replace(".out", ".err")
        out, _ = ssh(host, f"grep -c 'Application startup complete' {log_file} {err_file} 2>/dev/null")
        if "1" in out:
            print(f"  vLLM: ready (serving on {node}:{VLLM_PORT})")
            print(f"  Tunnel command: ssh -L {VLLM_PORT}:{node}:{VLLM_PORT} {host} -N")
        else:
            print("  vLLM: still loading...")


def cmd_stop(args):
    host = args.ssh_host

    # Close local tunnel
    close_tunnel()

    if not ssh_check(host):
        print(f"Cannot reach {host} — tunnel closed locally. Job may still be running.")
        return

    job_id, _ = get_running_job(host)
    if job_id:
        ssh(host, f"scancel {job_id}")
        print(f"Cancelled SLURM job {job_id}")
    else:
        print("No vLLM job found to cancel.")

    if ENV_FILE.exists() and not args.no_env_update:
        update_env_file("ollama")
        print(f"Reverted {ENV_FILE} to Ollama backend.")


def cmd_logs(args):
    host = args.ssh_host

    if not ssh_check(host):
        print(f"Cannot reach {host}.")
        sys.exit(1)

    job_id, _ = get_running_job(host)
    if not job_id:
        print("No vLLM job running. Showing most recent log:")
        out, _ = ssh(host, "ls -t ~/vllm-server-*.out 2>/dev/null | head -1")
        if not out:
            print("No log files found.")
            return
        log_file = out
    else:
        log_file = get_job_log_file(host, job_id)

    print(f"--- {log_file} ---")
    out, _ = ssh(host, f"tail -30 {log_file}")
    print(out)

    err_file = log_file.replace(".out", ".err")
    err_out, _ = ssh(host, f"tail -10 {err_file} 2>/dev/null")
    if err_out.strip():
        print(f"\n--- {err_file} ---")
        print(err_out)


def main():
    parser = argparse.ArgumentParser(
        description="Manage vLLM on Picotte HPC for a-proxy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--ssh-host", default=DEFAULT_SSH_HOST,
        help=f"SSH host alias for Picotte (default: {DEFAULT_SSH_HOST})",
    )
    parser.add_argument(
        "--no-env-update", action="store_true",
        help="Don't modify the .env file",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"Seconds to wait for vLLM to be ready (default: {DEFAULT_TIMEOUT})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("start", help="Submit job, wait for ready, open tunnel")
    subparsers.add_parser("status", help="Check vLLM job status")
    subparsers.add_parser("stop", help="Cancel job and close tunnel")
    subparsers.add_parser("logs", help="Show vLLM server logs")

    args = parser.parse_args()

    commands = {
        "start": cmd_start,
        "status": cmd_status,
        "stop": cmd_stop,
        "logs": cmd_logs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
