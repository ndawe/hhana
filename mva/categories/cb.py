import math
from rootpy.tree import Cut
from .common import Category_Preselection
from .selections import CUTS_VBF, CUTS_BOOSTED

# https://cds.cern.ch/record/1629891/files/ATL-COM-PHYS-2013-1558.pdf


DETA_JETS = Cut('dEta_jets > 2.6')
MASS_JETS = Cut('mass_jet1_jet2 > 250000')

TAU1_CENTR = Cut('tau1_centrality > %f' % (1. / math.e))
TAU2_CENTR = Cut('tau2_centrality > %f' % (1. / math.e))
TAUS_CENTR = TAU1_CENTR & TAU2_CENTR

CUTS_VBF_CUTBASED = (
    CUTS_VBF
    & DETA_JETS
    & MASS_JETS 
    & TAUS_CENTR
    )

CUTS_BOOSTED_CUTBASED = (
    CUTS_BOOSTED
    #     & Cut('dR_tau1_tau2 < 2.5')
    )

INF = 1E100

# Cut-based categories

# -----------> Main Categories used in the CB Signal Region
class Category_Cuts_VBF_LowDR(Category_Preselection):
    name = 'cuts_vbf_lowdr'
    label = '#tau_{had}#tau_{had} Cut-based VBF Low dR'
    latex = 'VBF High-$p_T^{H}$'
    cuts = (
        CUTS_VBF_CUTBASED
        & Cut('dR_tau1_tau2 < 1.5')
        & Cut('resonance_pt > 140000'))
    limitbins = [0,64,80,92,104,116,132,176,INF]
    norm_category = Category_Preselection


class Category_Cuts_VBF_HighDR_Tight(Category_Preselection):
    name = 'cuts_vbf_highdr_tight'
    label = '#tau_{had}#tau_{had} Cut-based VBF High dR Tight'
    latex = 'VBF Low-$p_T^{H}$ Tight'
    cuts = (
        CUTS_VBF_CUTBASED
        & (Cut('dR_tau1_tau2 > 1.5') | Cut('resonance_pt < 140000'))
        & Cut('mass_jet1_jet2 > (-250000 * dEta_jets + 1550000)'))
    limitbins = [0,64,80,92,104,116,132,152,176,INF]
    norm_category = Category_Preselection


class Category_Cuts_VBF_HighDR_Loose(Category_Preselection):
    name = 'cuts_vbf_highdr_loose'
    label = '#tau_{had}#tau_{had} Cut-based VBF High dR Loose'
    latex = 'VBF Low-$p_T^{H}$ Loose'
    cuts = (
        CUTS_VBF_CUTBASED
        & (Cut('dR_tau1_tau2 > 1.5') | Cut('resonance_pt < 140000'))
        & Cut('mass_jet1_jet2 < (-250000 * dEta_jets + 1550000)'))
    limitbins = [0,64,80,92,104,116,132,152,176,INF]
    norm_category = Category_Preselection

class Category_Cuts_VBF_HighDR(Category_Preselection):
    name = 'cuts_vbf_highdr'
    label = '#tau_{had}#tau_{had} Cut-based VBF High dR Loose'
    latex = 'VBF Low-$p_T^{H}$'
    cuts = Category_Cuts_VBF_HighDR_Loose.cuts | Category_Cuts_VBF_HighDR_Tight.cuts
    limitbins = [0,64,80,92,104,116,132,152,176,INF]
    norm_category = Category_Preselection

class Category_Cuts_Boosted_Tight(Category_Preselection):
    name = 'cuts_boosted_tight'
    label = '#tau_{had}#tau_{had} Cut-based Boosted Tight'
    latex = 'Boosted High-$p_T^{H}$'
    cuts = ((- CUTS_VBF_CUTBASED) & CUTS_BOOSTED_CUTBASED
            & (Cut('dR_tau1_tau2 < 1.5') & Cut('resonance_pt>140000')))
    #         & ((Cut('resonance_pt > (-200000 * dR_tau1_tau2 + 400000)') & Cut('resonance_pt > 140000')) | Cut('resonance_pt > 200000')))
    limitbins = [0,64,72,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,152,160,168,176,184,200,INF]
    norm_category = Category_Preselection


class Category_Cuts_Boosted_Loose(Category_Preselection):
    name = 'cuts_boosted_loose'
    label = '#tau_{had}#tau_{had} Cut-based Boosted Loose'
    latex = 'Boosted Low-$p_T^{H}$'
    cuts = ((- CUTS_VBF_CUTBASED) & CUTS_BOOSTED_CUTBASED
            & (Cut('dR_tau1_tau2 > 1.5') | Cut('resonance_pt<140000')))
#         & Cut('resonance_pt > (-200000 * dR_tau1_tau2 + 400000)') & Cut('resonance_pt < 140000')
#         & Cut('dEta_tau1_tau2 < 1'))
    limitbins = [0,72,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,152,176,184,INF]
    norm_category = Category_Preselection


# ------------> Categories designed for analysis control plots
class Category_Cuts_Boosted_Tight_NoDRCut(Category_Preselection):
    name = 'cuts_boosted_tight_nodrcut'
    label = '#tau_{had}#tau_{had} Cut-based Boosted Tight No dR Cut'
    cuts = ((- CUTS_VBF_CUTBASED) & CUTS_BOOSTED_CUTBASED
            & Cut('resonance_pt>140000') )
    limitbins = [0,64,72,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,152,160,168,176,184,200,INF]
    norm_category = Category_Preselection



# --------> Added by Quentin Buat quentin(dot)buat(at)cern(dot)ch
class Category_Cuts_VBF(Category_Preselection):
    name = 'cuts_vbf'
    label = '#tau_{had}#tau_{had} Cut-based VBF'
    cuts  = Category_Cuts_VBF_HighDR_Loose.cuts | Category_Cuts_VBF_HighDR_Tight.cuts | Category_Cuts_VBF_LowDR.cuts
    limitbins = [0,64,80,92,104,116,132,152,176,INF]
    norm_category = Category_Preselection


class Category_Cuts_Boosted(Category_Preselection):
    name = 'cuts_boosted'
    label = '#tau_{had}#tau_{had} Cut-based Boosted'
    cuts = Category_Cuts_Boosted_Tight.cuts | Category_Cuts_Boosted_Loose.cuts
    limitbins = [0,72,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,152,176,184,INF]
    norm_category = Category_Preselection