"""Comprehensive tests for decomp.corpus.corpus module to reach 100% coverage."""

from collections.abc import Hashable

import pytest

from decomp.corpus.corpus import Corpus


class MockCorpus(Corpus):
    """Concrete implementation of Corpus for testing."""

    def _graphbuilder(self, graphid: Hashable, rawgraph):
        """Mock graph builder that can be configured to raise exceptions."""
        if hasattr(self, '_raise_error'):
            if self._raise_error == 'ValueError':
                raise ValueError("Test ValueError")
            elif self._raise_error == 'RecursionError':
                raise RecursionError("Test RecursionError")

        # Return a simple mock graph
        return f"graph_{graphid}"


class TestCorpusMagicMethods:
    """Test Corpus magic methods for complete coverage."""

    def test_contains_method(self):
        """Test __contains__ method."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        # Test that existing keys return True
        assert 'graph1' in corpus
        assert 'graph2' in corpus

        # Test that non-existing keys return False
        assert 'graph3' not in corpus
        assert 'nonexistent' not in corpus

    def test_len_method(self):
        """Test __len__ method."""
        # Test with empty corpus
        empty_corpus = MockCorpus({})
        assert len(empty_corpus) == 0

        # Test with non-empty corpus
        test_data = {'graph1': 'data1', 'graph2': 'data2', 'graph3': 'data3'}
        corpus = MockCorpus(test_data)
        assert len(corpus) == 3

    def test_iter_method(self):
        """Test __iter__ method."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        # Test that iteration works
        graph_ids = list(corpus)
        assert set(graph_ids) == {'graph1', 'graph2'}

    def test_getitem_method(self):
        """Test __getitem__ method."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        # Test that we can get items
        assert corpus['graph1'] == 'graph_graph1'
        assert corpus['graph2'] == 'graph_graph2'

        # Test that KeyError is raised for non-existent keys
        with pytest.raises(KeyError):
            corpus['nonexistent']

    def test_items_method(self):
        """Test items() method."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        items = list(corpus.items())
        assert len(items) == 2
        assert ('graph1', 'graph_graph1') in items
        assert ('graph2', 'graph_graph2') in items


class TestCorpusExceptionHandling:
    """Test exception handling in _build_graphs method."""

    def test_build_graphs_value_error(self, caplog):
        """Test ValueError handling in _build_graphs."""
        import logging

        test_data = {'problematic_graph': 'data'}
        corpus = MockCorpus(test_data)

        # Configure mock to raise ValueError
        corpus._raise_error = 'ValueError'

        with caplog.at_level(logging.WARNING):
            # Re-run _build_graphs to trigger the exception
            corpus._build_graphs()

            # Check that warning was logged
            assert 'problematic_graph has no or multiple root nodes' in caplog.text

    def test_build_graphs_recursion_error(self, caplog):
        """Test RecursionError handling in _build_graphs."""
        import logging

        test_data = {'loop_graph': 'data'}
        corpus = MockCorpus(test_data)

        # Configure mock to raise RecursionError
        corpus._raise_error = 'RecursionError'

        with caplog.at_level(logging.WARNING):
            # Re-run _build_graphs to trigger the exception
            corpus._build_graphs()

            # Check that warning was logged
            assert 'loop_graph has loops' in caplog.text


class TestCorpusProperties:
    """Test Corpus property methods."""

    def test_graphs_property(self):
        """Test graphs property."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        graphs = corpus.graphs
        assert isinstance(graphs, dict)
        assert set(graphs.keys()) == {'graph1', 'graph2'}
        assert graphs['graph1'] == 'graph_graph1'
        assert graphs['graph2'] == 'graph_graph2'

    def test_graphids_property(self):
        """Test graphids property."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        graphids = corpus.graphids
        assert isinstance(graphids, list)
        assert set(graphids) == {'graph1', 'graph2'}

    def test_ngraphs_property(self):
        """Test ngraphs property."""
        # Test empty corpus
        empty_corpus = MockCorpus({})
        assert empty_corpus.ngraphs == 0

        # Test non-empty corpus
        test_data = {'graph1': 'data1', 'graph2': 'data2', 'graph3': 'data3'}
        corpus = MockCorpus(test_data)
        assert corpus.ngraphs == 3


class TestCorpusSampleMethod:
    """Test Corpus sample() method."""

    def test_sample_method_basic(self):
        """Test basic sampling functionality."""
        test_data = {f'graph{i}': f'data{i}' for i in range(10)}
        corpus = MockCorpus(test_data)

        # Test sampling with k=3
        sampled = corpus.sample(3)
        assert isinstance(sampled, dict)
        assert len(sampled) == 3

        # Verify all sampled keys are from original corpus
        for key in sampled.keys():
            assert key in corpus
            assert sampled[key] == corpus[key]

    def test_sample_method_edge_cases(self):
        """Test sample method edge cases."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        # Test sampling all graphs
        sampled_all = corpus.sample(2)
        assert len(sampled_all) == 2
        assert set(sampled_all.keys()) == {'graph1', 'graph2'}

        # Test sampling one graph
        sampled_one = corpus.sample(1)
        assert len(sampled_one) == 1
        assert list(sampled_one.keys())[0] in {'graph1', 'graph2'}

    def test_sample_method_error_cases(self):
        """Test sample method error cases."""
        test_data = {'graph1': 'data1', 'graph2': 'data2'}
        corpus = MockCorpus(test_data)

        # Test sampling more than available - should raise ValueError
        with pytest.raises(ValueError):
            corpus.sample(5)  # More than 2 available graphs


class TestCorpusIntegration:
    """Integration tests for Corpus functionality."""

    def test_full_corpus_workflow(self):
        """Test complete corpus workflow."""
        test_data = {
            'graph1': 'raw_data1',
            'graph2': 'raw_data2',
            'graph3': 'raw_data3'
        }

        corpus = MockCorpus(test_data)

        # Test that all functionality works together
        assert len(corpus) == 3
        assert 'graph1' in corpus
        assert corpus.ngraphs == 3

        # Test iteration
        all_ids = set(corpus)
        assert all_ids == {'graph1', 'graph2', 'graph3'}

        # Test sampling
        sampled = corpus.sample(2)
        assert len(sampled) == 2

        # Test properties
        assert len(corpus.graphids) == 3
        assert len(corpus.graphs) == 3

    def test_empty_corpus_behavior(self):
        """Test behavior with empty corpus."""
        empty_corpus = MockCorpus({})

        assert len(empty_corpus) == 0
        assert empty_corpus.ngraphs == 0
        assert empty_corpus.graphids == []
        assert empty_corpus.graphs == {}
        assert list(empty_corpus) == []
        assert list(empty_corpus.items()) == []

        # Sampling from empty corpus should raise error
        with pytest.raises(ValueError):
            empty_corpus.sample(1)
