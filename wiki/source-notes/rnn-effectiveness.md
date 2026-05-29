---
title: Source Note - The Unreasonable Effectiveness of Recurrent Neural Networks
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - rnn-effectiveness
tags:
  - source-note
  - rnn
  - neural-networks
  - education
aliases:
  - The Unreasonable Effectiveness of Recurrent Neural Networks
related:
  - ../concepts/neural-networks.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - The Unreasonable Effectiveness of Recurrent Neural Networks

## Source

- Source ID: `rnn-effectiveness`
- URL: https://karpathy.github.io/2015/05/21/rnn-effectiveness/
- Kind: essay

## Extracted Headings

- The Unreasonable Effectiveness of Recurrent Neural Networks
- May 21, 2015
- We’ll train RNNs to generate text character by character and ponder the question “how is that even possible?”
- Recurrent Neural Networks
- If training vanilla neural nets is optimization over functions, training recurrent nets is optimization over programs.
- Character-Level Language Models
- Fun with RNNs
- Paul Graham generator
- looks like we’ve reached an infinite loop about startups.
- Shakespeare

## Candidate Observations

- The Unreasonable Effectiveness of Recurrent Neural Networks
- We’ll train RNNs to generate text character by character and ponder the question “how is that even possible?”
- If training vanilla neural nets is optimization over functions, training recurrent nets is optimization over programs.
- The takeaway is that even if your data is not in form of sequences, you can still formulate and train powerful models that learn to process it sequentially. You’re learning stateful programs that process your fixed-sized data.
- The RNN class has some internal state that it gets to update every time is called. In the simplest case this state consists of a single vector . Here is an implementation of the step function in a Vanilla RNN:
- . RNNs are neural networks and everything works monotonically better (if done right) if you put on your deep learning hat and start stacking models up like pancakes. For instance, we can form a 2-layer recurrent network as follows:

## Useful Links

- [Andrej Karpathy blog](/)
- [Andrej Karpathy blog](#)
- [Andrej Karpathy blog About](/about/)
- [There’s something magical about Recurrent Neural Networks (RNNs). I still remember when I trained my first recurrent network for Image Captioning](http://cs.stanford.edu/people/karpathy/deepimagesent/)
- [By the way, together with this post I am also releasing code on Github](https://github.com/karpathy/char-rnn)
- [As you might expect, the sequence regime of operation is much more powerful compared to fixed networks that are doomed from the get-go by a fixed number of computational steps, and hence also much more appealing for those of us who aspire to build more intelligent systems. Moreover, as we’ll see in a bit, RNNs combine the input vector with their state vector with a fixed (but learned) function to produce a new state vector. This can in programming terms be interpreted as running a fixed program with certain inputs and some internal variables. Viewed this way, RNNs essentially describe programs. In fact, it is known that RNNs are Turing-Complete](http://binds.cs.umass.edu/papers/1995_Siegelmann_Science.pdf)
- [. You might be thinking that having sequences as inputs or outputs could be relatively rare, but an important point to realize is that even if your inputs/outputs are fixed vectors, it is still possible to use this powerful formalism to them in a sequential manner. For instance, the figure below shows results from two very nice papers from DeepMind](http://deepmind.com/)
- [. You might be thinking that having sequences as inputs or outputs could be relatively rare, but an important point to realize is that even if your inputs/outputs are fixed vectors, it is still possible to use this powerful formalism to them in a sequential manner. For instance, the figure below shows results from two very nice papers from DeepMind. On the left, an algorithm learns a recurrent network policy that steers its attention around an image; In particular, it learns to read out house numbers from left to right (Ba et al.](http://arxiv.org/abs/1412.7755)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
