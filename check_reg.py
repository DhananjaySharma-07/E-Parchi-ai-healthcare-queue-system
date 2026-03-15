import requests
import sys
base='http://127.0.0.1:5000'
s=requests.Session()
h=s.get(base+'/api/hospital/1', timeout=5)
print('hospital',h.status_code)
deps=s.get(base+'/api/departments?hospital_id=1', timeout=5)
print('deps',deps.status_code)
dlist=deps.json()
print('deps len',len(dlist))
if not dlist:
    sys.exit(0)
d0=dlist[0]['id']
docs=s.get(base+f'/api/doctors?department_id={d0}&hospital_id=1', timeout=5)
print('docs',docs.status_code, len(docs.json()))
docid=docs.json()[0]['id']
r=s.post(base+'/register_patient?hospital_id=1', data={'name':'Test User','phone':'9876543210','age':'30','gender':'Male','symptoms':'Cough','department_id':d0,'doctor_id':docid}, allow_redirects=False, timeout=5)
print('register status', r.status_code, r.headers.get('Location'))
if r.status_code==302:
    print('redirect', r.headers.get('Location'))
print('token confirmation', s.get(base+'/token_confirmation', timeout=5).status_code)
