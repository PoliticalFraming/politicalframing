phrase="iraq"
frame_words = Frame.get(Frame.name == 'crime').word_string
highlight_query = frame_words.replace(" ", " OR ")

query = si.query(phrase) \
		  .highlight(
			"speaking",
			useFastVectorHighlighter=True) \
		  .highlight(q=highlight_query) \
		  .terms('speaking') \
		  .terms(tf=True) \
		  .query(date__range=(datetime(2003,7,1), datetime(2004,1,1)))

params = query.params()
params.append(('frameFreq', "product(sum(" + ", ".join(map(lambda word: "termfreq(speaking,\"%s\")" % word,frame_words.split())) + "), norm(speaking))"))
params.append(("fl", "*, $frameFreq"))
params.append(("sort", "$frameFreq desc"))

# query($qq) desc

# qq={!v="speaking:(chain OR rob OR resistance OR gang OR holdout OR defraud OR shanghai OR violation OR breach)"}

response = si.conn.select(params)
parsed_response = si.schema.parse_response(response)
result = parsed_response.result

numFound = result.numFound
docs = result.docs
highlighting = parsed_response.highlighting
term_vectors = parsed_response.term_vectors

pp(numFound)

# {!frange l=0.85}query($qq)
# date
# qq=speaking:immigration