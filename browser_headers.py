import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
]

REFERRERS = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
    "https://duckduckgo.com/",
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "ar,en;q=0.9",
    "es-ES,es;q=0.9,en;q=0.8",
]

SCREEN_RESOLUTIONS = [
    "1920x1080",
    "1366x768",
    "1440x900",
    "1536x864",
    "1280x720",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_referrer():
    return random.choice(REFERRERS)

def get_random_language():
    return random.choice(ACCEPT_LANGUAGES)

def get_random_screen_resolution():
    return random.choice(SCREEN_RESOLUTIONS)
