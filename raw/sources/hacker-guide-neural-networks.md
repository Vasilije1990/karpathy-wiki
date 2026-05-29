# Source: Hacker's Guide to Neural Networks

source_id: hacker-guide-neural-networks
title: Hacker's Guide to Neural Networks
url: https://karpathy.github.io/neuralnets/
kind: tutorial
status: captured-as-excerpt
captured: 2026-05-28

## Extracted Headings

- Hacker's guide to Neural Networks
- “…everything became much clearer when I started writing code.”
- Chapter 1: Real-valued Circuits
- Base Case: Single Gate in the Circuit
- Lets first consider a single, simple circuit with one gate. Here’s an example:
- And in math form we can think of this gate as implementing the real-valued function:
- As with this example, all of our gates will take one or two inputs and produce a output value.
- The problem we are interested in studying looks as follows:
- We provide a given circuit some specific input values (e.g. , )
- The circuit computes an output value (e.g. )
- The core question then becomes:
- The derivative can be thought of as a force on each input as we pull on the output to become higher.

## Excerpt

Hi there, I’m a CS PhD student at Stanford. I’ve worked on Deep Learning for a few years as part of my research and among several of my related pet projects is ConvNetJS - a Javascript library for training Neural Networks. Javascript allows one to nicely visualize what’s going on and to play around with the various hyperparameter settings, but I still regularly hear from people who ask for a more thorough treatment of the topic. This article (which I plan to slowly expand out to lengths of a few book chapters) is my humble attempt. It’s on web instead of PDF because all books should be, and eventually it will hopefully include animations/demos etc.

My personal experience with Neural Networks is that everything became much clearer when I started ignoring full-page, dense derivations of backpropagation equations and just started writing code. Thus, this tutorial will contain (I don’t believe it is necessary and it can sometimes even obfuscate simple concepts). Since my background is in Computer Science and Physics, I will instead develop the topic from what I refer to as . My exposition will center around code and physical intuitions instead of mathematical derivations. Basically, I will strive to present the algorithms in a way that I wish I had come across when I was starting out.

“…everything became much clearer when I started writing code.”

You might be eager to jump right in and learn about Neural Networks, backpropagation, how they can be applied to datasets in practice, etc. But before we get there, I’d like us to first forget about all that. Let’s take a step back and understand what is really going on at the core. Lets first talk about real-valued circuits.

: I suspended my work on this guide a while ago and redirected a lot of my energy to teaching CS231n (Convolutional Neural Networks) class at Stanford. The notes are on cs231.github.io and the course slides can be found here. These materials are highly related to material here, but more comprehensive and sometimes more polished.

In my opinion, the best way to think of Neural Networks is as real-valued circuits, where real values (instead of boolean values ) “flow” along edges and interact in gates. However, instead of gates such as , , , etc, we have binary gates such as (multiply), (add), or unary gates such as , etc. Unlike ordinary boolean circuits, however, we will eventually also have flowing on the same edges of the circuit, but in the opposite direction. But we’re getting ahead of ourselves. Let’s focus and start out simple.

Lets first consider a single, simple circuit with one gate. Here’s an example:

The circuit takes two real-valued inputs and and computes with the gate. Javascript version of this would very simply look something like this:

And in math form we can think of this gate as implementing the real-valued function:

As with this example, all of our gates will take one or two inputs and produce a output value.

The problem we are interested in studying looks as follows:

We provide a given circuit some specific input values (e.g. , )

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
