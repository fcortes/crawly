import urllib
import bs4
import json
import re

#aa='http://dsrd.uc.cl/dara/libcursos/periodo21/ua6_0.html'

N_cursos = 100
url_root = 'http://dsrd.uc.cl/dara/libcursos/periodo22/'
file_root = 'ua'
titles = ['N','sigla','seccion','creditos','nombre','min','opt','ofg','profesores','horario','actividad','salas','campus','titulos']
#titles = ['N','sigla','seccion','creditos','nombre','vac','profesores','horario','actividad','salas','campus','titulos']
multiples = ['profesores','horario','actividad','salas']
otherUA = []#['bachhu','bachcs']
courses = []

def get_course(sigla):
	for c in courses:
		if c['sigla'] == sigla:
			return c
	return None

def start():
	for ua in otherUA + range(1,N_cursos + 1):

		page = 0
		aux = 0
		if(ua == 9):
			offset = 1
			continue
		else:
			offset = 0
		lastN = 30

		if(ua in otherUA):
			offset = -1

		while True:
			if(ua in otherUA):
				url = '%s%s%s'%(url_root,ua,'.html')
			else:
				url = '%s%s%s%s%s%s'%(url_root,file_root,ua,'_',page,'.html')
			
			f = urllib.urlopen(url)
			response_code = f.getcode()

			if(response_code != 200 or lastN < 25):
				break

			html = f.read()
			t = parse(html,offset)
			aux = aux + t
			print 'UA:  %s\tPage:  %s\tCourses:  %s'%(ua,page,t)
			lastN = t
			page = page + 1
			if(ua in otherUA):
				break
			#break
		print 'Total cursos UA %s: \t%s'%(ua,aux)
		open('aux/aux%s.json'%(ua),'w').write(json.dumps(courses))

def parse(html,offset):
	soup = bs4.BeautifulSoup(html)
	f = soup.find_all('tr')
	if(len(f) < 11):
		return 0
	table = f[10+offset]
	courses = table.find_all('tr')[1:]
	i = 0
	for course in courses[1:]:
		parseCourse(course)
		i = i + 1
	return i

def parseCourse(soup):
	course = {}
	i = 0
	aux = {}
	raw = {}
	for td in soup.find_all('td'):
		data = td.text
		if(titles[i] in multiples):
			data = td.find_all(text=True)
			aux[titles[i]] = data
			i = i + 1
			continue
		raw[titles[i]] = data
		i = i + 1
	#print(raw)
	seccion = {}	
	#seccion['vac'] = raw['vac']
	seccion['min'] = raw['min']
	seccion['opt'] = raw['opt']
	seccion['ofg'] = raw['ofg']
	seccion['seccion'] = raw['seccion']
	seccion['campus'] = raw['campus']
	
	H = {}  #horario
	S = {}  #salas
	for i in xrange(len(aux['actividad'])):
		H[aux['actividad'][i]] = aux['horario'][i]
		if(len(aux['salas']) > i):
			S[aux['actividad'][i]] = aux['salas'][i]
		else:
			S[aux['actividad'][i]] = aux['salas'][0]
			print 'algo raro paso aqui!!!'

	seccion['profesores'] = [x if not (x[0]=='-') else re.search('-\s(.*)',x).group(1) for x in aux['profesores']]
	seccion['horario'] = H
	seccion['salas'] = S

	#print raw['sigla']
	course = get_course(raw['sigla'])

	if course is None:
		course = {}
		course['sigla'] = raw['sigla']
		course['nombre'] = raw['nombre']
		course['creditos'] = raw['creditos']
		course['titulos'] = raw['titulos']
		course['secciones'] = [seccion]
		courses.append(course)
	else:
		course['secciones'].append(seccion)


#######################################################
#######################Descripciones###################
#######################################################

def startDesc():
	root_url = 'http://dsrd.uc.cl/alumnos-uc/descripcion-de-cursos/'
	uas = [u'actuacion', u'agronomia-e-ingenieria-forestal', u'arquitectura', u'arte', u'fisica', u'ciencias-biologicas', u'ciencia-politica', u'comunicaciones', u'construccion-civil', u'derecho', u'diseno', u'educacion-gral-basica', u'enfermeria', u'estetica', u'estudios-urbanos-y-territoriales', u'fisica', u'filosofia', u'geografia', u'historia', u'ingenieria-civil', u'ingenieria-comercial', u'kinesiologia', u'letras', u'matematicas', u'medicina', u'musica', u'nutricion-y-dietetica', u'odontologia', u'psicologia', u'quimica', u'sociologia', u'teologia', u'trabajo-social', u'villarrica', u'cursos-deportivos', u'requisitos-de-idioma', u'cursos-que-se-dictan-en-idioma-ingles', u'academia-internacional-de-filosofia', u'cursos-especiales-drai']
	#descripciones = []

	i = 0
	for u in uas:
		print 'buscando descripciones de %s'%(u)
		url = '%s%s'%(root_url,u)
		html = urllib.urlopen(url).read()
		soup = bs4.BeautifulSoup(html)
		ps = soup.find_all('p')
		for p in ps:
			#curso = {}
			if p.a is None:
				#print(p)
				continue
			sigla = p.a['name']
			#curso['sigla'] = sigla
			curso = get_course(sigla)
			if curso is None:
				curso = {}
				curso['sigla'] = sigla
				courses.append(curso)
			curso['descripcion'] = str(p)
			#cursos.append(curso)
		#print('encontrados %d cursos')%(len(cursos))
		i = i + 1

#######################################################
#######################Requisitos######################
#######################################################

def startReq():
	f = open('req/output2.json').read()
	reqs = json.loads(f)

	for r in reqs:
		sigla = r['sigla']
		curso = get_course(sigla)
		if curso == None:
			continue
		curso['requisitos'] = r['req']

start()
print 'Total cursos: \t\t%s'%(len(courses))
f = open('output.json','w')
f.write(json.dumps(courses,sort_keys=True))
f.close()
#print(get_course('MAT1630'))
startDesc()
print 'Total cursos: \t\t%s'%(len(courses))
f = open('output2.json','w')
f.write(json.dumps(courses,sort_keys=True))
startReq()
f.close()
print 'Total cursos: \t\t%s'%(len(courses))
f = open('output3.json','w')
f.write(json.dumps(courses,sort_keys=True))
f.close()

f = open('output3.json','r')
a=f.read()
f.close()
s=a[1:-1].replace('}, {"cre','}\n{"cre').replace('}, {"des','}\n{"des')
f = open('output4.json','w')
f.write(s)
f.close()






