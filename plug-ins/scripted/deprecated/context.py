
#-
# ==========================================================================
# Copyright (C) 1995 - 2006 Autodesk, Inc. and/or its licensors.  All
# rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its
# licensors, which is protected by U.S. and Canadian federal copyright
# law and by international treaties.
#
# The Data is provided for use exclusively by You. You have the right
# to use, modify, and incorporate this Data into other products for
# purposes authorized by the Autodesk software license agreement,
# without fee.
#
# The copyright notices in the Software and this entire statement,
# including the above license grant, this restriction and the
# following disclaimer, must be included in all copies of the
# Software, in whole or in part, and all derivative works of
# the Software, unless such copies or derivative works are solely
# in the form of machine-executable object code generated by a
# source language processor.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
# AUTODESK DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED
# WARRANTIES INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF
# NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR
# PURPOSE, OR ARISING FROM A COURSE OF DEALING, USAGE, OR
# TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS LICENSORS
# BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK
# AND/OR ITS LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY
# OR PROBABILITY OF SUCH DAMAGES.
#
# ==========================================================================
#+

#
#       Creation Date:   2 October 2006
#
#       Description:
#
#               moveTool.py
#
# Description:
#       Interactive tool for moving objects and components.
#
#       This plug-in will register the following two commands in Maya:
#               maya.cmds.spMoveToolCmd(x, y, z)
#       maya.cmds.spMoveToolContext()
#
#       Usage:
#       import maya
#       maya.cmds.loadPlugin("moveTool.py")
#       maya.cmds.spMoveToolContext("spMoveToolContext1")
#       shelfTopLevel = maya.mel.eval("global string $gShelfTopLevel;$temp = $gShelfTopLevel")
#       maya.cmds.setParent("%s|General" % shelfTopLevel)
#       maya.cmds.toolButton("spMoveTool1", cl="toolCluster", t="spMoveToolContext1", i1="moveTool.xpm")
#
#       Remove UI objects with
#       maya.cmds.deleteUI("spMoveToolContext1")
#       maya.cmds.deleteUI("spMoveTool1")
#

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import sys, math

kPluginCmdName="spMoveToolCmd"
kPluginCtxName="spMoveToolContext"
kVectorEpsilon = 1.0e-3

# keep track of instances of MoveToolCmd to get around script limitation
# with proxy classes of base pointers that actually point to derived
# classes
kTrackingDictionary = {}

# command
class MoveToolCmd(OpenMayaMPx.MPxToolCommand):
    kDoIt, kUndoIt, kRedoIt = 0, 1, 2

    def __init__(self):
        OpenMayaMPx.MPxToolCommand.__init__(self)
        self.setCommandString(kPluginCmdName)
        kTrackingDictionary[OpenMayaMPx.asHashable(self)] = self

    def __del__(self):
        print "DEL CMDjjj"
        del kTrackingDictionary[OpenMayaMPx.asHashable(self)]

    def doIt(self, args):
        self.__action(MoveToolCmd.kDoIt)

    def redoIt(self):
        self.__action(MoveToolCmd.kRedoIt)

    def undoIt(self):
        self.__action(MoveToolCmd.kUndoIt)

    def isUndoable(self):
        return True

    def finalize(self):
        """
        Command is finished, construct a string for the command
        for journalling.
        """
        command = OpenMaya.MArgList()
        command.addArg(self.commandString())
        command.addArg(0)
        command.addArg(1)
        command.addArg(2)

        # This call adds the command to the undo queue and sets
        # the journal string for the command.
        #
        try:
            OpenMayaMPx.MPxToolCommand._doFinalize(self, command)
        except:
            pass

    def __action(self, flag):
        """
        Do the actual work here to move the objects     by vector
        """
        print 'action'


class MoveContext(OpenMayaMPx.MPxSelectionContext):
    kTop, kFront, kSide, kPersp = 0, 1, 2, 3

    def __init__(self):
        OpenMayaMPx.MPxSelectionContext.__init__(self)
        self._setTitleString("moveTool")
        self.setImage("moveTool.xpm", OpenMayaMPx.MPxContext.kImage1)
        self.__cmd = None

    def toolOnSetup(self, event):
        print 'toolSetup'

    def toolOffCleanup(self):
        print kTrackingDictionary

    def doPress(self, event):
        print 'press'
        self._setHelpString("drag to move selected object")
        newCmd = self._newToolCommand()
        print 'toolcmd: ', newCmd
        self.__cmd = kTrackingDictionary.get(OpenMayaMPx.asHashable(newCmd), None)

    def doDrag(self, event):
        #  self.__cmd.undoIt()
        self.__cmd.redoIt()
        #  self.__view.refresh(True)

    def doRelease(self, event):
        self.__cmd.finalize()
        #  self.__view.refresh(True)


#############################################################################


class MoveContextCommand(OpenMayaMPx.MPxContextCommand):
        def __init__(self):
                OpenMayaMPx.MPxContextCommand.__init__(self)

        def makeObj(self):
                return OpenMayaMPx.asMPxPtr(MoveContext())

def cmdCreator():
        return OpenMayaMPx.asMPxPtr(MoveToolCmd())

def ctxCmdCreator():
        return OpenMayaMPx.asMPxPtr(MoveContextCommand())

def syntaxCreator():
        syntax = OpenMaya.MSyntax()
        syntax.addArg(OpenMaya.MSyntax.kDouble)
        syntax.addArg(OpenMaya.MSyntax.kDouble)
        syntax.addArg(OpenMaya.MSyntax.kDouble)
        return syntax

# Initialize the script plug-in

def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject, "Autodesk", "1.0", "Any")
        try:
                mplugin.registerContextCommand(kPluginCtxName, ctxCmdCreator, kPluginCmdName, cmdCreator, syntaxCreator)
        except:
                sys.stderr.write("Failed to register context command: %s\n" % kPluginCtxName)
                raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.deregisterContextCommand(kPluginCtxName, kPluginCmdName)
        except:
                sys.stderr.write("Failed to deregister context command: %s\n" % kPluginCtxName)
                raise
