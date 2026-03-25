"""Shared visualization config."""
import matplotlib.pyplot as plt
import seaborn as sns

def apply_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette('husl')
    plt.rcParams.update({'figure.figsize':(12,6),'figure.dpi':100,'savefig.dpi':150,'font.size':11,'axes.titlesize':14,'axes.titleweight':'bold'})

COLORS = {'primary':'#4C72B0','secondary':'#55A868','accent':'#DD8452','negative':'#C44E52'}
