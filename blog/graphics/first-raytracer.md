# First Raytracer

```{post} July 05, 2024
:tags: projects
:category: graphics
```

A month ago, I set out on a journey to learn Rust. At the same time,
I wanted to try my hand at something related to computer graphics,
so I decided to build my very own path tracer. I'm quite happy with
how it turned out, as you can see with my final render.

<img src="./assets/rust-raytracer.png">

But what is a Ray tracer or a path tracer?

The fundamental idea behind ray tracing (or more specifically, path tracing)
is to render images that accurately depict how something looks like in real life.
This means shadows, colors, all that stuff.

Any video game you play, or movie that involves semi-realistic CGI, is almost guarenteed
to have some ray tracing - otherwise it would just look even more fake!

But how does it work?

Effectively what happens is we pretend to take a ray of light, and shoot it at some pixels.
It then computes the color seen in the direction of the rays. Along the way, we have to calculate
which objects the ray intersects. There have been many advancements in physics that allow us to do this,
such as Snells law.

But if you naively try to implement this, you'll notice that the edges of every
shape are jagged. To fix this, we have to sample some rays *around* the pixel,
and average out the color. This way each pixel isn't the same color until suddently
the object ends. You can see the difference in these two images, where the left is before
and the right is after:

<img src="https://raytracing.github.io/images/img-1.06-antialias-before-after.png" class="pixelated" width="72ex">

The more rays we sample per pixel, the closer it will be to looking "smooth". This is
called *Antialiasing*!

So, that's the end of my first ray tracer. Where am I going next?
Well the next step is to improve the speed. To do so, I've started learning [Vulkan](https://www.vulkan.org/),
so that I can implement it on the GPU. I also might end up porting the
[Manim Community Renderer](https://github.com/ManimCommunity/manim/blob/experimental/manim/renderer/opengl_renderer.py)
into WGPU so that it works nicer on MacBooks.

As for where I learned this?
Check out [https://raytracing.github.io/](https://raytracing.github.io/). The guide
is written in C++, but you can find my Rust code [on Github](https://github.com/JasonGrace2282/raytracing/tree/rust-1)
