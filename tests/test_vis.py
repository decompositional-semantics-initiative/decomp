import json
import os 
from predpatt import PredPatt, PredPattOpts, load_conllu
from decomp.syntax.dependency import DependencyGraphBuilder
from decomp.semantics.predpatt import PredPattGraphBuilder
from decomp.semantics.uds import UDSSentenceGraph, UDSCorpus
from decomp.vis.uds_vis import UDSVisualization
from decomp import NormalizedUDSAnnotation

# rawtree = """1	From	from	ADP	IN	_	3	case	_	_
# 2	the	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
# 3	AP	AP	PROPN	NNP	Number=Sing	4	nmod	_	_
# 4	comes	come	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
# 5	this	this	DET	DT	Number=Sing|PronType=Dem	6	det	_	_
# 6	story	story	NOUN	NN	Number=Sing	4	nsubj	_	_
# 7	:	:	PUNCT	:	_	4	punct	_	_"""

# listtree = [l.split() for l in rawtree.split('\n')]


# annotation1 = '{"ewt-dev-1": {"ewt-dev-1-semantics-arg-3": {"genericity": {"arg-kind": {"confidence": 1.0, "value": -1.1642}, "arg-abstract": {"confidence": 1.0, "value": -1.1642}, "arg-particular": {"confidence": 1.0, "value": 1.2257}}}, "ewt-dev-1-semantics-arg-author": {}, "ewt-dev-1-semantics-arg-6": {"wordsense": {"supersense-noun.object": {"confidence": 1.0, "value": -3.0}, "supersense-noun.Tops": {"confidence": 1.0, "value": -3.0}, "supersense-noun.quantity": {"confidence": 1.0, "value": -3.0}, "supersense-noun.feeling": {"confidence": 1.0, "value": -3.0}, "supersense-noun.food": {"confidence": 1.0, "value": -3.0}, "supersense-noun.shape": {"confidence": 1.0, "value": -3.0}, "supersense-noun.event": {"confidence": 1.0, "value": -3.0}, "supersense-noun.motive": {"confidence": 1.0, "value": -3.0}, "supersense-noun.substance": {"confidence": 1.0, "value": -3.0}, "supersense-noun.time": {"confidence": 1.0, "value": -3.0}, "supersense-noun.person": {"confidence": 1.0, "value": -3.0}, "supersense-noun.process": {"confidence": 1.0, "value": -3.0}, "supersense-noun.attribute": {"confidence": 1.0, "value": -3.0}, "supersense-noun.artifact": {"confidence": 1.0, "value": -1.3996}, "supersense-noun.group": {"confidence": 1.0, "value": -3.0}, "supersense-noun.animal": {"confidence": 1.0, "value": -3.0}, "supersense-noun.location": {"confidence": 1.0, "value": -3.0}, "supersense-noun.plant": {"confidence": 1.0, "value": -3.0}, "supersense-noun.possession": {"confidence": 1.0, "value": -3.0}, "supersense-noun.relation": {"confidence": 1.0, "value": -3.0}, "supersense-noun.phenomenon": {"confidence": 1.0, "value": -3.0}, "supersense-noun.cognition": {"confidence": 1.0, "value": -3.0}, "supersense-noun.act": {"confidence": 1.0, "value": -3.0}, "supersense-noun.state": {"confidence": 1.0, "value": -3.0}, "supersense-noun.communication": {"confidence": 1.0, "value": 0.2016}, "supersense-noun.body": {"confidence": 1.0, "value": -3.0}}, "genericity": {"arg-kind": {"confidence": 0.7138, "value": -0.035}, "arg-abstract": {"confidence": 1.0, "value": -1.1685}, "arg-particular": {"confidence": 1.0, "value": 1.2257}}}, "ewt-dev-1-semantics-pred-4": {"factuality": {"factual": {"confidence": 1.0, "value": 0.967}}, "time": {"dur-weeks": {"confidence": 0.2564, "value": -1.3247}, "dur-decades": {"confidence": 0.2564, "value": -1.1146}, "dur-days": {"confidence": 0.2564, "value": 0.8558}, "dur-hours": {"confidence": 0.2564, "value": 0.9952}, "dur-seconds": {"confidence": 0.2564, "value": 0.8931}, "dur-forever": {"confidence": 0.2564, "value": -1.4626}, "dur-centuries": {"confidence": 0.2564, "value": -1.1688}, "dur-instant": {"confidence": 0.2564, "value": -1.4106}, "dur-years": {"confidence": 0.2564, "value": 0.9252}, "dur-minutes": {"confidence": 0.2564, "value": -0.9337}, "dur-months": {"confidence": 0.2564, "value": -1.2142}}, "genericity": {"pred-dynamic": {"confidence": 0.627, "value": -0.0469}, "pred-hypothetical": {"confidence": 0.5067, "value": -0.0416}, "pred-particular": {"confidence": 1.0, "value": 1.1753}}}, "ewt-dev-1-semantics-arg-addressee": {}, "ewt-dev-1-semantics-pred-root": {}, "ewt-dev-1-semantics-arg-0": {}}}'

