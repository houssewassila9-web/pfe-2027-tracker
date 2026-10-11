"""Collecteur gratuit Arbeitnow. Stage agroalimentaire en France uniquement.
Aucune offre inventée. Sans identifiant et sans scraping de sites tiers.
"""
import datetime, html, json, re, urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/'data'/'opportunities.json'
ENDPOINT='https://www.arbeitnow.com/api/job-board-api'
NOW=datetime.datetime.now(datetime.timezone.utc)
def normalize(s):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',str(s or '')))).strip()
def plain(s):
    return normalize(s).lower().translate(str.maketrans('éèêëàâîïôùûüç','eeeeaaiiouuuc'))
def appropriate(r):
    title=plain(r.get('title')); desc=plain(r.get('description')); location=plain(r.get('location'))
    stage=any(x in title for x in ('stage','stagiaire','internship','intern ','praktikum')) or any('internship' in plain(x) for x in r.get('job_types',[]))
    food=any(x in title+' '+desc for x in ('agroaliment','alimentaire','food science','food product','formulation','sensory','ingredients','food quality','food safety','nutrition','r&d alimentaire','recherche et developpement'))
    france=any(x in location for x in ('france','paris','lyon','nantes','rennes','lille','marseille','toulouse','bordeaux','saclay','ile-de-france','montpellier','strasbourg','grenoble','dijon','angers','tours','rouen','le mans','orleans'))
    return stage and food and france

def process(r):
    url=r.get('url','')
    if not isinstance(url,str) or not url.startswith('https://'):return None
    desc=normalize(r.get('description'))
    txt=plain(r.get('title','')+' '+desc)
    match=re.search(r'\b([56])\s*(?:mois|months)\b',txt)
    prio='P1' if any(t in txt for t in ('r&d','formulation','innovation','developpement produit','product development')) else 'P2'
    if any(t in plain(r.get('location')) for t in ('paris','ile-de-france','saclay')):prio='P1'
    slug=str(r.get('slug') or url)
    date=r.get('created_at')
    posted=datetime.datetime.fromtimestamp(date,datetime.timezone.utc).date().isoformat() if isinstance(date,(int,float)) else NOW.date().isoformat()
    return {'id':'arbeitnow-'+slug,'company':normalize(r.get('company_name')) or 'Entreprise non précisée', 'title':normalize(r.get('title')),
      'location':normalize(r.get('location')),'missions':desc[:750], 'skills':', '.join(map(str,r.get('tags') or []))[:300],
      'start':'À confirmer','duration':match.group(1)+' mois' if match else 'À confirmer', 'pay':'Non précisée',
      'priority':prio,'international':'À confirmer','availability':'Publiée sur Arbeitnow ; lien à vérifier',
      'status':'À examiner','source':'Arbeitnow (offre agrégée)','url':url,'added':posted}

def main():
   req = urllib.request.Request(
    ENDPOINT,
    headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
)
    with urllib.request.urlopen(req,timeout=35) as resp:
        payload=json.load(resp)
    listings=payload.get('data')
    if not isinstance(listings,list):raise RuntimeError('Format inattendu de la source: aucune modification')
    raw=json.loads(BASE.read_text(encoding='utf-8')) if BASE.exists() else {'offers':[]}
    existing={x['id']:x for x in raw.get('offers',[]) if x.get('id')}
    added=0
    for listing in listings:
        if not appropriate(listing):continue
        item=process(listing)
        if item and item['id'] not in existing:
            existing[item['id']]=item;added+=1
    raw['offers']=list(existing.values());raw['updated_at']=NOW.isoformat()
    BASE.parent.mkdir(parents=True,exist_ok=True)
    BASE.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{added} nouvelles offres; {len(existing)} offres au total. {len(listings)} annonces examinées. Source: Arbeitnow.')
    if added==0:print('Aucune annonce correspondant aux filtres stricts. Ne pas interpréter comme une panne.')
if __name__=='__main__':main()
