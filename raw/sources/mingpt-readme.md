# Source: minGPT README

source_id: mingpt-readme
title: minGPT README
url: https://raw.githubusercontent.com/karpathy/minGPT/master/README.md
kind: github-readme
status: captured-as-excerpt
captured: 2026-05-28

## Extracted Headings

- minGPT
- Library Installation
- Usage
- your subclass of torch.utils.data.Dataset that emits example
- torch LongTensor of lengths up to 1024, with integers from [0,50257)
- Unit tests
- todos
- References
- Improving Language Understanding by Generative Pre-Training (GPT-1)
- Language Models are Unsupervised Multitask Learners (GPT-2)
- Language Models are Few-Shot Learners (GPT-3)
- Generative Pretraining from Pixels (Image GPT)

## Excerpt

A PyTorch re-implementation of [GPT](https://github.com/openai/gpt-2), both training and inference. minGPT tries to be small, clean, interpretable and educational, as most of the currently available GPT model implementations can a bit sprawling. GPT is not a complicated model and this implementation is appropriately about 300 lines of code (see [mingpt/model.py](mingpt/model.py)). All that's going on is that a sequence of indices feeds into a [Transformer](https://arxiv.org/abs/1706.03762), and a probability distribution over the next index in the sequence comes out. The majority of the complexity is just being clever with batching (both across examples and over sequence length) for efficiency.

**note (Jan 2023)**: though I may continue to accept and change some details, minGPT is in a semi-archived state. For more recent developments see my rewrite [nanoGPT](https://github.com/karpathy/nanoGPT). Basically, minGPT became referenced across a wide variety of places (notebooks, blogs, courses, books, etc.) which made me less willing to make the bigger changes I wanted to make to move the code forward. I also wanted to change the direction a bit, from a sole focus on education to something that is still simple and hackable but has teeth (reproduces medium-sized industry benchmarks, accepts some tradeoffs to gain runtime efficiency, etc).

The minGPT library is three files: [mingpt/model.py](mingpt/model.py) contains the actual Transformer model definition, [mingpt/bpe.py](mingpt/bpe.py) contains a mildly refactored Byte Pair Encoder that translates between text and sequences of integers exactly like OpenAI did in GPT, [mingpt/trainer.py](mingpt/trainer.py) is (GPT-independent) PyTorch boilerplate code that trains the model. Then there are a number of demos and projects that use the library in the `projects` folder:

- `projects/adder` trains a GPT from scratch to add numbers (inspired by the addition section in the GPT-3 paper)

- `projects/chargpt` trains a GPT to be a character-level language model on some input text file

- `demo.ipynb` shows a minimal usage of the `GPT` and `Trainer` in a notebook format on a simple sorting example

- `generate.ipynb` shows how one can load a pretrained GPT2 and generate text given some prompt

If you want to `import mingpt` into your project:

```

git clone https://github.com/karpathy/minGPT.git

cd minGPT

pip install -e .

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
