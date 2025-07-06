from maya import cmds as mc
from maya.api import OpenMaya as om

from collections import OrderedDict
import logging

from BFX_masterclass.utils import controls as ctlFn
from BFX_masterclass.utils import functions as fn
from BFX_masterclass import static

class LegModule:

    '''
    Modules for constructing a leg.



    TODO: For production uses 
    '''
    def __init__(self, name, parent, legGuides):
        logging.info('Initializing Leg Module')
        self.name=name
        self.side=name[0]
        self.parent=parent

        self.hipGuide = legGuides
        legGuides = mc.listRelatives(legGuides, ad=1)
        legGuides.sort()
        self.kneeGuide = legGuides[0]
        self.ankleGuide = legGuides[1]
        self.toesGuide = legGuides[2]
        self.toeEndGuide = legGuides[3]

        # Un-parent toe guide from ankle
        mc.parent(self.toesGuide, w=1)
    
        # Hip Ctl
        hipCtl = ctlFn.add(self.hipGuide, name+'Hip', parent, shapeName='root', deleteGuide=False)

        # AnkleCtl        
        ankleCtl = ctlFn.add(self.ankleGuide, name+'Ankle', static.ctlGroup, shapeName='root', deleteGuide=False)
        mc.hide(self.ankleGuide)

        # Flip the right side ankle so that it points the same way as our left side
        if self.name[0] == 'R':
            mc.setAttr(ankleCtl.grp+'.rotateX', 0)
        # Settings Ctl
        # Settings ctl will sit at the side of our ankle control.
        # We want to extract our ctl's X axis and translate our ctl to the side
        guide = mc.createNode('transform', name='tmp')
        mc.xform(guide, ws=1, m=mc.xform(ankleCtl.trn, ws=1, m=1, q=1))
        # here we would want to find a reliable way of how far apart we want our settings ctl rather than have it hard coded value
        mc.setAttr(guide+'.tx', -1.5 if self.name[0]=='R' else 1.5) 
        self.settingsCtl = ctlFn.add(guide, self.name+'Settings', ankleCtl.trn, 'diamond')
        self.settingsCtl.scale_shape(.15)
        
        # Toe ctl
        toeCtl = ctlFn.add(self.toesGuide, name+'Toe', ankleCtl.trn, shapeName='root', deleteGuide=False)
        mc.parent(self.toesGuide, toeCtl.trn)

        # Build Leg IK
        mc.parent(self.hipGuide, hipCtl.trn)
        ikHandle = mc.ikHandle(self.hipGuide, ee=self.ankleGuide, name=self.name+'_IKH')[0]
        mc.parent(ikHandle, ankleCtl.jnt)

        # Pole Vector
        poleVectCtl = self.build_pole_vector_control(self.hipGuide, self.kneeGuide, self.ankleGuide)
        mc.poleVectorConstraint(poleVectCtl.trn, ikHandle)

        # Stretch
        self.stretch_IK(hipCtl.jnt, ankleCtl.jnt)

        # Store values
        self.ankleCtl = ankleCtl
        self.hipCtl = hipCtl
        self.toeCtl = toeCtl


    def build_pole_vector_control(self, hip, knee, ankle):
        '''
        This function will create the pole vector control.
         
        1. First we calculate the position of the pole vector.

        We will project the vector between the hip and knee onto the vector between the hip and ankle. 
        The pole vector will have the same length as the hip-knee vector and it will be along the vector between the knee projection and knee

        2. We build a control at the calculated location

        Parameters
        ----------
        hip     : str : name to hip guide
        knee    : str : name to knee guide 
        ankle   : str : name to ankle guide 

        Returns
        -------
        ctl: controlStruct

        '''
        hipPosition = om.MVector(*mc.xform(hip, ws=1, q=1, t=1))
        kneePosition = om.MVector(*mc.xform(knee, ws=1, q=1, t=1))
        anklePosition = om.MVector(*mc.xform(ankle, ws=1, q=1, t=1))

        # Vectors
        # Calculating the position of the pole vector 
        # We will project the vector between the hip and knee onto the vector between the hip and ankle. 
        # The pole vector will have the same length as the hip-knee vector and it will be along the vector between the knee projection and knee
        hipAnkleVector = anklePosition - hipPosition
        hipKneeVector = kneePosition - anklePosition
        kneeProjectionLength = (hipAnkleVector*hipKneeVector)/hipAnkleVector.length()
        kneeProjectionVector = hipAnkleVector.normal()*kneeProjectionLength

        poleVectorDirection = (hipKneeVector - kneeProjectionVector).normal()

        poleGuide = mc.createNode('transform')
        pos = kneePosition+(poleVectorDirection*hipKneeVector.length())
        mc.xform(poleGuide, ws=1, t=[pos.x, pos.y, pos.z])

        # Building the control
        pole_vect_ctl = ctlFn.add(poleGuide, self.name+'PoleVector', static.rigGroup, shapeName='locator')

        return pole_vect_ctl

    def stretch_IK(self, hipCtl, ankleCtl):
        '''
        This function will make our IK stretchy.
        
        We will do this by extracting a 
            lengthRatio = hipAnkle.len / hipAnkle.len0(in bind pose)
        
        Then we will multiply each joints translation x attribute by the lengthRatio:
            knee.tX = max(lengthRatio, 1) * knee.tX(in bind pose)
            ankle.tX = max(lengthRatio, 1) * ankle.tX(in bind pose)

        Returns
        -------
        None
        '''
        # Creating stretch guides
        hipStretch = mc.createNode('transform', name=self.name+'HipStretchGuide')
        mc.parent(hipStretch, hipCtl)
        mc.setAttr(hipStretch+'.translate', 0, 0, 0)
        ankleStretch = mc.createNode('transform', name=self.name+'AnkleStretchGuide')
        mc.parent(ankleStretch, ankleCtl)
        mc.setAttr(ankleStretch+'.translate', 0, 0, 0)

        legLen = mc.createNode('distanceBetween', name=self.name+'Length')
        mc.connectAttr(hipStretch+'.worldMatrix', legLen+'.inMatrix1')
        mc.connectAttr(ankleStretch+'.worldMatrix', legLen+'.inMatrix2')

        legRatio = mc.createNode('divide', name=self.name+'LengthRatio')
        mc.connectAttr(legLen+'.distance', legRatio+'.input1')
        mc.setAttr(legRatio+'.input2', mc.getAttr(legLen+'.distance'))

        # Clamping ratio to 1
        max = mc.createNode('max', name=self.name+'LengthRatioClamp')
        mc.connectAttr(legRatio+'.output', max+'.input[0]')
        mc.setAttr(max+'.input[1]', 1)

        globalLegLen = mc.createNode('multiplyDivide', name=self.name+'GlobalLength')
        mc.connectAttr(static.masterWalk+'.scaleY', globalLegLen+'.input1.input1X')
        mc.connectAttr(max+'.output', globalLegLen+'.input2.input2X')

        # Upper Leg Stretch
        upperLegStretch = mc.createNode('multDoubleLinear', name=self.name+'UpperLen')
        mc.connectAttr(globalLegLen+'.outputX', upperLegStretch+'.input1')
        mc.setAttr(upperLegStretch+'.input2', mc.getAttr(self.kneeGuide+'.translateX'))
        mc.connectAttr(upperLegStretch+'.output', self.kneeGuide+'.translateX')

        # Lower Leg Stretch
        lowerLegStretch = mc.createNode('multDoubleLinear', name=self.name+'LowerLen')
        mc.connectAttr(globalLegLen+'.outputX', lowerLegStretch+'.input1')
        mc.setAttr(lowerLegStretch+'.input2', mc.getAttr(self.ankleGuide+'.translateX'))
        mc.connectAttr(lowerLegStretch+'.output', self.ankleGuide+'.translateX')

    def __build_surface_controls(self):
        '''
        Constructing the surface controls: 
            - Hip control
            - Mid Upper leg ctl: at the mid point between the hip and knee
            - Knee ctl
            - Mid Lower leg ctl: at the mid point between knee and ankle
            - Ankle ctl

        Returns
        -------
        surfaceControls: dict = {
                                'ctlName' : controlStruct
                                }
        '''
        
        def create_guide(name, position, orientObjects):
            guide = mc.createNode('transform', name=name)
            mc.xform(guide, ws=1, t=position)
            mc.delete(mc.orientConstraint(*orientObjects+[guide]))
            return guide
        # Constructing our control guides
        hipPosition = om.MVector(*mc.xform(self.hipGuide, ws=1, q=1, t=1))
        kneePosition = om.MVector(*mc.xform(self.kneeGuide, ws=1, q=1, t=1))
        anklePosition = om.MVector(*mc.xform(self.ankleGuide, ws=1, q=1, t=1))
        
        hipGuide = create_guide('hip', hipPosition, [self.hipGuide])
        
        midUpperGuide = create_guide('legUpper', hipPosition+(kneePosition - hipPosition)/2, [self.hipGuide, self.kneeGuide])
        
        kneeGuide = create_guide('knee', kneePosition, [self.kneeGuide])
        
        midLowerGuide = create_guide('legLower', kneePosition+(anklePosition - kneePosition)/2, [self.kneeGuide])
        
        ankleGuide = create_guide('ankle', anklePosition, [self.kneeGuide])

        # Constructing controls from our guides
        surfaceControls = OrderedDict()
        for guide, name in zip([hipGuide, midUpperGuide, kneeGuide, midLowerGuide, ankleGuide], ['Hip', 'UpperLeg', 'Knee', 'LowerLeg', 'Ankle']):
            surfaceControls[name] = ctlFn.add(guide, self.name+name+'ShapeCtl', parent=self.hipCtl.trn, shapeName='root', deleteGuide=True)
        return surfaceControls
    
    def __attach_surface_joints(self, surface, jntGuides):
        '''
        Creating a surface joint for each guide
        
        Returns
        -------
        None
        '''
        for guide in jntGuides:
            bindJnt = mc.createNode('joint', name=guide.replace('LOC', 'JNT'))
            mc.parent(bindJnt, static.jntGroup)
            # Find closest point on surface
            u, v = fn.get_closest_UV_on_Surface(surface, mc.xform(guide, q=1, ws=1, t=1))
            # Rivet to surface
            fn.rivet_to_surface(surface, bindJnt, u, v)
            mc.delete(guide)

    def build_leg_surface(self, surface, jntGuides):
        '''
        This function takes in a nurbs surface and a list of joints and we construct a ribbon leg set-up.

        1. The control system will consist of the following controls:
            
            - Hip control
            - Mid Upper leg ctl: at the mid point between the hip and knee
            - Knee ctl
            - Mid Lower leg ctl: at the mid point between knee and ankle
            - Ankle ctl

        We will use these controls to drive our nurbs surface, by skinning the surface to the controls

        NOTE: To upgrade the implementation of this module we could generate the nurbs surface from our guides as well. After we have created the list of controls we can then define a set of 4 points along each of the up vectors of the control. 

        2. Second part of the set-up focuses on driving the  will requires us to drive the controls 
        '''

        # Let's construct our nurbs surface influences -> Our leg shape controls
        
        
        def localMatrix(shapeName, transform, parentTransform):
            matrixDifference = mc.createNode('multMatrix', name=self.name+shapeName+'Twist_MMT')
            mc.connectAttr(transform+'.worldMatrix', matrixDifference+'.matrixIn[0]')
            mc.connectAttr(parentTransform+'.worldInverseMatrix', matrixDifference+'.matrixIn[1]')
            # Decompose
            decomposeMatrix = mc.createNode('decomposeMatrix', name=self.name+shapeName+'Twist_DMT')
            mc.connectAttr(matrixDifference+'.matrixSum', decomposeMatrix+'.inputMatrix')

            return decomposeMatrix

        mc.parent(surface, static.rigGroup)
        
       
        surfaceControls = self.__build_surface_controls()     
        skinCluster = mc.skinCluster([elem.jnt for elem in surfaceControls.values()], surface)

        # DRIVING SHAPE CONTROLS
        # Parenting hip and ankle ctl(we want those to be hidden)
        mc.parent(surfaceControls['Hip'].grp, self.hipCtl.jnt)
        mc.parent(surfaceControls['Ankle'].grp, self.ankleCtl.jnt)
        # Parent Knee shape ctl to knee guide
        mc.parentConstraint(self.kneeGuide, surfaceControls['Knee'].grp, mo=0)
        # Drive upper and lower leg 
        surfaceControlsKeys = list(surfaceControls.keys())
        surfaceControlsValues = list(surfaceControls.values())
        for index in [1, 3]:
            shapeName = surfaceControlsKeys[index]

            # Point constraining mid controls between pairs
            upperInfluence = surfaceControlsValues[index-1]
            lowerInfluence = surfaceControlsValues[index+1]
            control = surfaceControls[shapeName]
            mc.pointConstraint(upperInfluence.trn, lowerInfluence.trn, control.grp)
            # Simple Aim
            # mc.aimConstraint(lowerInfluence.trn, surfaceControls[shapeName].grp, aim=[1, 0, 0], u=[0, 1, 0], wuo=upperInfluence.trn, wut='objectrotation', wu=[0, 1, 0])

            # Aim with up vector 
            # Getting an up vector
            # We want out up vector to blend the twist between our upper and lower influence. 
            # We will take the our two influences in the space of the hip. take their rotations and add 0.5 of each one
            upVectorTrn = mc.createNode('transform', name=self.name+shapeName+'UpObject_TRN')
            mc.parent(upVectorTrn, control.grp)
            mc.xform(upVectorTrn, ws=1, m=mc.xform(control.trn, ws=1, q=1, m=1))
            upperInfLocalMatrix = localMatrix(shapeName, upperInfluence.trn, self.hipCtl.trn)
            lowerInfLocalMatrix = localMatrix(shapeName, lowerInfluence.trn, self.hipCtl.trn)

            # Rotation * 0.5
            rotationMult = mc.createNode('animBlendNodeAdditiveDA', name=self.name+shapeName+'halfRotation')
            mc.connectAttr(upperInfLocalMatrix+'.outputRotateX', rotationMult+'.inputA')
            mc.connectAttr(lowerInfLocalMatrix+'.outputRotateX', rotationMult+'.inputB')
            mc.setAttr(rotationMult+'.weightA', 0.5)
            mc.setAttr(rotationMult+'.weightB', 0.5)
            mc.connectAttr(rotationMult+'.output', upVectorTrn+'.rotateX')

            mc.aimConstraint(lowerInfluence.trn, surfaceControls[shapeName].ofs, aim=[1, 0, 0], u=[0, 1, 0], wuo=upVectorTrn, wut='objectrotation', wu=[0, 1, 0])

            
        # Let's rivet jnts along surface
        self.__attach_surface_joints(surface, jntGuides)

    
    def foot_Roll(self, footGuides):
        # Sort our foot guides
        # footGuides = {'front':'', 'back':'', 'positiveX':'', 'negativeX':''}
        locators = mc.listRelatives(footGuides)
        # Sort from back to front
        locators = sorted(locators, key=lambda obj:mc.xform(obj, q=1, ws=1, t=1)[2])
        mc.hide(locators)

        # Create heel control and toe control
        if self.name[0] == 'R':
            [mc.xform(loc, ro=[0, 180, 0], r=1) for loc in locators]
        heelCtl = ctlFn.add(locators[0], name=self.name+'Heel', shapeName='locator', deleteGuide=False, parent=self.ankleCtl.trn)
        
        footTipCtl = ctlFn.add(locators[-1], name=self.name+'FootTip', shapeName='locator', deleteGuide=False, parent=self.ankleCtl.trn)

        # Create our inverse foot roll hierarchy
        inverseHierarchy = []
        guideName = ['Heel', 'FootTip', 'ToeTip', 'Tarsal']
        parent = self.ankleCtl.trn
        for i, guide in enumerate([locators[0], locators[-1], self.toeEndGuide, self.toesGuide]):
            inverseHierarchy.append(mc.createNode('transform', name=self.name+guideName[i]+'_TRN'))
            mc.parent(inverseHierarchy[-1], inverseHierarchy[-2] if len(inverseHierarchy)>1 else self.ankleCtl.trn)
            mc.xform(inverseHierarchy[-1], ws=1, m=mc.xform(guide, ws=1, q=1, m=1))

        # Parenting ankleJoint and toes to end of our hierarchy
        mc.parent(self.ankleCtl.jnt, inverseHierarchy[-1])
        mc.parent(self.toeCtl.grp, inverseHierarchy[-1])

        # Starting foot roll set-up
        # Creating the tarsal lock and straightening attributes
        tarsalLock = mc.addAttr(self.settingsCtl.trn, longName="tarsalLock", softMinValue=-1.7, defaultValue=30, softMaxValue=3.14, at="double", keyable=True)
        tarsalLock = self.settingsCtl.trn+'.tarsalLock'
        straighten = mc.addAttr(self.settingsCtl.trn, longName="straighten", softMinValue=-1.7, defaultValue=1, softMaxValue=3.14, at="double", keyable=True)
        straighten = self.settingsCtl.trn+'.straighten'


        # Heel Roll
        # Taking the negative rotation of our heel rotation and plugging it into our heel guide rotate X
        # min(Hell.rotateX, 0) -> heelTrn

        heelNegativeRotation = fn.min(self.name+'HeelNegativeRotation_MIN', heelCtl.trn +'.rotateX', 0)
        mc.connectAttr(heelNegativeRotation+'.outColorR', inverseHierarchy[0]+'.rotateX')

        # Reverse Tarsal rotation on TarsalFk rotation
        inversedRot = fn.multiply_Double(self.name+'NegateTarsalRotation_MLT', inverseHierarchy[-1]+'.rotateX', -1)
        mc.connectAttr(inversedRot+'.output', self.toeCtl.grp+'.rotateX')

        # Tarsal Rotation 
        # max(heelRotation, 0) = positive rotation
        # min(positiveRotation, tarsalLock) -> tarsalRotation
        heelPositiveRotation = fn.max(self.name+'HeelPositiveRotation_MAX', heelCtl.trn+'.rotateX', 0)
        tarsalLockRotation = fn.min(self.name+'TarsalLockRotation_MIN', heelPositiveRotation+'.outColorR', tarsalLock)
        # mc.connectAttr(tarsalLockRotation+'.output', inverseHierarchy[-1]+'.rotateX')

        # Toe tip
        # Rotate toe tip        
        # straightenAmount = max(heelPositive - TarsalLock, 0) -> toeTip.rotation
 
        toeRotation = fn.subtract(self.name+'ToeRotation_SUB', heelPositiveRotation+'.outColorR', tarsalLock)
        toeRotation = fn.max(self.name+'Straighten_MAX', toeRotation+'.output', 0)
        mc.connectAttr(toeRotation+'.outColorR', inverseHierarchy[1]+'.rotateX')

        # Straightening tarsal
        # tarsalRotation - tipRotation*straighten
        tarsalStraightening =  fn.multiply_Double(self.name+'TarsalStraightenRotation_MLT', toeRotation+'.outColorR', straighten)
        tarsalStraightening = fn.subtract(self.name+'TarsalStraightening_SUB', tarsalLockRotation+'.outColorR', tarsalStraightening+'.output')
        # Clamp value
        tarsalStraightening = fn.max(self.name+'TarsalStraightening_MAX', tarsalStraightening+'.output', 0)
        mc.connectAttr(tarsalStraightening+'.outColorR', inverseHierarchy[-1]+'.rotateX')
        



        