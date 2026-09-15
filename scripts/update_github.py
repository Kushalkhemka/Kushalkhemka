"""Refresh profile artwork from public GitHub data; retain old assets on fetch failure."""
from collections import Counter
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen
import json
import os
import re
import runpy
import time

ROOT = Path(__file__).resolve().parents[1]
USER = 'Kushalkhemka'
API = 'https://api.github.com'
FEATURED = {
    'cloudchase': 'mayank-jangid-moon/CloudChase',
    'txnguard': 'Kushalkhemka/txn-guard',
    'vton': 'Kushalkhemka/fashion-vton',
    'leetcode': 'Kushalkhemka/leetcode',
    'dataset': 'Kushalkhemka/dataset_pipelineV2',
}


def fetch(url):
    headers = {'User-Agent': 'Kushalkhemka-profile-artwork', 'Accept': 'application/vnd.github+json' if url.startswith(API) else 'text/html'}
    # The Actions repository token is optional. No personal access token is needed.
    if url.startswith(API) and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=30) as response:
                return response.read().decode(), dict(response.headers)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def api(path):
    return json.loads(fetch(API + path)[0])


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.labels = {}
        self.active = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date'):
            self.cells[attrs['id']] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        if tag == 'tool-tip':
            self.active = attrs.get('for')
            self.labels[self.active] = ''
    def handle_data(self, data):
        if self.active:
            self.labels[self.active] += data
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.active = None


