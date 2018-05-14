from bs4 import BeautifulSoup
import requests
import unicodedata
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cooking_techniques_url = "https://en.wikipedia.org/wiki/List_of_cooking_techniques"

def request_and_parse_html(url):
	response = requests.get(url)
	html = response.content
	return BeautifulSoup(html, "html.parser")

'''
gets all technique names from https://en.wikipedia.org/wiki/List_of_cooking_techniques
'''

def get_technique_names(url):

    techniques_soup = request_and_parse_html(url)

    div_children = techniques_soup.find('div', attrs={'id' : 'mw-content-text', 'class' : 'mw-content-ltr', 'lang' : 'en', 'dir' : 'ltr'}).find('div').children

    first_child = None

    for child in div_children:
        first_child = child
        break

    siblings =  first_child.next_siblings

    alpha_list_ul = [element for element in siblings if element.name == 'ul']

    # print alpha_list_ul
    technique_name_list = []
    technique_links = []
    for e in alpha_list_ul:
        final_elems = e.find_all('li')
        technique_name_list += [f.a.string for f in final_elems if f.a.string is not None]
        technique_links += [f.a['href'] for f in final_elems if f.a.string is not None]

    keys = technique_name_list[0:156] #list len 160, extra stuff at end
    values = technique_links[0:156]
    technique_dict = dict(zip(keys, values))
    return technique_dict


base_url = 'https://en.wikipedia.org'
'''
gets single technique descriptions using technique url
'''
def get_single_technique_description(technique_url):
    # HTML = '''\
    specific_technique_soup = request_and_parse_html(technique_url)

    specific_technique_soup = request_and_parse_html(technique_url)

    div_children = specific_technique_soup.find('div', attrs={'id' : 'mw-content-text', 'class' : 'mw-content-ltr', 'lang' : 'en', 'dir' : 'ltr'}).find('div').children

    first_child = None

    for child in div_children:
        first_child = child
        break

    siblings =  first_child.next_siblings

    paragraph_list = [element for element in siblings if element.name == 'p']

    if len(paragraph_list) > 0:
        HTML = str(paragraph_list[0])
    else:
        return "No description found"

    soup = BeautifulSoup(HTML, 'html.parser')
    text_no_links = [p.text for p in soup.findAll('p')]
    replace_pattern = r'\[[0-9]\]'
    text_no_brackets = re.sub(replace_pattern, '', text_no_links[0])

    return unicodedata.normalize('NFKD', text_no_brackets).encode('ascii','ignore')


'''
gets all technique descriptions using technique link dictionary (name : partial url)
'''

def get_all_technique_descriptions(technique_dictionary):
    final_technique_dict = {}
    for key in technique_dictionary:
        final_technique_dict[key] = get_single_technique_description(base_url + technique_dictionary[key])
    return final_technique_dict

'''
writes cooking methods to file techniques.txt
pattern is:
cooking method name
cooking method description
cooking method name
cooking method description
...

'''
def write_techniques_to_file(final_technique_dictionary):
    f = open('techniques.txt', 'w+')
    for key in final_technique_dictionary:
        f.write(key + '\n')
        f.write(final_technique_dictionary[key] + '\n')
        print key

# write_techniques_to_file(get_all_technique_descriptions(get_technique_names(cooking_techniques_url)))
