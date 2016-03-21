import sys,os
import re

#Usage 'python api_coverage_check.py spi'

class coverage:
	#public variable
	coverage_rate = 0
	#Private variable
    __source_path_list = []
    __header_path_list = []
    __code_path_list = []
    __module = ''
    __api_name_list = []
    __api_reuse_dict = {}
	__func_api_used = []
	__func_api_index = []

	def __init__(self,source_path_list, header_path_list, code_path_list, module):
		self.__source_path_list = source_path_list
		self.__header_path_list = header_path_list
		self.__code_path_list = code_path_list
		self.__module = module

	#Print out the apis
	def print_api_name_list():
		print __api_name_list

	# Function to analysis how many apis included.
	def header_analysis(header_path):
		module = __module.upper()
		header = open(header_path, 'r')
		content = header.read()
		re_char = module + '_\w*\(' + module + '_Type.*\)'
		# Get all module_xxx function
		api_list = re.findall(re_char, content)
		for name in api_list:
			__api_name_list.append(name.split('(')[0])
		# XXX_GetDefaultSettings() has no base as parameter
		getDefault_list = re.findall(module + '_\w*GetDefault.+\(.+\)', content)
		# Format each function name
		i = 0
		while i < len(getDefault_list):
			getDefault_list[i] = getDefault_list[i].split('(')[0]
			i += 1
		# Remove the duplicated ones
		getDefault_list = list(set(getDefault_list))
		for name in getDefault_list:
			__api_name_list.append(name)

	# Function to analysis the source file
	def source_analysis(source_path):
		module = __module.upper()
		source_file = open(source_path, 'r')
		while 1:
			line = source_file.readline()
			if not line:
				break
			if re.search(module + '_\w*\(.*\)', line):
				next_line = source_file.readline()
				#It is a function
				if r'{' in next_line:
					# Get the function analysis now
					func_name = re.findall(module + '_\w*\(.*\)', line)[0].split('(')[0]
					#print func_name
					# If it is function, do some operations
					if func_name in __api_name_list:
						#Get function content
						function_content = ''
						level = 1
						while level > 0:
							line_content = source_file.readline()
							if r'{' in line_content:
								level += 1
							if r'}' in line_content:
								level -= 1
							function_content += line_content
						#Check how many API this function used
						temp_list = re.findall(module + '_\w*\(.*\)', function_content)
						#print temp_list
						# Check the api used in function content
						i = 0
						api_used = []
						while i < len(temp_list):
							# Fliter the CMSIS macro
							if temp_list[i].split('(')[0] in __api_name_list:
								api_used.append(temp_list[i].split('(')[0])
							i += 1
						# Build the dict
						i = 0
						key_value = []
						# Transfer the function name to index number
						while i < len(api_used):
							key_value.append(__api_name_list.index(api_used[i]))
							i += 1
						__api_reuse_dict[__api_name_list.index(func_name)] = key_value
				# If next line is not '{', it is a static function statement
				else:
					if re.search(module + '_\w*\(' + module + '_Type.*\)', line):
						static_func_name = re.findall(module + '_\w*\(.*\)', line)[0].split('(')[0]
						#Add the static func name to __api_name_list
						__api_name_list.append(static_func_name)
		source_file.close()
		#print __api_reuse_dict
		#Operate the dict
		i = 0
		while i < len(__api_name_list):
	    	if i in __api_reuse_dict:
	    		# 1. Add key itself to the value
	    		__api_reuse_dict[i].append(i)
	    		# 2. Remove the duplicated elements for each list
	    		__api_reuse_dict[i] = list(set(__api_reuse_dict[i]))
	    	#No this key means it is a static inline function
	    	else:
	    		__api_reuse_dict[i] = [i]
	    	#print __api_reuse_dict
	    	i += 1
		#print __api_reuse_dict
		#print __api_name_list
		# 3. After all list formatted, do the nested call check
		# All element resloved nested feature, it quit
		nest_count = 0
		while 1:
			i = 0
			nest_count = 0
			while i < len(__api_name_list):
				# If only one element, no need to operate
				if len(__api_reuse_dict[i]) > 1:
					val_list = __api_reuse_dict[i]
					# Remove itself
					val_list.remove(i)
					# Do nest merge
					for x in val_list:
						# See if it is the sub list
						if len(set(__api_reuse_dict[x]).difference(val_list)) > 0:
							nest_count +=1
							val_list += __api_reuse_dict[x]
							val_list = list(set(val_list))
					val_list.append(i)
					__api_reuse_dict[i] = val_list
				i += 1
			if nest_count == 0:
				break
		#print __api_reuse_dict

	def search_test_code(code_path):
		module = __module.upper()
		src_file = open(code_path, 'r')
		content = src_file.read()
		# Search the API used
		__func_api_used += list(set(re.findall(module + '_\w*\(.*\)', content)))
		src_file.close()
		# Format the names
		i = 0
		while i < len(_func_api_used):
			__func_api_used[i] = __func_api_used[i].split('(')[0]
			i += 1
		__func_api_used = list(set(__func_api_used))
		# Add IRQ handler if there is
		if re.search(module + '_\w+HandleIRQ', ','.join(__api_name_list)):
			__func_api_used += re.findall(module + '_\w+HandleIRQ', ','.join(__api_name_list))
		# Check if all api used
		for func in __func_api_used:
			if func in __api_name_list:
				__func_api_index += __api_reuse_dict[__api_name_list.index(func)]
		__func_api_index = list(set(_func_api_index))

	def compute_coverage_rate():
		# Compute the coverage rate and print the function not covered
		coverage_rate = 100 * len(__func_api_index)/len(__api_name_list)
		temp_list = range(len(__api_name_list))
		api_not_covered = set(temp_list).difference(_func_api_index)


	def print_result():
		print "API Coverage Rate is " + str(coverage_rate) + r'%'
		print "Function not covered is:\n\r"
		for x in api_not_covered:
			print __api_name_list[x] + '\n\r'

compute_path(sys.argv[1])
header_analysis(sys.argv[1], header_path)
source_analysis(sys.argv[1], source_path)
if os.path.isfile(header_dma_path):
	header_analysis(sys.argv[1], header_dma_path)
	source_analysis(sys.argv[1], source_dma_path)
if os.path.isfile(header_edma_path):
	header_analysis(sys.argv[1], header_edma_path)
	source_analysis(sys.argv[1], source_edma_path)
#print __api_name_list
search_func_unit_test(sys.argv[1])
search_basic_unit_test(sys.argv[1])

