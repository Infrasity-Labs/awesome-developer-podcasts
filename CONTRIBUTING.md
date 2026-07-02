# Contributing to Awesome Developer Podcasts

Thank you for considering contributing to the **Awesome Developer Podcasts** directory! 

This repo is maintained by [Infrasity](https://infrasity.com) and updated automatically via GitHub Actions.

This document serves as a set of guidelines for contributing to the repository.

---
## Ways to Contribute
### 1. Submit a Podcast Manually

If you know of a developer podcast that isn't listed here yet, you can easily add it yourself!

1. **Fork the repository** to your own GitHub account.
2. Open `README.md` and locate the correct **Category** (e.g., Web Development, Cloud Computing, etc.).
3. Add a new row to the Markdown table in alphabetical order.
4. Follow the exact table format:
   ```markdown
   | **Podcast Name** | Description | [↗](link) |
   ```
5. Submit a **Pull Request** with a short description of the podcast you added!

---

### 2. The Automated Fetchers (Architecture)

This repository uses automated Python scripts to fetch podcasts from major directories (like PodcastIndex, Feedspot, etc.) via GitHub Actions. We use a **stateless architecture**:

1. **Fetchers (`fetchers/*.py`)**: Scrapers that pull podcasts and output them as JSON files into the `data/` directory.
2. **Aggregator (`aggregate.py`)**: A script that reads all the JSON files in `data/`, deduplicates them, automatically categorizes them, dynamically generates the Table of Contents, and builds the final `README.md` file.

If you are a developer, you can contribute by adding new automated scrapers!
* To add a new source, simply create a new Python script (e.g., `fetchers/my_source.py`) that parses a website and saves a JSON file (e.g., `data/my_source.json`) containing a list of dictionaries with `title`, `description`, and `link` keys.
* The GitHub Action (`.github/workflows/fetch_podcasts.yml`) will automatically detect and run your script, aggregate its data, and update the directory.

---

### 3. Improve the Code

If you want to improve existing Python fetchers, fix bugs, or add new ones, here is how you can set up the project locally on your machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Infrasity-Labs/awesome-developer-podcasts.git
   cd awesome-developer-podcasts
   ```

2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Run a fetcher locally to test your changes**:
   ```bash
   python fetchers/podcastindex.py
   ```

4. **Run the aggregator to update the README**:
   ```bash
   python aggregate.py
   ```

5. Check that the `README.md` file updated correctly with your changes, and then submit a Pull Request! *(Note: The `data/` directory should not be committed)*.

---

### 4. Pull Request Guidelines

* **Keep it relevant:** Only add podcasts that are strictly relevant to software engineers, developers, data scientists, or IT professionals.
* **No spam:** Please do not add promotional spam or dead podcasts that haven't published an episode in years.
* **Clean Code:** If you are contributing Python code to the `fetchers/` directory, please ensure your code handles network errors gracefully and uses Playwright/BeautifulSoup correctly.

---

### 5. Found a Bug?

If you spot a broken link, a dead podcast, or a bug in one of our Python fetchers, please [open an Issue](https://github.com/Infrasity-Labs/awesome-developer-podcasts/issues/new) on the repository so we can fix it!

Thank you for helping Infrasity build the best developer podcast directory on the internet!
