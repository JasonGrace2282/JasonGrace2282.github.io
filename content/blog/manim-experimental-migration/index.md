---
title: "A Migration Guide for Manim Community"
date: "2024-08-02"
description: "How to migrate your code from v0.19.0 to v0.21.0"
---

Manim v0.21.0 introduced a lot of changes, and was the result of
quite literally rewriting all of Manim. We aren't going to talk about
why this happened (see [here](https://jasongrace2282.github.io/manim-thoughts-7-17/) if you're interested),
but more about the big changes that *you*, as a user, should care about.
Towards the end, we will focus more on what plugin developers should change.

Note that Manim v0.21.0 has the most breaking changes out of any of the
most recent releases.

Let's get started!

#### OpenGL by default
Manim no longer uses Cairo by default (in fact, Cairo has been ripped out of
Manim). Instead, all renderings will use OpenGL by default. The `config.renderer`
option has also been removed - we'll talk later about how you can change the renderer.

Note that this also means you will have to use `-w` or set `config.write_to_movie=True`
in order to produce a video file. If neither `-p` nor `-w` is passed, Manim will
not write a video or live preview. Additionally, it is not recommended to use the live preview `-p`
and `write_to_movie` at the same time, as it will reduce the fps of the live preview.

#### OpenGLMobject to Mobject
Manim v0.21.0 got rid of the concept of an `OpenGLMobject` vs a `Mobject`.
Instead, a `Mobject` is simply a renderer independent Mathematical Object.
Therefore, you can replace everywhere you used `OpenGLMobject` with `Mobject`,
and likewise for every other mobject that started with `OpenGL` (e.g.
`OpenGLSurface` can be changed to `Surface`)

It's important to note that a concept of `z-index` no longer exists in OpenGL -
use `set_z` to set the `z` value instead.

#### Time-based Updaters
Previously, time based updaters could be created by having a parameter
called `dt` inside the function, e.g.
```py
def my_updater(mob, dt):
    ...
my_square.add_updater(my_updater)
```
Now, updaters have to be added via specific methods. `Mobject.add_updater`
is for updaters that do not want `dt`, and `Mobject.add_dt_updater` is
for updaters that need a `dt` parameter. Note that you no longer need
to call the parameter `dt`.


#### CLI Options
The deprecated config options `save_pngs` and `save_gif` were removed:
they can be replaced with `--format=png` or `config.format=gif`.
Additionally, the cli flags `--use_projection_fill_shaders` and  `--use_projection_stroke_shaders`
were removed, as they have no effect in the latest version of Manim.

#### Sections
Previously, you could start a new section with `Scene.next_section`. This
has been replaced with a completely new decorator-based API. For example,
the following code
```py
class MyVideo(Scene):
    def construct(self):
        c = Circle()
        self.play(Create(c))
        self.play(Uncreate(c))
        self.next_section(name="second_section")
        txt = Text("Hi!").to_edge(UP)
        self.play(Write(txt))
        self.next_section(
            name="After Introduction",
            skip_animations=True
        )
        m = ManimBanner()
        self.add(m)
        self.play(m.expand())
```
Can be replaced by
```py
class MyVideo(Scene):
    # state that you want to use sections
    sections_api = True

    @section
    def my_first_section(self):
        c = Circle()
        self.play(Create(c))
        self.play(Uncreate(c))

    @section  # by default the method name is used
    def second_section(self):
        txt = Text("Hi!").to_edge(UP)
        self.play(Write(txt))

    # but you can override the name, and other parameters of each section.
    @section(name="After Introduction", skip=True)
    def my_name_for_after_introduction(self):
        m = ManimBanner()
        self.add(m)
        self.play(m.expand())
```

#### `Scene().render()`
If you didn't like running your manim scripts from the command line, you
might have used an idiom that looked something like this:
```py
with tempconfig({"preview": True, ...}):
    MySceneName().render()
```
This has been replaced with the following:
```py
with tempconfig({"preview": True, ...}):
    Manager(MySceneName).render()
```


We'll talk more about what a `Manager` is in the next part.
For now, that's all that you, as a user, need to do to migrate your scripts.
Happy Manimating!


### Advanced Changes
This is mostly geared towards more advanced users and/or
plugin developers. With any luck, the changes mentioned here should make
it much easier to modify how Manim works with minimal changes and conflicts.

The main change is the `Manager`. Instead of the `Scene` controlling the `CairoRenderer`
and vice versa, the `Manager` now does all the hard work of synchronizing interactions
between the `Scene`, `Window`, `CairoRenderer`, and `FileWriter`. The `Manager` exposes
several public methods that you can override, and we'll go through some of the
most useful ones.

---
⚠️ **WARNING** ⚠️

Don't forget to call `super()` on each method! Just
because they are public doesn't mean that they don't do anything
in the default implementation!

---

#### Render, Setup, and Tear-down
The `Manager` exposes three methods that you can override to do
setup, actually render the scene, and to tear it down at the end.

#### Construct
The `Manager.construct` method either calls `Scene.construct` if `Scene.sections_api=False`
(the default), or plays each section in the scene. You can override this
if you want to e.g. dynamically create sections, or rearrange sections. Note
that each section is internally stored as a `SceneSection` class, which contains
the metadata about the `name`, `type_`, `skip`, etc.

As soon as `Manager.construct` is done, and right before the live interaction
with the final scene (note: no video is written there), the `Manager.post_construct`
method is called for cleanup.

#### `Manager.render_state`
This is where the renderer actually renders the scene data to the screen.
In psuedocode, the default implementation looks roughly like
```py
def render_state(self):
    state = self.scene.get_state()
    self.renderer.render(state)
```
Note that *no writing* should be performed here - it is intended to be
a quick rendering action to the window, and is not optimized for file writing.


#### `Manager.write_frame`
This method is where the frame is actually written to the output format.
This method is only called if `config.write_to_movie` is `True`, as well
as other conditions (i.e. the section or animation is not being skipped).

You should only really have to override this if the renderer is not able to
produce pixels after rendering, as the default implementation looks similar to
```py
def write_frame(self):
    frame = self.renderer.get_pixels()
    self.file_writer.write_frame(frame)
```

#### Changing the Core Classes
But what if you wanted to write your own file writer, that instead
of producing an `mp4` produced some other file format Manim doesn't support?
Sure you could override `write_frame`, and every other method that uses `FileWriter`.
Or you wanted to write a completely new web renderer written in another technology
like [`wgpu`](https://wgpu.rs)? Sure, you could override `render_state` and every other
method that used the renderer. But that's horrible to maintain!

Manim provides a solution for that! Whatever `FileWriter`, `Window`, or `Renderer`
you want to implement, just needs to implement the corresponding `Protocol`.

- Implement the `FileWriterProtocol` for a custom `FileWriter`
- Implement the `WindowProtocol` for a custom `Window`
- Implement the `RendererProtocol` for a cusotm `Renderer`

Let's say I had a custom renderer for example
```py
class WgpuRenderer(RendererProtocol):
    # implement the required methods
    ...
```
You could then write your own manager like this:
```py
class WgpuManager(Manager):
    renderer_class = WgpuRenderer
```
and that's it! Manim will use `WgpuRenderer` instead of the default
`OpenGLRenderer`!
If you need to do more initialization, you could always override `create_renderer`:
```py
class WgpuManager(Manager):
    renderer_class = WgpuRenderer

    def create_renderer(self) -> RendererProtocol:
        renderer = self.renderer_class()
        return renderer
```
The same logic applies for `FileWriter` and `Window`.
