from os import write
from requests.models import Response
from requests_html import HTMLSession
from create_opf import create_opf


start_url = "https://www2.hf.uio.no/polyglotta/index.php?page=library&bid=2"
pre_url = "https://www2.hf.uio.no/"

def make_request(url):
    s=HTMLSession()
    response =s.get(url)
    return response


def get_page():
    response = make_request(start_url)

    li = response.html.find('ul li a')

    for link in li:
        item = {
        'name' : link.text,
        'ref' : link.attrs['href']
        }

        yield item

def parse_page(item):
    response = make_request(item)
    links = response.html.find('div.venstrefelt table a',first=True)
    response = make_request(pre_url+links.attrs['href'])
    coninuous_bar = response.html.find('div.divControlMain li#nav-2 a',first=True)
    coninuous_bar_href = coninuous_bar.attrs['href'] 
    
    response = make_request(pre_url+coninuous_bar_href)
    nav_bar = response.html.find('div.venstrefulltekstfelt table a')

    links_iter = iter(nav_bar)

    opf_path = response.html.find('div.headline',first=True).text

    opf_path = f"{opf_path}/{opf_path}.opf"

    par_dir = None
    prev_dir = ""
    
    for link in links_iter:
        
        if 'onclick' in link.attrs:
            nxt  = next(links_iter)    

            if nxt.attrs['class'][0] == "ajax_tree0":
                par_dir = None
            elif nxt.attrs['class'][0] == "ajax_tree1":
                par_dir = par_dir.replace(f"_{prev_dir}","") if par_dir != None else par_dir

            par_dir = nxt.text if par_dir == None else f"{par_dir}_{nxt.text}"
            prev_dir = nxt.text
        elif link.text != "Complete text":
            if link.attrs['class'][0] == "ajax_tree0":
                par_dir = None
            parse_final(link,opf_path,par_dir)
            



def parse_final(link,opf_path,par_dir):
    base_text = []
    response = make_request(pre_url+link.attrs['href'])
    content = response.html.find('div.infofulltekstfelt div.BolkContainer')
    for block in content:
        div = block.find('div.textvar div.Tibetan,div.Chinese,div.English,div.Sanskrit')
        base_text.append(write_file(div))
    filename = link.text if par_dir == None else f"{par_dir}_{link.text}"
    create_opf(opf_path,base_text,filename)    

    """ with open(f"file/{link.text}.txt","w") as f:
        for text in base_text:
            f.write(text)
            f.write("************************************\n") """

def write_file(divs):
    base_text=""
    for div in divs:
        spans = div.find('span')
        for span in spans:
            if len(span.text) != 0:
                base_text+=span.text
        if len(spans) == 1 and len(spans[0].text) == 0:
            base_text+=""
        else:
            base_text+="\n\n"    
    return base_text

if __name__ == "__main__":
    values = get_page()
    for val in values:
        parse_page('https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=424')  
        break  



#https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=511

#https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=1124