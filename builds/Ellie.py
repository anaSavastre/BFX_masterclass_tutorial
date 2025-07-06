from maya import cmds as mc
from BFX_masterclass.utils import pipeline, control
from BFX_masterclass import legModule, static
import sys

def flush_python_cache():

    modules = dict(sys.modules)
    for k, v in modules.items():
        if v and hasattr(v, '__file__'):
            if v.__file__ is not None and ('BFX_masterclass' in v.__file__ or 'myScripts' in v.__file__):
                print(v.__file__)
                del sys.modules[k]

if __name__ == '__main__':

    flush_python_cache()
    pipeline.build_rig_scene('CHR_Ellie')

    # Create a COG control
    root = control.add_control('C_root00_JNT', 'C_root00', parent=static.ctlGroup, shapeName='root')
    control.scale_control(root.trn, 2)

    # Creating Leg
    for s in 'LR':
            
        leg = legModule.LegModule(name=s+'_leg', parent=root.trn, legGuides=s+'_leg00_JNT')
        leg.build_leg_surface(surface=s+'_legSurface00_NRB', 
            jntGuides= [s+elem[1:] for elem in['L_legBind00_LOC', 'L_legBind01_LOC', 
            'L_legBind02_LOC', 'L_legBind03_LOC', 'L_legBind04_LOC', 'L_legBind05_LOC', 'L_legBind06_LOC', 
            'L_legBind07_LOC', 'L_legBind08_LOC', 'L_legBind09_LOC']])
        leg.footRoll(s+'_footGuides00_GRP')
    
    