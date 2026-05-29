# Source: llm.c README

source_id: llm-c-readme
title: llm.c README
url: https://raw.githubusercontent.com/karpathy/llm.c/master/README.md
kind: github-readme
status: captured-as-excerpt
captured: 2026-05-28

## Extracted Headings

- llm.c
- quick start
- quick start (1 GPU, fp32 only)
- quick start (CPU)
- datasets
- test
- fp32 test (cudnn not supported)
- mixed precision cudnn test
- tutorial
- multi-GPU training
- multi-node training
- experiments / sweeps

## Excerpt

LLMs in simple, pure C/CUDA with no need for 245MB of PyTorch or 107MB of cPython. Current focus is on pretraining, in particular reproducing the [GPT-2](https://github.com/openai/gpt-2) and [GPT-3](https://arxiv.org/abs/2005.14165) miniseries, along with a parallel PyTorch reference implementation in [train_gpt2.py](train_gpt2.py). You'll recognize this file as a slightly tweaked [nanoGPT](https://github.com/karpathy/nanoGPT), an earlier project of mine. Currently, llm.c is a bit faster than PyTorch Nightly (by about 7%). In addition to the bleeding edge mainline code in [train_gpt2.cu](train_gpt2.cu), we have a simple reference CPU fp32 implementation in ~1,000 lines of clean code in one file [train_gpt2.c](train_gpt2.c). I'd like this repo to only maintain C and CUDA code. Ports to other languages or repos are very welcome, but should be done in separate repos, and I am happy to link to them below in the "notable forks" section. Developer coordination happens in the [Discussions](https://github.com/karpathy/llm.c/discussions) and on Discord, either the `#llmc` channel on the [Zero to Hero](https://discord.gg/3zy8kqD9Cp) channel, or on `#llmdotc` on [GPU MODE](https://discord.gg/gpumode) Discord.

The best introduction to the llm.c repo today is reproducing the GPT-2 (124M) model. [Discussion #481](https://github.com/karpathy/llm.c/discussions/481) steps through this in detail. We can reproduce other models from the GPT-2 and GPT-3 series in both llm.c and in the parallel implementation of PyTorch. Have a look at the [scripts README](scripts/README.md).

debugging tip: when you run the `make` command to build the binary, modify it by replacing `-O3` with `-g` so you can step through the code in your favorite IDE (e.g. vscode).

If you won't be training on multiple nodes, aren't interested in mixed precision, and are interested in learning CUDA, the fp32 (legacy) files might be of interest to you. These are files that were "checkpointed" early in the history of llm.c and frozen in time. They are simpler, more portable, and possibly easier to understand. Run the 1 GPU, fp32 code like this:

```bash

chmod u+x ./dev/download_starter_pack.sh

./dev/download_starter_pack.sh

make train_gpt2fp32cu

./train_gpt2fp32cu

```

The download_starter_pack.sh script is a quick & easy way to get started and it downloads a bunch of .bin files that help get you off the ground. These contain: 1) the GPT-2 124M model saved in fp32, in bfloat16, 2) a "debug state" used in unit testing (a small batch of data, and target activations and gradients), 3) the GPT-2 tokenizer, and 3) the tokenized [tinyshakespeare](https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt) dataset. Alternatively, instead of running the .sh script, you can re-create these artifacts manually as follows:

```bash

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
