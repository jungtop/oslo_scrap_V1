from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.annotation import AnnBase, Span
from uuid import uuid4


def create_opf(opf_path,base_text,filename):
    opf = OpenPechaFS(opf_path=opf_path)
    layers = {filename: {LayerEnum.segment: get_segment_layer(base_text)}}

    bases = {filename:get_base_text(base_text)}

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
