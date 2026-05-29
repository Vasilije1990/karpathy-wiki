---
title: Source Note - A Recipe for Training Neural Networks
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - training-nn-recipe
tags:
  - source-note
  - training
  - neural-networks
  - education
aliases:
  - A Recipe for Training Neural Networks
related:
  - ../concepts/neural-networks.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - A Recipe for Training Neural Networks

## Source

- Source ID: `training-nn-recipe`
- URL: https://karpathy.github.io/2019/04/25/recipe/
- Kind: essay

## Extracted Headings

- A Recipe for Training Neural Networks
- Apr 25, 2019
- The recipe
- Tips & tricks for this stage:
- A few tips & tricks for this stage:
- . The next best thing to real data is half-fake data - try out more aggressive data augmentation.
- . It rarely ever hurts to use a pretrained network if you can, even if you have enough data.
- . Increase the weight decay penalty.
- . Stop training based on your measured validation loss to catch your model just as it’s about to overfit.
- Andrej Karpathy blog

## Candidate Observations

- These libraries and examples activate the part of our brain that is familiar with standard software - a place where clean APIs and abstractions are often attainable. Requests library to demonstrate:
- . Always use a fixed random seed to guarantee that when you run the code twice you will get the same outcome. This removes a factor of variation and will help keep you sane.
- . When plotting the test loss run the evaluation over the entire (large) test set. Do not just plot test losses over batches and then rely on smoothing them in Tensorboard. We are in pursuit of correctness and are very willing to give up time for staying sane.
- . Verify that your loss starts at the correct loss value. E.g. if you initialize your final layer correctly you should measure on a softmax at initialization. The same default values can be derived for L2 regression, Huber losses, etc.
- . At this stage you will hopefully be underfitting on your dataset because you’re working with a toy model. Try to increase its capacity just a bit. Did your training loss go down as it should?
- Ideally, we are now at a place where we have a large model that is fitting at least the training set. Now it is time to regularize it and gain some validation accuracy by giving up some of the training accuracy. Some tips & tricks:

## Useful Links

- [Andrej Karpathy blog](/)
- [Andrej Karpathy blog](#)
- [Andrej Karpathy blog About](/about/)
- [Some few weeks ago I posted](https://twitter.com/karpathy/status/1013244313327681536?lang=en)
- [Some few weeks ago I posted a tweet on “the most common neural net mistakes”, listing a few common gotchas related to training neural nets. The tweet got quite a bit more engagement than I anticipated (including a webinar](https://www.bigmarker.com/missinglink-ai/PyTorch-Code-to-Unpack-Andrej-Karpathy-s-6-Most-Common-NN-Mistakes)
- [These libraries and examples activate the part of our brain that is familiar with standard software - a place where clean APIs and abstractions are often attainable. Requests](http://docs.python-requests.org/en/master/)
- [That’s cool! A courageous developer has taken the burden of understanding query strings, urls, GET/POST requests, HTTP connections, and so on from you and largely hidden the complexity behind a few lines of code. This is what we are familiar with and expect. Unfortunately, neural nets are nothing like that. They are not “off-the-shelf” technology the second you deviate slightly from training an ImageNet classifier. I’ve tried to make this point in my post “Yes you should understand backprop”](https://medium.com/@karpathy/yes-you-should-understand-backprop-e2f06eab496b)
- [. In the early stages of setting baselines I like to use Adam with a learning rate of 3e-4](https://twitter.com/karpathy/status/801621764144971776?lang=en)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
