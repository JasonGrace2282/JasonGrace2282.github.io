# Docker in Docker with Docker Compose

```{post} December 14, 2024
---
tags: docker docker-compose DinD
---
```

Docker in Docker is a technology to run docker services
inside of a docker container. In this, we'll take a look at
how to set it up with Docker Compose to integrate it with
your development environment.

```{admonition} TL;DR
If you're just interested in the end product, you can
find it [here](https://github.com/JasonGrace2282/docker-compose-dind).
```

## Networks
Our goal is going to be to have Docker in Docker (DinD) to be running
as a service, and have another service connect to it. First, we need
to set up the network so that the two services can actually communicate.
Create a file called `compose.yaml`, and place the following content inside:

```yaml
networks:
  docker-network:
    name: docker-network
    driver: bridge
```
This creates a network using the `bridge` driver. The bridge driver is
essentially a software bridge between two (or more) services, that
allow the connected services to communicate while providing
isolation from services that aren't connected to the network.
The actual creation of the network is handled by Docker itself.
You can read more about it [here](https://docs.docker.com/engine/network/drivers/bridge/).

```{note}
If you've worked with docker swarm before, you may have heard of
services in that context. However, in this article I will refer
to services as in the docker compose services.
```

## Volumes
According to the documentation of the [Docker-in-Docker image](https://hub.docker.com/_/docker),
we'll need some volumes to store the TLS certificates. Note
that we could skip TLS setup, but it's actually quite easy
and a good thing to do (especially because Docker-in-Docker
requires a priviledged service[^1]).

We can set up the volumes in by adding the following to our
setup:

```yaml
volumes:
  docker-tls-ca:
  docker-tls-client:
```
Volumes are a form of anonymous storage with docker.
They allow the sharing of data between the host and (one or more)
containers. However, they're completely managed by docker,
and as such aren't meant to be manipulated outside of containers.

```{note}
If you're curious, the volumes are stored in `/var/lib/docker/volumes/`
on Linux.
```

## Services
Now let's actually start putting the pieces together, and add our services!
Append the following to `compose.yaml`:
```yaml
services:
  docker:
    image: docker:27.3-dind
    privileged: true
    volumes:
      - docker-tls-ca:/certs/ca
      - docker-tls-client:/certs/client
    environment:
      DOCKER_TLS_CERTDIR: /certs
    networks:
      - docker-network

  client:
    image: docker:27.3-cli
    volumes:
      - docker-tls-client:/certs/client:ro
    entrypoint:
      - docker
      - version
    depends_on:
      - docker
    networks:
      - docker-network
```
Wow, that's a lot! Let's go through what's happening.
We have two services - one that's running our docker-in-docker
setup, and another that's acting as our application client.
For ease of testing, we've made the client just do `docker version`,
which will error if it cannot connect to the docker socket.

Both services are connected to the same network, so that they
can communicate with each other. The docker-in-docker service is
marked as a privileged service (we haven't used sysbox). Then,
on the `docker` service, we mounted our volumes to `/certs/ca`
and `/certs/client`. This means that when the `docker` service
creates the certificates, it will also be created somewhere
on your machine. The client certificates (`docker-tls-client`)
are then mounted to `/certs/client` on the client service,
so that the client can authenticate itself. The `:ro` at
the end marks the `docker-tls-client` volume as read-only
on the client service.

## Environment Variables
However, if we run it in it's current state, it still will not be
able to connect to the docker in docker service, because it's
still looking for a `/var/run/docker.sock` instead of the `tcp://`
socket the Docker-in-Docker image creates. You'll need to add
the following to the client service:

```yaml
    networks:
      - docker-network
    # NEW!!
    environment:
      DOCKER_TLS_CERTDIR: /certs
      DOCKER_HOST: tcp://docker:2376
      DOCKER_TLS_VERIFY: "1"
      DOCKER_CERT_PATH: /certs/client
```
This tells docker where the socket is, and how to use TLS.

```{tip}
If you named your Docker-in-Docker service something
other than docker, you'll need to change it's hostname
to something and change the `DOCKER_HOST` to `tcp//$HOSTNAME:2376`.
```

Finally, we can run
```
docker compose build
docker compose up -d
docker compose logs client
```
To see that the client was able to access docker, without needing to
access the host system!

## Quick Personal Note
While researching, I found almost zero reference compose files
for setting up this kind of thing (maybe Docker-in-Docker is a bit niche)!
As a result, once I figured it out, I decided to make a sample repository
so that others would hopefully not spend as much time as I did hunting
down environment variables :)

One thing I haven't (yet) figured out how to do is getting the `docker`
service to also start a Docker Swarm upon startup - for some reason, that
breaks the setup on my machine. If anyone figures it out, please file
[an issue](https://github.com/JasonGrace2282/JasonGrace2282.github.io/issues/new)
and I'll update this blog post.


[^1]: Nowadays there are solutions like [sysbox](https://github.com/nestybox/sysbox)
  that remove the need for the container to be priviledged.
