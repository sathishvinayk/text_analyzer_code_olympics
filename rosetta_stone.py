#!/usr/bin/env python3
# textool – One-Loop Warrior (exactly one while loop in the whole program)
# Does: edit, analyze, format, search, replace – all inside the same loop
# Rosetta Stone: Python version of JavaScript implementation
import sys
import re
import os
# ---------- state ----------
filename = sys.argv[1] if len(sys.argv) > 1 else 'scratch.txt'
lines = []

# load existing file
try:
    with open(filename, 'r') as f:
        content = f.read()
        lines = content.splitlines()
        # If file exists but is empty, start with one empty line
        if len(lines) == 0 or (len(lines) == 1 and lines[0] == '' and content == ''):
            lines = ['']
except FileNotFoundError:
    # File doesn't exist - start with one empty line
    lines = ['']

# ---------- helpers (no explicit loops) ----------
def escape_regex(s):
    return re.escape(s)

def wrap_text(text, width):
    if not text:
        return ['']
    # collapse multiple spaces
    collapsed = re.sub(r'\s+', ' ', text)
    # wrap at width
    pattern = r'(.{1,' + str(width) + r'})(\s+|$)'
    wrapped = re.sub(pattern, r'\1\n', collapsed)
    return wrapped.split('\n')

# ---------- text operations ----------
class Ops:
    @staticmethod
    def analyze(buf):
        text = '\n'.join(buf)
        chars = len(text)
        words = len(re.findall(r'\b\w+\b', text))
        lines_count = len(buf)
        
        # find longest line
        longest = ''
        def update_longest(match):
            nonlocal longest
            line = match.group(0)
            if len(line) > len(longest):
                longest = line
            return ''
        re.sub(r'^.*$', update_longest, text, flags=re.MULTILINE)
        
        # letter frequency
        freq = {}
        def count_letters(match):
            ch = match.group(0)
            freq[ch] = freq.get(ch, 0) + 1
            return ''
        re.sub(r'[a-z]', count_letters, text.lower())
        
        # top 5 letters
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"\n📊 {lines_count} lines, {words} words, {chars} chars")
        print(f"📏 Longest: {len(longest)} chars → \"{longest[:50]}\"")
        if top:
            letters_str = ', '.join([f"{l.upper()}:{c}" for l, c in top])
            print(f"🔤 Top letters: {letters_str}")
        print()

    @staticmethod
    def format(buf, width=72):
        whole = ' '.join(buf)
        return wrap_text(whole, width)

    @staticmethod
    def search(buf, pattern, case_sensitive=False):
        try:
            escaped = escape_regex(pattern)
            flags = 0 if case_sensitive else re.IGNORECASE
            # multiline search
            regex = re.compile(r'^.*' + escaped + r'.*$', flags | re.MULTILINE)
            matches = []
            text = '\n'.join(buf)
            
            def collect_matches(match):
                matches.append(match.group(0))
                return ''
            
            re.sub(regex, collect_matches, text)
            
            # add line numbers
            numbered = []
            for i, line in enumerate(buf):
                if re.search(regex, line):
                    numbered.append(f"{i+1}: {line}")
            
            if numbered:
                print('\n'.join(numbered))
            else:
                print('No matches')
        except Exception as e:
            print('Invalid search pattern')

    @staticmethod
    def replace(buf, old_pattern, new_text, case_sensitive=False):
        try:
            escaped = escape_regex(old_pattern)
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(escaped, flags)
            new_buf = [regex.sub(new_text, line) for line in buf]
            return new_buf
        except Exception as e:
            print('Invalid replace pattern')
            return buf

ops = Ops()

