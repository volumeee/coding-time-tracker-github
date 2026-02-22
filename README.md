<p align="center">
  <h1 align="center">📊 Coding Time Tracker</h1>
  <p align="center">
    <strong>Generate beautiful coding statistics cards for your GitHub profile README</strong>
  </p>
  <p align="center">
    <a href="https://coding-time-tracker-github.vercel.app/api/health">
      <img src="https://img.shields.io/badge/status-live-brightgreen?style=flat-square" alt="Status">
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License">
    </a>
    <a href="https://vercel.com">
      <img src="https://img.shields.io/badge/deployed%20on-Vercel-black?style=flat-square&logo=vercel" alt="Vercel">
    </a>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-features">Features</a> •
    <a href="#-examples">Examples</a> •
    <a href="#-api-reference">API Reference</a> •
    <a href="#-self-hosting">Self Hosting</a>
  </p>
</p>

---

## ⚡ Quick Start

Add this to your GitHub profile README — just replace `volumeee` with your GitHub username:

```markdown
![Coding Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee)
```

**Result:**

![Coding Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee)

---

## 🎯 Features

| Feature                    | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| 📊 **Language Breakdown**  | Top programming languages with colored progress bars |
| ⚡ **Framework Detection** | Auto-detects frameworks from config files            |
| 🎨 **4 Themes**            | Dark, Light, Radical, TokyoNight                     |
| 📐 **2 Layouts**           | Landscape (horizontal) & Portrait (vertical)         |
| 📱 **Responsive SVG**      | Auto-scales on desktop, tablet, and mobile           |
| 🌈 **Language Bar**        | GitHub-style combined proportion bar                 |
| 🔵 **Color Dots**          | Visual language indicators (like GitHub)             |
| 🔒 **Private Repos**       | Scans all repositories securely via GitHub token     |
| ⏱️ **Stat Pills**          | Total hours, repos scanned, time period              |
| 💬 **3 Formats**           | SVG Card, Code Block (text), JSON                    |
| 🚀 **Redis Cache**         | Upstash Redis for fast responses                     |
| ☁️ **Serverless**          | Deploys on Vercel in minutes                         |

---

## 🖼️ Examples

### 🌑 Dark Theme — Landscape (Default)

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=dark)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=dark)

---

### 📱 Portrait Layout

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&layout=portrait&theme=dark)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&layout=portrait&theme=dark)

---

### 🌃 TokyoNight Theme

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=tokyonight)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=tokyonight)

---

### 💜 Radical Theme

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=radical)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=radical)

---

### ☀️ Light Theme

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=light)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&theme=light)

---

### ⚙️ Minimal (No Title & Footer)

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&show_title=false&show_footer=false&theme=tokyonight)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&show_title=false&show_footer=false&theme=tokyonight)

---

### 🔢 Custom Language Count & Period

```markdown
![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&langs_count=5&period=180&theme=radical)
```

