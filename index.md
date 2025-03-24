---
layout: default
title: Home
---

# AI Debate Project

This project generates AI-simulated debates on various topics. Each debate features multiple AI personas with different ideological perspectives engaging in moderated discussions.

## About the Project

DebateAI explores how artificial intelligence can simulate complex social discourse across the political spectrum. The system orchestrates structured debates between AI agents representing distinct viewpoints, examining how different perspectives interact and whether AI can generate nuanced arguments on controversial topics.

**New debates are automatically generated every day at 12:00 UTC** through our automated workflow, providing fresh content to explore how AI handles different topics and perspectives.

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