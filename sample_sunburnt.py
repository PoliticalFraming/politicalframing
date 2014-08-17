phrase="immigration"
frame = Frame.get(Frame.name == 'common_words').word_string
highlight_query = frame.replace(" ", " OR ")

docs = si.query(phrase) \
		  .highlight(
			"speaking",
			useFastVectorHighlighter=True) \
		  .highlight(q=highlight_query) \
		  .terms('speaking') \
		  .terms(tf=True) \
		  .execute().result.docs

pp(docs)