![Stats](https://coding-time-tracker-github.vercel.app/api?username=volumeee&langs_count=5&period=180&theme=radical)

---

### 💻 Code Block Format

You can also get a **text-based code block** for your README:

```
GET https://coding-time-tracker-github.vercel.app/api/code?username=volumeee
```

<!-- language_times_start -->

```text
Coding Time Tracker🙆‍♂️ — volumeee

Total Time: 38 hrs 21 mins  (365 days)
Repos scanned: 6

💻 Languages:
TypeScript   21 hrs 36 mins  ███████████░░░░░░░░░  56.30 %
JavaScript   10 hrs 3 mins   █████░░░░░░░░░░░░░░░  26.20 %
Python       3 hrs 21 mins   █░░░░░░░░░░░░░░░░░░░   8.70 %
HTML         2 hrs 44 mins   █░░░░░░░░░░░░░░░░░░░   7.20 %
PLpgSQL      0 hrs 19 mins   ░░░░░░░░░░░░░░░░░░░░   0.90 %
CSS          0 hrs 9 mins    ░░░░░░░░░░░░░░░░░░░░   0.40 %
Dockerfile   0 hrs 5 mins    ░░░░░░░░░░░░░░░░░░░░   0.30 %

⚡ Frameworks & Tools:
Express.js   ...
FastAPI      ...
```

<!-- language_times_end -->

---

## 📐 API Reference

### `GET /api` — SVG Stats Card

| Parameter         | Type     | Default      | Description                                 |
| ----------------- | -------- | ------------ | ------------------------------------------- |
| `username`        | `string` | **required** | GitHub username                             |
| `theme`           | `string` | `dark`       | `dark` · `light` · `radical` · `tokyonight` |
| `layout`          | `string` | `landscape`  | `landscape` · `portrait`                    |
| `width`           | `int`    | auto         | Card width in px (0 = auto)                 |
| `langs_count`     | `int`    | `8`          | Max languages to show (1-20)                |
| `period`          | `int`    | `365`        | Analysis period in days (7-3650)            |
| `max_repos`       | `int`    | `200`        | Max repos to scan (1-500)                   |
| `show_frameworks` | `bool`   | `true`       | Show frameworks section                     |
| `show_languages`  | `bool`   | `true`       | Show languages section                      |
| `show_title`      | `bool`   | `true`       | Show header & stat pills                    |
| `show_footer`     | `bool`   | `true`       | Show footer                                 |
| `no_cache`        | `bool`   | `false`      | Bypass cache                                |

### `GET /api/code` — Text Code Block

Returns plain-text stats for README markdown embedding.

| Parameter         | Type     | Default      | Description             |
| ----------------- | -------- | ------------ | ----------------------- |
| `username`        | `string` | **required** | GitHub username         |
| `langs_count`     | `int`    | `10`         | Max languages           |
| `period`          | `int`    | `365`        | Analysis period in days |
| `show_frameworks` | `bool`   | `true`       | Include frameworks      |

### `GET /api/json` — Raw JSON

Returns complete stats data as JSON for programmatic use.

| Parameter   | Type     | Default      | Description             |
| ----------- | -------- | ------------ | ----------------------- |
| `username`  | `string` | **required** | GitHub username         |
| `period`    | `int`    | `365`        | Analysis period in days |
| `max_repos` | `int`    | `200`        | Max repos to scan       |

### `GET /api/health` — Health Check

```json
{
  "status": "ok",
  "cache": "connected",
  "token": "configured"
}
```

---

## 🎨 Themes

| Theme        | Style                             |
| ------------ | --------------------------------- |
| `dark`       | 🌑 Dark background, blue accents  |
| `light`      | ☀️ White background, dark text    |
| `radical`    | 💜 Dark with magenta/pink accents |
| `tokyonight` | 🌃 Deep blue/purple palette       |

---

## 🚀 Self Hosting

### Prerequisites

- [Vercel Account](https://vercel.com) (free tier)
- [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` scope
- [Upstash Redis](https://upstash.com) (free tier, optional but recommended)

### Step 1: Create GitHub Token

1. Go to [github.com/settings/tokens](https://github.com/settings/personal-access-tokens/new)
2. **Token name:** `coding-time-tracker`
3. **Expiration:** 90 days (or custom)
4. **Repository access:** All repositories
5. **Permissions → Repository:**
   - `Contents` → Read-only
   - `Metadata` → Read-only
6. Click **Generate token** & copy it

### Step 2: Deploy to Vercel

1. **Fork** this repository
2. Go to [vercel.com/new](https://vercel.com/new) → Import your fork
3. **Root Directory:** leave as default (or set to `codestats_api` if nested)
4. **Environment Variables:**

   | Variable                   | Value                                   |
   | -------------------------- | --------------------------------------- |
   | `GITHUB_TOKEN`             | `ghp_your_token_here`                   |
   | `UPSTASH_REDIS_REST_URL`   | `https://your-db.upstash.io` (optional) |
   | `UPSTASH_REDIS_REST_TOKEN` | `your_redis_token` (optional)           |

5. Click **Deploy!** 🚀

### Step 3: Use It

```markdown
![My Coding Stats](https://your-app.vercel.app/api?username=YOUR_USERNAME)
```

### Run Locally

```bash
# Clone
git clone https://github.com/volumeee/coding-time-tracker-github.git
cd coding-time-tracker-github

# Install
pip install -r requirements.txt

# Set env vars
export GITHUB_TOKEN="ghp_xxx"
export UPSTASH_REDIS_REST_URL="https://xxx.upstash.io"     # optional
export UPSTASH_REDIS_REST_TOKEN="xxx"                        # optional

# Run
python3 -m uvicorn api.index:app --reload --port 8000

# Test
# http://localhost:8000/api?username=volumeee
# http://localhost:8000/api/health
```

---

## 📁 Project Structure

```
├── api/
│   ├── index.py              # FastAPI routes (/api, /api/code, /api/json, /api/health)
│   ├── config.py             # Language colors, themes, framework detection maps
│   └── services/
│       ├── cache.py           # Upstash Redis caching (12h TTL)
│       ├── github_service.py  # GitHub API client
│       ├── svg_generator.py   # SVG card & code block renderer
│       └── tracker.py         # Core stats calculation engine
├── vercel.json                # Vercel serverless config
├── requirements.txt           # Python dependencies
├── test_svg.py                # Visual test suite
├── LICENSE                    # MIT License
└── README.md
```

---

## 🔧 How It Works

```
GitHub API  →  Fetch Repos  →  Analyze Commits  →  Calculate Time
                                                          ↓
                    SVG/Text/JSON  ←  Generate Card  ←  Detect Frameworks
```

1. **Fetches ALL repos** (public + private) securely via the authenticated GitHub API
2. **Analyzes commits** using intelligent session-gap detection (filters auto-commits, merges, bots)
3. **Detects frameworks** by parsing config files (`package.json`, `requirements.txt`, etc.)
4. **Generates output** — Responsive SVG card, text block, or JSON
5. **Caches results** in Upstash Redis (12-hour TTL) for instant loading

### Supported Framework Detection

| Config File                | Frameworks Detected                                                     |
| -------------------------- | ----------------------------------------------------------------------- |
| `package.json`             | React, Next.js, Vue, Svelte, Angular, Express, Tailwind CSS, Vite, Jest |
| `requirements.txt`         | Django, Flask, FastAPI, PyTorch, TensorFlow, Pandas                     |
| `composer.json`            | Laravel, Symfony, WordPress                                             |
| `go.mod`                   | Gin, Echo, Fiber                                                        |
| `build.gradle` / `pom.xml` | Spring Boot, Android, Kotlin                                            |
| `pubspec.yaml`             | Flutter, Dart                                                           |
| `Gemfile`                  | Rails, Sinatra                                                          |

---

## 📄 License

[MIT License](LICENSE) — feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/volumeee">@volumeee</a>
  <br>
  Inspired by <a href="https://github.com/anuraghazra/github-readme-stats">github-readme-stats</a>
</p>