# ---------- THE ONE AND ONLY LOOP ----------
def start_repl():
    global lines
    
    print(f"\n📝 Editing: {filename} ({len(lines)} lines)")
    print('Commands: :a, :f [width], :s pattern, :r old new, :i, :d, :n, :p, :j N, :w, :q, :help\n')
    
    current_line = 0
    
    def show():
        nonlocal current_line
        start = max(0, current_line - 5)
        end = min(len(lines), current_line + 6)
        visible = lines[start:end]
        
        # build numbered display
        output_lines = []
        for idx, line in enumerate(visible):
            line_num = start + idx + 1
            marker = '→' if (start + idx == current_line) else ' '
            display_line = '' if line == '' else line
            output_lines.append(f"{marker} {line_num:3} {display_line}")
        
        print(f"\n--- {filename} ---")
        print('\n'.join(output_lines))
        print("---")
        sys.stdout.write(f"{current_line+1}> ")
        sys.stdout.flush()
    
    # Show the buffer immediately on screen
    show()
    
    # THE ONLY LOOP
    while True:
        try:
            user_input = input()
        except EOFError:
            break
        
        if user_input.startswith(':'):
            parts = user_input[1:].strip().split()
            cmd = parts[0] if parts else ''
            
            if cmd == 'a':
                ops.analyze(lines)
            elif cmd == 'f':
                width = int(parts[1]) if len(parts) > 1 else 72
                if width < 1:
                    print('Invalid width. Using 72.')
                    width = 72
                lines = ops.format(lines, width)
                if current_line >= len(lines):
                    current_line = len(lines) - 1
                print(f"Formatted to {width} columns.")
            elif cmd == 's':
                pattern = ' '.join(parts[1:]) if len(parts) > 1 else ''
                if not pattern:
                    print('Usage: :s pattern')
                else:
                    ops.search(lines, pattern, False)
            elif cmd == 'r':
                if len(parts) < 3:
                    print('Usage: :r old new')
                else:
                    old_pattern = parts[1]
                    new_text = ' '.join(parts[2:])
                    lines = ops.replace(lines, old_pattern, new_text, False)
                    print('Replaced.')
            elif cmd == 'i':
                lines.insert(current_line + 1, '')
                current_line += 1
            elif cmd == 'd':
                if len(lines) == 1 and lines[0] == '':
                    print('Cannot delete last remaining line')
                else:
                    lines.pop(current_line)
                    if current_line >= len(lines):
                        current_line = len(lines) - 1
                    if current_line < 0 and lines:
                        current_line = 0
            elif cmd == 'n':
                if current_line < len(lines) - 1:
                    current_line += 1
            elif cmd == 'p':
                if current_line > 0:
                    current_line -= 1
            elif cmd == 'j':
                if len(parts) > 1:
                    try:
                        num = int(parts[1])
                        if 1 <= num <= len(lines):
                            current_line = num - 1
                        else:
                            print(f"Line number must be 1-{len(lines)}")
                    except ValueError:
                        print(f"Line number must be 1-{len(lines)}")
                else:
                    print("Usage: :j N")
            elif cmd == 'w':
                try:
                    with open(filename, 'w') as f:
                        f.write('\n'.join(lines))
                    print('Saved.')
                except Exception as e:
                    print(f'Error saving: {e}')
            elif cmd == 'q':
                print('Bye.')
                sys.exit(0)
            elif cmd == 'help':
                print("""
Commands:
  :a              analyze stats
  :f [width]      word wrap (default 72)
  :s pattern      search (with line numbers)
  :r old new      replace all occurrences
  :i              insert blank line after current
  :d              delete current line
  :n              next line
  :p              previous line
  :j N            jump to line N
  :w              save
  :q              quit
  :help           this help
Type to edit current line.
""")
            else:
                print('Unknown command. Try :help')
        else:
            # Handle Enter key (empty input) correctly
            if user_input == '':
                # Pressed Enter without typing - move to next line or append new line
                if current_line == len(lines) - 1:
                    # At last line, append a new empty line
                    lines.append('')
                    current_line += 1
                else:
                    # Not at last line, just move down
                    current_line += 1
            else:
                # User typed something - replace current line
                lines[current_line] = user_input
                # Move to next line if not at end
                if current_line < len(lines) - 1:
                    current_line += 1
                else:
                    # At last line, append new empty line after editing
                    lines.append('')
                    current_line += 1
        
        show()
# run it
if __name__ == '__main__':
    start_repl()