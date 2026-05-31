# Professional Builder code Olympics

A lightweight terminal-based text processing workstation built for **CODE_OLYMPICS 2026**.

# Live Demo
-> https://textanalyzercodeolympics--sathishvinayk.replit.app/

## Competition Combination

| Dimension | Assigned Constraint |
|------------|------------|
| D1 | One-Loop Warrior |
| D2 | Professional Builder (500 lines) |
| D3 | Text Processing |
| D4 | JavaScript |

## Project Overview

Textool is a command-line text processing utility that combines:

- Text editing
- Search
- Search and replace
- Text formatting
- Document analysis
- File navigation
- File persistence

into a single terminal application.

The goal was to build something genuinely useful rather than a toy demonstration while respecting the competition constraints.

---

# Features

## Editing

- Edit current line
- Insert new lines
- Delete lines
- Navigate through text
- Jump to a specific line

## Search

- Case-insensitive text search
- Line-numbered search results
- Safe handling of special characters

## Replace

- Replace all occurrences of a target string
- Supports multi-line documents

## Formatting

- Word-wrap text to a configurable width
- Basic whitespace normalization

## Analysis

Provides document statistics:

- Line count
- Word count
- Character count
- Longest line
- Most frequent letters

## File Operations

- Load existing files
- Save modifications
- Create new text documents

---

# Commands

| Command | Description |
|----------|-------------|
| `:a` | Analyze current document |
| `:f [width]` | Format text using specified width |
| `:s pattern` | Search for text |
| `:r old new` | Replace text |
| `:i` | Insert blank line |
| `:d` | Delete current line |
| `:n` | Move to next line |
| `:p` | Move to previous line |
| `:j N` | Jump to line N |
| `:w` | Save file |
| `:q` | Quit |
| `:help` | Show help |

Typing any text without a command edits the current line.

---

# Running

```bash
node analyzer.js sample.txt
```

```For rosetta (Second language) Python
python3 rosetta_stone.py sample.txt
```

If the file exists, it is loaded.

If it does not exist, a new document is created.

---

# Constraint Strategy

## One-Loop Warrior

The primary challenge was the requirement:

> Maximum one loop in the entire program.

The solution uses a single explicit loop:

```javascript
for await (const input of rl)
```

This loop drives the entire application lifecycle.

Where iteration was required elsewhere, JavaScript built-in methods and regular expression engines were used instead of additional explicit loop constructs.

---

# JavaScript-Specific Challenges

Several features that would normally be implemented with traditional iteration had to be redesigned using:

- Regular expressions
- String transformations
- Built-in collection methods
- Callback-driven processing

The result is a solution that leans heavily into JavaScript's strengths rather than fighting the language.

---

# Design Decisions

## Why a text processing tool?

The competition explicitly asks participants to build something useful.

A text-processing utility offers practical value while naturally supporting multiple features:

- Editing
- Searching
- Replacing
- Formatting
- Analysis

## Why terminal-based?

- Keeps the codebase compact
- Requires no external dependencies
- Works consistently across environments
- Allows focus on functionality rather than UI code

---

# Honest Self-Assessment

Strengths:

- Fully functional text-processing workflow
- Single explicit loop architecture
- Good feature coverage for the domain
- No external dependencies
- Easy to run and test

Limitations:

- Not intended to compete with full-featured editors
- Word wrapping is intentionally simple
- Search functionality is text-focused rather than regex-focused
- Large files are not heavily optimized

---

# What I Learned

The One-Loop Warrior constraint forced the design toward an event-driven model where one central loop orchestrates all behavior and everything else becomes transformation logic.

---
