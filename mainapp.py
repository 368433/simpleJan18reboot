import ui
from classified import Morpheus
from database import Patient, Act

def show_morpheus():
	#wh = ui.get_screen_size()
	#f=(0,0,wh[0],wh[1])
	f=(0,0,350,650)
	tabs = ['All', 'Outpt', 'Inpt', 'Inactive']
	extra_tabs= ui.SegmentedControl()
	extra_tabs.segments = ['To See', 'Seen']
	extra_tabs.name = 'todaytab'
	items_toAdd = [{'title':'Patient', 'object':Patient()}, {'title':'Act', 'object':Act()}]
	Morpheus(Patient, items_toAdd, frame = f, tabs_contents = tabs, extra_data = extra_tabs)


"""
try:
	reason = 'Use your fingerprint to log in. You have 10 seconds.'
	TouchID.authenticate(reason, allow_passcode=True, timeout=10)
	v = ui.load_view()
	#v.present('sheet', hide_title_bar=True)
	v.present('sheet')
except TouchID.AuthFailedException as e:
	print (e)
"""		

#v = ui.load_view()
#v.present('sheet')
#print(ui.get_screen_size())
show_morpheus()
