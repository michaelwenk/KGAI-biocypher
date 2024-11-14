import random
import string
from enum import Enum, auto
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")


class ExampleAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """

    DATASET = auto()
    # CHEMICAL_SUBSTANCE = auto()
    CREATIVE_WORK = auto()
    DATA_CATALOG = auto()


class ExampleAdapterDatasetField(Enum):
    """
    Define possible fields the adapter can provide for datasets.
    """

    ID = "id"    
    DESCRIPTION = "description"
    # CONFORMS_TO = "conformsTo"
    IDENTIFIER = "identifier"
    NAME = "name"
    # KEYWORDS = "keywords"
    LICENSE = "license"
    URL = "url"
    DATE_PUBLISHED = "datePublished"
    CITATION = "citation"
    # MEASUREMENT_TECHNIQUE = "measurementTechnique"
    # INCLUDED_IN_DATA_CATALOG = "includedinDataCatalog"


class ExampleAdapterCreativeWorkField(Enum):
    """
    Define possible fields the adapter can provide for creative work.
    """

    ID = "id"

class ExampleAdapterDataCatalogField(Enum):
    """
    Define possible fields the adapter can provide for data catalogs.
    """

    NAME = "name"
    URL = "url"

class ExampleAdapterEdgeType(Enum):
    """
    Enum for the types of edges.
    """

    DATASET_CREATIVE_WORK_EDGE = "dataset_creativeWork_edge"
    DATASET_DATA_CATALOG_EDGE = "dataset_dataCatalog_edge"



class ExampleAdapter:
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
            yield (node.get_id(), node.get_label(), {})

    def get_edges(self):
        relationship_id = generate_id()

        for edge in self.edges:
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
            self.node_types = [type for type in ExampleAdapterNodeType]

        if node_fields:
            self.node_fields = node_fields
        else:
            self.node_fields = [
                field
                for field in chain(
                    ExampleAdapterDatasetField,
                    ExampleAdapterCreativeWorkField,
                )
            ]

        if edge_types:
            self.edge_types = edge_types
        else:
            self.edge_types = [type for type in ExampleAdapterEdgeType]

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
            for item in self.data:
                if item["@type"] == "Dataset":
                    dataset_node = Node(label="dataset", fields=[
                        # field.value for field in ExampleAdapterDatasetField
                        ])
                    self.nodes.append(dataset_node)
                    # if "http://purl.org/dc/terms/conformsTo" in item and item["http://purl.org/dc/terms/conformsTo"]["@type"] == "CreativeWork":
                    #     creativeWork_node = Node(label="creativeWork", fields=[
                    #         # field.value for field in ExampleAdapterCreativeWorkField
                    #         ])
                    #     self.nodes.append(creativeWork_node)
                    #     self.edges.append(Edge(
                    #         parent_node=dataset_node,
                    #         child_node=creativeWork_node,
                    #         type=ExampleAdapterEdgeType.DATASET_CREATIVE_WORK_EDGE,
                    #         fields=[
                    #             # field.value for field in ExampleAdapterDatasetDatasetEdgeField
                    #         ],
                    #     ))
                    if "includedInDataCatalog" in item and item["includedInDataCatalog"]["@type"] == "DataCatalog":
                        dataCatalog_node = Node(label="dataCatalog", fields=[
                            # field.value for field in ExampleAdapterCreativeWorkField
                            ])
                        self.nodes.append(dataCatalog_node)
                        self.edges.append(Edge(
                            parent_node=dataset_node,
                            child_node=dataCatalog_node,
                            type=ExampleAdapterEdgeType.DATASET_DATA_CATALOG_EDGE.value,
                            fields=[
                                # field.value for field in ExampleAdapterDatasetDatasetEdgeField
                            ],
                        ))         
        

class Node:
    """
    Base class for nodes.
    """

    def __init__(self, label, fields: Optional[list] = None):
        self.id = generate_id()
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
    
class Edge:
    """
    Base class for edges.
    """

    def __init__(self, type, parent_node, child_node, fields: Optional[list] = None):
        self.id = generate_id()
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


#################

def generate_id():
    return "".join(                
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
