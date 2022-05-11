# -*- coding: utf-8 -*-
import maya.cmds as cmds
import pymel.core as pm
from mgear.rigbits import sdk_io

VERSION = 'v1.0'

class SDK_Manager_mGear(object):

    def __init__(self):
        self.createWindow()

    def getSDKanimCurve(self, dvnNode, *args):
        ac = pm.listConnections(dvnNode, type=("animCurveUA", "animCurveUL", "animCurveUU"), d=False, scn=True)
        return ac

    def getAllSDKanimCurves(self, *args):
        sdk_animcurves = []
        for o in pm.ls(type=("animCurveUA", "animCurveUL", "animCurveUU")):
            if not '_profile' in o.name():
                sdk_animcurves.append(o)
        return sdk_animcurves

    def getAllSDKdrivenNodes(self, *args):
        sdk_driven_nodes = []
        for ac in self.getAllSDKanimCurves():
            dvn = pm.listConnections('{}.output'.format(ac), d=True, s=False)
            sdk_driven_nodes.extend(dvn)
        sdk_driven_nodes = list(set(sdk_driven_nodes))
        return sdk_driven_nodes

    def copySDKtoRside(self, objs, searchStr='_L', replaceStr='_R', *args):
        for o in objs:
            dvr = None
            ac = self.getSDKanimCurve(o)
            if ac:
                dvr = pm.listConnections(ac[0].input, d=False, scn=True)
            else:
                print('Not found driver. ({})'.format(o.name()))
                
            if dvr:
                dvr = dvr[0]
                
                dvn_tgt_name = o.name().replace(searchStr, replaceStr)
                dvn_tgt = None
                if pm.objExists(dvn_tgt_name):
                    dvn_tgt = pm.PyNode(dvn_tgt_name)
                    
                dvr_tgt_name = dvr.name().replace(searchStr, replaceStr)
                dvr_tgt = None
                if pm.objExists(dvr_tgt_name):
                    dvr_tgt = pm.PyNode(dvr_tgt_name)
                
                if dvn_tgt and dvr_tgt:
                    if o.name() != dvn_tgt.name():
                        ac = self.getSDKanimCurve(dvn_tgt)
                        if ac:
                            pm.delete(ac)

                        sdk_io.copySDKsToNode(o, dvr_tgt, dvn_tgt)

    def mirrorSDKkeys(self, objs, mirrorAttr=[], invDvr=False, invDvn=False, *args):
        for o in objs:
            sdk_io.mirrorSDKkeys(o,
                        attributes=mirrorAttr,
                        invertDriver=invDvr,
                        invertDriven=invDvn)

    def exportSDKFileDialog(self, *args):
        startDir = pm.workspace(q=True, rootDirectory=True)
        SDK_path = pm.fileDialog2(fileMode=0,
                                startingDirectory=startDir,
                                fileFilter='mGear SDK file (*.json)')
        if not SDK_path:
            return
        else:
            SDK_path = SDK_path[0]
            if not SDK_path.endswith('.json'):
                SDK_path += '.json'
            return SDK_path

    def button_selectAllSDKanimCurves(self, *args):
        pm.select(self.getAllSDKanimCurves())

    def button_selectAllSDKdrivenNodes(self, *args):
        pm.select(self.getAllSDKdrivenNodes())

    def button_copySDKtoRside(self, *args):
        searchString = cmds.textField(self.left_TxFld, q=True, tx=True)
        replaceString = cmds.textField(self.right_TxFld, q=True, tx=True)
        self.copySDKtoRside(pm.selected(), 
                            searchStr=searchString, 
                            replaceStr=replaceString)

    def button_copySDKtoLside(self, *args):
        searchString = cmds.textField(self.right_TxFld, q=True, tx=True)
        replaceString = cmds.textField(self.left_TxFld, q=True, tx=True)
        self.copySDKtoRside(pm.selected(), 
                            searchStr=searchString, 
                            replaceStr=replaceString)    

    def button_mirrorSDKkeys(self, *args):
        mirrorAttrList = []
        if cmds.checkBox(self.mirror_tx, q=True, v=True):
            mirrorAttrList.append('translateX')
        if cmds.checkBox(self.mirror_ty, q=True, v=True):
            mirrorAttrList.append('translateY')
        if cmds.checkBox(self.mirror_tz, q=True, v=True):
            mirrorAttrList.append('translateZ')
        if cmds.checkBox(self.mirror_rx, q=True, v=True):
            mirrorAttrList.append('rotateX')
        if cmds.checkBox(self.mirror_ry, q=True, v=True):
            mirrorAttrList.append('rotateY')
        if cmds.checkBox(self.mirror_rz, q=True, v=True):
            mirrorAttrList.append('rotateZ')
        invDvr = cmds.checkBox(self.mirror_invertDriver, q=True, v=True)
        invDvn = cmds.checkBox(self.mirror_invertDriven, q=True, v=True)
        self.mirrorSDKkeys(pm.selected(), 
                        mirrorAttr=mirrorAttrList, 
                        invDvr=invDvr, 
                        invDvn=invDvn)

    def button_exportSDKfile(self, *args):
        if pm.selected():
            filePath = self.exportSDKFileDialog()
            if filePath:
                print('Export SDK    : ' + filePath)
                sdk_io.exportSDKs(pm.selected(), filePath)


    def createWindow(self, *args):
        cmds.window(title='SDK Manager {}'.format(VERSION), width=300, sizeable=False)

        cmds.columnLayout(adj=True, cat=['both',5], rs=5)
        cmds.text(label='using  mgear.rigbits.sdk_io  module')
        cmds.separator(h=10, st='in')

        # select
        # ---------------------------------------
        cmds.rowLayout(nc=2)
        cmds.button(l="Select all animCurves", w=150, c=self.button_selectAllSDKanimCurves)
        cmds.button(l="Select all driven nodes", w=150, c=self.button_selectAllSDKdrivenNodes)
        cmds.setParent('..')
        # ---------------------------------------
        
        cmds.separator(h=10, st='in')
        
        # copy sdk
        # ---------------------------------------
        cmds.rowLayout(nc=2)
        self.right_TxFld = cmds.textField(tx='_R', w=150)
        self.left_TxFld = cmds.textField(tx='_L', w=150)
        cmds.setParent('..')
        cmds.rowLayout(nc=2)
        cmds.button(l="Copy SDK  L -> R", w=150, c=self.button_copySDKtoRside)
        cmds.button(l="Copy SDK  R -> L", w=150, c=self.button_copySDKtoLside)
        cmds.setParent('..')
        # ---------------------------------------
        
        cmds.separator(h=10, st='in')
        
        # mirror sdk
        # ---------------------------------------
        cmds.rowLayout(nc=6)
        self.mirror_tx = cmds.checkBox(label='tx')
        self.mirror_ty = cmds.checkBox(label='ty')
        self.mirror_tz = cmds.checkBox(label='tz')
        self.mirror_rx = cmds.checkBox(label='rx')
        self.mirror_ry = cmds.checkBox(label='ry')
        self.mirror_rz = cmds.checkBox(label='rz')
        cmds.setParent('..')
        cmds.rowLayout(nc=2)
        self.mirror_invertDriver = cmds.checkBox(label='invertDriver')
        self.mirror_invertDriven = cmds.checkBox(label='invertDriven')
        cmds.setParent('..')    
        cmds.button(l="Mirror SDK keys", c=self.button_mirrorSDKkeys)
        # ---------------------------------------

        cmds.separator(h=10, st='in')

        # export sdk file
        # ---------------------------------------
        cmds.button(l="Export SDK File (.json)", c=self.button_exportSDKfile)
        # ---------------------------------------
        cmds.setParent('..')

        cmds.showWindow()

SDK_Manager_mGear()