import dialogs, ui, collections, re, console, datetime, photos, hashlib

import sys
PY3 = sys.version_info[0] >= 3
if PY3:
	basestring = str

class _FormDialogController (object):
	def __init__(self, title, sections, done_button_title='Done', font=None):
		self.was_canceled = True
		#self.was_canceled = False
		self.shield_view = None
		self.values = {}
		self.container_view = _FormContainerView()
		self.container_view.frame = (0, 0, 500, 500)
		self.container_view.delegate = self
		self.view = ui.TableView('grouped')
		self.view.flex = 'WH'
		self.container_view.add_subview(self.view)
		self.container_view.name = title
		self.view.frame = (0, 0, 500, 500)
		self.view.data_source = self
		self.view.delegate = self
		self.cells = []
		self.tf_ramq = 'xxxxxxxxxxxx'
		
		self.sections = sections
		
		for section in self.sections:
			section_cells = []
			self.cells.append(section_cells)
			items = section[1]
			for i, item in enumerate(items):
				cell = ui.TableViewCell('value1')
				icon = item.get('icon', None)
				tint_color = item.get('tint_color', None)
				if font:
					cell.text_label.font=font
				if tint_color:
					cell.tint_color = tint_color
				if icon:
					if isinstance(icon, basestring):
						icon = ui.Image.named(icon)
					if tint_color:
						cell.image_view.image = icon.with_rendering_mode(ui.RENDERING_MODE_TEMPLATE)
					else:
						cell.image_view.image = icon
					
				title_color = item.get('title_color', None)
				if title_color:
					cell.text_label.text_color = title_color
				
				t = item.get('type', None)
				key = item.get('key', item.get('title', str(i)))
				item['key'] = key
				title = item.get('title', '')
				if t == 'segmented':
					value = item.get('value', '')
					self.values[key] = value
					#bgcolor = 0.9
					
					#Set up cell
					cell.selectable = False
					cell.text_label.text = title
					label_width = ui.measure_string(title, font=cell.text_label.font)[0]
					cell_width, cell_height = cell.content_view.width, cell.content_view.height
					#cell.background_color= bgcolor

					
					#Set up scroll view
					scroll = ui.ScrollView()
					scroll_width = max(40, cell_width - label_width - 32)
					scroll.frame = (cell_width - scroll_width - 8, 1, scroll_width, cell_height-2)
					scroll.flex = 'W'
					#scroll_width = max(40, cell_width - label_width )
					#scroll.frame = (cell_width - scroll_width+40, 1, scroll_width, cell_height-2)
					scroll.shows_horizontal_scroll_indicator = False
					#scroll.background_color = bgcolor
					
					#Set up segment
					segment = ui.SegmentedControl()
					choices = item.get('choice', '').split("|")
					segment.segments = choices
					if value != '':
						segment.selected_index = choices.index(value)
					#segment.value = value
					segment.name = key
					segment.action = self.segment_action
					segment.frame = (0, 0, len(segment.segments)*65, scroll.height )
					
					#Combining SUBVIEWS
					scroll.content_size = (len(segment.segments)*65, scroll.height)
					scroll.add_subview(segment)
					cell.content_view.add_subview(scroll)
				
				elif t == 'photo':
					value = item.get('value', False)
					self.values[key] = value
					cell.text_label.text = title
					cell.selectable = False
					photo_button = ui.Button()
					photo_button.name = key
					show_photo = ui.Button()
					show_photo.name = key
					label_width = ui.measure_string(title, font=cell.text_label.font)[0]
					cell_width, cell_height = cell.content_view.width, cell.content_view.height
					ph_width = max(40, cell_width - label_width - 32)
					photo_button.frame = (cell_width - ph_width - 8, 1, ph_width/3, cell_height-2)
					show_photo.frame = ( cell_width - ph_width/2 ,1, ph_width/2, cell_height-2)
					photo_button.flex = 'W'
					photo_button.background_color = 0.9
					show_photo.background_color = 0.95
					photo_button.title = 'Take picture'
					show_photo.title = 'Show picture'
					cell.content_view.add_subview(photo_button)
					cell.content_view.add_subview(show_photo)
					photo_button.action = self.take_photo
					#photo_button.action = self.photoBooth
					show_photo.action = self.photo_quicklook
					
				elif t == 'switch':
					value = item.get('value', False)
					self.values[key] = value
					cell.text_label.text = title
					cell.selectable = False
					switch = ui.Switch()
					w, h = cell.content_view.width, cell.content_view.height
					switch.center = (w - switch.width/2 - 10, h/2)
					switch.flex = 'TBL'
					switch.value = value
					switch.name = key
					switch.action = self.switch_action
					if tint_color:
						switch.tint_color = tint_color
					cell.content_view.add_subview(switch)
				elif t == 'text' or t == 'url' or t == 'email' or t == 'password' or t == 'number':
					value = item.get('value', '')
					self.values[key] = value
					placeholder = item.get('placeholder', '')
					cell.selectable = False
					cell.text_label.text = title
					label_width = ui.measure_string(title, font=cell.text_label.font)[0]
					if cell.image_view.image:
						label_width += min(64, cell.image_view.image.size[0] + 16)
					cell_width, cell_height = cell.content_view.width, cell.content_view.height
					tf = ui.TextField()
					
					tf.name = key
					if tf.name == 'fname' :
						self.tf_fname = tf
					if tf.name == 'lname' :
						self.tf_lname = tf
					if tf.name == 'ramq' :
						self.tf_ramq = tf
					
					tf_width = max(40, cell_width - label_width - 32)
					tf.frame = (cell_width - tf_width - 8, 1, tf_width, cell_height-2)
					tf.bordered = False
					tf.placeholder = placeholder
					tf.flex = 'W'
					tf.text = value
					tf.text_color = '#337097'
					if t == 'text':
						tf.autocorrection_type = item.get('autocorrection', None)
						tf.autocapitalization_type = item.get('autocapitalization', ui.AUTOCAPITALIZE_SENTENCES)
						tf.spellchecking_type = item.get('spellchecking', None)
					if t == 'url':
						tf.keyboard_type = ui.KEYBOARD_URL
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'email':
						tf.keyboard_type = ui.KEYBOARD_EMAIL
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'number':
						tf.keyboard_type = ui.KEYBOARD_NUMBERS
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'password':
						tf.secure = True
					
					tf.clear_button_mode = 'while_editing'
					tf.name = key
					tf.delegate = self
					cell.content_view.add_subview(tf)

				elif t == 'check':
					value = item.get('value', False)
					group = item.get('group', None)
					if value:
						cell.accessory_type = 'checkmark'
						cell.text_label.text_color = cell.tint_color
					cell.text_label.text = title
					if group:
						if value:
							self.values[group] = key
					else:
						self.values[key] = value
				elif t == 'date' or t == 'datetime' or t == 'time':
					value = item.get('value', datetime.datetime.now())
					if type(value) == datetime.date:
						value = datetime.datetime.combine(value, datetime.time())
					if type(value) == datetime.time:
						value = datetime.datetime.combine(value, datetime.date.today())
					date_format = item.get('format', None)
					if not date_format:
						if t == 'date':
							date_format = '%Y-%m-%d'
						elif t == 'time':
							date_format = '%H:%M'
						else:
							date_format = '%Y-%m-%d %H:%M'
					item['format'] = date_format
					cell.detail_text_label.text = value.strftime(date_format)
					self.values[key] = value
					self.ramq_dob = ''
					cell.text_label.text = title
				else:
					cell.selectable = False
					cell.text_label.text = item.get('title', '')

				section_cells.append(cell)
				
		done_button = ui.ButtonItem(title=done_button_title)
		done_button.action = self.done_action
		self.container_view.right_button_items = [done_button]

	def update_kb_height(self, h):
		self.view.content_inset = (0, 0, h, 0)
		self.view.scroll_indicator_insets = (0, 0, h, 0)
	
	def tableview_number_of_sections(self, tv):
		return len(self.cells)
	
	def tableview_title_for_header(self, tv, section):
		return self.sections[section][0]

	def tableview_title_for_footer(self, tv, section):
		s = self.sections[section]
		if len(s) > 2:
			return s[2]
		return None
	
	def tableview_number_of_rows(self, tv, section):
		return len(self.cells[section])
	
	def tableview_did_select(self, tv, section, row):
		sel_item = self.sections[section][1][row]
		t = sel_item.get('type', None)
		if t == 'check':
			key = sel_item['key']
			tv.selected_row = -1
			group = sel_item.get('group', None)
			cell = self.cells[section][row]
			if group:
				for i, s in enumerate(self.sections):
					for j, item in enumerate(s[1]):
						if item.get('type', None) == 'check' and item.get('group', None) == group and item is not sel_item:
							self.cells[i][j].accessory_type = 'none'
							self.cells[i][j].text_label.text_color = None
				cell.accessory_type = 'checkmark'
				cell.text_label.text_color = cell.tint_color
				self.values[group] = key
			else:
				if cell.accessory_type == 'checkmark':
					cell.accessory_type = 'none'
					cell.text_label.text_color = None
					self.values[key] = False
				else:
					cell.accessory_type = 'checkmark'
					self.values[key] = True
		elif t == 'date' or t == 'time' or t == 'datetime':
			tv.selected_row = -1
			self.selected_date_key = sel_item['key']
			self.selected_date_value = self.values.get(self.selected_date_key)
			self.selected_date_cell = self.cells[section][row]
			self.selected_date_format = sel_item['format']
			self.selected_date_type = t
			if t == 'date':
				mode = ui.DATE_PICKER_MODE_DATE
			elif t == 'time':
				mode = ui.DATE_PICKER_MODE_TIME
			else:
				mode = ui.DATE_PICKER_MODE_DATE_AND_TIME
			self.show_datepicker(mode)
	
	def show_datepicker(self, mode):
		ui.end_editing()
		self.shield_view = ui.View()
		self.shield_view.flex = 'WH'
		self.shield_view.frame = (0, 0, self.view.width, self.view.height)
		
		self.dismiss_datepicker_button = ui.Button()
		self.dismiss_datepicker_button.flex = 'WH'
		self.dismiss_datepicker_button.frame = (0, 0, self.view.width, self.view.height)
		self.dismiss_datepicker_button.background_color = (0, 0, 0, 0.5)
		self.dismiss_datepicker_button.action = self.dismiss_datepicker
		self.dismiss_datepicker_button.alpha = 0.0
		self.shield_view.add_subview(self.dismiss_datepicker_button)

		self.date_picker = ui.DatePicker()
		self.date_picker.date = self.selected_date_value
		self.date_picker.background_color = 'white'
		self.date_picker.mode = mode
		self.date_picker.frame = (0, self.shield_view.height - self.date_picker.height, self.shield_view.width, self.date_picker.height)
		self.date_picker.flex = 'TW'
		self.date_picker.transform = ui.Transform.translation(0, self.date_picker.height)
		self.shield_view.add_subview(self.date_picker)

		self.container_view.add_subview(self.shield_view)
		
		def fade_in():
			self.dismiss_datepicker_button.alpha = 1.0
			self.date_picker.transform = ui.Transform.translation(0, 0)
		ui.animate(fade_in, 0.3)

	def dismiss_datepicker(self, sender):
		value = self.date_picker.date
		
		if self.selected_date_type == 'date':
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)
		elif self.selected_date_type == 'time':
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)
		else:
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)
		self.values[self.selected_date_key] = value
		
		def fade_out():
			self.dismiss_datepicker_button.alpha = 0.0
			self.date_picker.transform = ui.Transform.translation(0, self.date_picker.height)
			
		def remove():
			self.container_view.remove_subview(self.shield_view)
			self.shield_view = None
			
			year = self.values[self.selected_date_key].strftime('%y')
			month = self.values[self.selected_date_key].strftime('%m')
			day = self.values[self.selected_date_key].strftime('%d')
			#self.ramq_dob = self.values[self.selected_date_key].strftime('%y%m%d')
			if self.values['is_female']:
				month = str(50+int(month))
			self.ramq_dob = year + month + day
			self.set_ramq_number()
		
		ui.animate(fade_out, 0.3, completion=remove)
			
	def tableview_cell_for_row(self, tv, section, row):
		return self.cells[section][row]
	
	def textfield_did_change(self, tf):
		self.values[tf.name] = tf.text
	
	def textfield_did_end_editing(self, tf):
		if tf.name == 'lname' or tf.name == 'fname':
			self.set_ramq_number()
		
	def set_ramq_number(self):
		#add 50 to month if female
		clean_lname = re.sub(r'[^a-zA-Z ]', '', self.tf_lname.text)
		clean_fname = re.sub(r'[^a-zA-Z ]', '', self.tf_fname.text)
		ramq_letters = (clean_lname[:3] + clean_fname[:1]).upper()
		self.tf_ramq.text = ramq_letters + self.ramq_dob
		self.values['ramq'] = self.tf_ramq.text

	def photoBooth(self, sender):
		ui.end_editing()
		self.booth = ui.View()
		self.booth.flex = 'WH'
		self.booth.frame = (0, 0, self.view.width, self.view.height)
		
		self.dismiss_booth_button = ui.Button()
		self.dismiss_booth_button.flex = 'WH'
		self.dismiss_booth_button.frame = (0, 0, self.view.width, self.view.height)
		self.dismiss_booth_button.background_color = (0, 0, 0, 0.5)
		self.dismiss_booth_button.action = self.dismiss_booth
		self.dismiss_booth_button.alpha = 1.0
		self.booth.add_subview(self.dismiss_booth_button)

		self.snap = ui.Button()
		self.snap.title = 'Snap!'
		self.snap.background_color = 'white'
		self.snap.height = 200
		self.snap.frame = (0, self.booth.height - self.snap.height, self.booth.width, self.snap.height)
		self.snap.flex = 'TW'
		self.snap.action = self.take_photo
		self.booth.add_subview(self.snap)
		
		self.container_view.add_subview(self.booth)

		
	def dismiss_booth(self, sender):
		#value = self.photo_booth.path
		
		def fade_out():
			self.dismiss_booth_button.alpha = 0.0
			
		def remove():
			self.container_view.remove_subview(self.booth)
			self.booth = None
			
		ui.animate(fade_out, 0.3, completion=remove)

	def take_photo(self, sender):
		self.img = photos.capture_image()
		if self.img:
			time_now = datetime.datetime.now().strftime('%c')
			photo_hash = hashlib.sha1(time_now.encode('UTF-8')).hexdigest()
			self.card_photo_path = 'capture/' + photo_hash + '.jpeg'
			self.values[sender.name] = self.card_photo_path
			self.img.save(self.card_photo_path)
		
		"""
		time_now = datetime.datetime.now().strftime('%c')
		photo_hash = hashlib.sha1(time_now.encode('UTF-8')).hexdigest()
		self.card_photo_path = 'capture/' + photo_hash + '.jpeg'
		self.values[self.photo_key] = self.card_photo_path
		out_file = ModCameraScanner.main(self.card_photo_path)
		self.values[self.photo_key] = out_file
		"""
	
	def photo_quicklook(self, sender):
		if self.values[sender.name] == '':
			dialogs.hud_alert('There are no pictures associated')
		else:
			console.quicklook(self.values[sender.name])
	
	def switch_action(self, sender):
		self.values[sender.name] = sender.value
	
	def segment_action(self, sender):
		self.values[sender.name] = sender.segments[sender.selected_index]

	def done_action(self, sender):
		if self.shield_view:
			self.dismiss_datepicker(None)
		#elif self.booth:
			#self.dismiss_booth(None)
		else:
			ui.end_editing()
			self.was_canceled = False
			self.container_view.close()			


