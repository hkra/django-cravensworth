# Experimentation

Cravensworth is a library for carrying out software experiments. Software
experiments are much like their scientific namesake:

1. Start with a problem you want to solve.
2. Come up with a hypothesis.
3. Design a experimental protocol to test your hypothesis.
4. Carry out the experiment.
5. Analyze the results.
6. Modify your hypothesis as needed, and test again.

As a contrived example, let's say you are running an e-commerce marketplace for
apes. Businsess has been good, so you decide to expand to serve internet cats,
too.

## 1. Problem

After a few weeks, cat merch is barely moving at all.

You do some research on cats, and come across an interesting fact: cats can't
see orange good. Your add to cart button is orange. Your signup button is
orange. All interactables are orange, because apes love orange (obviously).
Maybe cat merch isn't moving because the cats are having trouble with your
orange buttons.

## 2. Hypothesis

If you change the button color to blue, then cat merch sales will skyrocket.

## 3. Protocol

Now you must design a protocol for testing your hypothesis. There are many ways
you could do this, but the simplest is a two-variant split test—commonly known
as an A/B test.

A/B testing involves creating two versions of the thing you're testing:

* **Version A (control)**: This is your current live version, with the orange
    "Add to Cart" and "Signup" buttons. You'll continue to show this to a
    portion of your users.
* **Version B (variant)**: This is the modified version where you've changed the
    buttons to blue. Another portion of your users will see this version.

The key to a good A/B test is randomization. You'll randomly split your incoming
traffic, ensuring that each user has an equal chance of seeing either Version A
or Version B. This helps to eliminate bias, so you can be confident that any
differences in sales are due to the button color, and not some other factor
(like apes being inherently more spendy).

You'll also need to define the duration of your experiment and the metrics
you'll track. For this example, your primary metric would be "cat merch sales."

## 4. Carry out the experiment

With your protocol in place, you run your experiment. This is where Cravensworth
comes into play. Cravensworth will help you to:

* Split the incoming cat traffic into two groups.
* Show Version A (orange buttons) to one group.
* Show Version B (blue buttons) to the other group.

You let the experiment run long enough to gather a statistically significant
amount of data. How long this takes, will likely vary based on how much traffic
your site gets.

## 5. Analyze the results

Once enough data has been collected, you'll analyze the results. Cravensworth,
helps you to run experiments, but data collection and analysis are up to you.

When comparing the performance of Version A and Version B. You'll look for:

* Statistical Significance: Is the observed difference in cat merch sales
    between the two groups likely due to the button color change, or could it be
    random chance? Statistical analysis (often involving p-values and confidence
    intervals) helps you determine this. A common—albiet arbitrary—threshold is
    a p-value of less than 0.05, meaning there's less than a 5% chance the
    results are random.
* Practical Significance: Even if a difference is statistically significant, is
    it large enough to be meaningful for your business? A 0.1% increase in sales
    might be statistically significant but not worth implementing. A 20%
    increase, on the other hand, is highly impactful.

Let's say your analysis shows that Version B (blue buttons) resulted in a
to-the-moon increase in cat merch sales.

It would seem that your hypothesis was correct!

## 6. Modify your hypothesis as needed, and test again

Based on your analysis, you now have a data-driven decision.

* If Version B was successful: You might decide to roll out the blue buttons
    all users (if it doesn't negatively impact ape sales). You might then
    formulate new hypotheses about other aspects of your web app based on your
    success.
* If Version B was unsuccessful or inconclusive: You would not implement the
    blue buttons. Instead, you'd iterate on your hypothesis. Perhaps the color
    wasn't the issue, or blue isn't the best cat color. You might then formulate
    a new hypothesis, such as "If we make the buttons as large as the mean cat
    paw size, cat merch sales will skyrocket," and design another experiment to
    test it.

## Wrapping up

This iterative process of problem definition, hypothesis generation,
experimentation, analysis, and refinement is the core of effective software
experimentation. It allows you to make data-driven decisions, reduce risk, and
continuously improve your product based on real user behavior.
