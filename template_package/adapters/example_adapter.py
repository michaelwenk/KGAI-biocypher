import random
import string
from enum import Enum, auto
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")

class Node:
    """
    Base class for nodes.
    """

    def __init__(self, label: str, id: Optional[str | int], fields: Optional[dict] = {}):
        self.id = id if id != None and id != "" else generate_id()
        self.label = label
        self.fields = fields              

    def get_id(self):
        """
        Returns the node id.
        """
        return self.id
    
    def get_label(self):
        """
        Returns the node label.
        """
        return self.label
    
    def get_fields(self):
        """
        Returns the node fields.
        """
        return self.fields
    
    def set_field(self, field, value):
        """
        Sets a field value.
        """
        if not self.fields:
            self.fields = {}
        self.fields[field] = value

    
class Edge:
    """
    Base class for edges.
    """

    def __init__(self, type, parent_node, child_node, id: Optional[str | int], fields: Optional[dict] = {}):
        self.id = id if id != None and id != "" else generate_id()
        self.type = type
        self.parent_node = parent_node
        self.child_node = child_node
        self.fields = fields

    def get_id(self):
        """
        Returns the edge id.
        """
        return self.id
    
    def get_type(self):
        """
        Returns the edge type.
        """
        return self.type
    
    def get_parent_node(self):
        """
        Returns the parent node.
        """
        return self.parent_node
    
    def get_child_node(self):
        """
        Returns the child node.
        """
        return self.child_node
    
    def get_fields(self):
        """
        Returns the edge fields.
        """
        return self.fields
    
    def set_field(self, field, value):
        """
        Sets a field value.
        """
        self.fields[field] = value


class NodePropertyLabel(Enum):
    """
    Define property labels for the adapter.
    """

    ID = "id"
    DESCRIPTION = "description"
    CONFORMS_TO = "http://purl.org/dc/terms/conformsTo"
    IDENTIFIER = "identifier"
    NAME = "name"
    LICENSE = "license"
    URL = "url"
    DATE_PUBLISHED = "datePublished"
    CITATION = "citation"
    INCLUDED_IN_DATA_CATALOG = "includedInDataCatalog"
    MEASUREMENT_TECHNIQUE = "measurementTechnique"
    IN_DEFINED_TERM_SET = "inDefinedTermSet"
    CHEMICAL_COMPOSITION = "chemicalComposition"
    ALTERNATE_NAME = "alternateName"
    HAS_BIO_CHEM_ENTITY_PART = "hasBioChemEntityPart"
    INCHI = "inChI"
    INCHI_KEY = "inChIKey"
    SMILES = "smiles"
    MOLECULAR_FORMULA = "molecularFormula"
    MONOISOTOPIC_MOLECULAR_WEIGHT = "monoisotopicMolecularWeight"
    ABOUT = "about"
    SUBJECT_OF = "subjectOf"

class NodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """

    DATASET = "dataset"    
    CREATIVE_WORK = "creativeWork"
    DATA_CATALOG = "dataCatalog"
    DEFINED_TERM = "definedTerm"
    DEFINED_TERM_SET = "definedTermSet"
    CHEMICAL_SUBSTANCE = "chemicalSubstance"
    MOLECULAR_ENTITY = "molecularEntity"


class DatasetField(Enum):
    """
    Define possible fields the adapter can provide for datasets.
    """

    ID = NodePropertyLabel.ID.value   
    DESCRIPTION = NodePropertyLabel.DESCRIPTION.value
    IDENTIFIER = NodePropertyLabel.IDENTIFIER.value
    NAME = NodePropertyLabel.NAME.value
    LICENSE = NodePropertyLabel.LICENSE.value
    URL = NodePropertyLabel.URL.value
    DATE_PUBLISHED =NodePropertyLabel.DATE_PUBLISHED.value
    CITATION = NodePropertyLabel.CITATION.value

class ChemicalSubstanceField(Enum):
    """
    Define possible fields the adapter can provide for chemical substances.
    """

    ID = NodePropertyLabel.ID.value   
    IDENTIFIER = NodePropertyLabel.IDENTIFIER.value
    NAME = NodePropertyLabel.NAME.value
    URL = NodePropertyLabel.URL.value
    CHEMICAL_COMPOSITION = NodePropertyLabel.CHEMICAL_COMPOSITION.value
    ALTERNATE_NAME = NodePropertyLabel.ALTERNATE_NAME.value

class MolecularEntityField(Enum):
    """
    Define possible fields the adapter can provide for molecular entities.
    """

    ID = NodePropertyLabel.ID.value
    IDENTIFIER = NodePropertyLabel.IDENTIFIER.value
    NAME = NodePropertyLabel.NAME.value
    URL = NodePropertyLabel.URL.value
    INCHI = NodePropertyLabel.INCHI.value
    INCHI_KEY = NodePropertyLabel.INCHI_KEY.value
    SMILES = NodePropertyLabel.SMILES.value
    MOLECULAR_FORMULA = NodePropertyLabel.MOLECULAR_FORMULA.value
    MONOISOTOPIC_MOLECULAR_WEIGHT = NodePropertyLabel.MONOISOTOPIC_MOLECULAR_WEIGHT.value


class CreativeWorkField(Enum):
    """
    Define possible fields the adapter can provide for creative works.
    """

    ID = NodePropertyLabel.ID.value


class DataCatalogField(Enum):
    """
    Define possible fields the adapter can provide for data catalogs.
    """

    NAME = NodePropertyLabel.NAME.value
    URL = NodePropertyLabel.URL.value


class DefinedTermField(Enum):
    """
    Define possible fields the adapter can provide for defined terms.
    """

    NAME = "name"
    URL = "url"


class EdgeType(Enum):
    """
    Enum for the types of edges.
    """

    DATASET_CREATIVE_WORK_EDGE = "dataset_creativeWork_edge"
    DATASET_DATA_CATALOG_EDGE = "dataset_dataCatalog_edge"
    DATASET_DEFINED_TERM_EDGE = "dataset_definedTerm_edge"
    DEFINED_TERM_DEFINED_TERM_SET_EDGE = "definedTerm_definedTermSet_edge"
    CHEMICAL_SUBSTANCE_CREATIVE_WORK_EDGE = "chemicalSubstance_creativeWork_edge"
    CHEMICAL_SUBSTANCE_MOLECULAR_ENTITY_EDGE = "chemicalSubstance_molecularEntity_edge"
    DATASET_CHEMICAL_SUBSTANCE_EDGE = "dataset_chemicalSubstance_edge"
    CHEMICAL_SUBSTANCE_DATASET_EDGE = "chemicalSubstance_dataset_edge"

def findNode(label: str, id: str, hmap: dict[str, Node]) -> Node | None:
    if id in hmap and hmap[id].get_label() == label:
        return hmap[id]
    return None

def buildNode(self, label: str, id: str, hmap: dict[str, Node]) -> Node:  
    node = findNode(label=label, id=id, hmap=hmap)
    if node != None:
        return node
    node = Node(label=label, id=id)
    node.set_field(field="id", value=id)
    self.nodes.append(node)
    hmap[id] = node

    return node

def buildEdgeHashMapKey(parent_node: Node, child_node: Node, type: str) -> str:
    return parent_node.get_id() + "_" + child_node.get_id() + "_" + type

def findEdge(parent_node: Node, child_node: Node, type: str,  hmap: dict[str, Edge]) -> Edge | None:
    mapKey = buildEdgeHashMapKey(parent_node=parent_node, child_node=child_node, type=type)
    if mapKey in hmap:
        return hmap[mapKey]

    return None

def buildEdge(self, parent_node: Node, child_node: Node, type: str, hmap: dict[str, Edge]) -> Edge:
    edge = findEdge(parent_node=parent_node, child_node=child_node, type=type, hmap=hmap)
    if edge != None:
        return edge    
    edge = Edge(
        parent_node=parent_node,
        child_node=child_node,
        type=type,
        id=generate_id(),
    )
    self.edges.append(edge)
    hmap[buildEdgeHashMapKey(parent_node=parent_node, child_node=child_node, type=type)] = edge

    return edge

def insertProperty(node: Node, value: str | int, fieldName: Enum):
    if isinstance(value, str | int):
        if isinstance(value, str):                        
                node.set_field(fieldName.value, value.replace("\'", "\'\'"))
        else:
            node.set_field(fieldName.value, value)

def insertProperties(node: Node, item: dict, fields: Enum):
    for fieldName in fields:
        for itemKey in item.keys():           
            if fieldName.value.casefold() == itemKey.casefold():
                if isinstance(item[itemKey], str | int):
                    insertProperty(node=node, value=item[itemKey], fieldName=fieldName)   
                elif isinstance(item[itemKey], list):
                    isStr = True
                    for value in item[itemKey]:
                        if not isinstance(value, str | int):
                            isStr = False                                                
                    if isStr:
                        combindedValue = ""
                        for value in item[itemKey]:
                            combindedValue += value + ";"
                        insertProperty(node=node, value=value, fieldName=fieldName)



def insert(self, item: dict, hmap_node: dict[str, Node], hmap_edge: dict[str, Edge]):
    if item["@type"].casefold() == NodeType.DATASET.value.casefold():     
            dataset_node = buildNode(self=self, label=NodeType.DATASET.value, id=item["@id"], hmap=hmap_node)
            if NodePropertyLabel.CONFORMS_TO.value in item and item[NodePropertyLabel.CONFORMS_TO.value]["@type"].casefold() == NodeType.CREATIVE_WORK.value.casefold():                       
                creativeWork_node = buildNode(self=self, label=NodeType.CREATIVE_WORK.value, id=item[NodePropertyLabel.CONFORMS_TO.value]["@id"], hmap=hmap_node)
                buildEdge(self=self, parent_node=dataset_node, child_node=creativeWork_node, type=EdgeType.DATASET_CREATIVE_WORK_EDGE.value, hmap=hmap_edge)
            
            insertProperties(node=dataset_node, item=item, fields=DatasetField)

            if NodePropertyLabel.MEASUREMENT_TECHNIQUE.value in item:
                for mt in item[NodePropertyLabel.MEASUREMENT_TECHNIQUE.value]:
                    if mt["@type"].casefold() == NodeType.DEFINED_TERM.value.casefold():
                        definedTerm_node = buildNode(self=self, label=NodeType.DEFINED_TERM.value, id=mt["termCode"], hmap=hmap_node)
                        buildEdge(self=self, parent_node=dataset_node, child_node=definedTerm_node, type=EdgeType.DATASET_DEFINED_TERM_EDGE.value, hmap=hmap_edge)
                        definedTerm_node.set_field("name", mt["name"])
                        definedTerm_node.set_field("url", mt["url"])
                        definedTerm_node.set_field("termCode", mt["termCode"])

                        if NodePropertyLabel.IN_DEFINED_TERM_SET.value in mt and mt[NodePropertyLabel.IN_DEFINED_TERM_SET.value]["@type"].casefold() == NodeType.DEFINED_TERM_SET.value.casefold():
                            definedTermSet_node = buildNode(self=self, label=NodeType.DEFINED_TERM_SET.value, id=mt[NodePropertyLabel.IN_DEFINED_TERM_SET.value]["url"], hmap=hmap_node)
                            buildEdge(self=self, parent_node=definedTerm_node, child_node=definedTermSet_node, type=EdgeType.DEFINED_TERM_DEFINED_TERM_SET_EDGE.value, hmap=hmap_edge)
                            definedTermSet_node.set_field("name", mt[NodePropertyLabel.IN_DEFINED_TERM_SET.value]["name"])
                            definedTermSet_node.set_field("url", mt[NodePropertyLabel.IN_DEFINED_TERM_SET.value]["url"])

            if NodePropertyLabel.INCLUDED_IN_DATA_CATALOG.value in item and item[NodePropertyLabel.INCLUDED_IN_DATA_CATALOG.value]["@type"].casefold() == NodeType.DATA_CATALOG.value.casefold():
                dataCatalog_node = buildNode(self=self, label=NodeType.DATA_CATALOG.value, id=item[NodePropertyLabel.INCLUDED_IN_DATA_CATALOG.value]["url"], hmap=hmap_node)
                dataCatalog_node.set_field("name", item[NodePropertyLabel.INCLUDED_IN_DATA_CATALOG.value]["name"])
                dataCatalog_node.set_field("url", item[NodePropertyLabel.INCLUDED_IN_DATA_CATALOG.value]["url"])
                buildEdge(self=self, parent_node=dataset_node, child_node=dataCatalog_node, type=EdgeType.DATASET_DATA_CATALOG_EDGE.value, hmap=hmap_edge)            

            if NodePropertyLabel.ABOUT.value in item:
                chemical_substance_node = buildNode(self=self, label=NodeType.CHEMICAL_SUBSTANCE.value, id=item[NodePropertyLabel.ABOUT.value]["@id"], hmap=hmap_node)
                buildEdge(self=self, parent_node=dataset_node, child_node=chemical_substance_node, type=EdgeType.DATASET_CHEMICAL_SUBSTANCE_EDGE.value, hmap=hmap_edge)

    elif item["@type"].casefold() == NodeType.CHEMICAL_SUBSTANCE.value.casefold():
        chemical_substance_node = buildNode(self=self, label=NodeType.CHEMICAL_SUBSTANCE.value, id=item["@id"], hmap=hmap_node)
        if NodePropertyLabel.CONFORMS_TO.value in item and item[NodePropertyLabel.CONFORMS_TO.value]["@type"].casefold() == NodeType.CREATIVE_WORK.value.casefold():                       
            creativeWork_node = buildNode(self=self, label=NodeType.CREATIVE_WORK.value, id=item[NodePropertyLabel.CONFORMS_TO.value]["@id"], hmap=hmap_node)
            buildEdge(self=self, parent_node=chemical_substance_node, child_node=creativeWork_node, type=EdgeType.CHEMICAL_SUBSTANCE_CREATIVE_WORK_EDGE.value, hmap=hmap_edge)
       
        insertProperties(node=chemical_substance_node, item=item, fields=ChemicalSubstanceField)

        if NodePropertyLabel.HAS_BIO_CHEM_ENTITY_PART.value in item:
            for part in item[NodePropertyLabel.HAS_BIO_CHEM_ENTITY_PART.value]:
                if part["@type"].casefold() == NodeType.MOLECULAR_ENTITY.value.casefold():
                    part_node = buildNode(self=self, label=NodeType.MOLECULAR_ENTITY.value, id=part["@id"], hmap=hmap_node)
                    buildEdge(self=self, parent_node=chemical_substance_node, child_node=part_node, type=EdgeType.CHEMICAL_SUBSTANCE_MOLECULAR_ENTITY_EDGE.value, hmap=hmap_edge)                    
                    insertProperties(node=part_node, item=part, fields=MolecularEntityField)

        if NodePropertyLabel.SUBJECT_OF.value in item:
            dataset_node = buildNode(self=self, label=NodeType.DATASET.value, id=item[NodePropertyLabel.SUBJECT_OF.value]["@id"], hmap=hmap_node)
            buildEdge(self=self, parent_node=chemical_substance_node, child_node=dataset_node, type=EdgeType.CHEMICAL_SUBSTANCE_DATASET_EDGE.value, hmap=hmap_edge)

        # dataset_id = item["@id"].replace("ChemicalSubstance", "Dataset")
        # dataset_node = findNode(label=NodeType.DATASET.value, id=dataset_id, hmap=hmap_node)
        # if dataset_node != None:
        #     buildEdge(self=self, parent_node=dataset_node, child_node=chemical_substance_node, type=EdgeType.DATASET_CHEMICAL_SUBSTANCE_EDGE.value, hmap=hmap_edge)        
        #     buildEdge(self=self, parent_node=chemical_substance_node, child_node=dataset_node, type=EdgeType.CHEMICAL_SUBSTANCE_DATASET_EDGE.value, hmap=hmap_edge)
        

class MassBankAdapter:
    """
    Example BioCypher adapter. Generates nodes and edges for creating a
    knowledge graph.

    Args:
        node_types: List of node types to include in the result.
        node_fields: List of node fields to include in the result.
        edge_types: List of edge types to include in the result.
        edge_fields: List of edge fields to include in the result.
        data: Data to use for generating nodes and edges.
    """

    def __init__(
        self,
        node_types: Optional[list] = None,
        node_fields: Optional[list] = None,
        edge_types: Optional[list] = None,
        edge_fields: Optional[list] = None,
        data: Optional[dict] = None,
    ):
        self._set_types_and_fields(node_types, node_fields, edge_types, edge_fields, data)

    def get_nodes(self):
        for node in self.nodes:
            yield (node.get_id(), node.get_label(), node.get_fields())

    def get_edges(self):
        for edge in self.edges:
            relationship_id = generate_id()
            yield (
                relationship_id,
                edge.parent_node.get_id(),
                edge.child_node.get_id(),
                edge.type,
                {},
            )

    def get_node_count(self):
        """
        Returns the number of nodes generated by the adapter.
        """
        return len(self.nodes)
    
    def get_edge_count(self):
        """
        Returns the number of edges generated by the adapter.
        """
        return len(self.edges)

    def _set_types_and_fields(self, node_types, node_fields, edge_types, edge_fields, data):
        if node_types:
            self.node_types = node_types
        else:
            self.node_types = [type for type in NodeType]

        if node_fields:
            self.node_fields = node_fields
        else:
            self.node_fields = [
                field
                for field in chain(
                    DatasetField,
                    DataCatalogField,
                )
            ]

        if edge_types:
            self.edge_types = edge_types
        else:
            self.edge_types = [type for type in EdgeType]

        if edge_fields:
            self.edge_fields = edge_fields
        else:
            self.edge_fields = [field for field in chain()]
        
        if data:
            self.data = data
        else:
            self.data = None

        self.nodes = []
        self.edges = []
        if self.data:
            
            hmap_node = dict[str, Node]()
            hmap_edge = dict[str, Edge]()
            
            for item in self.data:                
                insert(self=self, item=item, hmap_node=hmap_node, hmap_edge=hmap_edge)


#################

def generate_id():
    return "".join(                
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
