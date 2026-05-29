---
title: Source Note - Deep Reinforcement Learning: Pong from Pixels
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - deep-rl-pong
tags:
  - source-note
  - reinforcement-learning
  - neural-networks
  - education
aliases:
  - Deep Reinforcement Learning: Pong from Pixels
related:
  - ../concepts/neural-networks.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - Deep Reinforcement Learning: Pong from Pixels

## Source

- Source ID: `deep-rl-pong`
- URL: https://karpathy.github.io/2016/05/31/rl/
- Kind: essay

## Extracted Headings

- Deep Reinforcement Learning: Pong from Pixels
- May 31, 2016
- Compute (the obvious one: Moore’s Law, GPUs, ASICs),
- Data (in a nice form, not just out there somewhere on the internet - e.g. ImageNet),
- Algorithms (research and ideas, e.g. backprop, CNN, LSTM), and
- Infrastructure (software under you - Linux, TCP/IP, Git, ROS, PR2, AWS, AMT, TensorFlow, etc.).
- Pong from pixels
- Policy Gradients: Run a policy for a while. See what actions led to high rewards. Increase their probability.
- What isn’t happening
- Non-differentiable computation in Neural Networks

## Candidate Observations

- It’s interesting to reflect on the nature of recent progress in RL. I broadly like to think about four separate factors that hold back AI:
- Compute (the obvious one: Moore’s Law, GPUs, ASICs),
- Data (in a nice form, not just out there somewhere on the internet - e.g. ImageNet),
- Algorithms (research and ideas, e.g. backprop, CNN, LSTM), and
- Infrastructure (software under you - Linux, TCP/IP, Git, ROS, PR2, AWS, AMT, TensorFlow, etc.).
- and to make things concrete here is how you might implement this policy network in Python/numpy. Suppose we’re given a vector that holds the (preprocessed) pixel information. We would compute:

## Useful Links

- [Andrej Karpathy blog](/)
- [Andrej Karpathy blog](#)
- [Andrej Karpathy blog About](/about/)
- [This is a long overdue blog post on Reinforcement Learning (RL). RL is hot! You may have noticed that computers can now automatically learn to play ATARI games](http://www.nature.com/nature/journal/v518/n7540/abs/nature14236.html)
- [This is a long overdue blog post on Reinforcement Learning (RL). RL is hot! You may have noticed that computers can now automatically learn to play ATARI games (from raw game pixels!), they are beating world champions at Go](http://googleresearch.blogspot.com/2016/01/alphago-mastering-ancient-game-of-go.html)
- [This is a long overdue blog post on Reinforcement Learning (RL). RL is hot! You may have noticed that computers can now automatically learn to play ATARI games (from raw game pixels!), they are beating world champions at Go, simulated quadrupeds are learning to run and leap](https://www.cs.ubc.ca/~van/papers/2016-TOG-deepRL/index.html)
- [This is a long overdue blog post on Reinforcement Learning (RL). RL is hot! You may have noticed that computers can now automatically learn to play ATARI games (from raw game pixels!), they are beating world champions at Go, simulated quadrupeds are learning to run and leap, and robots are learning how to perform complex manipulation tasks](http://www.bloomberg.com/features/2015-preschool-for-robots/)
- [This is a long overdue blog post on Reinforcement Learning (RL). RL is hot! You may have noticed that computers can now automatically learn to play ATARI games (from raw game pixels!), they are beating world champions at Go, simulated quadrupeds are learning to run and leap, and robots are learning how to perform complex manipulation tasks that defy explicit programming. It turns out that all of these advances fall under the umbrella of RL research. I also became interested in RL myself over the last ~year: I worked through Richard Sutton’s book](https://webdocs.cs.ualberta.ca/~sutton/book/the-book.html)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
