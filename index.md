---
layout: default
title: Home
---

# AI Debate Project

This project generates AI-simulated debates on various topics. Each debate features multiple AI personas with different ideological perspectives engaging in moderated discussions.

## Latest Debates

<ul class="post-list">
  {% for post in site.posts limit:10 %}
    <li>
      <h2>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </h2>
      <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
      <p>{{ post.excerpt }}</p>
      <a href="{{ post.url | relative_url }}" class="read-more">Read full debate →</a>
    </li>
  {% endfor %}
</ul>