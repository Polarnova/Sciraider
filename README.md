# Sciraider

Sciraider aggregates recent scirate votes, new arXiv papers and website changes
into a single email digest. It is designed to be triggered periodically by a
GitHub Action.

## Features
- Scrapes scirate user pages for recent "scites".
- Queries arXiv for authors' updated papers.
- Detects updates on arbitrary websites by hashing their HTML.
- Renders results into a HTML email via Jinja2 template.

## Usage
Install requirements and run the CLI with a YAML configuration:

```bash
pip install -r requirements.txt
python -m sciraider.cli --cfg config/targets.yaml
```

The GitHub Actions workflow runs this command weekly and sends the email if
anything changed.
