import urllib
import bs4
import json
import re

N_cursos = 100
url_root = 'http://dsrd.uc.cl/dara/libcursos/periodo21/'
file_root = 'ua'
titles = ['N','sigla','seccion','creditos','nombre','min','opt','ofg','profesores','horario','actividad','salas','campus','titulos']
multiples = ['profesores','horario','actividad','salas']
otherUA = ['bachhu','bachcs']
courses = []

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
		open('aux%s.json'%(ua),'w').write(json.dumps(courses))

def parse(html,offset):
	soup = bs4.BeautifulSoup(html)
	f = soup.find_all('tr')
	if(len(f) < 11):
		return 0
	table = f[10+offset]
	courses = table.find_all('tr')[2:]
	i = 0
	for course in courses:
		parseCourse(course)
		i = i + 1
	return i

def parseCourse(soup):
	course = {}
	i = 0
	aux = {}
	for td in soup.find_all('td'):
		data = td.text
		if(titles[i] in multiples):
			data = td.find_all(text=True)
			aux[titles[i]] = data
			i = i + 1
			continue
		course[titles[i]] = data
		i = i + 1
	index = {'nombre': course.pop('nombre'),'sigla': 
	course['curso'] = index
	H = {}
	S = {}
	for i in xrange(len(aux['actividad'])):
		H[aux['actividad'][i]] = aux['horario'][i]
		if(len(aux['salas']) > i):
			S[aux['actividad'][i]] = aux['salas'][i]
		else:
			S[aux['actividad'][i]] = aux['salas'][0]
			print 'algo raro paso aqui!!!'
	#m = re.search('-\s(.*)',)
	#print(aux['profesores'])
	course['profesores'] = [x if not (x[0]=='-') else re.search('-\s(.*)',x).group(1) for x in aux['profesores']]
	#print(course['profesores'])
	course['horario'] = H
	course['salas'] = S
	courses.append(course)




start()
print 'Total cursos: \t\t%s'%(len(courses))

f = open('output.json','w')

f.write(json.dumps(courses,indent=4))



