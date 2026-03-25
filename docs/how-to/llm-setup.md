# LLM Setup Guide

A-Proxy requires an LLM backend for persona conversations, attribute extraction, and structured generation. This guide covers setting up a **local model** (recommended) as well as using **HPC clusters** for larger models.

## Option 1: Local Model with Ollama (Recommended)

[Ollama](https://ollama.com) is the easiest way to run a local LLM. No API keys, no cloud costs, no account required.

### Install Ollama

=== "Windows"

    Download and install from [ollama.com](https://ollama.com), or use winget:
    ```powershell
    winget install Ollama.Ollama
    ```

    Ollama runs as a background service (system tray icon).

    **Optional — store models on a different drive:**

    If your C: drive is low on space, set the model storage location before pulling any models:
    ```powershell
    [System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', 'D:\Ollama\models', 'User')
    ```
    Restart Ollama after setting this.

=== "macOS"

    Download and install from [ollama.com](https://ollama.com), or use Homebrew:
    ```bash
    brew install ollama
    ```

=== "Linux"

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

### Pull a Model

We recommend **Qwen 2.5 7B** — it's capable, fast, and runs well on most machines with 8GB+ RAM:

```bash
ollama pull qwen2.5:7b
```

This downloads approximately 4.7 GB.

**Other model options:**

| Model | Size | RAM Needed | Best For |
|-------|------|-----------|----------|
| `qwen2.5:7b` | 4.7 GB | 8 GB+ | General use (recommended) |
| `qwen2.5:3b` | 2.0 GB | 4 GB+ | Low-resource machines |
| `qwen2.5:14b` | 9.0 GB | 16 GB+ | Higher quality responses |
| `llama3.1:8b` | 4.7 GB | 8 GB+ | Alternative to Qwen |

### Configure A-Proxy

Edit your `.env` file (copy from `.env.example` if you don't have one):

```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
OPENAI_COMPATIBLE_API_KEY=none
```

### Verify It Works

Start a-proxy and try the agent chat:

```bash
python app.py --port 5002
```

Open http://localhost:5002, log in, select a persona, and start a conversation in the Agent tab.

### Troubleshooting Ollama

**"timed out waiting for server to start"**

Something else may be holding Ollama's port (11434). Check and kill stale processes:

=== "Windows"

    ```powershell
    netstat -ano | findstr 11434
    taskkill /F /IM "ollama.exe"
    taskkill /F /IM "ollama app.exe"
    ```
    Then restart Ollama from the Start menu.

=== "Linux/macOS"

    ```bash
    lsof -i :11434
    killall ollama
    ollama serve
    ```

**VPN interference**

Some VPNs (e.g., Cisco AnyConnect) can interfere with localhost networking. If Ollama won't start while connected to a VPN, disconnect the VPN, restart Ollama, then reconnect.

---

## Option 2: Cloud LLM Providers

If you prefer not to run a local model, you can use a commercial API instead.

### Anthropic (Claude)

```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
# ANTHROPIC_MODEL=claude-sonnet-4-20250514  # optional, this is the default
```

### OpenAI (GPT)

```bash
OPENAI_API_KEY=sk-YOUR_KEY_HERE
# OPENAI_MODEL=gpt-4o-mini  # optional, this is the default
```

If multiple providers are configured, auto-detection priority is: **local > Anthropic > OpenAI**. Set `LLM_PROVIDER` to force a specific one.

---

## Option 3: HPC Cluster with vLLM (Advanced)

If you have access to an HPC cluster with GPUs, you can serve larger models (14B, 72B+) using [vLLM](https://docs.vllm.ai/) and connect a-proxy to it. This section uses Drexel's Picotte cluster as an example, but the approach works on any SLURM-based cluster with NVIDIA GPUs.

### Overview

The setup has three parts:

1. **On the cluster:** Install vLLM, download a model, and run it as a SLURM job
2. **SSH tunnel:** Forward the cluster's vLLM port to your local machine
3. **On your machine:** Point a-proxy at `localhost` via the tunnel

### Cluster Setup (One-Time)

SSH into your cluster and set up a conda environment with vLLM:

```bash
# Load your cluster's Python and CUDA modules (names vary by cluster)
module load python/anaconda3
module load cuda12.3/toolkit/12.3.2   # or whatever CUDA version is available

# Create conda environment
conda create -n vllm python=3.12 -y
conda activate vllm

# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Install vLLM
pip install vllm --no-build-isolation
```

!!! note "vLLM install troubleshooting"
    If `pip install vllm` fails with version mismatch errors (e.g., `expected '0.18.0', but metadata has '0.18.0+cu123'`), this is because vLLM's build system detects CUDA and appends a local version suffix. The fix is to install PyTorch first with the correct CUDA wheels, then install vLLM with `--no-build-isolation`.

Download the model to a shared/large filesystem:

```bash
# Set model cache to a directory with enough space (~18 GB for 7B model)
export HF_HOME=/path/to/your/data/huggingface
mkdir -p $HF_HOME

# Download the model
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-7B-Instruct')"
```

### SLURM Job Script

Create a file like `~/vllm-serve.slurm`:

```bash
#!/bin/bash
#SBATCH --job-name=vllm-server
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

# Load modules (adjust for your cluster)
module load python/anaconda3
module load cuda12.3/toolkit/12.3.2

# Activate environment
source activate vllm

# Set model cache location
export HF_HOME=/path/to/your/data/huggingface

# Print connection info
PORT=8000
echo "============================================"
echo "vLLM server starting on $(hostname):${PORT}"
echo "Connect via SSH tunnel:"
echo "  ssh -L ${PORT}:$(hostname):${PORT} your-cluster"
echo "============================================"

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port ${PORT} \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --dtype float16
```

Adjust `--gres`, `--partition`, and module names to match your cluster. For larger models, increase `--tensor-parallel-size` and request more GPUs.

### Running the Server

**Step 1:** Submit the job:
```bash
sbatch ~/vllm-serve.slurm
```

**Step 2:** Check the output for the GPU node hostname:
```bash
# Wait for the job to start
squeue -u $USER

# Read the hostname from the output
cat ~/vllm-server-*.out | head -5
# Example output: "vLLM server starting on gpu003:8000"
```

**Step 3:** Open an SSH tunnel from your local machine (replace `gpu003` with the actual node):
```bash
ssh -L 8000:gpu003:8000 your-cluster
```

**Step 4:** Configure a-proxy `.env`:
```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:8000/v1
OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-7B-Instruct
OPENAI_COMPATIBLE_API_KEY=none
```

### Managing the Job

```bash
# Check running jobs
squeue -u $USER

# Cancel a job
scancel <JOB_ID>

# View server logs
tail -f ~/vllm-server-*.out
```

### Choosing a Model for Your GPU

| GPU | VRAM | Recommended Model |
|-----|------|-------------------|
| V100 (16 GB) | 16 GB | Qwen2.5-7B-Instruct |
| V100 (32 GB) | 32 GB | Qwen2.5-14B-Instruct |
| A100 (40 GB) | 40 GB | Qwen2.5-32B-Instruct |
| A100 (80 GB) | 80 GB | Qwen2.5-72B-Instruct |
| 2x A100 (80 GB) | 160 GB | Qwen2.5-72B-Instruct (tensor-parallel-size=2) |

### Notes for Drexel Picotte Users

- **VPN required:** You must be connected to Drexel VPN (Cisco AnyConnect) to reach Picotte
- **SSH host:** `picotte001.urcf.drexel.edu`, username is your Drexel ID (e.g., `abc123`)
- **GPU partition:** 12 nodes with 4x NVIDIA V100 each, request via `--partition=gpu --gres=gpu:v100:1`
- **CUDA:** Available as `cuda12.3/toolkit/12.3.2`
- **Storage:** Use your group data directory for model storage (home directories have limited space)

---

## How A-Proxy Connects to the LLM

A-Proxy uses a provider-agnostic LLM client (`utils/llm_client.py`). When you set `OPENAI_COMPATIBLE_URL`, it creates an OpenAI SDK client pointed at your endpoint — whether that's Ollama on localhost, vLLM on an HPC cluster, or any other OpenAI-compatible API.

The model name in your `.env` must match what the server reports:

- **Ollama:** `qwen2.5:7b` (Ollama's naming convention)
- **vLLM:** `Qwen/Qwen2.5-7B-Instruct` (HuggingFace model ID)
