import bpy
from node_s import *
from util import *


class WifiOutNode(Node, SverchCustomTreeNode):
    ''' WifiOutNode '''
    bl_idname = 'WifiOutNode'
    bl_label = 'Wifi output'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    var_name = bpy.props.StringProperty(name = 'var_name', default='a', update=updateNode)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "var_name", text="var name")
    
    def init(self, context):
        self.outputs.new('StringsSocket', "a[0]", "a[0]")
        

    def update(self):
        global sv_Vars
        # outputs
        
        list_vars = []
        if self.var_name in sv_Vars.keys():
            dest = []
            for v in sv_Vars.keys():
                fs = v.find('sv_typ'+self.var_name)
                if fs>=0:
                    iv = v.find('[')
                    sv = int(v[iv+1:-1])
                    # dest - (index, typ)
                    dest.append((sv, sv_Vars[v]))
                    dest.sort()
            
            lsvn = len(self.var_name)
            if len(self.outputs)>0 and \
                self.var_name!=self.outputs[self.outputs.keys()[0]].name[:lsvn]:
                    for c in self.outputs:
                        self.outputs.remove(c)
                    self.outputs.new('StringsSocket', str(self.var_name)+"[0]", str(self.var_name)+"[0]")
                        
            # без цветовой дифференциации штанов цивилизация обречена (c)
            if self.outputs[0].links:
                self.use_custom_color=True
                self.color = (0.4,0,0.8)
            else:
                self.use_custom_color=True
                self.color = (0.05,0,0.2)
                
            if dest:
                dic_typ = {'s':'StringsSocket', 'v':'VerticesSocket', 'm':'MatrixSocket'}
                for i, dst in enumerate(dest):
                    if dst[0]>len(sv_Vars[self.var_name])-1: break
                    typ = dst[1]
                    var = sv_Vars[self.var_name][dst[0]]
                    flag = True
                    flag2 = True
                    while(flag):
                        flag = False
                        louts = len(self.outputs)
                        a_name = self.var_name + '['+str(dst[0])+']'
                        if dst[0]==louts:
                            self.outputs.new(dic_typ[typ], a_name, a_name)
                            if   typ=='s':
                                self.outputs[a_name].StringsProperty = str(var)
                            elif typ=='v':
                                self.outputs[a_name].VerticesProperty = str(var)
                            elif typ=='m':
                                self.outputs[a_name].MatrixProperty = str(var)
                                    
                        else:
                            if a_name in self.outputs and louts>dst[0] and \
                                str(type(self.outputs[a_name]))[15:-2]==dic_typ[typ]:
                                    
                                if   typ=='s':
                                    self.outputs[a_name].StringsProperty = str(var)
                                elif typ=='v':
                                    self.outputs[a_name].VerticesProperty = str(var)
                                elif typ=='m':
                                    self.outputs[a_name].MatrixProperty = str(var)
                                    
                            elif flag2:
                                flag2 = False
                                flag = True
                                cl = min(louts-1,dst[0])
                                for c in self.outputs[cl:]:
                                    self.outputs.remove(c)
                                
            
def register():
    bpy.utils.register_class(WifiOutNode)
    
def unregister():
    bpy.utils.unregister_class(WifiOutNode)

if __name__ == "__main__":
    register()