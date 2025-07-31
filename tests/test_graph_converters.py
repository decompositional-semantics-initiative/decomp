"""Comprehensive tests for decomp.graph modules to reach 100% coverage."""

import pytest
from networkx import DiGraph
from rdflib import Graph, URIRef

from decomp.graph.nx import NXConverter
from decomp.graph.rdf import RDFConverter


@pytest.fixture(autouse=True)
def reset_rdf_converter():
    """Reset RDFConverter class attributes before each test to ensure isolation."""
    # Store original values
    original_subspaces = RDFConverter.SUBSPACES.copy()
    original_properties = RDFConverter.PROPERTIES.copy()
    original_values = RDFConverter.VALUES.copy()

    yield

    # Reset to original values after test
    RDFConverter.SUBSPACES = original_subspaces
    RDFConverter.PROPERTIES = original_properties
    RDFConverter.VALUES = original_values


class TestNXConverter:
    """Test NXConverter class to cover missing lines."""

    def test_nx_converter_init(self):
        """Test NXConverter initialization."""
        rdf_graph = Graph()
        converter = NXConverter(rdf_graph)

        # Test that attributes are set correctly
        assert isinstance(converter.nxgraph, DiGraph)
        assert converter.rdfgraph is rdf_graph

    def test_rdf_to_networkx_not_implemented(self):
        """Test that rdf_to_networkx raises NotImplementedError."""
        rdf_graph = Graph()

        with pytest.raises(NotImplementedError):
            NXConverter.rdf_to_networkx(rdf_graph)


class TestRDFConverter:
    """Test RDFConverter class to cover missing lines."""

    def test_rdf_converter_list_tuple_error(self):
        """Test error handling for list/tuple valued attributes."""
        # Create a NetworkX graph with list-valued attributes
        nx_graph = DiGraph()
        nx_graph.add_node('node1', bad_attr=['list', 'value'])

        with pytest.raises(ValueError, match='Cannot convert list- or tuple-valued attributes to RDF'):
            RDFConverter.networkx_to_rdf(nx_graph)

    def test_rdf_converter_tuple_valued_error(self):
        """Test error handling for tuple-valued attributes."""
        # Create a NetworkX graph with tuple-valued attributes
        nx_graph = DiGraph()
        nx_graph.add_node('node1', bad_attr=('tuple', 'value'))

        with pytest.raises(ValueError, match='Cannot convert list- or tuple-valued attributes to RDF'):
            RDFConverter.networkx_to_rdf(nx_graph)

    def test_rdf_converter_construct_edge_existing(self):
        """Test _construct_edge when edge already exists."""
        nx_graph = DiGraph()
        nx_graph.add_edge('node1', 'node2', attr1='value1')

        converter = RDFConverter(nx_graph)

        # First, construct the nodes
        converter._construct_node('node1')
        converter._construct_node('node2')

        # First call should create the edge
        edgeid1 = converter._construct_edge('node1', 'node2')
        assert edgeid1 == 'node1%%node2'

        # Second call with same nodes should return existing edge
        edgeid2 = converter._construct_edge('node1', 'node2')
        assert edgeid2 == 'node1%%node2'
        assert edgeid1 == edgeid2

    def test_rdf_converter_comprehensive_workflow(self):
        """Test complete RDF conversion workflow with various attribute types."""
        # Create a comprehensive NetworkX graph
        nx_graph = DiGraph()

        # Add nodes with various attribute types
        nx_graph.add_node('node1',
                         domain='test_domain',
                         type='test_type',
                         simple_attr='simple_value',
                         numeric_attr=42)

        nx_graph.add_node('node2',
                         regular_prop='regular_value')

        # Add edges with attributes
        nx_graph.add_edge('node1', 'node2',
                         edge_prop='edge_value',
                         numeric_edge=3.14)

        # Convert to RDF
        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)

        # Verify RDF graph was created
        assert isinstance(rdf_graph, Graph)
        assert len(rdf_graph) > 0

        # Verify that triples were added
        triples = list(rdf_graph)
        assert len(triples) > 0

    def test_rdf_converter_nested_dict_attributes(self):
        """Test RDF conversion with nested dictionary attributes (subspaces)."""
        nx_graph = DiGraph()

        # Add node with nested dict attribute (simulating UDS subspace structure)
        nx_graph.add_node('node1',
                         test_subspace={
                             'test_prop': {
                                 'value': 1.0,
                                 'confidence': 0.9
                             }
                         })

        # Convert to RDF
        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)

        # Verify conversion succeeded
        assert isinstance(rdf_graph, Graph)
        assert len(rdf_graph) > 0

    def test_rdf_converter_special_properties(self):
        """Test RDF conversion with special properties (domain, type)."""
        nx_graph = DiGraph()

        # Add nodes with domain and type properties
        nx_graph.add_node('node1',
                         domain='semantic',
                         type='predicate')

        nx_graph.add_node('node2',
                         domain='syntax',
                         type='token')

        # Convert to RDF
        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)

        # Verify conversion succeeded
        assert isinstance(rdf_graph, Graph)
        assert len(rdf_graph) > 0

    def test_rdf_converter_class_attributes_initialization(self):
        """Test that class attributes are properly initialized."""
        # Before any conversion, class attributes should be empty
        RDFConverter.SUBSPACES = {}
        RDFConverter.VALUES = {}

        nx_graph = DiGraph()
        nx_graph.add_node('node1', domain='test', custom_prop='value')

        # Convert to RDF
        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)

        # Verify class attributes were populated
        assert 'test' in RDFConverter.VALUES
        assert 'custom_prop' in RDFConverter.PROPERTIES

    def test_rdf_converter_edge_with_dict_attributes(self):
        """Test edge conversion with dictionary attributes."""
        nx_graph = DiGraph()

        # Add edge with simple dict attribute (not the complex UDS format)
        nx_graph.add_edge('node1', 'node2',
                         simple_dict={'key': 'value'})

        # Convert to RDF
        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)

        # Verify conversion succeeded
        assert isinstance(rdf_graph, Graph)
        assert len(rdf_graph) > 0


