---
title: Source Note - neuraltalk2 README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - neuraltalk2-readme
tags:
  - source-note
  - project
  - computer-vision
  - neural-networks
aliases:
  - neuraltalk2 README
related:
  - ../concepts/neural-networks.md
  - ../projects/cs231n.md
confidence: medium
---

# Source Note - neuraltalk2 README

## Source

- Source ID: `neuraltalk2-readme`
- URL: https://raw.githubusercontent.com/karpathy/neuraltalk2/master/README.md
- Kind: github-readme

## Extracted Headings

- NeuralTalk2
- Requirements
- For evaluation only
- For training
- I just want to caption images
- I'd like to train my own network on MS COCO
- I'd like to train on my own data
- I'd like to distribute my GPU trained checkpoints for CPU
- License
- Acknowledgements

## Candidate Observations

- This current code (and the pretrained model) gets ~0.9 CIDEr, which would place it around spot #8 on the [codalab leaderboard](https://competitions.codalab.org/competitions/3221#results). I will submit the actual result soon.
- You can find a few more example results on the [demo page](http://cs.stanford.edu/people/karpathy/neuraltalk2/demo.html). These results will improve a bit more once the last few bells and whistles are in place (e.g. beam search, ensembling, reranking).
- There's also a [fun video](https://vimeo.com/146492001) by [@kcimc](https://twitter.com/kcimc), where he runs a neuraltalk2 pretrained model in real time on his laptop during a walk in Amsterdam.
- This code is written in Lua and requires [Torch](http://torch.ch/). If you're on Ubuntu, installing Torch in your home directory may look something like:
- $ curl -s https://raw.githubusercontent.com/torch/ezinstall/master/install-deps | bash
- $ git clone https://github.com/torch/distro.git ~/torch --recursive

## Useful Links

- [released the image captioning model](https://research.googleblog.com/2016/09/show-and-tell-image-captioning-open.html)
- [im2txt](https://github.com/tensorflow/models/tree/master/im2txt/im2txt)
- [NeuralTalk](https://github.com/karpathy/neuraltalk)
- [codalab leaderboard](https://competitions.codalab.org/competitions/3221#results)
- [teaser results](https://raw.github.com/karpathy/neuraltalk2/master/vis/teaser.jpeg)
- [demo page](http://cs.stanford.edu/people/karpathy/neuraltalk2/demo.html)
- [fun video](https://vimeo.com/146492001)
- [@kcimc](https://twitter.com/kcimc)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
