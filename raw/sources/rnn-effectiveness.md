# Source: The Unreasonable Effectiveness of Recurrent Neural Networks

source_id: rnn-effectiveness
title: The Unreasonable Effectiveness of Recurrent Neural Networks
url: https://karpathy.github.io/2015/05/21/rnn-effectiveness/
kind: essay
status: captured-as-excerpt
captured: 2026-05-28

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
- Wikipedia
- Sometimes the model snaps into a mode of generating random but valid XML:

## Excerpt

The Unreasonable Effectiveness of Recurrent Neural Networks

We’ll train RNNs to generate text character by character and ponder the question “how is that even possible?”

By the way, together with this post I am also releasing code on Github that allows you to train character-level language models based on multi-layer LSTMs. You give it a large chunk of text and it will learn to generate text like it one character at a time. You can also use it to reproduce my experiments below. But we’re getting ahead of ourselves; What are RNNs anyway?

. Depending on your background you might be wondering: ? A glaring limitation of Vanilla Neural Networks (and also Convolutional Networks) is that their API is too constrained: they accept a fixed-sized vector as input (e.g. an image) and produce a fixed-sized vector as output (e.g. probabilities of different classes). Not only that: These models perform this mapping using a fixed amount of computational steps (e.g. the number of layers in the model). The core reason that recurrent nets are more exciting is that they allow us to operate over of vectors: Sequences in the input, the output, or in the most general case both. A few examples may make this more concrete:

If training vanilla neural nets is optimization over functions, training recurrent nets is optimization over programs.

. You might be thinking that having sequences as inputs or outputs could be relatively rare, but an important point to realize is that even if your inputs/outputs are fixed vectors, it is still possible to use this powerful formalism to them in a sequential manner. For instance, the figure below shows results from two very nice papers from DeepMind. On the left, an algorithm learns a recurrent network policy that steers its attention around an image; In particular, it learns to read out house numbers from left to right (Ba et al.). On the right, a recurrent network images of digits by learning to sequentially add color to a canvas (Gregor et al.):

The takeaway is that even if your data is not in form of sequences, you can still formulate and train powerful models that learn to process it sequentially. You’re learning stateful programs that process your fixed-sized data.

So how do these things work? At the core, RNNs have a deceptively simple API: They accept an input vector and give you an output vector . However, crucially this output vector’s contents are influenced not only by the input you just fed in, but also on the entire history of inputs you’ve fed in in the past. Written as a class, the RNN’s API consists of a single function:

The RNN class has some internal state that it gets to update every time is called. In the simplest case this state consists of a single vector . Here is an implementation of the step function in a Vanilla RNN:

We initialize the matrices of the RNN with random numbers and the bulk of work during training goes into finding the matrices that give rise to desirable behavior, as measured with some loss function that expresses your preference to what kinds of outputs you’d like to see in response to your input sequences .

. RNNs are neural networks and everything works monotonically better (if done right) if you put on your deep learning hat and start stacking models up like pancakes. For instance, we can form a 2-layer recurrent network as follows:

In other words we have two separate RNNs: One RNN is receiving the input vectors and the second RNN is receiving the output of the first RNN as its input. Except neither of these RNNs know or care - it’s all just vectors coming in and going out, and some gradients flowing through each module during backpropagation.

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
