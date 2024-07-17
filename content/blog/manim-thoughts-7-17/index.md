---
title: "Reworking Manim"
date: "2024-07-17"
description: "A short guide through a rework of Manim"
---

It's been over a year now since the developers of the mathematical animations
library [Manim](https://www.manim.community/) started working on a rework of
the entire backend. A year is a long time to work on something like this, so
let me walk you through what we've done in that time, and what's left. As we go along,
try to remember this:

<p align="center">
  <img src="https://github.com/user-attachments/assets/aa04daf8-8550-4434-b228-8af8c3e583f9" width=500>
</p>

With that out of the way, let's start with a quick walkthrough of how the Cairo renderer works in Manim.

#### The Old Render Loop
First let's take an (admittedly very quick) look at what happens when you
do `Scene.play` in the current version of Manim. It essentially boils down
to a series of steps that must happen

1. Get the file writer ready to write frames.
1. Call `begin()` on every animation, to get it ready
1. Iterate over every value of ``t`` in until the end of the animations
1. For every value of ``t``, compute ``dt`` (the change in time since the last frame),\
    and use it to update all of the animations, then the mobjects, and finally the scene.
1. Render all moving mobjects at that value of ``t``
1. Write the frame for that value of ``t``
1. Call ``finish()`` on every animation.
1. Close the animation pipe on the file writer.

In code, something like
```py
class Scene:
    ...

    def play(self, *animations: Animation) -> None:
        # step 1
        self.file_writer.prepare()
        # step 2
        for animation in animations:
            animation.begin()

        # step 3
        last_t = 0
        for t in compute_t_range(animations):
            dt = t - last_t
            last_t = t
            # update animations (step 4)
            for animation in animations:
                alpha = t / animation.get_run_time()
                animation.interpolate(alpha)
            # step 5
            self.update_mobjects(dt)
            # step 6
            self.renderer.render(self.moving_mobjects)
            # step 7
            self.file_writer.write_frame()

        # step 8
        for animation in animations:
            animation.finish()
        # step 9
        self.file_writer.finish()
```
It's really not much more complicated than this. So what's the problem?
Well, in the actual code, the flow goes something like this

1. `Scene.play` calls `CairoRenderer.play`
2. `CairoRenderer.play` does the file writer preparation
3. `CairoRenderer.play` calls `Scene.play_internal`
4. `Scene.play_internal` does steps 2-5
5. `Scene.play_internal` calls the `CairoRenderer` for step 6
6. `CairoRenderer`, in step 6, uses the `Camera` to render the mobjects
7. `Scene.play_internal` does step 8
8. `CairoRenderer` then finishes up step 9

Wow, that's a headache! There's so much interplay between `Scene`,
`CairoRenderer`, `SceneFileWriter`, and `Camera` it's hard to keep track.
Fixing this annoying communication was one of the big reasons 

Before we move on to the refactor, let's talk about one other thing:
how do we actually render the mobjects when we do `self.renderer.render(self.moving_mobjects)`?

For now let's consider the most common case, a `VMobject` (such as a square). Internally,
it is just a list of a set of points. Each set of points make up a [Bézier Curve](https://pomax.github.io/bezierinfo/).
Luckily for us, Cairo comes with a way to [automatically render Cubic Béziers](https://pycairo.readthedocs.io/en/latest/reference/context.html#cairo.Context.curve_to),
so we don't have to worry much about it: just know that the `Camera` is the one that
does everything related to Cairo (which doesn't make sense, but just go with it).


#### The Rewrite
There are three major changes in the rewrite:

1. Organizing the control flow of the `Scene`, via the introduction of a `Manager` class.
2. Changing from Cairo to OpenGL for live rendering.
3. Using interfaces instead of concrete objects (more on this later!)

##### The Manager
The `Manager` has one, and only one job: it has to organize calls between `Scene`, the renderer, and the file writer.
It also has to communicate with a new class, the `Window`, which is used for live rendering with OpenGL. Let's take a look
at how the (slightly modified) code, now looks for `Manager._play`:

```py
class Manager:
    ...

    def _play(self, *animations: AnimationProtocol) -> None:
        # prepare file writer
        self._write_hashed_movie_file(animations)

        # call begin on all the animations
        self.scene.begin_animations(animations)
        self._progress_through_animations(animations)
        # call finish() on all animations
        self.scene.finish_animations(animations)

        # finish the file writer
        self.file_writer.end_animation()


    def _progress_through_animations(
        self, animations: Sequence[AnimationProtocol]
    ) -> None:
        last_t = 0.0
        run_time = self._calc_runtime(animations)
        progression = self._calc_time_progression(run_time)
        for t in progression:
            dt, last_t = t - last_t, t
            # interpolate animations
            self.scene._update_animations(animations, t, dt)
            self._update_frame(dt)

    def _update_frame(self, dt: float) -> None:
        # run updaters
        self.scene._update_mobjects(dt)

        state = self.scene.get_state()  # get how the scene looks
        self.renderer.render(state)

        pixels = self.renderer.get_pixels()
        self.file_writer.write_frame(pixels)
```
No more weird `Scene` and renderer interplay! The `Manager` makes sure to call the right
methods on the right object.

This also has one effect on mainstream users: instead of running your code via something
like
```py
if __name__ == "__main__":
    SceneName().render()
```
It would be changed to
```py
if __name__ == "__main__":
    manager = Manager(SceneName)
    manager.render()
```
If you ever want to access the scene, you can do so by accessing
the `scene` attribute on `Manager`.


##### Cairo to OpenGL
You might be thinking, if Cairo works why change it? Well, let's take a look at how
Cairo does its job. It essentially calculates the color for every pixel in the video on the CPU.
Every frame. Calculating the color of a pixel is an operation that is embarresingly parallel: once
you have the data you don't really need to know about the color of a previous pixel. In fact,
creating frames really fast is the exact reason that GPUs, or Graphical Processing Units, were invented!

Now our implementation of an OpenGL renderer is still undergoing changes, mostly due to the difficulty of the task.
Unfortunately, OpenGL, a GPU API, doesn't have a nice interface for rendering Bézier Curves - we have
to code it ourselves. Most shapes in OpenGL are created with _triangles_. For example, a square could be
made out of two right isosceles triangles. There has been some [research](https://www.microsoft.com/en-us/research/wp-content/uploads/2005/01/p1000-loop.pdf)
on how to do this effectively, but our implementation still has several bugs as of right now.

This has a few other benefit. One of them is that you no longer have to worry about using `OpenGLMobject`
vs `Mobject` depending on the renderer: it's all (going to be) consolidated into one single `Mobject` class!
Another benefit is that now 3D scenes should be _much_ easier to work with, just because OpenGL
has really good 3D support.

##### Protocols
Have you ever wondered something along the lines of "hmm, I want to make my own
`Animation`, but I don't know what methods to override"? Well, we have an advancement
for you: many items in Manim now have a stable interface of methods that they _must_
implement in order to function without errors! You might have noticed in the code above
something called `AnimationProtocol`: that is a class that tells you exactly which methods need
to be overridden to make a fully functioning animation!


#### Conclusion
The new rewrite is still nowhere near complete - there is still so many things to do, but this
is a brief overview of the main changes. If you're interested in helping out, feel free to ping
me (`@jasongrace2282`) on the [Manim Discord Server](https://manim.community/discord/), or if you
just want to check out the progress take a look at the [tracker issue](https://github.com/ManimCommunity/manim/issues/3817).
Until next time!
