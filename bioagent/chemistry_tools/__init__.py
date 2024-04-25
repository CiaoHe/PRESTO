from bioagent.chemistry_tools.evaluator import (
    MoleculeSMILESEvaluator, 
    MoleculeSEELFIESEvaluator,
    MoleculeCaptionEvaluator,
    ClassificationEvaluator,
    RegressionEvaluator,
)
from bioagent.chemistry_tools.reaction import ReactionEquation, multicomponent_smiles_to_list, list_to_multicomponent_smiles
from bioagent.chemistry_tools.smiles import smiles_to_graph, graph_to_smiles, smiles_to_coords

EVALUATOR_BUILDERS = {
    "smiles": MoleculeSMILESEvaluator,
    "selfies": MoleculeSEELFIESEvaluator,
    "caption": MoleculeCaptionEvaluator,
    "classification": ClassificationEvaluator,
    "regression": RegressionEvaluator,
}