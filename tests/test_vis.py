from decomp import UDSCorpus
from decomp.vis.uds_vis import UDSVisualization

if __name__ == "__main__":
    problem = UDSCorpus(split="train")['ewt-train-13']
    vis = UDSVisualization(problem, add_syntax_edges=False)
    vis.serve()
#     vis.show()
