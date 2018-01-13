import ui, dialogs, AIdialogs, console, photos, datetime, hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Patient, Act

engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)


class _MorpheusContainer (object):

	def __init__(self, items_toAdd, frame=None, tabs_contents =None, patient_id=None, extra_data=None):

		#SETUP VIEW
		self.view = ui.View()
		self.view.background_color = 'white'
		if frame:
			self.view.frame = frame
		else:
			self.view.frame = (0,0,500,500)
		height = self.view.height
		width = self.view.width
		self.patient_id = patient_id
				
		#SETUP THE TOP SEGMENTED TABS AND CONTAINER
		self.tab_container = ui.View()
		self.tabs = ui.SegmentedControl()
		self.tab_container.frame = (0, 0, width, 50)
		self.tab_container.add_subview(self.tabs)
		self.tabs.frame = (10, 10, width-20, self.tab_container.height-10)
		self.tabs.segments = tabs_contents
		self.tabs.selected_index = 0
		
		#SETUP EXTRA DATA CONTAINER
		self.extra_container = ui.View()
		self.extra_container.frame = (0, self.tab_container.height, width, 50)
		self.extra_container.background_color = 'white'
		self.extra_data = extra_data
		if self.extra_data:
			self.extra_container.add_subview(extra_data)
			if self.extra_data.name == 'todaytab':
				self.extra_data.selected_index = 0
				self.extra_data.enabled = False
				self.extra_data.center = (self.extra_container.width * 0.5, self.extra_container.height * 0.5)
		
		#SETUP THE TABLE LISTING THE ITEMS
		self.table = ui.TableView()
		self.LDS = modListDataSource([2, 3, 4, 5])
		self.LDS.accessory = 'detail_button'
		self.LDS.font = ('Courier', 16)
		self.table.data_source = self.table.delegate = self.LDS
		self.table.frame = (0, self.tab_container.height + self.extra_container.height +10, width, height)
		
		#SETUP THE ADD BUTTON
		self.addButton = ui.Button()
		self.addButton.background_color = 'salmon'
		self.addButton.title = 'Add'
		bt_height = self.addButton.height = 60
		self.addButton.frame = (0, height-bt_height, width, bt_height)

		#ADD ALL SUBVIEWS
		self.view.add_subview(self.tab_container)
		self.view.add_subview(self.extra_container)
		self.view.add_subview(self.table)
		self.view.add_subview(self.addButton)

		#SETUP UI ITEMS ACTIONS
		def parse_segments(sender):
			self.parse_segments()
		
		def add_item(sender):
			if self.patient_id:
				pt_id = self.patient_id
				self.add_item(self.items_toAdd, pt_id = pt_id)
			else:
				self.add_item(self.items_toAdd)
		
		def show_options(sender):
			show_all_options(self)
		
		def show_data(sender):
			show_full_data(self)
		
		self.tabs.action = parse_segments
		self.items_toAdd = items_toAdd
		self.addButton.action = add_item
		self.LDS.accessory_action = show_data
		self.LDS.action = show_options
	
	def parse_segments(self):
		self.update_list()
			
	def populate_list(self, db_table, criteria=None):
		session = Session()
		if self.patient_id:
			self.LDS.items = session.query(db_table).filter(db_table.id == self.patient_id).all()
		else:
			self.LDS.items = session.query(db_table).all()
		session.close()
		
	def update_list(self, filter=None):
		session = Session()
		option = self.tabs.segments[self.tabs.selected_index]
		if option == 'Inactive' :
			if self.extra_data.name == 'todaytab' :
				self.extra_data.enabled = False
			self.LDS.items = session.query(Patient).filter(Patient.is_active == False).all()
		if option == 'Outpt' :
			if self.extra_data.name == 'todaytab' :
				self.extra_data.enabled = True
			self.LDS.items = session.query(Patient).filter(Patient.is_active == True, Patient.is_inpatient == False).all()
		if option == 'Inpt':
			if self.extra_data.name == 'todaytab' :
				self.extra_data.enabled = True
			self.LDS.items = session.query(Patient).filter(Patient.is_active == True, Patient.is_inpatient == True).all()
		if option == 'All Acts' :
			if self.patient_id:
				self.LDS.items = session.query(Act).filter(Act.patient_id == self.patient_id).all()
		if option == 'Notes':
			self.LDS.items = ['hust','hiding']
		if option == 'Reminder':
			self.LDS.items = ['JJJJJust','KKiding']
		if option == 'All':
			if self.extra_data.name == 'todaytab' :
				self.extra_data.enabled = False
			self.LDS.items = session.query(Patient).all()
		session.close()
		
	def add_item(self, items, pt_id=None):
		#items is a list of dictionaries containing a title of section
		#and an object to be created.
		#The attribute of the object are the entries in the form
		# once done, the object is added to database
		#example:
		#item=[{'title':'section title', 'object':Patient()}]

		query_fields = []
		created_objects = {}
		for item in items:
			title = item.get('title','')
			object = item.get('object',None)
			section = (title, get_entry_fields(object))
			query_fields.append(section)
		data = AIdialogs.form_dialog(sections = query_fields, frame=self.view.frame)
		
		#CHECK DATA INTEGRITY
		if data is None:
			return
		for i, item in enumerate(items):
			if isinstance(item.get('object'), Patient):
				if data['fname'] == '' and data['lname'] == '' and data['mrn'] == '' and data['ramq'] == '':
					#dialogs.hud_alert("Patient not created. At least one valid unique identifier required")
					console.alert(title='Patient Not Created', message='At least one valid unique identifier require')
					return

		#ADD TO DATABASE
		session = Session()
		for i, item in enumerate(items):
			inclusion = item.get('object')
			for column in inclusion.__table__.columns.keys():
				if column == 'id' or column == 'last_seen':
					continue
				elif column == 'patient_id':
					if pt_id:
						setattr(inclusion, column, pt_id)
				else:
					setattr(inclusion, column, data[column])	
			session.add(inclusion)
			created_objects[type(inclusion)] = inclusion
			session.commit()
		
		new_pt = created_objects.get(Patient, None)
		new_act = created_objects.get(Act, None)
		if new_act:
			if new_pt:
				new_pt.last_seen = str(new_act.date)+','+str(new_act.id)
				new_act.patient_id = new_pt.id
				session.commit()
		session.close()
		
		#UPDATE LIST
		self.update_list()
		
	def update_db(self, item, newdic):
		#Updates a patient or an act object with newdic in database
		session = Session()
		subject = session.query(type(item)).filter(type(item).id == item.id).first()
		for values in newdic:
			setattr(subject,values,newdic[values] )
		session.commit()
		session.close()

