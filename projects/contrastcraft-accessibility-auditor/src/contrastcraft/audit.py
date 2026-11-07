from html.parser import HTMLParser
from dataclasses import dataclass,asdict
import json
from .colors import grade

@dataclass(frozen=True)
class Finding:
    rule:str
    severity:str
    line:int
    message:str

class Auditor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.findings=[]
        self.ids=set()
        self.refs=[]
        self.labels=set()
        self.inputs=[]
        self.title=False
        self.stack=[]
        self.images=[]
        self.links=[]
        self.buttons=[]

    def flag(self,rule,message,line=None,severity='error'):
        self.findings.append(Finding(rule,severity,line or self.getpos()[0],message))

    def handle_starttag(self,tag,attrs):
        a=dict(attrs);line=self.getpos()[0]
        ident=a.get('id')
        if ident:
            if ident in self.ids:self.flag('duplicate-id',f'Duplicate id: {ident}')
            self.ids.add(ident)
        if tag=='html' and not a.get('lang'):self.flag('document-language','html element needs lang')
        if tag=='title':self.title=True
        if tag=='img' and 'alt' not in a:self.flag('image-alt','Image needs alt attribute')
        if tag=='input':
            if a.get('type','text') not in ('hidden','submit','button','reset','image'):
                self.inputs.append((line,ident,a.get('aria-label'),a.get('aria-labelledby')))
        if tag=='label' and a.get('for'):self.labels.add(a['for'])
        for key in ('aria-labelledby','aria-describedby'):
            if a.get(key):self.refs.extend((line,ref) for ref in a[key].split())
        if tag in ('a','button'):
            self.stack.append([tag,line,[],a.get('aria-label','')])
        if tag=='a' and not a.get('href'):self.flag('link-href','Anchor needs href',line,'warning')
        if tag=='meta' and a.get('name','').lower()=='viewport' and 'user-scalable=no' in a.get('content','').replace(' ','').lower():
            self.flag('zoom-disabled','Viewport disables zoom',line)
        if tag=='input' and a.get('type')=='image' and not a.get('alt'):
            self.flag('image-input-alt','Image input needs alt',line)
        if tag=='font':self.flag('deprecated-font','Deprecated font tag',line,'warning')

    def handle_data(self,data):
        for frame in self.stack:frame[2].append(data)

    def handle_endtag(self,tag):
        if self.stack and self.stack[-1][0]==tag:
            _,line,text,aria=self.stack.pop()
            if not (''.join(text).strip() or aria.strip()):
                self.flag('accessible-name',f'{tag} has no accessible text',line)

    def finish(self):
        if not self.title:self.flag('document-title','Document needs a title',1)
        for line,ident,aria,ref in self.inputs:
            if not (aria or ref or (ident and ident in self.labels)):
                self.flag('input-label','Form control needs associated label',line)
        for line,ref in self.refs:
            if ref not in self.ids:self.flag('aria-reference',f'Missing ARIA target: {ref}',line)
        return sorted(self.findings,key=lambda x:(x.line,x.rule))

def audit_html(html):
    parser=Auditor();parser.feed(html);return parser.finish()

def audit_file(path):
    from pathlib import Path
    return audit_html(Path(path).read_text(encoding='utf-8'))

def report(findings):
    return {'count':len(findings),'by_severity':{s:sum(x.severity==s for x in findings) for s in ('error','warning')},'findings':[asdict(f) for f in findings]}
