import bpy, bmesh, mathutils
from bpy.props import StringProperty, BoolProperty
from node_s import *
from util import *
#from curve_utils import *

class SvObjSelected(bpy.types.Operator):
    """ G E T   SELECTED OBJECTS """
    bl_idname = "node.sverchok_object_insertion"
    bl_label = "Sverchok object selector"
    bl_options = {'REGISTER', 'UNDO'}
    
    node_name = StringProperty(name='name node', default='', description='it is name of node')
    tree_name = StringProperty(name='name tree', default='', description='it is name of tree')
    grup_name = StringProperty(name='grup tree', default='', description='it is name of grup')
    
    def enable(self, name_no, name_tr, handle):
        objects = []
        if self.grup_name and len(bpy.data.groups[self.grup_name].objects)>0:
            objs = bpy.data.groups[self.grup_name].objects
        elif bpy.context.selected_objects:
            objs = bpy.context.selected_objects
        else:
            self.report('Go home, you tired, there is no object selected')
            return
        for o in objs:
            objects.append(o.name)
        handle_write(name_no+name_tr, objects)
        # временное решение с группой. надо решать, как достать имя группы узлов
        if bpy.data.node_groups[name_tr]:
            handle = handle_read(name_no+name_tr)
            #print ('exec',name)
            bpy.data.node_groups[name_tr].nodes[name_no].objects_local = str(handle[1])
        
    
    def disable(self, name, handle):
        if not handle[0]:
            return
        handle_delete(name)
    
    def execute(self, context):
        name_no = self.node_name
        name_tr = self.tree_name
        handle = handle_read(name_no+name_tr)
        self.disable(name_no+name_tr, handle)
        self.enable(name_no, name_tr, handle)
        print('have got {0} items from scene.'.format(handle[1]))
        return {'FINISHED'}
    
class ObjectsNode(Node, SverchCustomTreeNode):
    ''' Objects Input slot '''
    bl_idname = 'ObjectsNode'
    bl_label = 'Objects_in'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    #def object_select(self, context):
        #return [tuple(3 * [ob.name]) for ob in context.scene.objects if ob.type == 'MESH' or ob.type == 'EMPTY']
    objects_local = StringProperty(
        name='local objects in', description='objects, binded to current node',
        default='', 
        update=updateNode)
    #ObjectProperty = EnumProperty(items = object_select, name = 'ObjectProperty')
    groupname = StringProperty(
        name='groupname', description='group that gather objects',
        default='', 
        update=updateNode)
    modifiers = BoolProperty(
        name='Modifiers',
        description='Apply modifier geometry to import (original untouched)',
        default=False,
        update=updateNode)
    vergroups = BoolProperty(
        name='Vergroups',
        description='Use vertex groups to nesty insertion',
        default=False,
        update=updateNode)


    def init(self, context):
        self.outputs.new('VerticesSocket', "Vertices", "Vertices")
        self.outputs.new('StringsSocket', "Edges", "Edges")
        self.outputs.new('StringsSocket', "Polygons", "Polygons")
        self.outputs.new('MatrixSocket', "Matrixes", "Matrixes")
        
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.scale_y = 4.0
        opera = row.operator('node.sverchok_object_insertion', text='G E T')
        opera.node_name = self.name
        opera.tree_name = self.id_data.name
        opera.grup_name = self.groupname
        layout.prop(self, 'groupname', text='Group')
        handle = handle_read(self.name+self.id_data.name)
        if self.objects_local:
            if handle[0]:
                for o in handle[1]:
                    layout.label(o)
            else:
                handle_write(self.name+self.id_data.name, eval(self.objects_local))
        else:
            layout.label('--None--')

        row = layout.row(align=True)
        row.prop(self, "modifiers", text="Post modifiers")             
        row = layout.row(align=True)
        row.prop(self, "vergroups", text="Vertex groups")             

    def update(self):
        # check for grouping socket
        if self.vergroups and not ('Vers_grouped' in self.outputs):
            self.outputs.new('StringsSocket', "Vers_grouped", "Vers_grouped")
        elif not self.vergroups and ('Vers_grouped' in self.outputs):
            self.outputs.remove('StringsSocket', "Vers_grouped", "Vers_grouped")
        
        name = self.name + self.id_data.name
        handle = handle_read(name)
        print (handle)
        if self.objects_local:
            # bpy.ops.node.sverchok_object_insertion(node_name=self.name, tree_name=self.id_data.name, grup_name=self.groupname)
            # not updating. need to understand mechanic of update
            self.use_custom_color=True
            self.color = (0,0.5,0.2)
        else:
            self.use_custom_color=True
            self.color = (0,0.1,0.05)
        if self.objects_local and not handle[0]:
            handle_write(name, eval(self.objects_local))
        elif handle[0]:
            objs = handle[1]
            edgs_out = []
            vers_out = []
            vers_out_grouped = []
            pols_out = []
            mtrx_out = []
            for obj_ in objs: # names of objects
                edgs = []
                vers = []
                vers_grouped = []
                pols = []
                mtrx = []
                obj = bpy.data.objects[obj_] # objects itself
                if obj.type == 'EMPTY':
                    for m in obj.matrix_world:
                        mtrx.append(m[:])

                else:
                    #obj_data = obj.data
                    # post modifier geometry if ticked
                    scene = bpy.context.scene
                    settings = 'PREVIEW'
                    obj_data = obj.to_mesh(scene, self.modifiers, settings)

                    for m in obj.matrix_world:
                        mtrx.append(list(m))
                    for k, v in enumerate(obj_data.vertices):
                        if self.vergroups and v.groups.values():
                            vers_grouped.append(k)
                        vers.append(list(v.co))
                    for edg in obj_data.edges:
                        edgs.append([edg.vertices[0],edg.vertices[1]])
                    for p in obj_data.polygons:
                        pols.append(list(p.vertices))
                    #print (vers, edgs, pols, mtrx)
                edgs_out.append(edgs)
                vers_out.append(vers)
                vers_out_grouped.append(vers_grouped)
                pols_out.append(pols)
                mtrx_out.append(mtrx)
            if vers_out[0]:
                
                if 'Vertices' in self.outputs and self.outputs['Vertices'].links:
                    SvSetSocketAnyType(self, 'Vertices',vers_out)
                    
                if 'Edges' in self.outputs and self.outputs['Edges'].links:
                    SvSetSocketAnyType(self, 'Edges',edgs_out)
                    
                if 'Polygons' in self.outputs and self.outputs['Polygons'].links:
                    SvSetSocketAnyType(self, 'Polygons',pols_out)
                
                if 'Vers_grouped' in self.outputs and self.outputs['Vers_grouped'].links:
                    SvSetSocketAnyType(self, 'Vers_grouped',vers_out_grouped)
            
            if 'Matrixes' in self.outputs and self.outputs['Matrixes'].links:
                SvSetSocketAnyType(self, 'Matrixes',mtrx_out)
                
    def update_socket(self, context):
        self.update()



def register():
    bpy.utils.register_class(SvObjSelected)
    bpy.utils.register_class(ObjectsNode)
    
def unregister():
    bpy.utils.unregister_class(ObjectsNode)
    bpy.utils.unregister_class(SvObjSelected)

if __name__ == "__main__":
    register()



