extends Node

func _ready():
	pass

func http_get_request(request, dictionaryPayload):
	var err = 0
	var http = HTTPClient.new()
	var err = http.connect("http://127.0.0.1", 5000)
	var json = ""
	if dictionaryPayload != "":
		json = "REWORK"
		#var json = dictionaryPayload.to_json()
		#var json = http.query_string_from_dict(dictionaryPayload)
		#var json = str(dictionaryPayload)
		
		#print("HTTP JSON",json)
		#var typepath = typeof(json)
		#print(typepath)
	assert(err==OK)
	
	print("starting to connect")
	# Wait until resolved and connected
	while( http.get_status()==HTTPClient.STATUS_CONNECTING or http.get_status()==HTTPClient.STATUS_RESOLVING):
		http.poll()
		print("Connecting..")
		OS.delay_msec(500)

	assert( http.get_status() == HTTPClient.STATUS_CONNECTED ) # Could not connect
	
	var headers=["Content-Type: application/json"] #[""]
	
	#var typepath = typeof(json)
	#print(typepath)
	err = http.request(HTTPClient.METHOD_POST, request, headers, json)# was json
	
	assert(err == OK)
	
	while (http.get_status() == HTTPClient.STATUS_REQUESTING) :
		# Keep polling until the request is going on
		http.poll()
		print("Requesting..")
		OS.delay_msec(500)
		
	assert( http.get_status() == HTTPClient.STATUS_BODY or http.get_status() == HTTPClient.STATUS_CONNECTED ) # Make sure request finished well.
	
	if (http.has_response()):
		print("code: ", http.get_response_code())
		
		var rb = RawArray()
		while(http.get_status()==HTTPClient.STATUS_BODY):
			http.poll()
			var chunk = http.read_response_body_chunk()
			if (chunk.size()==0):
				OS.delay_usec(1000)
			else:
				rb = rb + chunk
		var text = rb.get_string_from_ascii()
		return text
