# Jumping off a Train

```{post} January 28, 2025
---
tags: physics momentum
---
```

Recently, I came across this cool problem (which is from Kleppner and Kolenkow, as well as INPhO 2014):

> Two men, each with mass $m$, stand on a railway flatcar of mass $M$ initially at rest. They
> jump off one end of the flatcar with velocity $u$ relative to the car. The car rolls in the opposite
> direction without friction. Find the final velocities of the flatcar if they jump off at the same
> time, and if they jump off one at a time. Generalize to the case of $N ≫1$ men, with a total
> mass of $m_\mathrm{tot}$.

I highly suggest you try solving it before looking at my solution.

:::{dropdown} My Solution
:animate: fade-in

Let's start with the easy part: finding the final velocity if they jump off at the same time.
In this case, we have $p_0=0$ and $p_f=m_\mathrm{tot}(v-u)+Mv$, where $v$ is the final velocity of the flatcar.
By conservation of momentum, $p_0=p_f$ and we have that

$$v=\dfrac{m_\mathrm{tot}u}{M+m_\mathrm{tot}}$$

In the second case, by a similar logic, we have that after the first man jumps, the flatcar moves at

$$v_1=\dfrac{mu}{M+2m}$$

We can find the velocity after the second man jumps by transforming into the frame moving with the flatcar
at a velocity $v_1$. In this frame, the second man exerts a further impulse onto the train of magnitude
$v_2=\dfrac{mu}{M+m}$. Therefore, the final speed of the flatcar is then

$$v=v_1+v_2=mu\left(\dfrac{1}{M+2m}+\dfrac{1}{M+m}\right)$$

Extending it to $N$ people, we then have

$$v=\dfrac{m_\mathrm{tot}u}{N}\sum_{i=1}^N\dfrac{1}{M+(i/N)m_\mathrm{tot}}$$

Now comes the cool part. For a large enough $N$, we can turn this into an integral
with $x=i/N$ and $\mathrm{d}x=\mathrm{d}i/N$. Substituting it in, we get

$$v \approx m_\mathrm{tot}u\int_0^1 \dfrac{\mathrm{d}x}{M+xm}=\ln\left(\dfrac{M+m_\mathrm{tot}}{M}\right)u$$

Which turns out to be almost exactly the rocket equation!
Definitely a cool problem, and the first one where I've seen the idea of turning
a series into an integral.

:::
