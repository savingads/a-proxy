# Running A-Proxy with vLLM on Drexel Picotte

This guide covers running a-proxy's LLM backend on Drexel's Picotte HPC cluster using vLLM. It automates submitting a SLURM GPU job, establishing an SSH tunnel, and configuring a-proxy to use the remote model.

**Related guides:**

- [LLM Setup Guide](llm-setup.md) -- General LLM configuration (Ollama, cloud APIs, generic HPC)
- [Installation](../getting-started/installation.md) -- Setting up a-proxy itself
- [Picotte Cluster Documentation](https://docs.urcf.drexel.edu/clusters/picotte/) -- Official URCF docs (partitions, policies, software)

## Prerequisites

- **Picotte account** with access to the `gpu` partition (Drexel URCF account)
- **Drexel VPN** (Cisco AnyConnect) connected
- **SSH key** registered on Picotte (`ssh-copy-id` or manual)
- **SSH config** entry for Picotte (see below)
- **One-time cluster setup** completed (conda env + model download)

## SSH Configuration

Add to your `~/.ssh/config` (Windows: `C:\Users\<you>\.ssh\config`):

```
Host picotte
    HostName picotte001.urcf.drexel.edu
    User <your-drexel-id>
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
```

Replace `<your-drexel-id>` with your Drexel username (e.g., `cr625`).

## One-Time Cluster Setup

SSH into Picotte and run the following. This only needs to be done once per user.

### 1. Create the conda environment

```bash
ssh picotte

module load python/anaconda3
module load cuda12.3/toolkit/12.3.2

conda create -n vllm python=3.12 -y
source activate vllm

pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install vllm --no-build-isolation
```

### 2. Download the model

Store the model in your group's shared directory so all members can reuse it. On Picotte, each research group has shared storage (e.g., `~/data` may symlink to `/ifs/groups/<your-group>/`). Home directories have limited space, so use group storage for large model files.

```bash
# Point HF_HOME to your group's shared storage (at least 20 GB free)
export HF_HOME=~/data/huggingface
mkdir -p $HF_HOME
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-7B-Instruct')"
```

If another group member has already downloaded the model, you can skip this step -- just point `HF_HOME` to the same path. Check with your group or ask URCF support if you're unsure where your group storage is.

### 3. Install the SLURM job script

```bash
cat > ~/vllm-serve.slurm << 'EOF'
#!/bin/bash
#SBATCH --job-name=vllm-server
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

module load python/anaconda3
module load cuda12.3/toolkit/12.3.2

source activate vllm

export HF_HOME=~/data/huggingface

PORT=8000
echo "============================================"
echo "vLLM server starting on $(hostname):${PORT}"
echo "From your local machine, open an SSH tunnel:"
echo "  ssh -L ${PORT}:$(hostname):${PORT} picotte -N"
echo "============================================"

python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port ${PORT} \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --dtype float16
EOF
```

## Using the Automation Script

The `picotte_vllm.py` script in the project root automates the full workflow: submitting the SLURM job, waiting for vLLM to be ready, opening the SSH tunnel, and optionally updating your `.env`.

### Quick start

```bash
# From the a-proxy project directory, with venv activated:
python picotte_vllm.py start
```

This will:

1. Submit a SLURM job on Picotte
2. Wait for vLLM to load the model and become ready
3. Open an SSH tunnel from `localhost:8000` to the GPU node
4. Update your `.env` to use the Picotte backend

### Other commands

```bash
python picotte_vllm.py status    # Check if a vLLM job is running
python picotte_vllm.py stop      # Cancel the SLURM job and close the tunnel
python picotte_vllm.py logs      # Tail the vLLM server logs
```

### Using a different Picotte account

The script defaults to the SSH host alias `picotte` (configured in `~/.ssh/config`). If your SSH config uses a different host name or you want to use a different account:

```bash
python picotte_vllm.py start --ssh-host myhost
```

Or set the environment variable:

```bash
export PICOTTE_SSH_HOST=myhost
```

The script reads whatever SSH config you have for that host, so all you need is a working `ssh <host>` command.

## Manual Workflow

If you prefer to do it by hand:

### 1. Submit the SLURM job

```bash
ssh picotte "sbatch ~/vllm-serve.slurm"
# Output: Submitted batch job 12345678
```

### 2. Wait for the job to start and find the GPU node

```bash
ssh picotte "squeue -u \$USER"
# Look for the NODELIST column, e.g., gpu009
```

### 3. Wait for vLLM to finish loading

The model takes 3-5 minutes to load on a V100. The very first run after submitting a job takes longer (5-8 minutes) because vLLM compiles CUDA kernels; these are cached for subsequent runs on the same node. Check the logs:

```bash
ssh picotte "tail -5 ~/vllm-server-*.out"
# Ready when you see: "Application startup complete"
```

### 4. Open an SSH tunnel

```bash
ssh -L 8000:gpu009:8000 picotte -N
```

Replace `gpu009` with the actual node from step 2. The `-N` flag keeps the connection open without a shell.

### 5. Configure a-proxy

Edit `.env`:

```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:8000/v1
OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-7B-Instruct
OPENAI_COMPATIBLE_API_KEY=none
```

### 6. Verify

```bash
curl http://localhost:8000/v1/models
```

You should see `Qwen/Qwen2.5-7B-Instruct` in the response.

## Sharing Within Your Research Group

The model weights in your group's shared storage are group-readable. Any group member can use them without re-downloading. Each user needs their own:

- **SSH key** registered on Picotte
- **conda environment** (conda envs live in the user's home directory and can't be shared)
- **SLURM script** (`~/vllm-serve.slurm` -- copy from above or from another group member)

New group members should follow the [One-Time Cluster Setup](#one-time-cluster-setup) above, but can skip the model download if it's already present in the group's shared `huggingface` directory.

## Cost and Usage

Picotte charges based on **all allocated (reserved) resources for the actual elapsed time** of a job. Two things to understand:

- **Time:** You're charged for elapsed time, not the requested time limit. Cancel early and you pay less.
- **Resources:** You're charged for everything you *reserved*, not what you used. Don't request more GPUs or memory than you need.

For current rates and billing examples, see the [Picotte Usage Rates](https://docs.urcf.drexel.edu/clusters/picotte/usage-rates/) page.

Our SLURM script requests 1 GPU, 8 CPUs, and 48 GB RAM. This is the minimum for serving Qwen2.5-7B -- don't increase these unless you have a specific reason.

**Practical guidance:**

- **Always cancel when done** -- `python picotte_vllm.py stop` or `ssh picotte "scancel <JOB_ID>"`. Idle jobs still burn allocation.
- The default time limit is **4 hours** (`--time=04:00:00`). Adjust in `~/vllm-serve.slurm` if needed.
- Shorter requests get scheduled faster (`PriorityFavorSmall` is enabled).
- Fairshare usage resets monthly.

**Suggested time limits:**

| Session type | `--time` |
|---|---|
| Quick test | `02:00:00` |
| Normal work session | `04:00:00` |
| Extended session | `08:00:00` |

## Startup Time and Performance

vLLM is not instant — expect a warmup period before the server is ready to take requests:

| Scenario | Typical wait | What's happening |
|----------|-------------|------------------|
| First run on a new node | 5-8 minutes | CUDA kernel compilation (Triton attention) + model weight loading |
| Subsequent runs on same node | 3-5 minutes | Kernels cached, only model loading |
| `picotte_vllm.py start` | Handles this automatically | Polls logs and reports progress |

The warmup is dominated by two steps:

1. **CUDA kernel compilation** — vLLM compiles optimized GPU kernels on first use. These are cached in `/local/scratch/` on the GPU node, so subsequent SLURM jobs on the same node skip this step. A different node means recompilation.
2. **Model weight loading** — The Qwen2.5-7B model has 4 safetensor shards (~15 GB total) loaded from the network filesystem into GPU memory.

Other performance notes:

- **V100 (32 GB)** comfortably serves Qwen2.5-7B-Instruct in float16 (~15 GB VRAM), leaving room for KV cache.
- **Flash Attention 2** is not supported on V100 (compute capability 7.0). vLLM automatically falls back to Triton attention, which works correctly but is slightly slower than FA2.
- Inference throughput is roughly **40-50 tokens/s prompt, 5-10 tokens/s generation** on a single V100.

## Troubleshooting

**"Connection refused" on localhost:8000**
- vLLM may still be loading. Check logs: `ssh picotte "tail -5 ~/vllm-server-*.out"`
- The SSH tunnel may have dropped. Re-run the `ssh -L` command.
- Verify the SLURM job is still running: `ssh picotte "squeue -u \$USER"`

**Job stuck in PENDING state**
- GPU nodes may be fully allocated. Check with: `ssh picotte "sinfo -p gpu"`
- Consider using `--time=04:00:00` (shorter jobs get scheduled faster)

**"CUDA out of memory"**
- Another job may be using the same GPU. Picotte nodes have 4x V100 GPUs; SLURM should isolate them, but check with: `ssh picotte "ssh <gpu-node> nvidia-smi"`

**VPN disconnected during session**
- The SSH tunnel will break. The SLURM job keeps running on Picotte.
- Reconnect VPN, check the job is still running (`squeue`), and re-open the tunnel.
