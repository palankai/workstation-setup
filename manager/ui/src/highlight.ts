import type { HighlighterCore, LanguageInput, LanguageRegistration } from 'shiki/core'

/** Brewfiles are a tiny Ruby DSL; the full Ruby grammar is ~2 MB. */
const BREWFILE: LanguageRegistration = {
  name: 'brewfile',
  scopeName: 'source.brewfile',
  repository: {},
  patterns: [
    { match: '#.*$', name: 'comment.line.number-sign' },
    { match: '^\\s*(tap|brew|cask|mas|vscode|whalebrew|cargo|go|uv)\\b', captures: { 1: { name: 'keyword.control' } } },
    { begin: '"', end: '"', name: 'string.quoted.double' },
    { begin: "'", end: "'", name: 'string.quoted.single' },
    { match: '\\b[a-z_]+:(?!:)', name: 'constant.other.symbol' },
    { match: ':[a-z_]+\\b', name: 'constant.other.symbol' },
    { match: '\\b(true|false|nil)\\b', name: 'constant.language' },
    { match: '\\b\\d+\\b', name: 'constant.numeric' },
  ],
}

const LANGUAGES = {
  brewfile: () => BREWFILE,
  ruby: () => import('shiki/langs/ruby.mjs'),
  shellscript: () => import('shiki/langs/shellscript.mjs'),
  python: () => import('shiki/langs/python.mjs'),
  yaml: () => import('shiki/langs/yaml.mjs'),
  toml: () => import('shiki/langs/toml.mjs'),
  json: () => import('shiki/langs/json.mjs'),
  markdown: () => import('shiki/langs/markdown.mjs'),
} satisfies Record<string, () => LanguageInput>
type Language = keyof typeof LANGUAGES

let highlighter: Promise<HighlighterCore> | undefined

function load(): Promise<HighlighterCore> {
  highlighter ??= Promise.all([import('shiki/core'), import('shiki/engine/javascript')]).then(
    ([{ createHighlighterCore }, { createJavaScriptRegexEngine }]) =>
      createHighlighterCore({
        themes: [import('shiki/themes/github-light.mjs'), import('shiki/themes/github-dark.mjs')],
        langs: [],
        engine: createJavaScriptRegexEngine(),
      }),
  )
  return highlighter
}

const BY_EXTENSION: Record<string, Language> = {
  rb: 'ruby',
  sh: 'shellscript',
  bash: 'shellscript',
  zsh: 'shellscript',
  py: 'python',
  yaml: 'yaml',
  yml: 'yaml',
  toml: 'toml',
  json: 'json',
  md: 'markdown',
}

export function languageOf(file: string, code: string): Language | 'text' {
  const name = file.split('/').pop() ?? file
  if (name.endsWith('Brewfile')) return 'brewfile'
  if (/^\.?(zshrc|bashrc|zprofile|zshenv|profile)$/.test(name)) return 'shellscript'
  const extension = name.includes('.') ? name.split('.').pop()!.toLowerCase() : ''
  if (extension in BY_EXTENSION) return BY_EXTENSION[extension]
  const shebang = code.match(/^#!.*\b(sh|bash|zsh|python3?|ruby)\b/)
  if (shebang) return shebang[1].startsWith('python') ? 'python' : shebang[1] === 'ruby' ? 'ruby' : 'shellscript'
  return 'text'
}

/** HTML with both themes as CSS variables; index.css picks one per color scheme. */
export async function highlight(file: string, code: string): Promise<string> {
  const shiki = await load()
  const lang = languageOf(file, code)
  if (lang !== 'text' && !shiki.getLoadedLanguages().includes(lang)) {
    await shiki.loadLanguage(LANGUAGES[lang]())
  }
  return shiki.codeToHtml(code, {
    lang,
    themes: { light: 'github-light', dark: 'github-dark' },
    defaultColor: false,
  })
}
