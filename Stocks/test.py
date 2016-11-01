with open("shiller_pe.csv", 'rb') as pe_input:
	with open("DJA.csv", 'rb') as dja_input:
		dja_input.next()
		pe_input.next()
		output_list = []
		
		dja_dates = {}
		for x in dja_input:
			line = x.split(',')[0]
			parts = line.split('/')
			if len(parts[0]) == 1:
				parts[0] = '0' + parts[0]
			if len(parts[1]) == 1:
				parts[1] = '0' + parts[1]
				
			line = parts[2]+'-'+parts[0]+'-'+parts[1]
			dja_dates[line] = ''
		
		pe_dates = {}
		for x in pe_input:
			line = x.split(',')
			line[0] = line[0][0:7]
			pe_dates[line[0]] = line[1]
			
		for date in dja_dates:
			day = date
			day = day.split('-')
			day = day[0:2]
			day = '-'.join(day)
			
			try:
				pe = pe_dates[day]
			except KeyError:
				print day, date
				exit()
				
			finalDate = date
			output_list.append((finalDate, pe.strip()))
		
		with open('test.csv', 'wb') as output:
			for k in output_list:
				output.write(k[0])
				output.write(',')
				output.write(k[1])
				output.write('\n')
			
		
