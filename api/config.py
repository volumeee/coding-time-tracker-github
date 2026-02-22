"""Configuration constants for CodeStats API."""
import os

# === API Settings ===
GITHUB_API_BASE = "https://api.github.com"
GITLAB_API_BASE = "https://gitlab.com/api/v4"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")

# === Processing Settings ===
MAX_WORKERS = 8
MAX_REPOS = 50
SESSION_GAP_HOURS = 2
BASE_COMMIT_MINUTES = 30
CACHE_TTL = 43200  # 12 hours

# === Language Colors (GitHub official) ===
LANGUAGE_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "PHP": "#4F5D95",
    "Kotlin": "#A97BFF", "Java": "#b07219", "C++": "#f34b7d",
    "C": "#555555", "C#": "#178600", "Vue": "#41b883",
    "Svelte": "#ff3e00", "Shell": "#89e051", "Dockerfile": "#384d54",
    "Go": "#00ADD8", "Ruby": "#701516", "Rust": "#dea584",
    "Swift": "#F05138", "Dart": "#00B4AB", "SCSS": "#c6538c",
}

# === Framework Colors ===
FRAMEWORK_COLORS = {
    "React": "#61dafb", "React Native": "#61dafb", "Next.js": "#808080",
    "Nuxt.js": "#00dc82", "Vue.js": "#41b883", "Angular": "#dd1b16",
    "Svelte": "#ff3e00", "Express.js": "#808080", "NestJS": "#e0234e",
    "Fastify": "#808080", "Electron": "#47848f", "Capacitor": "#119eff",
    "Ionic": "#3880ff", "Cordova": "#808080", "Tailwind CSS": "#06b6d4",
    "Bootstrap": "#7952b3", "Sass": "#cf649a", "Redux": "#764abc",
    "Pinia": "#ffd859", "Vite": "#646cff", "Webpack": "#8dd6f9",
    "Jest": "#c21325", "Vitest": "#6e9f18", "Cypress": "#69d3a7",
    "Prisma": "#5567e0", "Mongoose": "#880000", "Django": "#44b78b",
    "FastAPI": "#009688", "Flask": "#808080", "Laravel": "#ff2d20",
    "Spring Boot": "#6db33f", "Android SDK": "#3ddc84", "Flutter": "#02569b",
    "Rails": "#cc0000", "Scrapy": "#60a839", "PyTorch": "#ee4c2c",
    "TensorFlow": "#ff6f00", "Pandas": "#150458", "NumPy": "#4d77cf",
}

# === Framework detection maps ===
PACKAGE_JSON_FW = {
    "react": "React", "react-native": "React Native", "expo": "React Native",
    "next": "Next.js", "nuxt": "Nuxt.js", "vue": "Vue.js",
    "svelte": "Svelte", "@angular/core": "Angular",
    "express": "Express.js", "@nestjs/core": "NestJS", "fastify": "Fastify",
    "koa": "Koa", "jquery": "jQuery",
    "electron": "Electron", "@capacitor/core": "Capacitor",
    "@capacitor/cli": "Capacitor", "@ionic/core": "Ionic",
    "@ionic/vue": "Ionic", "@ionic/react": "Ionic",
    "@ionic/angular": "Ionic", "cordova": "Cordova",
    "tailwindcss": "Tailwind CSS", "bootstrap": "Bootstrap",
    "bulma": "Bulma", "sass": "Sass", "node-sass": "Sass",
    "redux": "Redux", "@reduxjs/toolkit": "Redux",
    "pinia": "Pinia", "vuex": "Vuex", "mobx": "MobX",
    "webpack": "Webpack", "vite": "Vite", "rollup": "Rollup",
    "parcel": "Parcel", "jest": "Jest", "cypress": "Cypress",
    "mocha": "Mocha", "vitest": "Vitest",
    "prisma": "Prisma", "@prisma/client": "Prisma",
    "mongoose": "Mongoose", "typeorm": "TypeORM", "sequelize": "Sequelize",
}

REQUIREMENTS_FW = {
    "django": "Django", "fastapi": "FastAPI", "flask": "Flask",
    "tornado": "Tornado", "pandas": "Pandas", "numpy": "NumPy",
    "scikit-learn": "Scikit-learn", "tensorflow": "TensorFlow",
    "torch": "PyTorch", "pytorch": "PyTorch", "keras": "Keras",
    "matplotlib": "Matplotlib", "streamlit": "Streamlit",
    "pytest": "Pytest", "sqlalchemy": "SQLAlchemy",
    "scrapy": "Scrapy", "kivy": "Kivy", "flet": "Flet",
}

COMPOSER_FW = {
    "laravel/framework": "Laravel", "symfony/symfony": "Symfony",
    "codeigniter4/framework": "CodeIgniter", "yiisoft/yii2": "Yii",
    "cakephp/cakephp": "CakePHP", "livewire/livewire": "Livewire",
}

GO_MOD_FW = {
    "github.com/gin-gonic/gin": "Gin", "github.com/gofiber/fiber": "Fiber",
    "github.com/labstack/echo": "Echo", "gorm.io/gorm": "GORM",
}

BUILD_FW = {"spring-boot": "Spring Boot", "hibernate": "Hibernate"}

# === SVG Themes ===
THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#0969da",
        "text": "#24292f", "muted": "#656d76", "bar_bg": "#eaeef2",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#58a6ff",
        "text": "#c9d1d9", "muted": "#8b949e", "bar_bg": "#21262d",
    },
    "radical": {
        "bg": "#141321", "border": "#fe428e", "title": "#fe428e",
        "text": "#a9fef7", "muted": "#f8d847", "bar_bg": "#2a2139",
    },
    "tokyonight": {
        "bg": "#1a1b27", "border": "#70a5fd", "title": "#70a5fd",
        "text": "#38bdae", "muted": "#a9b1d6", "bar_bg": "#24283b",
    },
}