#def take_photo(sender):
	#img = photos.capture_image()
		
class _FormContainerView (ui.View):
	def __init__(self):
		self.delegate = None
		
	def keyboard_frame_will_change(self, f):
		r = ui.convert_rect(f, to_view=self)
		if r[3] > 0:
			kbh = self.height - r[1]
		else:
			kbh = 0
		if self.delegate:
			self.delegate.update_kb_height(kbh)

def form_dialog(title='', fields=None, sections=None, done_button_title='Done', font=None, frame=None):
	if not sections and not fields:
		raise ValueError('sections or fields are required')
	if not sections:
		sections = [('', fields)]
	if not isinstance(title, basestring):
		raise TypeError('title must be a string')
	for section in sections:
		if not isinstance(section, collections.Sequence):
			raise TypeError('Sections must be sequences (title, fields)')
		if len(section) < 2:
			raise TypeError('Sections must have 2 or 3 items (title, fields[, footer]')
		if not isinstance(section[0], basestring):
			raise TypeError('Section titles must be strings')
		if not isinstance(section[1], collections.Sequence):
			raise TypeError('Expected a sequence of field dicts')
		for field in section[1]:
			if not isinstance(field, dict):
				raise TypeError('fields must be dicts')

	c = _FormDialogController(title, sections, done_button_title=done_button_title, font=font)
	if frame:
		c.container_view.frame = frame
	c.container_view.present('sheet')
	c.container_view.wait_modal()
	# Get rid of the view to avoid a retain cycle:
	#c.container_view = None
	if c.was_canceled:
		return None
	return c.values

def list_dialog(title='', items=None, multiple=False, done_button_title='Done', frame =None):
	if not items:
		items = []
	if not isinstance(title, basestring):
		raise TypeError('title must be a string')
	if not isinstance(items, collections.Sequence):
		raise TypeError('items must be a sequence')

	c = dialogs._ListDialogController(title, items, multiple, done_button_title=done_button_title)
	if frame:
		c.view.frame = frame
	c.view.present('sheet')
	c.view.wait_modal()
	return c.selected_item
