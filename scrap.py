from os import write
from requests.models import Response
from requests_html import HTMLSession
from openpecha.core.ids import get_pecha_id
from datetime import datetime
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.annotation import AnnBase, Span
from uuid import uuid4


start_url = "https://www2.hf.uio.no/polyglotta/index.php?page=library&bid=2"
pre_url = "https://www2.hf.uio.no/"
lang = []
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

    pecha_name = response.html.find('div.headline',first=True).text
    pecha_id = get_pecha_id()
    opf_path = f"{pecha_id}/{pecha_id}.opf"

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
            
    create_description(pecha_id,pecha_name)
    save_meta(pecha_name,opf_path)


def save_meta(pecha_name,opf_path):
    global lang
    opf = OpenPechaFS(opf_path=opf_path)
    source_metadata = {
        "id": "",
        "title": pecha_name,
        "language": list(set(lang)),
        "author": "",
    }

    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata=source_metadata)    

    opf._meta = instance_meta
    opf.save_meta()


def create_description(pecha_id,pecha_name):
    path = f"{pecha_id}/{pecha_id}.opf/README.md"

    with open(path,"w") as f:
        f.write(f"# {pecha_name}")


def parse_final(link,opf_path,par_dir):
    base_text = []
    response = make_request(pre_url+link.attrs['href'])
    content = response.html.find('div.infofulltekstfelt div.BolkContainer')
    for block in content:
        div = block.find('div.textvar div.Tibetan,div.Chinese,div.English,div.Sanskrit')
        base_text.append(write_file(div))
    filename = link.text if par_dir == None else f"{par_dir}_{link.text}"
    create_opf(opf_path,base_text,filename)    


def write_file(divs):
    global lang
    base_text=""
    for div in divs:
        lang.append(div.attrs["class"][0])
        spans = div.find('span')
        for span in spans:
            if len(span.text) != 0:
                base_text+=span.text
        if len(spans) == 1 and len(spans[0].text) == 0:
            base_text+=""
        else:
            base_text+="\n\n"    
    return base_text



def create_opf(opf_path,base_text,filename):
    opf = OpenPechaFS(opf_path=opf_path)
    layers = {f"v{filename}": {LayerEnum.segment: get_segment_layer(base_text)}}

    bases = {f"v{filename}":get_base_text(base_text)}

    opf.layers = layers
    opf.base = bases
    opf.save_base()
    opf.save_layers()
    

def get_base_text(base_texts):
    text = ""

    for base_text in base_texts:
        if base_text:
            text+=base_text+"\n"

    return text    

def get_segment_layer(base_texts):

    segment_annotations = {}
    char_walker =0
    for base_text in base_texts:
        if base_text:
            segment_annotation = get_segment_annotation(base_text,char_walker)
            segment_annotations.update(segment_annotation)

        char_walker += len(base_text)+1

    segment_layer = Layer(annotation_type= LayerEnum.segment,
    annotations=segment_annotations
    )        

    return segment_layer


def get_segment_annotation(base_text,char_walker):
    
    segment_annotation = {
        uuid4().hex:AnnBase(span=Span(start=char_walker, end=char_walker + len(base_text) - 3))
    }

    return segment_annotation


if __name__ == "__main__":
    values = get_page()
    for val in values:
        parse_page('https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=424')  
        break  



#https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=511

#https://www2.hf.uio.no/polyglotta/index.php?page=volume&vid=1124