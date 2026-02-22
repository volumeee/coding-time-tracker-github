<p align="center">
  <h1 align="center">📊 Coding Time Tracker</h1>
  <p align="center">
    <strong>Generate beautiful coding statistics cards for your GitHub profile README</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-features">Features</a> •
    <a href="#-api-reference">API Reference</a> •
    <a href="#-self-hosting">Self Hosting</a> •
    <a href="#-themes">Themes</a>
  </p>
</p>

---

## ⚡ Quick Start

Add this to your GitHub profile README:

```markdown
![Coding Stats](https://YOUR-VERCEL-URL.vercel.app/api?username=YOUR_GITHUB_USERNAME)
```

**That's it!** Replace `YOUR-VERCEL-URL` with your deployed Vercel URL and `YOUR_GITHUB_USERNAME` with your GitHub username.

---

## 🎯 Features

- � **Language Breakdown** — Shows your top programming languages with colored progress bars
- ⚡ **Framework Detection** — Auto-detects frameworks from `package.json`, `requirements.txt`, `composer.json`, `go.mod`, etc.
- 🎨 **4 Themes** — Dark, Light, Radical, TokyoNight
- 📐 **2 Layouts** — Landscape (horizontal) & Portrait (vertical)
- 📱 **Responsive** — Auto-scales on desktop, tablet, and mobile
- 🔄 **3 Output Formats** — SVG Card, Code Block (text), JSON
- ⏱️ **Stat Pills** — Total hours, repos scanned, time period
- 🌈 **Language Bar** — GitHub-style combined proportion bar
- 🔵 **Color Dots** — Visual language indicators (like GitHub)
- 🚀 **Redis Caching** — Upstash Redis for fast responses
- ☁️ **Serverless** — Deploys on Vercel in minutes

---

## 🖼️ Examples

### Landscape Layout (Default)

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&theme=dark)
```

### Portrait Layout

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&layout=portrait&theme=dark)
```

### TokyoNight Theme

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&theme=tokyonight)
```

### Radical Theme

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&theme=radical)
```

### Light Theme

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&theme=light)
```

### Languages Only (No Frameworks)

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&show_frameworks=false)
```