@ui.in_background
def show_full_data(sender):
	item = sender.LDS.items[sender.LDS.tapped_accessory_row]
	field = get_entry_fields(item, subject = item)
	section = [('Selected Data', field)]
	updated = AIdialogs.form_dialog(sections=[('Selected data', field)], frame = sender.view.frame)

	if updated:
		#update database entry
		sender.update_db(item, updated)
		#update tableview list
		sender.update_list()

@ui.in_background
def show_all_options(self):
	options = ['See All Acts', 'Add Note', 'Add Reminder', 'Add Act', 'show edit', 'Change Picture']
	option = AIdialogs.list_dialog(title = 'Choose an option', items=options, frame=self.view.frame)
	
	caller = self.LDS.items[self.LDS.selected_row]
	if isinstance(caller, Patient):
		patient_id = caller.id
	if isinstance(caller, Act):
		patient_id = caller.patient_id
		
	#session = Session()
	if option == 'See All Acts' :
		tabs = ['All Acts', 'Notes', 'Reminders']
		items_toAdd = [{'title':'Act', 'object':Act()}]
		Morpheus(Act, items_toAdd, frame = self.view.frame, tabs_contents = tabs, patient_id = patient_id)
	if option == 'Add Act':
		items_toAdd = [{'title':'Act', 'object':Act()}]
		self.add_item(items_toAdd, pt_id = patient_id)
		#AddAct(patient).toDB(process.prompt_data(), session)
	if option=='show edit':
		show_full_data(self)
	if option=='Change Picture':
		take_photo(patient_id)
	#session.close()
	self.update_list()
	self.table.reload()


def take_photo(patient_id):
	img = photos.capture_image()
	if img:
		time_now = datetime.datetime.now().strftime('%c')
		photo_hash = hashlib.sha1(time_now.encode('UTF-8')).hexdigest()
		card_photo_path = 'capture/' + photo_hash + '.jpeg'
		img.save(card_photo_path)
		session=Session()
		patient=session.query(Patient).filter(Patient.id==patient_id).first()
		patient.idCard_path = card_photo_path
		session.commit()
		session.close()


def get_entry_fields(item, subject = None):
	#item has to be an instance of Patient, Act, etc....
	#subject is a populated instance of those types
	fields = get_fields(item)
	if subject:
		for dic in fields:
			dic['value'] = getattr(subject, dic['key'])
		return fields
	else:
		return fields

