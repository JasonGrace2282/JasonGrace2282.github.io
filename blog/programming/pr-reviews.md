# Reflections on Maintaining Open Source Software

```{post} November 16, 2024
---
tags: reflections
category: oss
---
```

It's hard to believe it's been a full year now since I was given the
chance to become a maintainer of [Manim](https://www.manim.community), a python animations library.
I've learned a lot through that time, about open source and communities,
so here goes my attempt at writing down most of the stuff I've learned!

## Interpersonal Skills
As a maintainer of the project, you're sort of the face to the code.
You represent the direction the code will go, and the views of the project.
For me, this resulted in a lot of interesting encounters that forced me to
reevaluate the way I look at feedback.

If you're looking for a blog post solely about import interpersonal skills,
I found this post about [doing code reviews like a human](https://mtlynch.io/human-code-reviews-1/)
extremely interesting.

### Getting Feedback from a Community
#### Finding Pain points, and saying No
Ultimately, Manim is a project by the community for the community, so getting
feedback on what the community thinks on the roadmap of what features to implement
is important to us as maintainers. 

However, people also have their own agenda's - they might want to create their next
video on linear transformations, so they may try really hard to get new features merged
in. I've learned that sometimes, **it's a good idea to say no**, we're not going to
spend time implementing what you're asking for right now, because there's more
important changes we need to focus on.

#### Dealing with Toxcitity
People have a tendency to [expect open source maintainers to solve their problems](https://mikemcquaid.com/entitlement-in-open-source/).
I'm glad that Manim has a community where there are helpers who
are willing to help people with their specific problems - however, people constantly
demanding that their problems are fixed, or pinging maintainers as "what's the update
on this issue" can be extremely discouraging.

For example, on Manim, we regularly get requests to [make Manim faster](https://github.com/ManimCommunity/manim/discussions/3897).
This got worse after 3Blue1Brown released [a video](https://www.youtube.com/watch?v=rbu7Zu5X1zI)
on his Manim workflow. After that, we got a lot of comments saying "use ManimGL,
it's better", and lots of requests to implement features like live-reloading.
They're not wrong - [ManimGL](https://github.com/3b1b/manim) is more featureful, because Grant has the ability to work on it
full time, without worrying about documentation or compatibility (which is what ManimCE
excels at). Also note that none of it is neccessarily people *trying* to be toxic,
but hearing constant demands for new features, and not enough positive feedback
about the project, can make it pretty demoralizing to work on Manim.

I haven't found a way around feeling demoralized yet, but I have found that taking breaks really helps.
I'm essentially forced to take breaks from Manim (by school), and it's a lot easier to get
back into the vibe of working on a project again after several days (or in severe cases, weeks)
of being inactive.



### Dealing with Pull Requests
I've realized that most of "maintaining" a project essentially boils down to reviewing PRs.
Lots and lots of PRs. Most of them can be put into categories:

1. High quality PRs. These are usually well written, and require a maximum of one or two
  reviews before they're merged.
2. Middle quality PRs. These are usually sent by people with good intention, but either their
  programming, or version control skills are not up to par. With a bit more effort, they usually
  get merged eventually.
3. Low quality PRs. These are usually extremely opinionated, with little to low rationale.

Initially, I used to spend an equal amount of effort on all types: asking why they made certain
decisions (even when they didn't make sense, like mixing `pygame` with `ffmpeg`). However,
this is a massive effort drain: PRs that are low or middle quality tend to get abandoned, so after
a review or two, they're dead in the water. Lately, I've gotten a bit more proactive with this, marking
PRs as drafts after a week without any update (after a review), and closing them after a month.
I've come to strongly believe that **maintainer time is much more valuable then contributer time**.
I always have at least 30 PRs that I want to review, in addition to the architectural changes and
refactoring that are (almost always) left to core developers.

To be clear, that's not to say that contributer time and effort doesn't matter. I'd rather just
spend 10 minutes praising a something someone did right than 10 minutes trying to figure out
what a PR was trying to do when it brought in 50 external dependencies to make some nonsensical change.

```{admonition} Fun stuff that worked

The first PR I ever made to an open source library, I got a review that started
with the words:
> Hi JasonGrace2282,
> 
> Thank you so much for your interest in contributing to \<project name\>.

I don't know why such a simple greeting made me feel valued, but it did, so on almost all
of my PRs, my first review often starts with those exact lines :)
```

## Technical Skills
Interpersonal skills are pretty important, but I also learned a lot of
technical skills while working on Manim. There's too many to list,
so I decided to make a short compilation of the ones I found most useful.

### Know how to use `git`
I cannot state how much knowing how to use `git` has saved me many times.
When contributing, usually all you need to know is `git add`, `git commit`,
`git push`, and `git checkout`. You can almost always just follow the same steps:

- `git checkout main`
- `git pull <upstream> main`
- `git checkout -b new-branch`
- Make changes
- `git add .`
- `git commit -m "My commit message"`
- `git push`

However, as a maintainer, most of your time isn't spent *writing* code, but reading
and reviewing it. Without the idea of remotes, you end up having
to clone the repos of every persons fork, and maintain separate repositories
for the upstream branch and your own fork.

```{tip}
If you haven't already, be sure to install github's cli - it's
a huge timesaver.
```

If you don't know how to rebase or merge, it's a lot more difficult to
handle multiple branches with overlapping changes. For example, in Manim,
we had a refactor branch that hadn't been updated with `main` in over a year,
with over 400 commits passing through `main` in that time. Being able to decide
when to `git merge` and `git rebase` was essential for us to keep working on that branch.

### Github Workflows are amazing
Automation is key. You only have so much time in a day, let github's servers
do all of the tedious stuff like compiling, rebuilding documentation, and running tests.

Github workflows have lots of extremely useful features, like [matrix strategies](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow#using-a-matrix-strategy),
[composite actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action),
and [reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
which allow you to write workflows with minimal boilerplate.

Additionally, make sure to look into making your tests run as FAST as possible.
It's a lot better of an experience when you can see the simple errors you made within
a few seconds, and see tests fail within 10 minutes of making a PR.

```{note}
If you're working with python linting tools like `flake8`, `black`,
or `isort`, I *highly* recommend trying out [ruff](https://docs.astral.sh/ruff).

Additionally, I also recommend using [`uv`](https://docs.astral.sh/uv) as a replacement
for `pip` and `poetry` - it's amazing how much faster these two tools are.
```

### Smaller PRs
Please, I beg of you, do not show up to an open source repository with a change that has
a +1000-500 character diff. I personally promise you, I will not review any PR with a diff greater than
+300 characters.

I've started to ask people with PRs greater than a +300 character `git diff` to split their
PR into smaller chunks within the size. It's much easier (and faster to review) to test a bunch of small chunks
individually, than one massive addition of code.
