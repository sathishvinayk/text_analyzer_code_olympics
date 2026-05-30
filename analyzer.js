#!/usr/bin/env node
// textool – One‑Loop Warrior (exactly one `for` in the whole program)
// Does: edit, analyze, format, search, replace – all inside the same loop

const fs = require('fs').promises
const readline = require('readline')

// ---------- state ----------
let filename = process.argv[2] || 'scratch.txt'
let lines = []

// load existing file
;(async () => {
  try {
    const data = await fs.readFile(filename, 'utf8')
    lines = data.split(/\r?\n/)
    // If file exists but is empty, start with one empty line
    if (lines.length === 0 || (lines.length === 1 && lines[0] === '' && data === '')) {
      lines = ['']
    }
  } catch {
    // File doesn't exist - start with one empty line
    lines = ['']
  }
  startRepl()
})()

// ---------- helpers (no explicit loops) ----------
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function wrapText(text, width) {
  if (!text) return ['']
  const collapsed = text.replace(/\s+/g, ' ')
  const wrapped = collapsed.replace(new RegExp(`(.{1,${width}})(\\s+|$)`, 'g'), '$1\n')
  return wrapped.split('\n')
}

// ---------- text operations ----------
const ops = {
  analyze(buf) {
    const text = buf.join('\n')
    const chars = text.length
    const words = (text.match(/\b\w+\b/g) || []).length
    const linesCount = buf.length
    let longest = ''
    text.replace(/^.*$/gm, (line) => { if(line.length > longest.length) longest = line })
    const freq = {}
    text.toLowerCase().replace(/[a-z]/g, (ch) => { freq[ch] = (freq[ch]||0)+1 })
    const top = Object.entries(freq).sort((a,b)=>b[1]-a[1]).slice(0,5)
    console.log(`\n📊 ${linesCount} lines, ${words} words, ${chars} chars`)
    console.log(`📏 Longest: ${longest.length} chars → "${longest.slice(0,50)}"`)
    if(top.length) console.log(`🔤 Top letters: ${top.map(([l,c])=>`${l.toUpperCase()}:${c}`).join(', ')}`)
    console.log('')
  },

  format(buf, width=72) {
    const whole = buf.join(' ')
    return wrapText(whole, width)
  },

  search(buf, pattern, caseSensitive=false) {
    try {
      const escaped = escapeRegex(pattern)
      const flags = caseSensitive ? '' : 'i'
      const re = new RegExp(`^.*${escaped}.*$`, flags + 'gm')
      const matches = []
      const text = buf.join('\n')
      text.replace(re, (match, offset) => {
        const before = text.substring(0, offset)
        const lineNum = (before.match(/\n/g) || []).length + 1
        matches.push(`${lineNum}: ${match}`)
      })
      if(matches.length) console.log(matches.join('\n'))
      else console.log('No matches')
    } catch(e) {
      console.log('Invalid search pattern')
    }
  },

  replace(buf, oldPattern, newText, caseSensitive=false) {
    try {
      const escaped = escapeRegex(oldPattern)
      const flags = caseSensitive ? '' : 'i'
      const re = new RegExp(escaped, flags + 'g')
      const newBuf = buf.map(line => line.replace(re, newText))
      return newBuf
    } catch(e) {
      console.log('Invalid replace pattern')
      return buf
    }
  }
}

// ---------- THE ONE AND ONLY LOOP ----------
async function startRepl() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  console.log(`\n📝 Editing: ${filename} (${lines.length} lines)`)
  console.log('Commands: :a, :f [width], :s pattern, :r old new, :i, :d, :n, :p, :j N, :w, :q, :help\n')

  let currentLine = 0

  function show() {
    const start = Math.max(0, currentLine-5)
    const end = Math.min(lines.length, currentLine+6)
    const visible = lines.slice(start, end)
    const numbered = visible.reduce((acc, line, idx) => {
      const lineNum = start + idx + 1
      const marker = (start + idx === currentLine) ? '→' : ' '
      const displayLine = line === '' ? '' : line
      return acc + `${marker} ${lineNum.toString().padStart(3)} ${displayLine}\n`
    }, '')
    console.log(`\n--- ${filename} ---\n${numbered}---`)
    process.stdout.write(`${currentLine+1}> `)
  }

  // Show the buffer immediately
  show()

  // THE ONLY LOOP
  for await (const input of rl) {
    if (input.startsWith(':')) {
      const parts = input.slice(1).trim().split(/\s+/)
      const cmd = parts[0]
      switch(cmd) {
        case 'a':
          ops.analyze(lines)
          break
        case 'f': {
          let width = parts[1] ? parseInt(parts[1]) : 72
          if (isNaN(width) || width < 1) {
            console.log('Invalid width. Using 72.')
            width = 72
          }
          lines = ops.format(lines, width)
          if (currentLine >= lines.length) currentLine = lines.length - 1
          console.log(`Formatted to ${width} columns.`)
          break
        }
        case 's': {
          const pattern = parts.slice(1).join(' ')
          if (!pattern) { console.log('Usage: :s pattern'); break }
          ops.search(lines, pattern, false)
          break
        }
        case 'r': {
          if (parts.length < 3) { console.log('Usage: :r old new'); break }
          const oldPattern = parts[1]
          const newText = parts.slice(2).join(' ')
          lines = ops.replace(lines, oldPattern, newText, false)
          console.log('Replaced.')
          break
        }
        case 'i':
          lines.splice(currentLine+1, 0, '')
          currentLine++
          break
        case 'd':
          if (lines.length === 1 && lines[0] === '') {
            console.log('Cannot delete last remaining line')
            break
          }
          lines.splice(currentLine, 1)
          if (currentLine >= lines.length) currentLine = lines.length - 1
          if (currentLine < 0 && lines.length) currentLine = 0
          break
        case 'n':
          if (currentLine < lines.length - 1) currentLine++
          break
        case 'p':
          if (currentLine > 0) currentLine--
          break
        case 'j': {
          const num = parseInt(parts[1])
          if (!isNaN(num) && num >= 1 && num <= lines.length) currentLine = num - 1
          else console.log(`Line number must be 1-${lines.length}`)
          break
        }
        case 'w':
          await fs.writeFile(filename, lines.join('\n'))
          console.log('Saved.')
          break
        case 'q':
          console.log('Bye.')
          rl.close()
          process.exit(0)
        case 'help':
          console.log(`
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
`)
          break
        default:
          console.log('Unknown command. Try :help')
      }
    } else {
      // FIX: Handle Enter key (empty input) correctly
      if (input === '') {
        // User pressed Enter without typing - move to next line or append new line
        if (currentLine === lines.length - 1) {
          // At last line, append a new empty line
          lines.push('')
          currentLine++
        } else {
          // Not at last line, just move down
          currentLine++
        }
      } else {
        // User typed something - replace current line
        lines[currentLine] = input
        // Move to next line if not at end
        if (currentLine < lines.length - 1) {
          currentLine++
        } else {
          // At last line, append new empty line after editing
          lines.push('')
          currentLine++
        }
      }
    }
    show()
  }
}