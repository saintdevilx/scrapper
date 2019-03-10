 #!/usr/bin/python

import requests
from lxml import html
from selenium import webdriver
from time import sleep, time
from lxml.etree import XMLSyntaxError
import sys, getopt, json , datetime, random
from six.moves.html_parser import HTMLParser
from pprint import pprint
import logging, csv, sys,traceback, os, pickle
from os.path import expanduser
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


log_file = 'scrapper.log'

logging.info('Starting logger for...')
logger = logging.getLogger(__name__)
fh = logging.FileHandler(filename=log_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


LINKEDIN_UNAME='' # e.g. 'abc@xyz.com'
SESSION_PASS = '' # e.g. 'pass123'

if os.path.exists('config.py'):
	from config import *

LINKEDIN_AUTH_USERS={
	('')
}

default_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}


join_field ={
	'education':['title', 'fieldOfStudy']
}

schema_map = {
    'education':{
        'degreeName':'title',
        'schoolName':'institution',
        'is_current':'is_current',
        'description':'description',
        'activities':'description',
        'start_date':'start_date',
        'end_date':'end_date',
    },
   'work_experience':{
       'title':'designation',
       'companyName':'organisation_name',
       'start_date':'start_date',
       'end_date':'end_date',
       'is_current':'is_current',
       'description':'description'
    },
    'portfolio':{
        'title':'header',
        'name':'header',
        'description':'description',
        'url':'click_url'
    },
    'achievements':{
        'title':'header',
        'role':'header',
        'description':'description'
    },
    'profile':{
    	'firstName':'first_name',
    	'lastName':'last_name',
    	'locationName':'location_name',
    	'headline':'headline',
    	'summary':'summary'
    },
    'skill':{
    	'name':'name'
    }
}


def create_date(dt):
	if not dt:
		return
	if not dt.get('day') or dt['day'] == '-':
		dt['day'] = 1
	if not dt.get('month') or dt['month'] == '-':
		dt['month'] = 1
	if dt.get('$type'):
		dt.pop('$type')
	return dt


def validate_data(data, key):
	if data.get('timePeriod'):
		data['start_date'] = create_date(data.get('timePeriod').get('startDate'))
		data['end_date'] = create_date(data.get('timePeriod').get('endDate'))
	for old_key,replace in schema_map[key].items():

		if data.get(old_key):
			data[replace] = data.pop(old_key)

	invalid_keys = set(data.keys()) - set(schema_map[key].values())

	if join_field.get(key):
		try:
			data[join_field.get(key)[0]] = ", ".join([data.get(f,'') for f in join_field.get(key,'')])
		except Exception as ex:
			print('validate_data error',key , str(ex) )
			traceback.print_exc(file=sys.stdout)

	for k in invalid_keys:
		data.pop(k)
	return data