class TestRDFConverterStaticMethods:
    """Test RDFConverter static methods."""

    def test_construct_subspace(self):
        """Test _construct_subspace static method."""
        # Reset class attributes and initialize required properties
        RDFConverter.SUBSPACES = {}
        RDFConverter.PROPERTIES = {
            'subspace': URIRef('subspace'),
            'confidence': URIRef('confidence')
        }

        # Test constructing a new subspace
        triples = RDFConverter._construct_subspace('test_subspace', 'test_prop')

        # Verify triples were created
        assert len(triples) == 3

        # Verify class attributes were updated
        assert 'test_subspace' in RDFConverter.SUBSPACES
        assert 'test_prop' in RDFConverter.PROPERTIES
        assert 'test_prop-confidence' in RDFConverter.PROPERTIES

    def test_construct_subspace_existing(self):
        """Test _construct_subspace with existing subspace."""
        # Pre-populate class attributes with required properties
        RDFConverter.SUBSPACES = {'existing_subspace': URIRef('existing_subspace')}
        RDFConverter.PROPERTIES = {
            'existing_prop': URIRef('existing_prop'),
            'subspace': URIRef('subspace'),
            'confidence': URIRef('confidence')
        }

        # Construct subspace that partially exists
        triples = RDFConverter._construct_subspace('existing_subspace', 'new_prop')

        # Verify triples were created
        assert len(triples) == 3

        # Verify new properties were added
        assert 'new_prop' in RDFConverter.PROPERTIES
        assert 'new_prop-confidence' in RDFConverter.PROPERTIES


class TestGraphModulesIntegration:
    """Integration tests for graph modules."""

    def test_graph_modules_import(self):
        """Test that graph modules can be imported successfully."""
        from decomp.graph import NXConverter, RDFConverter

        # Verify classes are available
        assert NXConverter is not None
        assert RDFConverter is not None

    def test_graph_converters_basic_functionality(self):
        """Test basic functionality of both converters."""
        # Test RDFConverter (which is implemented)
        nx_graph = DiGraph()
        nx_graph.add_node('test_node', test_attr='test_value')

        rdf_graph = RDFConverter.networkx_to_rdf(nx_graph)
        assert isinstance(rdf_graph, Graph)

        # Test NXConverter (which raises NotImplementedError)
        empty_rdf = Graph()
        with pytest.raises(NotImplementedError):
            NXConverter.rdf_to_networkx(empty_rdf)
