name: check
on:
  workflow_dispatch:
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install playwright requests
      - run: playwright install --with-deps chromium
      - run: python check.py
        env:
          TARGET_URL: ${{ secrets.TARGET_URL }}
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
