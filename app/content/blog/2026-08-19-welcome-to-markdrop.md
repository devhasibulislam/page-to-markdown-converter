---
title: "Welcome to MarkDrop"
slug: "welcome-to-markdrop"
date: 2026-08-19
author: "Hasibul Islam"
excerpt: "Why we built MarkDrop, how it works, and what it's for."
tags: [announcement, markdown]
---

MarkDrop turns any web page you're looking at into clean Markdown. Not "any URL
we can reach" — any page you can see, including the JavaScript-heavy dashboards,
the paywalled articles, and the internal wikis that live behind a login.

## The problem

Every tool that "converts a URL to Markdown" runs into the same wall: the modern
web renders in the browser. Server-side fetchers get an empty shell of HTML and
a `<script>` tag. Users get a `.md` file with one sentence in it.

## The fix

Do the rendering in the browser that already rendered it. The MarkDrop extension
reads the fully-hydrated DOM and hands it to a small Python service that
extracts the main content using trafilatura. You get clean Markdown back —
preview, download, or email.

## What's inside

- A **browser extension** for Chrome, Edge, Firefox, Brave, Opera, Arc, Vivaldi
- A **Python API** built with FastAPI (accepts either raw HTML or a URL)
- A **landing page** with a "try it" box that works for public URLs
- No account, no analytics, no cookies

## Try it now

Head back to the [home page](/) and paste a URL into the "Try it with a URL" box.
Or download the extension and click it on any page.

We're just getting started. More posts on how MarkDrop works internally are on
the way.
