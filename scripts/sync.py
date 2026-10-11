"""Free optional France Travail offers feed. Requires authorized API credentials.
Does not claim to confirm eligibility of international students or precise start dates.
"""
import base64, datetime, json, os, re, urllib.parse, urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/'data'/'opportunities.json'
CLIENT=os.environ.get('FRANCE_TRAVAIL_CLIENT_ID','').strip()
SECRET=os.environ.get('FRANCE_TRAVAIL_CLIENT_SECRET','').strip()
SCOPE=os.environ.get('FRANCE_TRAVAIL_SCOPE','api_offresdemploiv2 o2dsoffre').strip()
TOKEN_ENDPOINT='https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire'
API='https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search'
TERMS=['stage ingenieur agroalimentaire','stage recherche developpement agroalimentaire','stage formulation alimentaire','stage qualite agroalimentaire']
NOW=datetime.datetime.now(datetime.timezone.utc)

def request(url, method='GET',data=None, headers=None):
    req=urllib.request.Request(url,data=data,headers=headers or {},method=method)
    with urllib.request.urlopen(req,timeout=25) as resp:return resp.status,dict(resp.headers),json.loads(resp.read().decode())

def token():
    payload=urllib.parse.urlencode({'grant_type':'client_credentials','client_id':CLIENT,'client_secret':SECRET,'scope':SCOPE}).encode()
    return request(TOKEN_ENDPOINT,'POST',payload,{'Content-Type':'application/x-www-form-urlencoded'})[2]['access_token']

def clean(x):return re.sub(r'<[^>]+>',' ',str(x or '')).strip()

def relevance(title,desc):
    text=(title+' '+desc).lower()
    if not any(x in text for x in ['agroaliment','alimentaire','formulation','food','nutrition','ingredient','sensoriel','qualité','qualite']):return False
    if not any(x in text for x in ['stage','stagiaire','internship','intern','pfe']):return False
    return True

def process(entry):
    title=clean(entry.get('intitule'));desc=clean(entry.get('description'))
    if not relevance(title,desc):return None
    company=clean((entry.get('entreprise') or {}).get('nom')) or 'Entreprise non précisée'
    location=clean((entry.get('lieuTravail') or {}).get('libelle'))
    origin=entry.get('origineOffre') or {}
    url=clean(origin.get('urlOrigine'))
    if not url.startswith('https://') and not url.startswith('http://'):
        url='https://candidat.francetravail.fr/offres/recherche/detail/'+urllib.parse.quote(clean(entry.get('id')))
    if not clean(entry.get('id')):return None
    text=(title+' '+desc).lower()
    prio='P1' if any(x in text for x in ['r&d','recherche et développement','recherche et developpement','formulation','innovation','développement produit','developpement produit']) else 'P2'
    if 'paris' in location.lower() or any(x in location for x in ['(75)','(91)','(92)','(93)','(94)','(95)','(77)','(78)']):prio='P1'
    duration='À confirmer'
    match=re.search(r'\b([456])\s*mois\b',text)
    if match:duration=match.group(1)+' mois'
    return {'id':'ft-'+clean(entry.get('id')),'company':company,'title':title,'location':location,
      'missions':desc[:750], 'skills':clean(entry.get('competences'))[:350] if isinstance(entry.get('competences'),str) else '',
      'start':'À confirmer','duration':duration,'pay':'Non précisée','priority':prio,'international':'À confirmer',
      'availability':'Répertoriée sur API France Travail lors de la synchronisation','status':'À examiner',
      'source':'France Travail API','url':url,'added':NOW.date().isoformat()}

def main():
    if not CLIENT or not SECRET:
        print('Identifiants API absents. Aucune modification apportée au flux.');return
    raw=json.loads(BASE.read_text(encoding='utf-8'))
    existing={r['id']:r for r in raw.get('offers',[]) if r.get('id')}
    auth=token();new=0
    for term in TERMS:
        params=urllib.parse.urlencode({'motsCles':term,'range':'0-49'})
        try: status,h,b=request(API+'?'+params,headers={'Authorization':'Bearer '+auth,'Accept':'application/json'})
        except Exception as e:print('Recherche indisponible pour',term,repr(e));continue
        for obj in b.get('resultats',[]):
            item=process(obj)
            if item and item['id'] not in existing:existing[item['id']]=item;new+=1
    raw['offers']=list(existing.values());raw['updated_at']=NOW.isoformat()
    BASE.write_text(json.dumps(raw,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(new,'new offers; total',len(existing))
if __name__=='__main__':main()
