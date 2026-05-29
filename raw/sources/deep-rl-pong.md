# Source: Deep Reinforcement Learning: Pong from Pixels

source_id: deep-rl-pong
title: Deep Reinforcement Learning: Pong from Pixels
url: https://karpathy.github.io/2016/05/31/rl/
kind: essay
status: captured-as-excerpt
captured: 2026-05-28

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
- Conclusions
- Andrej Karpathy blog

## Excerpt

Deep Reinforcement Learning: Pong from Pixels

It’s interesting to reflect on the nature of recent progress in RL. I broadly like to think about four separate factors that hold back AI:

Compute (the obvious one: Moore’s Law, GPUs, ASICs),

Data (in a nice form, not just out there somewhere on the internet - e.g. ImageNet),

Algorithms (research and ideas, e.g. backprop, CNN, LSTM), and

Infrastructure (software under you - Linux, TCP/IP, Git, ROS, PR2, AWS, AMT, TensorFlow, etc.).

As we go through the solution keep in mind that we’ll try to make very few assumptions about Pong because we secretly don’t really care about Pong; We care about complex, high-dimensional problems like robot manipulation, assembly and navigation. Pong is just a fun toy test case, something we play with while we figure out how to write very general AI systems that can one day do arbitrary useful tasks.

. First, we’re going to define a that implements our player (or “agent”). This network will take the state of the game and decide what we should do (move UP or DOWN). As our favorite simple block of compute we’ll use a 2-layer neural network that takes the raw image pixels (100,800 numbers total (210*160*3)), and produces a single number indicating the probability of going UP. Note that it is standard to use a policy, meaning that we only produce a of moving UP. Every iteration we will sample from this distribution (i.e. toss a biased coin) to get the actual move. The reason for this will become more clear once we talk about training.

and to make things concrete here is how you might implement this policy network in Python/numpy. Suppose we’re given a vector that holds the (preprocessed) pixel information. We would compute:

where in this snippet and are two matrices that we initialize randomly. We’re not using biases because meh. Notice that we use the non-linearity at the end, which squashes the output probability to the range [0,1]. Intuitively, the neurons in the hidden layer (which have their weights arranged along the rows of ) can detect various game scenarios (e.g. the ball is in the top, and our paddle is in the middle), and the weights in can then decide if in each case we should be going UP or DOWN. Now, the initial random and will of course cause the player to spasm on spot. So the only problem now is to find and that lead to expert play of Pong!

Ideally you’d want to feed at least 2 frames to the policy network so that it can detect motion. To make things a bit simpler (I did these experiments on my Macbook) I’ll do a tiny bit of preprocessing, e.g. we’ll actually feed to the network (i.e. subtraction of current and last frame).

Policy Gradients: Run a policy for a while. See what actions led to high rewards. Increase their probability.

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
