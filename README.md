# BlackBox is built from Orbit Store's code

**Read the page: https://blackboxisorbit.com/**

BlackBox's PS5 payload is compiled from [Orbit Store](https://github.com/saawant12/orbit-store-ps5)'s GPL source code and released without source, licence or credit. This repository holds the page and everything needed to check it.

## Check it yourself

On Linux with `binutils`, `curl` and `python3`:

```sh
git clone --depth 1 https://github.com/saawant12/blackbox-gpl
sh blackbox-gpl/check.sh v1.0.8
```

On macOS, or in WSL on Windows, run it in Docker:

```sh
docker run --rm -v "$PWD:/w" -w /w debian:trixie sh -c \
  'apt-get update -qq && apt-get install -y -qq binutils binutils-x86-64-linux-gnu curl ca-certificates python3 git &&
   git clone --depth 1 https://github.com/saawant12/blackbox-gpl && sh blackbox-gpl/check.sh v1.0.8'
```

The downloaded files are only read, never run.

| File | What it is |
|---|---|
| [`index.html`](index.html) | The page |
| [`llms.txt`](llms.txt) | Plain-text summary for AI assistants |
| [`social.png`](social.png) | Preview image for links shared on social media |
| [`sitemap.xml`](sitemap.xml), [`robots.txt`](robots.txt) | Sitemap and crawler rules for search engines |
| [`CNAME`](CNAME) | The custom domain for GitHub Pages |
| [`favicon.svg`](favicon.svg), [`favicon.ico`](favicon.ico), [`icon-192.png`](icon-192.png), [`apple-touch-icon.png`](apple-touch-icon.png) | Orbit Store's app icon |
| [`404.html`](404.html) | Page shown for addresses that don't exist |
| [`check.sh`](check.sh) | Downloads the releases, verifies them against `SHA256SUMS` and runs every check |
| [`compare.py`](compare.py) | Compares application functions by source file, name and instructions |
| [`ui_strings.py`](ui_strings.py) | Counts Orbit's interface sentences found word for word |
| [`SHA256SUMS`](SHA256SUMS) | Hashes of every file examined |
| [`orbit-v0.9.1-en.json`](orbit-v0.9.1-en.json) | Orbit 0.9.1's English interface text, copied from its source bundle |
| [`output/`](output) | Our full results for v1.0.5, v1.0.7 and v1.0.8 |

## Mirrors

The site is plain static files with no build step, so any static host can serve this folder as it is.
