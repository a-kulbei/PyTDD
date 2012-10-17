import os.path
import sublime, sublime_plugin
import re
import sys

from pyrefactor import ClassMenager

class CreateClassCommand(sublime_plugin.TextCommand):

    def _get_view(self, fileName):

        views = self.window.views()

        fileView = None
        for view in views:
            if fileName == view.file_name():
                fileView = view

        return fileView


    def run(self, edit):
        self.window = self.view.window()

        # get all selections in active view
        selections = self.view.sel() 

        # At the moment we are interesting only in first selection
        # TODO: Loop over all selections in the feature
        # Extract a class name
        if not selections[0].empty():
            self.className = self.view.substr(selections[0])
        else:
            return

        self.window.show_input_panel("Path to file", "", self.on_done, None, None)

    def on_done(self, fileName):
        # Firstly check that file exist
        if not os.path.exists(fileName):
            return # TODO we have to create this file in case it does not exist

        # Trying to find a view associated with this filename
        fileView = self._get_view(fileName)

        # if was not found let's open it
        if not fileView:
            fileView = self.window.open_file(fileName)

        classText = ClassMenager.get_class_text(self.className)

        fEdit = fileView.begin_edit()
        # TODO: at the moment there is an assumption that file is empty
        fileView.insert(fEdit, 0, classText)
        fileView.end_edit(fEdit)
	

class AddMethodCommand(sublime_plugin.TextCommand):

    def add_method(self, className, methodText, edit):
        window = self.view.window()

        regExp = "^\s*class\s*" + className + "[(]?[.\w)]*:$"

        # list of touples (View, region)
        points = []
        views = window.views()

        for view in views:
            regions = view.find_all(regExp)
            
            if regions:
                reg = view.line(regions[0])
                points.append((view, reg))

        # TODO: what to do in case few views were found
        if len(points) > 0:
            view = points[-1][0]
            reg = points[-1][1]
            edit = view.begin_edit()
            view.insert(edit, reg.end(), methodText)
            view.end_edit(edit)


    def get_class_name(self, points, selRegion):

        if len(points) < 0:
            return ""

        # Trying to find the closest region to the
        # region with selected method
        size = len(points)
        for i in range(size):
            reg = points[i][0]

            if selRegion.a - reg.a < 0:
                return points[i - 1][1]

        return points[-1][1]

    def _get_object_defs(self, objName):

        # Trying to find object declaration
        # Syntax should something like:
        # <objName> = <ClassName>([args])
        # TODO: object may be returned by function, 
        # to think about how to deal with it
        regExp = "^\s*" + objName + "\s*=\s*(\w+)\(.*\).*$"
        regions = self.view.find_all(regExp)

        # Array of touples (region, className)
        points = []
        for reg in regions:
            region = self.view.line(reg)
            text = self.view.substr(region)

            # extraxt a class name by applying the same regExp
            match = re.search(regExp, text)
            if match:
                points.append((region, match.group(1)))

        return points

    def _get_numofargs(self, args):
        if len(args) > 0:
            return len(args.split(','))
        else:
            return 0

    def _parse_selection(self, methodName, lineText):
        """
        Parsing of selected method invocation

        Method is returning touple (<objectName>, <method args>)
        """
        # Get object name and args in a method
        regExp = "(\w+)\.(" + methodName + ")\((.*)\)"
        match = re.search(regExp, lineText)

        # exit in case we did not match the selection
        assert(match)

        return (match.group(1), match.group(3))

    def _get_selection(self):
        """
        Get selected text

        Method is returning touple (<full line text>, <selected text>)
        """
        selections = self.view.sel()
        # TODO at the moment only first selection will be processed
        selRegion = selections[0]

        # Selection should not be empty
        assert(not selRegion.empty())

        # Get full line text with selection
        self.lineRegion = self.view.line(selRegion)
        lineText = self.view.substr(self.lineRegion)

        # Get selected text
        selText = self.view.substr(selRegion)

        return (lineText, selText)

    def run(self, edit):
        # get selected text
        (lineText, methodName) = self._get_selection()

        (objName, args) = self._parse_selection(methodName, lineText)

        # get all defenition of object in current view
        points = self._get_object_defs(objName)

        className = self.get_class_name(points, self.lineRegion)
        
        numOfArgs = self._get_numofargs(args)

        methodText = ClassMenager.get_method_text(methodName, numOfArgs)
        self.add_method(className, methodText, edit)
