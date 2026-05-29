# Source: neuraltalk2 README

source_id: neuraltalk2-readme
title: neuraltalk2 README
url: https://raw.githubusercontent.com/karpathy/neuraltalk2/master/README.md
kind: github-readme
status: captured-as-excerpt
captured: 2026-05-28

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

## Excerpt

**Update (September 22, 2016)**: The Google Brain team has [released the image captioning model](https://research.googleblog.com/2016/09/show-and-tell-image-captioning-open.html) of Vinyals et al. (2015). The core model is very similar to NeuralTalk2 (a CNN followed by RNN), but the Google release should work significantly better as a result of better CNN, some tricks, and more careful engineering. Find it under [im2txt](https://github.com/tensorflow/models/tree/master/im2txt/im2txt) repo in tensorflow. I'll leave this code base up for educational purposes and as a Torch implementation.

Recurrent Neural Network captions your images. Now much faster and better than the original [NeuralTalk](https://github.com/karpathy/neuraltalk). Compared to the original NeuralTalk this implementation is **batched, uses Torch, runs on a GPU, and supports CNN finetuning**. All of these together result in quite a large increase in training speed for the Language Model (~100x), but overall not as much because we also have to forward a VGGNet. However, overall very good models can be trained in 2-3 days, and they show a much better performance.

This is an early code release that works great but is slightly hastily released and probably requires some code reading of inline comments (which I tried to be quite good with in general). I will be improving it over time but wanted to push the code out there because I promised it to too many people.

This current code (and the pretrained model) gets ~0.9 CIDEr, which would place it around spot #8 on the [codalab leaderboard](https://competitions.codalab.org/competitions/3221#results). I will submit the actual result soon.

You can find a few more example results on the [demo page](http://cs.stanford.edu/people/karpathy/neuraltalk2/demo.html). These results will improve a bit more once the last few bells and whistles are in place (e.g. beam search, ensembling, reranking).

There's also a [fun video](https://vimeo.com/146492001) by [@kcimc](https://twitter.com/kcimc), where he runs a neuraltalk2 pretrained model in real time on his laptop during a walk in Amsterdam.

This code is written in Lua and requires [Torch](http://torch.ch/). If you're on Ubuntu, installing Torch in your home directory may look something like:

```bash

$ curl -s https://raw.githubusercontent.com/torch/ezinstall/master/install-deps | bash

$ git clone https://github.com/torch/distro.git ~/torch --recursive

$ cd ~/torch;

$ ./install.sh # and enter "yes" at the end to modify your bashrc

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