### Minimal (No Title, No Footer)

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&show_title=false&show_footer=false&theme=tokyonight)
```

### Custom Width & Language Count

```markdown
![Stats](https://YOUR-URL.vercel.app/api?username=volumeee&width=800&langs_count=10&period=180)
```

### Code Block Format

You can also get a **text-based code block** for your README:

<!-- language_times_start -->

```text
Coding Time Tracker🙆‍♂️ — volumeee

Total Time: 181 hrs 24 mins  (1454 days)
Repos scanned: 15

💻 Languages:
TypeScript   57 hrs 37 mins  ██████░░░░░░░░░░░░░░  31.82 %
JavaScript   41 hrs 46 mins  ████░░░░░░░░░░░░░░░░  23.07 %
C++          34 hrs 19 mins  ███░░░░░░░░░░░░░░░░░  18.96 %
Python       30 hrs 55 mins  ███░░░░░░░░░░░░░░░░░  17.08 %
HTML         8 hrs 10 mins   ░░░░░░░░░░░░░░░░░░░░   4.52 %
CSS          4 hrs 4 mins    ░░░░░░░░░░░░░░░░░░░░   2.25 %
Java         3 hrs 34 mins   ░░░░░░░░░░░░░░░░░░░░   1.98 %
PHP          0 hrs 34 mins   ░░░░░░░░░░░░░░░░░░░░   0.31 %

⚡ Frameworks & Tools:
Express.js     29 hrs 1 mins   ███░░░░░░░░░░░░░░░░░  16.03 %
React          26 hrs 6 mins   ██░░░░░░░░░░░░░░░░░░  14.42 %
Tailwind CSS   18 hrs 34 mins  ██░░░░░░░░░░░░░░░░░░  10.26 %
React Native   17 hrs 1 mins   █░░░░░░░░░░░░░░░░░░░   9.41 %
Vite           9 hrs 3 mins    ░░░░░░░░░░░░░░░░░░░░   5.00 %
Jest           3 hrs 23 mins   ░░░░░░░░░░░░░░░░░░░░   1.88 %
```

<!-- language_times_end -->

Fetch the code block via API:

```
GET /api/code?username=volumeee
```

---

## 📐 API Reference

### `GET /api` — SVG Card

| Parameter         | Default      | Description                                     |
| ----------------- | ------------ | ----------------------------------------------- |
| `username`        | **required** | GitHub username                                 |
| `theme`           | `dark`       | Theme: `dark`, `light`, `radical`, `tokyonight` |
| `layout`          | `landscape`  | Layout: `landscape`, `portrait`                 |
| `width`           | auto         | Card width in px (`300`-`1200`, `0` = auto)     |
| `langs_count`     | `8`          | Max languages to show (`1`-`20`)                |
| `period`          | `365`        | Analysis period in days (`7`-`3650`)            |
| `max_repos`       | `50`         | Max repos to scan (`1`-`100`)                   |
| `show_frameworks` | `true`       | Show frameworks section                         |
| `show_languages`  | `true`       | Show languages section                          |
| `show_title`      | `true`       | Show title & stat pills                         |
| `show_footer`     | `true`       | Show footer                                     |
| `no_cache`        | `false`      | Force refresh (bypass cache)                    |

### `GET /api/code` — Text Code Block

Returns a plain-text code block format, perfect for README markdown.

| Parameter         | Default      | Description             |
| ----------------- | ------------ | ----------------------- |
| `username`        | **required** | GitHub username         |
| `langs_count`     | `10`         | Max languages           |
| `period`          | `365`        | Analysis period in days |
| `show_frameworks` | `true`       | Include frameworks      |

### `GET /api/json` — Raw JSON Data

Returns raw stats data as JSON for programmatic use.

| Parameter   | Default      | Description             |
| ----------- | ------------ | ----------------------- |
| `username`  | **required** | GitHub username         |
| `period`    | `365`        | Analysis period in days |
| `max_repos` | `50`         | Max repos to scan       |

### `GET /api/health` — Health Check

Returns server status, cache availability, and token configuration.

---

## 🎨 Themes

| Theme        | Preview                       |
| ------------ | ----------------------------- |
| `dark`       | Dark background, blue accents |
| `light`      | White background, dark text   |
| `radical`    | Dark with magenta accents     |
| `tokyonight` | Deep blue/purple palette      |

---

## � Self Hosting

### Prerequisites

- [Vercel Account](https://vercel.com) (free)
- [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` scope
- [Upstash Redis](https://upstash.com) database (free tier, optional but recommended)

### Deploy to Vercel

1. **Fork this repository**

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your forked repo
   - Set the Root Directory to `codestats_api` (or project root if you only have the API files)

3. **Set Environment Variables** in Vercel:

   | Variable                   | Required | Description                  |
   | -------------------------- | -------- | ---------------------------- |
   | `GITHUB_TOKEN`             | ✅ Yes   | GitHub Personal Access Token |
   | `UPSTASH_REDIS_REST_URL`   | Optional | Upstash Redis REST URL       |
   | `UPSTASH_REDIS_REST_TOKEN` | Optional | Upstash Redis REST Token     |

4. **Deploy!** — Vercel will auto-deploy

5. **Use your URL:**
   ```markdown
   ![Stats](https://your-app.vercel.app/api?username=YOUR_USERNAME)
   ```

### Run Locally

```bash
# Clone
git clone https://github.com/volumeee/coding-time-tracker-github.git
cd coding-time-tracker-github/codestats_api

# Install dependencies
pip install -r requirements.txt

# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Run development server
uvicorn api.index:app --reload --port 8000

# Test
open http://localhost:8000/api?username=YOUR_USERNAME
```

---

## 📁 Project Structure

```
codestats_api/
├── api/
│   ├── index.py              # FastAPI endpoints
│   ├── config.py             # Colors, themes, framework maps
│   └── services/
│       ├── cache.py           # Upstash Redis caching
│       ├── github_service.py  # GitHub API client
│       ├── svg_generator.py   # SVG & code block renderer
│       └── tracker.py         # Core stats calculation
├── vercel.json                # Vercel config
├── requirements.txt           # Python dependencies
├── test_svg.py                # Test suite
└── README.md
```

---

## 🔧 How It Works

1. **Fetches repos** via GitHub API for the given username
2. **Analyzes commits** to calculate coding time per language (session-based detection)
3. **Detects frameworks** by parsing config files (`package.json`, `requirements.txt`, etc.)
4. **Generates SVG** with responsive layout, animated bars, and themed styling
5. **Caches results** in Upstash Redis (12-hour TTL) to minimize API calls

### Supported Framework Detection

| Config File                | Frameworks Detected                                                           |
| -------------------------- | ----------------------------------------------------------------------------- |
| `package.json`             | React, Next.js, Vue, Svelte, Angular, Express, Tailwind CSS, Vite, Jest, etc. |
| `requirements.txt`         | Django, Flask, FastAPI, PyTorch, TensorFlow, Pandas, etc.                     |
| `composer.json`            | Laravel, Symfony, WordPress, etc.                                             |
| `go.mod`                   | Gin, Echo, Fiber, etc.                                                        |
| `build.gradle` / `pom.xml` | Spring Boot, Android, Kotlin, etc.                                            |
| `pubspec.yaml`             | Flutter, Dart                                                                 |
| `Gemfile`                  | Rails, Sinatra                                                                |

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🙏 Credits

Built with ❤️ by [@volumeee](https://github.com/volumeee)

Inspired by [github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
