# Source: micrograd README

source_id: micrograd-readme
title: micrograd README
url: https://raw.githubusercontent.com/karpathy/micrograd/master/README.md
kind: github-readme
status: captured-as-excerpt
captured: 2026-05-28

## Extracted Headings

- micrograd
- Installation
- Example usage
- Training a neural net
- Tracing / visualization
- Running tests
- License

## Excerpt

A tiny Autograd engine (with a bite! :)). Implements backpropagation (reverse-mode autodiff) over a dynamically built DAG and a small neural networks library on top of it with a PyTorch-like API. Both are tiny, with about 100 and 50 lines of code respectively. The DAG only operates over scalar values, so e.g. we chop up each neuron into all of its individual tiny adds and multiplies. However, this is enough to build up entire deep neural nets doing binary classification, as the demo notebook shows. Potentially useful for educational purposes.

```bash

pip install micrograd

```

Below is a slightly contrived example showing a number of possible supported operations:

```python

from micrograd.engine import Value

a = Value(-4.0)

b = Value(2.0)

c = a + b

d = a * b + b**3

c += c + 1

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