def Morpheus(db_object, items_toAdd, frame=None, tabs_contents=None, patient_id=None, extra_data=None):
	c = _MorpheusContainer(items_toAdd, frame=frame, tabs_contents = tabs_contents, patient_id=patient_id, extra_data=extra_data)
	c.populate_list(db_object)
	c.update_list()
	#return  c.view
	c.view.present('sheet')
	#c.view.wait_modal()


def get_fields(item):
	if isinstance(item, Patient):
		return [{'type':'photo' ,'key':'idCard_path' ,'value':'' ,'title':'Photo' },
						{'type':'text' ,'key':'fname' ,'value':'' ,'title':'First name' },
						{'type':'text' ,'key':'lname' ,'value':'' ,'title':'Last name' },
						{'type':'check' ,'key':'is_female' ,'value':False ,'title':'Genre Female' },
						{'type':'date' ,'key':'dob' ,'title':'Date of birth' },
						{'type':'number' ,'key':'mrn' ,'value':'' ,'title':'MRN' },
						{'type':'text' ,'key':'ramq' ,'value':'' ,'title':'RAMQ' },
						{'type':'number' ,'key':'phone' ,'value':'' ,'title':'Phone' },
						{'type':'text' ,'key':'postalcode' ,'value':'' ,'title':'Postal Code' },
						{'type':'date' ,'key':'next_visit' ,'title':'Next visit' },
						{'type':'check' ,'key':'is_active' ,'value':True ,'title':'Active' },
						{'type':'check' ,'key':'is_inpatient' ,'value':True ,'title':'Inpatient' }]
	if isinstance(item, Act):
		return [{'type':'photo' ,'key':'act_photo_path' ,'value':'' ,'title':'Photo' },
						{'type':'text' ,'key':'subject' ,'value':'' ,'title':'subject' },
						{'type':'text' ,'key':'root_act' ,'value':'-1' ,'title':'Root Act' },
						{'type':'segmented' ,'key':'facility' ,'choice':'HPB|ICM|PCV', 'value':'' ,'title':'Facility' },
						{'type':'segmented' ,'key':'location' ,'choice':'CPriv|CHCD|ICU|CExt|Urg', 'value':'' ,'title':'Location' },
						{'type':'segmented' ,'key':'category' ,'choice':'Rout|MIEE|OPAT|EcloMaj|EclMin', 'value':'' ,'title':'Category' },
						{'type':'segmented' ,'key':'type' ,'choice':'VP|C|VC|TW', 'value':'' ,'title':'Type' },
						{'type':'text' ,'key':'diagnosis' ,'value':'' ,'title':'Diagnosis' },
						{'type':'text' ,'key':'addendum' ,'value':'' ,'title':'Addendum' },
						{'type':'text' ,'key':'bed' ,'value':'' ,'title':'Bed' },
						{'type':'datetime' ,'key':'date' ,'title':'Date' }]

class modListDataSource(ui.ListDataSource):
	
	def __init__(self, items = None):
		super().__init__(items)
	
	def get_tableview(self):
		return self.tableview
		
	def tableview_delete(self, tableview, section, row):
		element = self.items[row]
		session = Session()
		element = session.query(type(element)).filter_by(id = element.id).first()
		session.delete(element)
		session.commit()
		session.close()
		
		self.reload_disabled = True
		del self.items[row]
		self.reload_disabled = False
		tableview.reload_data()
		#uncomment following line if want animation on delete:
		#tableview.delete_rows([row])
		if self.edit_action:
			self.edit_action(self)

	def tableview_cell_for_row(self, tableview, section, row):
		item = self.items[row]
		cell = ui.TableViewCell('subtitle')
		cell.text_label.number_of_lines = self.number_of_lines
		cell.text_label.text = str(item)
		if type(item) is Patient:
			cell.detail_text_label.text = "Last seen: {0}".format(item.last_seen[:10])
		if type(item) is Act:
			cell.detail_text_label.text = "Seen: {0}".format(item.date.strftime("%a %d/%b/%Y at %Hh%M"))
		cell.accessory_type = self.accessory
		if self.text_color:
			cell.text_label.text_color = self.text_color
		if self.highlight_color:
			bg_view = View(background_color=self.highlight_color)
			cell.selected_background_view = bg_view
		if self.font:
			cell.text_label.font = self.font
		return cell


"""
if __name__ == '__main__':
	f=(0,0,350,650)
	tabs = ['All', 'Outpt', 'Inpt', 'Inactive']
	todaytab= ui.SegmentedControl()
	todaytab.segments = ['To See', 'Seen']
	todaytab.name = 'todaytab'
	items_toAdd = [{'title':'Patient', 'object':Patient()}, {'title':'Act', 'object':Act()}]
	
	Morpheus(Patient, items_toAdd, frame = f, tabs_contents = tabs, extra_data = todaytab)
"""