# annotation2 = '{"ewt-dev-1": {"ewt-dev-1-semantics-pred-4%%ewt-dev-1-semantics-arg-3": {"protoroles": {"manner": {"confidence": 1.0, "value": -1.3932}, "location": {"confidence": 1.0, "value": 1.4353}, "time": {"confidence": 1.0, "value": -1.3913}, "purpose": {"confidence": 1.0, "value": -1.3941}}}, "ewt-dev-1-semantics-pred-4%%ewt-dev-1-semantics-arg-6": {"protoroles": {"instigation": {"confidence": 0.1128, "value": 0.0458}, "change_of_possession": {"confidence": 0.7669, "value": -0.0561}, "existed_before": {"confidence": 0.1128, "value": 0.1096}, "was_for_benefit": {"confidence": 0.7669, "value": -0.1343}, "change_of_state_continuous": {"confidence": 1.0, "value": -0.0}, "change_of_state": {"confidence": 0.7669, "value": -0.1343}, "volition": {"confidence": 0.3073, "value": -0.0}, "change_of_location": {"confidence": 0.7669, "value": -0.0561}, "partitive": {"confidence": 0.5736, "value": -0.2656}, "existed_during": {"confidence": 0.4211, "value": 0.236}, "existed_after": {"confidence": 0.4211, "value": 0.236}, "awareness": {"confidence": 0.7669, "value": -0.0}, "sentient": {"confidence": 0.4612, "value": -0.3556}, "was_used": {"confidence": 0.013, "value": -0.0204}}}, "ewt-dev-1-semantics-pred-root%%ewt-dev-1-semantics-arg-0": {}, "ewt-dev-1-semantics-pred-root%%ewt-dev-1-semantics-arg-author": {}, "ewt-dev-1-semantics-pred-root%%ewt-dev-1-semantics-arg-addressee": {}, "ewt-dev-1-semantics-arg-0%%ewt-dev-1-semantics-pred-4": {}}}'

# def setup_annotations():
    # ann1 = NormalizedUDSAnnotation.from_json(annotation1)
    # ann2 = NormalizedUDSAnnotation.from_json(annotation2) 

    # return ann1, ann2

def setup_graph():
    # ann1, ann2 = setup_annotations()
    
    # ud = DependencyGraphBuilder.from_conll(listtree, 'ewt-dev-1')
    
    # pp = PredPatt(next(load_conllu(rawtree))[1],
    #               opts=PredPattOpts(resolve_relcl=True,
    #                                 borrow_arg_for_relcl=True,
    #                                 resolve_conj=False,
    #                                 cut=True))

    # pp_graph = PredPattGraphBuilder.from_predpatt(pp, ud, 'ewt-dev-1')

    # graph = UDSSentenceGraph(pp_graph, "ewt-dev-1")
    # graph.add_annotation(*ann1['ewt-dev-1'])
    # graph.add_annotation(*ann2['ewt-dev-1'])
    # TODO (elias) use pytest fixture for this 
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(test_dir, 'data/')
    graph_data = json.load(open(os.path.join(test_data_dir, "vis_data.json")))
    graph = UDSSentenceGraph.from_dict(graph_data)
    return graph

def test_vis():
    graph = setup_graph()
    vis = UDSVisualization(graph, add_syntax_edges=True)
    vis.serve()


if __name__ == "__main__":
    test_vis() 
