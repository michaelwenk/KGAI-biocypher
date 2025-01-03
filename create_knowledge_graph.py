
from biocypher import BioCypher
from template_package.adapters.example_adapter import (
    MassBankAdapter
)
import json
from rdflib import Graph


def js_r(filename: str):
    with open(filename) as f_in:
        return json.load(f_in)
    
# data = js_r("data/schema.org.jsonld")
# for item in data["@graph"]:
#     if item["@type"] == "rdfs:Class" and "rdfs:label" in item and isinstance(item["rdfs:label"], str):
#         value = item["rdfs:label"]
#         value = value[0].lower() + value[1:]
#         item["rdfs:label"] = value

# g = Graph()
# g.parse(data=json.dumps(data), format="json-ld")
# g.serialize("data/schemaorg-current-http_edited.rdf", format="xml")

    
data = js_r("data/test_MB3.jsonld")

# Instantiate the BioCypher interface
# You can use `config/biocypher_config.yaml` to configure the framework or
# supply settings via parameters below
bc = BioCypher()

# Create a protein adapter instance
adapter = MassBankAdapter(data=data)

print(adapter.get_node_count())
# for node in adapter.get_nodes():
#     print(node)
print(adapter.get_edge_count())
# for edge in adapter.get_edges():
#     print(edge)

# Create a knowledge graph from the adapter
bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

# Write admin import statement
bc.write_import_call()

# tell BioChatter to use the schema info
bc.write_schema_info(as_node=True)

# Print summary
# bc.show_ontology_structure(full=True)

bc.summary()




