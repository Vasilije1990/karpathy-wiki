---
title: Source Note - micrograd README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - micrograd-readme
tags:
  - source-note
  - project
  - autograd
  - education
aliases:
  - micrograd README
related:
  - ../concepts/neural-networks.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - micrograd README

## Source

- Source ID: `micrograd-readme`
- URL: https://raw.githubusercontent.com/karpathy/micrograd/master/README.md
- Kind: github-readme

## Extracted Headings

- micrograd
- Installation
- Example usage
- Training a neural net
- Tracing / visualization
- Running tests
- License

## Candidate Observations

- Below is a slightly contrived example showing a number of possible supported operations:
- print(f'{g.data:.4f}') # prints 24.7041, the outcome of this forward pass
- print(f'{a.grad:.4f}') # prints 138.8338, i.e. the numerical value of dg/da
- print(f'{b.grad:.4f}') # prints 645.5773, i.e. the numerical value of dg/db

## Useful Links

- [awww](puppy.jpg)
- [2d neuron](moon_mlp.png)
- [2d neuron](gout.svg)
- [PyTorch](https://pytorch.org/)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
