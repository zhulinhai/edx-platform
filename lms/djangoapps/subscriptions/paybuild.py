#
# build cb payment
#
def build_cb_payment(typesus, studentid, studentemail, debug_mode='0'):
	import uuid
	
	sustype = "Basic"
	sysmodel = "For Individuals"
	amount = 0
	amount_monthly = 0
	if typesus == '2' or typesus == '3':
		if typesus == '2':
			sustype = "Plus"
			amount = 99.00
			amount_monthly = 19.00
		else:
			sustype = "Pro"
			amount = 199.00
			amount_monthly = 39.00
	elif typesus == '6':
		sysmodel = "For Entrerprise"
		sustype = "Premium"
		amount = 499.00
		amount_monthly = 99.00

	# amount Format EUR (####.##)
	if amount > 0:
		amount = str(amount)
		amount = amount.replace(',', '.')
		amount = float(amount)
		# amount = "{0:0.2f}".format(amount)
	else:
		amount = 0
	if amount_monthly > 0:
		amount_monthly = str(amount_monthly)
		amount_monthly = amount_monthly.replace(',', '.')
		amount_monthly = float(amount_monthly)
		# amount = "{0:0.2f}".format(amount)
	else:
		amount_monthly = 0

    #
	# Params and return form
	#
	#url_pay = 'https://www.sandbox.paypal.com/cgi-bin/webscr'  # url payment develop
	#merchan_id = "calzada-facilitator@iblstudios.com"  # merchan_id or merchan_email
	url_pay='https://www.paypal.com/cgi-bin/webscr' #url payment production
	merchan_id = "sales@buildacademy.com"  # merchan_id or merchan_email
	
	item_name = "Subscription %s %s" % (sysmodel, sustype)
	item_name_monthly = "Subscription Monthly %s %s" % (sysmodel, sustype)
	item_number = uuid.uuid4().hex  # uniqueid
	currency_code = "USD"
	locale_code = "en_US"
	btn_txt = 'Pay with PayPal Year'
	btn_txt_monthly = 'Pay with PayPal Monthly'
	notify_url = "https://courses.buildacademy.com/paysubscallback"  # post process
	return_url = "https://courses.buildacademy.com/membership?m=%s&pay=done" % (typesus) # back url user
	custom = '%s|%s' % (studentid, typesus)


    # construct dict
	import collections
	
	arr_data_to_send = collections.OrderedDict()
	arr_data_to_send.update({ 'business' : merchan_id })
	arr_data_to_send.update({ 'cmd' : '_ext-enter' })
	arr_data_to_send.update({ 'redirect_cmd' : '_xclick-subscriptions' })
	arr_data_to_send.update({ 'display' : '0' })
	arr_data_to_send.update({ 'no_shipping' : '1' })
	arr_data_to_send.update({ 'item_name' : item_name })
	arr_data_to_send.update({ 'item_number' : item_number })
	arr_data_to_send.update({ 'quantity' : '1' })
	arr_data_to_send.update({ 'amount' : amount })
	arr_data_to_send.update({ 'currency_code' : currency_code })
	arr_data_to_send.update({ 'lc' : locale_code })
	#arr_data_to_send.update({ 'login_email' : studentemail })
	arr_data_to_send.update({ 'email' : studentemail })
	arr_data_to_send.update({ 'user_id' : studentid })
	arr_data_to_send.update({ 'type_sus' : typesus })
	arr_data_to_send.update({ 'no_note' : 1 })
	arr_data_to_send.update({ 'custom' : custom })
    # control payment
	arr_data_to_send.update({ 'notify_url' : notify_url })
	arr_data_to_send.update({ 'rm' : 2 })
	arr_data_to_send.update({ 'cbt' : 'Back To Build Academy' })
	arr_data_to_send.update({ 'return' : return_url })
	arr_data_to_send.update({'a3': amount})
	arr_data_to_send.update({'t3': 'Y'})
	arr_data_to_send.update({'p3': '1'})
	arr_data_to_send.update({'src': '1'})

	arr_data_to_send_monthly = collections.OrderedDict()
	arr_data_to_send_monthly.update({ 'business' : merchan_id })
	arr_data_to_send_monthly.update({ 'cmd' : '_ext-enter' })
	arr_data_to_send_monthly.update({ 'redirect_cmd' : '_xclick-subscriptions' })
	arr_data_to_send_monthly.update({ 'display' : '0' })
	arr_data_to_send_monthly.update({ 'no_shipping' : '1' })
	arr_data_to_send_monthly.update({ 'item_name' : item_name_monthly })
	arr_data_to_send_monthly.update({ 'item_number' : item_number })
	arr_data_to_send_monthly.update({ 'quantity' : '1' })
	arr_data_to_send_monthly.update({ 'amount' : amount_monthly })
	arr_data_to_send_monthly.update({ 'currency_code' : currency_code })
	arr_data_to_send_monthly.update({ 'lc' : locale_code })
	#arr_data_to_send.update({ 'login_email' : studentemail })
	arr_data_to_send_monthly.update({ 'email' : studentemail })
	arr_data_to_send_monthly.update({ 'user_id' : studentid })
	arr_data_to_send_monthly.update({ 'type_sus' : typesus })
	arr_data_to_send_monthly.update({ 'no_note' : 1 })
	arr_data_to_send_monthly.update({ 'custom' : custom })
    # control payment
	arr_data_to_send_monthly.update({ 'notify_url' : notify_url })
	arr_data_to_send_monthly.update({ 'rm' : 2 })
	arr_data_to_send_monthly.update({ 'cbt' : 'Back To Build Academy' })
	arr_data_to_send_monthly.update({ 'return' : return_url })
	arr_data_to_send_monthly.update({'a3': amount_monthly})
	arr_data_to_send_monthly.update({'t3': 'M'})
	arr_data_to_send_monthly.update({'p3': '1'})
	arr_data_to_send_monthly.update({'src': '1'})

	# create form
	if debug_mode != '0':
		result = '<form action="%s" name="payment_submit" id="payment_submit" method="post">' % (url_pay)
		for (k, v) in arr_data_to_send.items():
			result += '<input type="text" name="%s" value="%s">' % (k, v)
		result += '<br><span class="submitbutton"><i class="fa fa-paypal"></i> %s</span>' % (btn_txt)
		result += "</form>"
		result += '<form action="%s" name="payment_submit" id="payment_submit" method="post">' % (url_pay)
		for (k, v) in arr_data_to_send_monthly.items():
			result += '<input type="text" name="%s" value="%s">' % (k, v)
		result += '<br><span class="submitbutton"><i class="fa fa-paypal"></i> %s</span>' % (btn_txt_monthly)
		result += "</form>"
	else:
		result = '<form action="%s" name="payment_submit" id="payment_submit" method="post">' % (url_pay)
		for (k, v) in arr_data_to_send.items():
			result += '<input type="hidden" name="%s" value="%s">' % (k, v)
		result += '<button type="submit" class="submitbutton"><i class="fa fa-paypal"></i> %s</button>' % (btn_txt)
		result += "</form>"
		result += '<form action="%s" name="payment_submit" id="payment_submit" method="post">' % (url_pay)
		for (k, v) in arr_data_to_send_monthly.items():
			result += '<input type="hidden" name="%s" value="%s">' % (k, v)
		result += '<button type="submit" class="submitbutton"><i class="fa fa-paypal"></i> %s</button>' % (btn_txt_monthly)
		result += "</form>"
	return result