delay_list= [i for i in xrange(2000,5000, 200)]
print('delay List', delay_list)
class Scrapper:
	"""
	Scrapper just a tiny scrapping tool to fetch linked in profile details using selenium

	Usage:

	command line :
	scrapper.py <options>

		options could be:
		-u,--url=,   url to be crawl or path to a text file containing list of url 1 url per line
		-t,--test=,  with any integer value to run test
		-d,--delay=  delay between 2 request in seconds, in case of multiple urls
		-o,--out=	output file name
		-e,--export= export data to csv format
	"""

	list_user_agent = [
	                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
	                "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
	                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
	                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
	                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
	                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
	                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
	                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
	                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
	                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]
	auth_session_file="auth.pkl"	         

	def __init__(self,url, *args, **kwargs):
		self.selenium=kwargs.get('selenium')
		self.url = url or kwargs.get('url')
		self.session = requests.session()
		self.delay = kwargs.get('delay') or 0.5
		self.export = kwargs.get('export') or False
		self.urls_list=[]
		self.result_list=[]
		self.skip_before = kwargs.get('skip_before',False)
		self.skip_after = kwargs.get('skip_after',False)

		MAX_ROW_URL = 50

		columns =['expert_email','linkedin_url']
		count=0
		if os.path.exists(url):					
			with open(url,'rb') as csvfile:
				reader = csv.reader(csvfile, delimiter=',', quotechar='"')
				for ind,row in enumerate(reader,0):

					try:
						data = {name:row[ind] for ind,name in enumerate(columns,0)}
						if data.get('user_id','').lower() == 'user id' or not data.get('linkedin_url') or len(data.get('linkedin_url',''))<10:
							continue
						self.urls_list.append(data)
					except:						
						traceback.print_exc(file=sys.stdout)
						print('invalid row', row)

				if self.skip_before:
					print(' skip before', self.skip_before)									
					self.urls_list = self.urls_list[int(self.skip_before):]
				if self.skip_after:						
					print(' skip after', self.skip_after)
					limit = int(self.skip_after) if not self.skip_before else int(self.skip_after)-int(self.skip_before)
					print('----',limit)
					self.urls_list = self.urls_list[:limit]				
					
		else:
			self.urls_list=[self.url]


		self.auth_required = kwargs.get('auth') or True
		self.out_file = kwargs.get('out_file')
		self.old_session = kwargs.get('old_session' , False)

		if self.selenium:
 			home = expanduser("~")
 			print('selenium')
			self.driver = webdriver.Chrome(executable_path=os.path.join(home,'chromedriver'))

	def intercept_ajax_request(self):
		script_str="""
		$.ajaxSettings.complete=function(a,b){
		    var req =this.currentApi || this.url || this._req || this._url;
		    if(typeof(req)==='undefined' && typeof(this)==='object'){
		    	$.each(Object.keys(this), function(i,v){
		    		if(v.indexOf('/api/')>-1){
		    		  req = v;
		    		  return;
		    		}
		    	})
		    }
			var section=req.split('/').lastObject.split('?')[0].toLowerCase();
			allowed_sections=['positiongroups','educations']
			if(allowed_sections.indexOf(section)<0)return;
            if(!window.hasOwnProperty('section_data'))window.section_data={};
			window.section_data[section]=a.responseJSON;}		
		"""
		try:
			print('adding ajax intercepter')
			self.driver.execute_script(script_str)
			sec_data = self.driver.execute_script('return window.hasOwnProperty("section_data")')
			print('sec_data=%s'%sec_data)
		except:
			traceback.print_exc(file=sys.stdout)
			print(" waiting $ to be load.....")
			sleep(2)
			try:
				self.driver.execute_script(script_str)
				self.driver.execute_script('return window.hasOwnProperty("section_data")')
			except:
				traceback.print_exc(file=sys.stdout)
				print "script ajax hooks failed."

	def format_date(self,date_dict):
		if isinstance(date_dict,dict):
			return "{day}/{month}/{year}".format(day=date_dict.get('day','-'),year=date_dict.get('year','-'),
				month=date_dict.get('month','-'))
		return date_dict

	def get_essential_data(self, section,data,date_list):
		keys = ['description','url','title','companyName','role','activities','degreeeName','schoolName','fieldOfStudy']
		result_text ="{section}\n\n".format(section=section)
		
		def parse_essential_data(dt):
			res=""
			for k,v in dt.items():
				if k in keys:
					res += v or ''
				# if k.lower() == 'timeperiod':
				# 	start= self.format_date(date_list.get(v+',startDate',''))
				# 	end= self.format_date(date_list.get(v+',endDate','present'))
				# 	res +="\n%s - %s"%(start, end)
				# res+="\n"
			return res

		if isinstance(data,dict):
			result_text +=parse_essential_data(data)
		elif isinstance(data,list):			
			for item in data:
				result_text +=parse_essential_data(item)+'\n\n'
		return result_text

	def export_to_file(self, results):
		out_file_name = "%s.csv"%(self.out_file or '%s'%time())
		with open(out_file_name,'w') as out_file:
			csv_file_writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			columns=['firstName','lastName','headline','summary','locationName','industryName','skill',
			'project','publication','volunteerexperience','honor','position','certification','patent','course']
			row_data={}
			#pprint(results)
			csv_file_writer.writerow(columns)
			for data in results:
				orig_data = data
				data = data.get('profileview',{})
				profile_data = data.get('profile',{}) or data.get('profile',{})
				profile_data = profile_data[0] if isinstance(profile_data,list) else profile_data
				for col_name in columns[:7]:
					print col_name
					row_data[col_name] = profile_data.get(col_name)

				#
				date_list = orig_data.get('profileview',{}).get('date')

				for col_name in columns[7:]:
					row_data[col_name] = self.get_essential_data( col_name,data.get(col_name), date_list)

				#csv_file_writer.writeheader()
				#pprint(row_data)
				csv_file_writer.writerow(row_data.values())
		print 'data exported to file : %s'%out_file_name

	def get_formatted_data(self,results):
		columns = ['profile','education','portfolio','work_experience','achievements','skill']
		result_data_out=[]
		for row in results:
			profile_details = row.get('profileview',{})
			result_data={}
			result_data['profile'] = profile_details.get('profile',[{}])[0]
			result_data['education'] = profile_details.get('education',[])
			result_data['portfolio'] = profile_details.get('project',[]) + profile_details.get('publication',[]) + profile_details.get('patent',[])
			result_data['work_experience'] = profile_details.get('position',[])
			result_data['achievements']= profile_details.get('honor',[])

			
			for key in  schema_map.keys():				
				if isinstance(result_data.get(key), list):					
					tmp=[]
					for item in result_data.get(key):
						tmp += [validate_data(item, key)]
					result_data[key] = tmp
				elif isinstance(result_data.get(key), dict):
					result_data[key] = validate_data(result_data.get(key), key)
			result_data['skill'] = [ skill for skill in profile_details.get('skill',[]) if isinstance(skill,unicode) or isinstance(skill,str)]
			result_data.update(row.get('csv_data',{}))
			result_data_out.append(result_data)


		return result_data_out

	def export_json_dump(self, results):
		print('exporting json....')
		today_date = datetime.datetime.strftime( datetime.datetime.now(), '%d-%b-%Y')
		if not os.path.exists(today_date):
			os.makedirs(today_date)		
		out_file_name = "%s/%s.json"%(today_date, self.out_file or ('%s'%time()))
		from pprint import pprint
		try:
			with open(out_file_name, 'w+') as outfile:
				json.dump(self.get_formatted_data(results), outfile)
		except Exception as ex:
			traceback.print_exc(file=sys.stdout)
			print('Exception occured export_json_dump', str(ex))

	def get_request(self,url,headers=default_headers,**kwargs):
		if kwargs.get('random_ua'):
			headers['User-Agent'] = random.choices(self.list_user_agent)		
		return self.session.get(url,headers=headers)

	def post_request(self,url,data={},headers=default_headers, **kwargs):
		if kwargs.get('random_ua'):
			headers['User-Agent'] = random.choices(self.list_user_agent)
		return self.session.post(url, data=data, headers=headers)

	def parse_data(self,response):
		root_el= html.fromstring(response)

		classes = ['name', 'headline', 'location','summary-text']
		data={}
		try:
			for class_name in classes:
				cl_name = "'pv-top-card-section__%s'"%class_name
				find_by= ".//*[contains(@class,%s)]/descendant-or-self::*/text()"%cl_name
				data[class_name] = [el.text.strip() for el in root_el.xpath( find_by)]
		except:
			logger.info(data)
			logger.exception('While parsing selenium data')
			#self.driver.quit()

	def read_raw_html_data(self,content):
		h_parser = HTMLParser()
		content = h_parser.unescape(content)
		return content

	def get_section(self,url):
		sec = url.rsplit('/')[-1:]
		if len(sec):
			return sec[0].rsplit('?')[0]
	
	def read_data(self, content):
		root_el= html.fromstring(content)
		codes = root_el.xpath('.//code')
		data={}
		data_let ={}

		logger.info("{count} codes block found !!".format(count=len(codes)))
		print "{count} codes block found !!".format(count=len(codes))
		for ind,code in enumerate(codes,1):
			el_id = code.get('id','')
			if el_id.lower().startswith('bpr-guid-'): 
				try:
					js_data = json.loads(code.text)
				except Exception as e:
					traceback.print_exc(file=sys.stdout)
					print str(e), '** %s **'%el_id, '\n',code.text
					continue
				data_let[el_id] = js_data

		#print('cached bodies ', data_let.keys())

		for ind,code in enumerate(codes,1):
			el_id = code.get('id','')
			try:
				js_data = json.loads(code.text)
			except Exception as ex:
				logger.info(code.text)
				logger.info(" Exception,"+unicode(ex))
				# logger.info(unicode(code.text.encode('ascii','ignore')))
				# print el_id,' +++ ', str(ex)
				continue

			if js_data.has_key('request') and js_data.has_key('body'):
				section = self.get_section(js_data.get('request',"")).lower()
				data[section] = data_let.get(js_data.get('body'),{})
			# else:
			# 	data_let[el_id] = js_data

		paging_required=self.load_paginated_sections()
		if paging_required:
			print('paging required...')
			section_data=self.get_section_paginated_data()
		else:
			section_data=[]
			print('paging not required...')

		if data.get('profileview',{}).get('included'):
			print('section length',len(data['profileview']['included']))
			data['profileview']['included']+=section_data
			print('After section length',len(data['profileview']['included']))
		logger.info(data.keys())
		return data

	def get_csrf_token(self,res):
		csrf_elem_id='loginCsrfParam-login'
		try:
			root_el= html.fromstring(res)
		except Exception as error:
			logger.exception(error)
			return 

		input_el = root_el.xpath(".//input[@id='loginCsrfParam-login']")
		return input_el[0].value if len(input_el) else None

	def need_auth(self,res):
		count = 0
		while True and count <2:		
			csrf_token = self.get_csrf_token(res.content)
			if not csrf_token:
				res = self.get_request('https://www.linkedin.com/')
			else:
				break
			count +=1

		logger.info('COUNT %s %s'%(count, csrf_token))

		payload={'session_key':LINKEDIN_UNAME,'session_password':'%s'%SESSION_PASS,'isJsEnabled':False,'loginCsrfParam':csrf_token}
		response =self.post_request('https://www.linkedin.com/uas/login-submit',data=payload)
		self.auth_required = False
		return response

	def login_to_linkedin(self,driver):
		response=self.driver.get('https://www.linkedin.com/')
		elem_key= self.driver.find_element_by_name('session_key')
		elem_key.send_keys(LINKEDIN_UNAME)
		elem_pass= self.driver.find_element_by_name('session_password')
		elem_pass.send_keys(SESSION_PASS)

		submit_button = self.driver.find_element_by_css_selector('#login-submit')
		submit_button.click()

	def save_session(self):
		pickle.dump(self.driver.get_cookies() , open(self.auth_session_file ,"wb"))

	def load_session(self):
		print "loading.... session", self.old_session
		if self.old_session:
			print "session file check", self.auth_session_file
			if os.path.exists(self.auth_session_file):
				self.driver.get('http://www.linkedin.com')
				for cookie in pickle.load(open(self.auth_session_file, "rb")):
					self.driver.add_cookie(cookie)	
				self.auth_required=False
				return True

	def selenium_auth(self):				
		self.login_to_linkedin(self.driver)	
		self.save_session()
		self.auth_required = False

	def get_sanitized_data(self, data):
		d={}
		for k,v in data.items():
			if not '$' in k  and  not 'urn:' in unicode(v):
				d[k] =v
		return d

	def get_flat_string(self, dt):
		if isinstance(dt,list):
			return ",".join(dt)
		elif isinstance(dt,dict):
			return dt.values()
		return dt

	def get_date_range(self, date_range_key,date_map):
		print date_range_key, date_map
		return date_map.get(date_range_key+',startDate'),date_map.get(date_range_key+',endDate')

	def fix_date_range(self, results):
		if not results:
			return results
		for key,val in results.items():
			if isinstance(val, list):
				for v in val:
					if isinstance(v, dict) and v.get('timePeriod'):
						v['start_date'],v['end_date'] = self.get_date_range(v.get('timePeriod'), results.get('date'))
						v.pop('timePeriod')
						if not v['end_date']:
							v['is_current']=True						
			else:
				v=val
				if v.get('timePeriod'):
						v['start_date'],v['end_date'] = self.get_date_range(v.get('timePeriod'), results.get('date'))
						v.pop('timePeriod')
						if not v['end_date']:
							v['is_current']=True
		return results							

	def get_data(self,data, section):
		res={}
		key=section
		allowed_sections=['education','project','skill','volunteerexperience','position','honor','profile','timeperiod','publication', 'patent']
		source_data = data.get(section,{}).get('included',{}) or {}		
		#pprint(data)
		if not source_data:
			print("No source data",data.get(section,"--EMPTY--"), section, section in data.keys())
			raise ValueError("{section} is not found in source_data\n{keys}\n{data_keys}".format(section=section, 
				keys=source_data.keys(), data_keys=data.keys()))

		for item in source_data:

			data_type = item.get('$type','').rsplit('.')[-1:][0].lower()
			#print('date === >', data_type == 'date')
			if key == 'me':
				if  data_type == 'miniprofile':
					res['miniprofile'] = self.get_sanitized_data(item)

			elif key == 'profileview':
				orig_item = item			
				item = self.get_sanitized_data(item)				
				if data_type.lower() in allowed_sections or item.has_key('description') or item.has_key('summary'):					
					item_key = data_type or key
					tp =orig_item.get('timePeriod') or orig_item.get('date')
					tp
					if tp:
						item.update({'timePeriod':tp})
					if res.get(item_key):
						res[item_key] += [item]
					else:
						res[item_key] = [item]					

				if 'skill' == data_type:
					if res.get('skill'):						
						res['skill'] +=[self.get_flat_string(item.get('name'))]
					else:
						res['skill'] =[self.get_flat_string(item.get('name'))]

				if 'date' == data_type:
					k = orig_item.get('$id')
					if not res.get('date'):
						res['date']={}
					if orig_item.get('year') or orig_item.get('month') or orig_item.get('day'):
						res['date'][k]={
							'day':orig_item.get('day','-'),
							'month':orig_item.get('month','-'),
							'year':orig_item.get('year','-'),
						}

		if res.get('date'):
			res = self.fix_date_range(res)

			if res.get('date'):
				res.pop('date')
		return res
	
	def scroll_to_bottom(self):
		SCROLL_PAUSE_TIME = 0.2

		# Get scroll height
		last_height = 200
		count=200
		while True:
			# Scroll down to bottom
			self.driver.execute_script("window.scrollTo(0, %s);"%count)
			count+=200

			# Wait to load page
			sleep(SCROLL_PAUSE_TIME)
			

			# Calculate new scroll height and compare with last scroll height
			new_height = self.driver.execute_script("return document.body.scrollHeight")
			print('scrolling to %s'%count, last_height, new_height)
			if new_height == last_height:
			    break
			last_height = new_height	
		sleep(1)	

	def load_paginated_sections(self):
		elem_roots=['experience-section','education-section']
		print('loading paginated section ')
		pagination_required=False
		for elem_id in elem_roots:
			try:
				WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#{elem_id} button".format(elem_id=elem_id))))
			except:
				# doesn't exist
				continue
			sect = self.driver.find_element(By.CSS_SELECTOR,"#{elem_id} button".format(elem_id=elem_id))			
			if sect:
				print(sect.text,'section-----', sect.tag_name, sect.parent)
				#sect.click()
				self.driver.execute_script("$('#{elem_id} button').click()".format(elem_id=elem_id))				
				pagination_required=True
				sleep(0.5)
			else:
				continue

			try:
				length = len(self.driver.find_elements_by_css_selector("#{elem_id} ul li".format(elem_id=elem_id)))
				print('existing length', length, "//{elem_id}//ul//li[{length}]".format(elem_id=elem_id,length=length+1))
				#WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//{elem_id}//ul//li[{length}]".format(elem_id=elem_id,length=length+1))))
			except Exception, ex:				
				traceback.print_exc(file=sys.stdout)
				print("pagination exception for ",sect, str(ex))
			finally:
				print("completed.. loading %s section"%sect)
		return pagination_required

	def wait_until_get_section_data(self):
		class wait_until_section_data:
			def __init__(self,*args,**kwargs):
				pass
			def __call__(self,driver):
				return driver.execute_script('return window.hasOwnProperty("section_data")')
		try:
			print('waiting till get section data....')
			WebDriverWait(self.driver,5).until(wait_until_section_data())
		except Exception as ex:
			traceback.print_exc(file=sys.stdout)
			try:
				WebDriverWait(self.driver,5).until(wait_until_section_data())
			except:
				traceback.print_exc(file=sys.stdout)

	def get_section_paginated_data(self):
		self.wait_until_get_section_data()
		script_code="return window.section_data"		
		data = self.driver.execute_script(script_code) or {}
		results=[]

		print('getting section paginated data', data.keys())
		for sect,dt in data.items():
			included = dt.get('included')	
			print('section pagination ....', sect)		
			for x in included:
				results +=[x.get('attributes')]
		return results

	def crawl(self):
		print('Crawling started....')

		orig_dat = []
		for ind,csv_row in enumerate(self.urls_list,1):
			url = csv_row['linkedin_url']
			if url and len(url)<20 :
				print "skipping url ",url
				continue
			else:
				print "*** %s/%s *** "%(ind,len(self.urls_list)),"opening url ",url

			if not self.selenium:	
				# We dont't use this right now						
				response = self.get_request(url,headers=default_headers)

				logger.info("Authenticating.....")
				res = self.need_auth(response)		
				logger.info(res.status_code)

				logger.info("redirecting to profile url")
				response = self.get_request(url['linkedin_url'])				

				if response.ok:
					#print response.content
					pass
					#parse_data(response.content)
				else:
					logger.info(response)
			else:
				results = {}

				if self.auth_required:
					if not self.load_session():
						self.selenium_auth()					
				self.driver.get(url)				

				page_content = self.driver.page_source.encode('utf-32', 'ignore')
				self.scroll_to_bottom()
				page_content = self.read_raw_html_data(page_content)			
				self.intercept_ajax_request()
				data = self.read_data(page_content)				

				for key in ['profileview']:
					try:
						orig_dat +=[data]
						results[key] =self.get_data(data, key)									
						results.update({'csv_data':csv_row})
					except ValueError as ve:
						print 'error while expert data',csv_row.get('expert_username')
						print str(ve)
				self.result_list.append(results)
				# pprint(result_list)
				delay_time = delay_list[random.randint(0,len(delay_list)-1)]
				print('delayed for %s ms'%delay_time)
				sleep(delay_time/1000.0)

				if ind%50 == 0:
					self.out_file +=(str(ind/50))
					if self.export:
						frm=ind-51 if ind>=50 else ind-1
						to=ind
						print('exporting.......', self.export, frm,to)
						self.export_json_dump(self.result_list[frm:to])

				

		if self.export:
			print('exporting.......', self.export)
			if self.export=='json':
				self.export_json_dump(self.result_list)
			else:
				self.export_to_file(self.result_list)
		
		with open('scrapper.json','w') as scrp:
			json.dump(orig_dat, scrp)	

		return self.result_list


	def __del__(self):
		if self.selenium:
			#self.save_session()	
			print('__del__ exiting...')
			self.out_file = 'exit_crash_data_%s'%time()
			self.export_json_dump(self.result_list)			
			self.driver.quit()					

	def __exit__(self):
		if self.selenium:
			# login code
			#self.save_session()
			self.driver.quit()					

	def test_demo(self, file_name='profile1.html'):

		content=""
		logger.debug("\n%s\n"%file_name)
		with open(file_name,'r') as fl:
			content	= fl.read().decode('utf-8','ignore')

		data = self.read_raw_html_data(unicode(content.encode('ascii', 'ignore')))			
		data = self.read_data(data)
		results = {}
		for key in ['profileview']:
			try:
				results[key] =self.get_data(data, key)
			except:
				pass

		return results
	
	@staticmethod
	def test():
		print('test started')
		scp = Scrapper('',out_file='test_output.csv',auth=False, selenium=True)
		results=[]
		print "Runnig test 1\n"
		results +=[scp.test_demo(file_name='test/test_1234.html')]

		print "_"*60
		scp.export_to_file(results)
		scp.export_json_dump(results)
		return True