def collect():
    user = api(f'/users/{USER}')
    repos = []
    for page in range(1, 101):
        batch = api(f'/users/{USER}/repos?per_page=100&type=owner&page={page}')
        assert isinstance(batch, list), 'Unexpected repositories response'
        repos.extend(repo for repo in batch if not repo['private'])
        if len(batch) < 100:
            break
    else:
        raise RuntimeError('Repository pagination incomplete')
    original = [repo for repo in repos if not repo['fork']]
    _, starred_headers = fetch(API + f'/users/{USER}/starred?per_page=1')
    last = re.search(r'[?&]page=(\d+)>; rel="last"', starred_headers.get('Link', ''))
    if last:
        starred_count = int(last.group(1))
    else:
        starred_count = len(api(f'/users/{USER}/starred?per_page=1'))

    calendar_html, _ = fetch(f'https://github.com/users/{USER}/contributions')
    parser = Calendar()
    parser.feed(calendar_html)
    days = []
    for key, cell in parser.cells.items():
        label = parser.labels.get(key, '')
        match = re.match(r'\s*([\d,]+|No) contributions?\b', label)
        if not match:
            raise ValueError(f'Missing contribution count for {cell["date"]}')
        count = 0 if match.group(1) == 'No' else int(match.group(1).replace(',', ''))
        days.append({**cell, 'count': count})
    days.sort(key=lambda d: d['date'])
    assert 350 <= len(days) <= 380, 'Contribution calendar incomplete'
    advertised = re.search(r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions', calendar_html)
    assert advertised, 'Contribution total missing'
    assert sum(d['count'] for d in days) == int(advertised.group(1).replace(',', '')), 'Calendar total mismatch'
    streak = longest = 0
    for day in days:
        streak = streak + 1 if day['count'] else 0
        longest = max(longest, streak)
    by_name = {repo['full_name'].lower(): repo for repo in repos}
    featured = {}
    for slug, name in FEATURED.items():
        repo = by_name.get(name.lower()) or api('/repos/' + name)
        assert not repo['private'], 'Featured repository must be public'
        featured[slug] = {k: repo[k] for k in ('full_name', 'html_url', 'stargazers_count', 'forks_count', 'language')}
    return {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'source': f'https://github.com/{USER}',
        'scope': 'Public GitHub profile and public repositories. No private repository data.',
        'followers': user['followers'], 'public_repos': user['public_repos'],
        'stars_earned': sum(repo['stargazers_count'] for repo in original),
        'repos_starred': starred_count,
        'contributions': sum(day['count'] for day in days),
        'active_days': sum(day['count'] > 0 for day in days),
        'longest_streak': longest,
        'languages': dict(Counter(repo['language'] for repo in original if repo['language']).most_common()),
        'featured': featured, 'days': days,
    }


def render(data):
    # Shared typography and colors also rebuild project star/fork metadata.
    art = runpy.run_path(str(ROOT / 'scripts/build_assets.py'))
    SVG, FG, MUTED, GREEN, LINE, BG = (art[k] for k in ('SVG', 'FG', 'MUTED', 'GREEN', 'LINE', 'BG'))
    stats = [(data['contributions'], 'Contributions / year'),
             (data['stars_earned'], 'Stars earned'),
             (data['public_repos'], 'Public repositories'),
             (data['followers'], 'Followers'),
             (data['repos_starred'], 'Repositories starred'),
             (str(data['longest_streak']) + ' days', 'Longest streak / year')]
    description = 'GitHub activity. ' + '. '.join(f'{label}: {value}' for value, label in stats) + '. Updated ' + data['updated']
    for mobile in (False, True):
        w, h = (480, 490) if mobile else (960, 320)
        s = SVG(w, h, description)
        s.text('On GitHub', 28 if mobile else 36, 51, 30, FG, 500)
        for i, (value, label) in enumerate(stats):
            cols = 2 if mobile else 3
            x = (28 if mobile else 36) + (i % cols) * (232 if mobile else 310)
            y = 119 + (i // cols) * (118 if mobile else 106)
            s.text(f'{value:,}' if isinstance(value, int) else value, x, y, 39, GREEN, 500)
            s.text(label, x, y + 32, 18, MUTED)
        s.line(28 if mobile else 36, h-49, w-28, h-49)
        s.text('Public data · Updated ' + data['updated'], 28 if mobile else 36, h-22, 17, MUTED)
        s.save('github-stats-mobile.svg' if mobile else 'github-stats.svg')

    days = data['days']
    # Week-major order, beginning Sunday, as in GitHub's public calendar.
    first = date.fromisoformat(days[0]['date'])
    offset = (first.weekday() + 1) % 7
    weeks = [[] for _ in range((len(days)+offset+6)//7)]
    for i, day in enumerate(days):
        weeks[(i+offset)//7].append(((i+offset)%7, day))
    palette = ['#182016', '#365520', '#578632', '#8ac24b', GREEN]
    for mobile in (False, True):
        w, h = (480, 428) if mobile else (960, 278)
        s = SVG(w, h, f'{data["contributions"]:,} contributions across {data["active_days"]} active days. {days[0]["date"]} to {days[-1]["date"]}.')
        x0 = 28 if mobile else 36
        s.text('A year of contributions', x0, 49, 28, FG, 500)
        s.text(f'{data["contributions"]:,} contributions  /  {data["active_days"]} active days', x0, 81, 19, MUTED)
        step = 15.7 if mobile else 16.7
        side = 12 if mobile else 13
        for i, week in enumerate(weeks):
            block = i // 27 if mobile else 0
            col = i % 27 if mobile else i
            y0 = 132 + block * 148
            for row, day in week:
                x = x0 + col*step
                y = y0 + row*step
                s.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{side}" height="{side}" rx="2" fill="{palette[day["level"]]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>')
            if col == 0:
                s.text(week[0][1]['date'], x0, y0-13, 16, MUTED)
        s.text(days[-1]['date'], w-124, h-18, 16, MUTED)
        s.text('Less', x0, h-18, 16, MUTED)
        for i, color in enumerate(palette):
            s.raw(f'<rect x="{x0+45+i*19}" y="{h-31}" width="13" height="13" rx="2" fill="{color}"/>')
        s.text('More', x0+148, h-18, 16, MUTED)
        s.save('contributions-mobile.svg' if mobile else 'contributions.svg')

    language_items = list(data['languages'].items())
    top = language_items[:5]
    remainder = sum(v for _, v in language_items[5:])
    if remainder:
        top.append(('Other', remainder))
    total = sum(data['languages'].values())
    colors = [GREEN, '#91cba5', '#90bed3', '#d8bd82', '#c3a7d6', '#788a70']
    for mobile in (False, True):
        w, h = (480, 345) if mobile else (960, 249)
        s = SVG(w, h, 'Languages by primary language of public, non-fork repositories. ' + ', '.join(f'{k}: {v} repositories' for k,v in top))
        x0 = 28 if mobile else 36
        s.text('Languages in my repositories', x0, 49, 26 if mobile else 30, FG, 500)
        s.text('Primary language · Public, non-fork repositories', x0, 79, 16 if mobile else 19, MUTED)
        x = x0
        for i, (name, count) in enumerate(top):
            width = (w - 2*x0)*count/total if total else 0
            s.raw(f'<rect x="{x:.3f}" y="106" width="{width:.3f}" height="14" fill="{colors[i]}"/>')
            x += width
            cols = 2 if mobile else 3
            lx = x0 + (i%cols)*(230 if mobile else 310)
            ly = 160 + (i//cols)*60
            label = 'Jupyter' if mobile and name == 'Jupyter Notebook' else name
            s.circle(lx+5, ly-6, 4, colors[i], 1, colors[i])
            s.text(label, lx+18, ly, 19, FG)
            s.text(f'{count} repos · {count/total:.0%}', lx+18, ly+23, 16, MUTED)
        s.save('languages-mobile.svg' if mobile else 'languages.svg')

    readme = ROOT / 'README.md'
    content = readme.read_text()
    for slug, repo in data['featured'].items():
        counts = f'{repo["stargazers_count"]} stars, {repo["forks_count"]} forks. Updated {data["updated"]}.'
        pattern = rf'(<img src="assets/{slug}\.svg" width="100%" alt=")([^"]*)(">)'
        def update_alt(match):
            base = match.group(2).split(' GitHub:')[0]
            return match.group(1) + base + ' GitHub: ' + escape(counts, quote=True) + match.group(3)
        content = re.sub(pattern, update_alt, content)
    readme.write_text(content)


if __name__ == '__main__':
    data = collect()  # Fetch and validate everything before replacing the snapshot.
    snapshot = ROOT / 'assets/github-data.json'
    snapshot.write_text(json.dumps(data, indent=2) + '\n')
    render(data)
    print(json.dumps({k: data[k] for k in ['updated', 'contributions', 'stars_earned', 'followers', 'repos_starred']}))
