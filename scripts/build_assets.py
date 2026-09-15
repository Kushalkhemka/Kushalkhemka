from pathlib import Path
from html import escape
import math, shutil, json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
FONT = Path(__file__).resolve().parent / 'fonts/SpaceGrotesk.ttf'
fonts = {}
for weight in (400, 500, 600, 700):
    fonts[weight] = instantiateVariableFont(TTFont(FONT), {'wght': weight})

BG='#090b09'; FG='#f1f3ef'; MUTED='#aab4a5'; GREEN='#c5fa72'; LINE='#293126'
snapshot = ASSETS / 'github-data.json'
github_data = json.loads(snapshot.read_text()) if snapshot.exists() else {}

class SVG:
    def __init__(self,w,h,title):
        self.w,self.h=w,h
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>',f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    def raw(self,s): self.parts.append(s)
    def text(self,text,x,y,size,fill=FG,weight=400,tracking=0):
        f=fonts[weight]; glyphs=f.getGlyphSet(); cmap=f.getBestCmap(); scale=size/f['head'].unitsPerEm
        p=[]; offset=0
        for c in text:
            glyph=cmap.get(ord(c),'space'); pen=SVGPathPen(glyphs); glyphs[glyph].draw(pen)
            p.append(f'<path transform="translate({offset:.3f} 0)" d="{pen.getCommands()}"/>')
            offset+=f['hmtx'][glyph][0]+tracking/scale
        self.raw(f'<g aria-label="{escape(text)}" fill="{fill}" transform="translate({x} {y}) scale({scale:.6f} {-scale:.6f})">'+''.join(p)+'</g>')
        return offset*scale
    def line(self,x1,y1,x2,y2,color=LINE,width=1): self.raw(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def circle(self,x,y,r,stroke=LINE,width=1,fill='none'): self.raw(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    def arrow(self,x,y,color=GREEN): self.raw(f'<path d="M{x} {y+16} L{x+16} {y} M{x} {y} H{x+16} V{y+16}" fill="none" stroke="{color}" stroke-width="2"/>')
    def save(self,name): (ASSETS/name).write_text(''.join(self.parts)+'</svg>')

def lens(s,x,y,r):
    s.circle(x,y,r,LINE)
    s.circle(x,y,r*.84,FG,1.1)
    s.circle(x,y,r*.78,LINE)
    for i in range(64):
        a=i*math.pi/32
        inner=r*(.94 if i%4 else .9)
        s.line(round(x+math.cos(a)*inner,2),round(y+math.sin(a)*inner,2),round(x+math.cos(a)*r,2),round(y+math.sin(a)*r,2),GREEN if i%8==0 else LINE,1.3)
    # Exact optical aperture geometry; decorative, not a live metric.
    for i in range(6):
        a=i*math.pi/3
        p1=(x+math.cos(a)*r*.78,y+math.sin(a)*r*.78)
        p2=(x+math.cos(a+.8)*r*.31,y+math.sin(a+.8)*r*.31)
        p3=(x+math.cos(a+math.pi/3+.8)*r*.31,y+math.sin(a+math.pi/3+.8)*r*.31)
        s.raw(f'<path d="M{p1[0]:.2f} {p1[1]:.2f} L{p2[0]:.2f} {p2[1]:.2f} L{p3[0]:.2f} {p3[1]:.2f}" fill="none" stroke="{GREEN}" stroke-width="1.5"/>')
    s.circle(x,y,3,GREEN,1,GREEN)
    for dx,dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        a=x+dx*(r+14); b=y+dy*(r+14)
        s.line(a,b,a-dx*20,b,MUTED); s.line(a,b,a,b-dy*20,MUTED)

for mobile in (False,True):
    w,h=(480,430) if mobile else (960,410)
    s=SVG(w,h,'Kushal Khemka — AI, security, and engineering. OpenSec co-founder. Delhi, India. DTU CSE 2028.')
    if mobile:
        s.text('Kushal',28,89,72,weight=600,tracking=-2)
        s.text('Khemka',28,164,72,weight=600,tracking=-2)
        s.text('AI. Security. Engineering.',30,215,25,GREEN,500)
        s.text('Co-founder, OpenSec',30,249,20,MUTED)
        lens(s,389,332,46)
        s.line(30,284,450,284)
        s.text('From research',30,327,22)
        s.text('to working systems.',30,355,22)
        s.text("Delhi, India  /  DTU CSE ’28",30,400,17,MUTED)
    else:
        s.text('Kushal',42,118,94,weight=600,tracking=-2.5)
        s.text('Khemka',42,215,94,weight=600,tracking=-2.5)
        s.text('AI. Security. Engineering.',46,269,29,GREEN,500)
        s.text('Co-founder, OpenSec',46,307,21,MUTED)
        lens(s,766,177,124)
        s.line(46,344,914,344)
        s.text('From research to working systems.',46,382,20,FG)
        s.text("Delhi, India  /  DTU CSE ’28",663,382,17,MUTED)
    s.save('hero-mobile.svg' if mobile else 'hero.svg')

for mobile in (False,True):
    w,h=(480,330) if mobile else (960,320)
    s=SVG(w,h,'OpenSec — From vulnerability to visibility. AI-native security, from code context to reviewed fixes.')
    s.text('Open',30 if mobile else 40,56,30,FG,600)
    s.text('Sec',104 if mobile else 114,56,30,GREEN,600)
    s.arrow(w-58,34)
    s.line(30 if mobile else 40,80,w-30,80)
    x=30 if mobile else 40
    s.text('From vulnerability',x,141,38 if mobile else 49,FG,500,tracking=-.8)
    s.text('to visibility.',x,190 if mobile else 198,48 if mobile else 56,GREEN,500,tracking=-1)
    s.text('AI-native security, from code context',x,242 if mobile else 248,21 if mobile else 22,MUTED)
    s.text('to reviewed fixes.',x,272 if mobile else 278,21 if mobile else 22,MUTED)
    if not mobile:
        # Repository context converging toward a reviewed result.
        nodes=[(701,139),(788,114),(858,161),(711,224),(804,242)]
        for nx,ny in nodes:
            s.line(nx,ny,787,179,LINE,1.5)
            s.raw(f'<rect x="{nx-5}" y="{ny-5}" width="10" height="10" fill="{BG}" stroke="{MUTED}"/>')
        s.circle(787,179,31,GREEN,1.4)
        s.raw(f'<path d="M774 179 L783 188 L801 169" fill="none" stroke="{GREEN}" stroke-width="2"/>')
    s.save('opensec-mobile.svg' if mobile else 'opensec.svg')

projects=[
('cloudchase','CloudChase','Predicting cloud cover from satellite imagery.',['Predicting cloud cover','from satellite imagery.'],'U-Net / INSAT-3DS / Nowcasting'),
('txnguard','TxnGuard','Turning transaction evidence into fraud intelligence.',['Turning transaction evidence','into fraud intelligence.'],'Multi-agent systems / Retrieval / AML'),
('vton','Virtual Try-On','Connecting pose, fit, and visual search.',['Connecting pose, fit,','and visual search.'],'Computer vision / OpenPose / Retrieval'),
('leetcode','LeetCode','A practice in patterns, precision, and problem solving.',['A practice in patterns, precision,','and problem solving.'],'C++ / Algorithms / Data structures'),
('dataset','Dataset Pipeline','The data engineering behind the intelligence.',['The data engineering','behind the intelligence.'],'Python / Data engineering')]
for slug,name,desc,mobdesc,stack in projects:
    for mobile in (False,True):
        w,h=(480,239) if mobile else (960,154)
        meta=github_data.get('featured',{}).get(slug)
        counts=f'{meta["stargazers_count"]} stars · {meta["forks_count"]} forks' if meta else ''
        s=SVG(w,h,f'{name} — {desc} {stack}. {counts}. Open repository.')
        x=28 if mobile else 36
        s.text(name,x,53,32 if mobile else 34,FG,500,tracking=-.6)
        s.arrow(w-54,30)
        if mobile:
            for i,line in enumerate(mobdesc): s.text(line,x,96+28*i,21,MUTED)
            s.text(stack,x,169,18,GREEN)
            if counts: s.text(counts,x,213,18,MUTED)
        else:
            s.text(desc,x,88,22,MUTED)
            s.text(stack,x,125,17,GREEN)
            if counts: s.text(counts,690,125,18,MUTED)
        s.save(f'{slug}-mobile.svg' if mobile else f'{slug}.svg')

for mobile in (False,True):
    w,h=(480,156) if mobile else (960,152)
    s=SVG(w,h,'Let’s build something that matters. Connect with Kushal Khemka on LinkedIn.')
    if mobile:
        s.text('Let’s build something',28,55,30,FG,500,tracking=-.5)
        s.text('that matters.',28,92,30,GREEN,500,tracking=-.5)
        s.text('Connect on LinkedIn',28,131,17,MUTED)
        s.arrow(426,100)
    else:
        s.text('Let’s build something that matters.',36,65,43,FG,500,tracking=-1)
        s.text('AI security / Research / Open source',38,111,20,GREEN)
        s.arrow(895,57)
    s.save('connect-mobile.svg' if mobile else 'connect.svg')

for slug, label in [('linkedin', 'LinkedIn'), ('leetcode', 'LeetCode'), ('tryhackme', 'TryHackMe'), ('github', 'GitHub'), ('opensec', 'OpenSec')]:
    s = SVG(160, 44, label + ' — open profile' if slug != 'opensec' else 'OpenSec — visit website')
    s.raw(f'<rect x="0.5" y="0.5" width="159" height="43" rx="7" fill="#152010" stroke="#526b3b"/>')
    s.text(label, 14, 28, 18, FG, 500)
    s.raw(f'<path d="M133 28 L143 18 M133 18 H143 V28" stroke="{GREEN}" stroke-width="1.5" fill="none"/>')
    s.save('link-' + slug + '.svg')

license_text = (Path(__file__).parent/'fonts/OFL.txt').read_text()
(ASSETS/'FONT-LICENSE.txt').write_text('\n'.join(line.rstrip() for line in license_text.splitlines())+'\n')
print('Generated',len(list(ASSETS.glob('*.svg'))),'self-contained SVG assets')