if __name__ =="__main__":

	if len(sys.argv)>1:
		try:
		  opts, args = getopt.getopt(sys.argv[1:],"h:u:s:t:d:o:v:e:r:a:b",['help',"url=","selenium=",'test=','delay=',
																   'out=','verbose=','export=','reuse=','skip_before=','skip_after='])
		except getopt.GetoptError:
		  print 'scrapper.py -u <url or file_path_of_list_of_url> -s <selenium> -t <any positive_number> -d <delay_in_seconds> -o <ouput_file>'
		  sys.exit(2)

		kwargs={}
		for opt, arg in opts:
			if opt in ['-u','--url']:
				kwargs['url'] = arg
			elif opt in ['-s','--selenium']:
				kwargs['selenium']=True
			elif opt in ['-t','--test']:
				kwargs['test']=True
			elif opt in ['-d','--delay']:
				try:
					kwargs['delay'] = float(arg)
				except:
					print "invalid value for delay %s"%arg
			elif opt in ['-v','--verbose']:
				logger.setLevel(logging.DEBUG)
				if arg == 'console':
					console = logging.StreamHandler()
					formatter = logging.Formatter('%(asctime)s - %(message)s')
					console.setFormatter(formatter)
					logger.addHandler(console)
			elif opt in ['-v','--out']:
				kwargs['out_file'] = arg
			elif opt in ['e','--export']:
				kwargs['export']=arg
			elif opt in ['-r','--reuse']:
				kwargs['old_session'] = True
			elif opt in ['e','--help']:
				print Scrapper.__doc__
			elif opt in ['-b','--skip_before']:
				kwargs['skip_before']=arg
			elif opt in ['-a','--skip_after']:
				kwargs['skip_after']=arg				
			else:
				sys.exit(0)

		if kwargs.get('url'):
			if LINKEDIN_UNAME and SESSION_PASS:
				url =kwargs.get('url')			
				Scrapper(**kwargs).crawl()
			else:
				print "Need to set LINKEDIN_UNAME and SESSION_PASS on line no 25,26s"
		elif kwargs.get('test'):
			Scrapper.test()
		else:
			print 'scrapper.py -u <url or file_path_of_list_of_url> -s <selenium> -t -d'
			sys.exit(2)
	else:
		print Scrapper.__doc__
		sys.exit(0)