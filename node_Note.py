import bpy
from node_s import *
from util import *

Sv_handle_Note = {}

class SverchokNote(bpy.types.Operator):
    """Sverchok Note"""
    bl_idname = "node.sverchok_note_button"
    bl_label = "Sverchok notes"
    bl_options = {'REGISTER', 'UNDO'}
    
    text = bpy.props.StringProperty(name='text', default='')
    
    def execute(self, context):
        name = context.screen.name
        areas = bpy.data.screens[name].areas
        text = eval(self.text)
        for ar in areas:
            if ar.type=='NODE_EDITOR':
                ar.spaces.active.node_tree.nodes[text[0]].use_custom_color = True
                ar.spaces.active.node_tree.nodes[text[0]].color = (0.6,0.3,0.012)
        
        
        Sv_handle_Note[text[0]] = True
        out = []
        lenth = len(text[1])
        width = min(47,lenth) #min(round(text[2]/10), lenth)
        text2=''
        k=1
        for i, t in enumerate(text[1]):
            text2 += t
            if k == width or i==len(text[1])-1:
                out.append(text2)
                text2=''
                k=1
            k+=1
        Sv_handle_Note[text[0]+'text'] = str(out)
        return {'FINISHED'}
    
class SverchokUnNote(bpy.types.Operator):
    """Sverchok UnNote"""
    bl_idname = "node.sverchok_note_unbutton"
    bl_label = "Sverchok Un notes"
    bl_options = {'REGISTER', 'UNDO'}
    
    text = bpy.props.StringProperty(name='text', default='')
    
    def execute(self, context):
        name = context.screen.name
        areas = bpy.data.screens[name].areas
        text = eval(self.text)
        for ar in areas:
            if ar.type=='NODE_EDITOR':
                ar.spaces.active.node_tree.nodes[text[0]].use_custom_color = True
                ar.spaces.active.node_tree.nodes[text[0]].color = (1.0,0.8,0.4)
        Sv_handle_Note[text[0]] = False
        Sv_handle_Note[text[0]+'text'] = str(['your text here'])
        return {'FINISHED'}

class NoteNode(Node, SverchCustomTreeNode):
    ''' Note '''
    bl_idname = 'NoteNode'
    bl_label = 'Note'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    text = bpy.props.StringProperty(name='text', default='your text here')
    
    
    def draw_buttons(self, context, layout):
        global Sv_handle_Note
        if not self.name in Sv_handle_Note:
            Sv_handle_Note[self.name] = False
            name = context.screen.name
            areas = bpy.data.screens[name].areas
            for ar in areas:
                if ar.type=='NODE_EDITOR':
                    ar.spaces.active.node_tree.nodes[self.name].width = 320
                    ar.spaces.active.node_tree.nodes[self.name].width_hidden = 320
                    ar.spaces.active.node_tree.nodes[self.name].location[0]+=10
            # not works in this context. Have to be rewrited.
            # aim - to esteblish width of node 320 
            
        if not Sv_handle_Note[self.name]:
            row = layout.row(align=True)
            row.prop(self, 'text', text='')
            row = layout.row(align=True)
            row.operator('node.sverchok_note_button', text='MIND').text=str([self.name,self.text,self.width])
        
        else:
            ev = eval(Sv_handle_Note[self.name+'text'])
            for t in ev:
                row = layout.row(align=True)
                row.label(t)
            row = layout.row(align=True)
            row.operator('node.sverchok_note_unbutton', text='CHANGE').text=str([self.name,self.text,self.width])
                        
        
    def init(self, context):
        pass
        
    def update(self):
        pass
    
def register():
    bpy.utils.register_class(NoteNode)
    bpy.utils.register_class(SverchokNote)
    bpy.utils.register_class(SverchokUnNote)
    
def unregister():
    bpy.utils.unregister_class(SverchokUnNote)
    bpy.utils.unregister_class(SverchokNote)
    bpy.utils.unregister_class(NoteNode)


if __name__ == "__main__":
    register()
