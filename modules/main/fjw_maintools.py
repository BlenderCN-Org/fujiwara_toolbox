﻿import bpy
#パス関連のユーティリティ
#http://xwave.exblog.jp/7155003
import os.path
import os
import re
import bmesh
import datetime
import subprocess
import shutil
import time
import copy
from collections import OrderedDict
from fujiwara_toolbox.fjw import *
import fujiwara_toolbox.conf
import random
from mathutils import *

assetdir = fujiwara_toolbox.conf.assetdir

#コードtips
#
#bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#mode (enum in [‘OBJECT’, ‘EDIT’, ‘POSE’, ‘SCULPT’, ‘VERTEX_PAINT’,
#‘WEIGHT_PAINT’, ‘TEXTURE_PAINT’, ‘PARTICLE_EDIT’], (optional)) – Mode
#
#obj = bpy.context.active_object
#bpy.context.scene.objects.active = obj
#
#for obj in bpy.context.selected_objects:
#
#for obj in bpy.data.objects:

#dir = os.path.dirname(bpy.data.filepath)


#self.report({"INFO"},"")



#import mypac.filewrap
#mypac.filewrap.debug = True


#http://blender.stackexchange.com/questions/717/is-it-possible-to-print-to-the-report-window-in-the-info-view
#info出力はself.report({"INFO"},str)で！

#http://matosus304.blog106.fc2.com/blog-entry-257.html

bl_info = {
    "name": "FJW_Myaddon",
    "description": "スクリプトの概要",
    "author": "作者名",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Object"}


from bpy.app.handlers import persistent

settings = {"test":""}

@persistent
def load_handler(context):
    test = settings





#外部スクリプト実行
#__file__が、関数が定義されてるスクリプトのパスを返すのでここで指定
def exec_externalutils(scriptname):
    #プレビューレンダをバックグラウンドに投げとく
    blenderpath = sys.argv[0]
    scrpath = get_dir(__file__) + "utils" + os.sep +  scriptname
    cmdstr = qq(blenderpath) + " " + qq(bpy.data.filepath) + " -b " + " -P " + qq(scrpath)
    print("********************")
    print("__file__:"+__file__)
    print("scrpath:"+scrpath)
    print("cmdstr:"+cmdstr)
    print("********************")
    subprocess.Popen(cmdstr)
    pass



SelectedFile = ""
FileBrouserExecute = dummy

##############################################################
#ファイルセレクター
#
#FileBrouserExec(func)にファイルロード後に実行する関数を指定して開く
#SelectedFileにロードしたパスが入ってる。
#
##############################################################
#http://www.blender.org/documentation/blender_python_api_2_57_release/bpy.types.Operator.html#calling-a-file-selector
#Calling a File Selector
class FileBrouser(bpy.types.Operator):#ファイルセレクター
    """Test exporter which just writes hello world"""
    bl_idname = "file.selector"
    bl_label = "File Selector"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    #filepath =bpy.context.blend_data.filepath
    directory = bpy.props.StringProperty(subtype="DIR_PATH")#"c:\\"
    #あらかじめディレクトリ指定するの無理みたい

    @classmethod
    #optional
    def poll(cls, context):
        return context.object is not none

    def execute(self, context):
        print("execute")
        global SelectedFile
        SelectedFile = self.filepath
        FileBrouserExecute()



        #dbg
        #import mypac.filewrap
        #mypac.filewrap.debug = True
        #mypac.filewrap.dbg("")
        #mypac.filewrap.dbg("")
        #mypac.filewrap.dbg("self")
        #mypac.filewrap.dbg(self)
        #mypac.filewrap.dbg("self.filepath")
        #mypac.filewrap.dbg(self.filepath)
        #mypac.filewrap.dbg("self.directory")
        #mypac.filewrap.dbg(self.directory)

        print("execute おわり")
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
#        context.window_manager.fileselect_add(self,directory=bpy.context.blend_data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



# Register and add to the file selector
bpy.utils.register_class(FileBrouser)
#bpy.types.INFO_MT_file_export.append(menu_func)


# test call
#bpy.ops.file.selector('INVOKE_DEFAULT')


#ファイルブラウザに実行する関数を渡して開く
def FileBrouserExec(exefunc):
    print("FileBrouserExec")
    global FileBrouserExecute
    FileBrouserExecute = exefunc
    bpy.ops.file.selector('INVOKE_DEFAULT')
    return




############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#ui表示上の各種コンフィグを記述するクラス。ボタンリストに代替。
#これをリスト化すればいい！
#途中でこのコンフィグだけのやつ挟めばラベルとか挿入できる

"""
uicategory{}
みたいのを用意して[]をいれていく
uiitemlistには新規で作ったのを指定すればどんどんカテゴリわけされていく

label時に新規登録処理をしていきたい

label:[]的な感じ
"""

uicategories = OrderedDict()

uiitemList = []
class uiitem():
    type = "button"
    idname = ""
    label = ""
    icon = ""
    mode = ""
    #ボタンの表示方向
    direction = ""
    
    #宣言時自動登録
    def __init__(self,label="",iscat=False):
        global uiitemList
        global uicategories
      
        if label != "":
            self.type = "label"
            self.label = label

            if iscat:
                #uicategoryに登録
                uicategories[label] = []
                uiitemList = uicategories[label]

        uiitemList.append(self)
    
    #簡易セットアップ
    def button(self,idname,label,icon,mode):
        self.idname = idname
        self.label = label
        self.icon = icon
        self.mode = mode
        return

    #フィックス用
    def vertical(self):
        self.type = "fix"
        self.direction = "vertical"
        return
    
    def horizontal(self):
        self.type = "fix"
        self.direction = "horizontal"
        return



dialog_uicat = ""
#http://blender.stackexchange.com/questions/6512/how-to-call-invoke-popup
class DialogPanel(bpy.types.Operator):
    """ダイアログ"""
    bl_idname = "object.dialog"
    bl_label = "ダイアログ"
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):
        #メニューのペンディングに使えるぞ！？
        #return context.window_manager.invoke_props_dialog(self) 
        return context.window_manager.invoke_popup(self,width=500) 


    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        self.report({"INFO"},"called")
        global uicategories
        global dialog_uicat
        uiitemList = uicategories[dialog_uicat]

        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols

        #ペンディング
        #active.label(text="")
        active = active.row(align=True)
        #active.label(text="")
        active.operator("object.myobject_30808",icon="PINNED",text="")

        #縦並び
        #cols = b.column(align=True)
        #active = cols.column(align=True)

        for item in uiitemList:
            #スキップ処理
            if item.mode == "none":
                continue
            
            #if item.mode == "edit":
                ##編集モード以外飛ばす
                #if bpy.context.edit_object != None:
                #    continue
            
            #縦横
            if item.type == "fix":
                if item.direction == "vertical":
                    active = cols.column(align=True)
                if item.direction == "horizontal":
                    active = active.row(align=True)
                continue
            
            #描画
            if item.type == "label":
                if item.icon != "":
                    active.label(text=item.label, icon=item.icon)
                else:
                    active.label(text=item.label)
                active = cols.column(align=True)

            if item.type == "button":
                if item.icon != "":
                    active.operator(item.idname, icon=item.icon)
                else:
                    active.operator(item.idname)



#メインパネル
class MyaddonView3DPanel(bpy.types.Panel):#メインパネル
    bl_label = "メインパネル"
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    def draw(self, context):
        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols


        #超よく使う
        active = cols.column(align=True)
        active.label(text="クイック")
        active = active.row(align=True)
        active.operator("object.myobject_490317",text="保存",icon="FILE_TICK")
        active.operator("object.myobject_960554",text="BGレンダ")
        active.operator("pageutils.topage",text="ページに戻る")
        #active.operator("object.myobject_420416",text="+辺")
        active = cols.column(align=True)
        active = active.row(align=True)
        #roomtools
        active.operator("object.myobject_288056",text="Grp化")#グループ化
        #maintools内
        active.operator("object.myobject_b424289a",text="Proxy")#プロクシ作成
        active.operator("object.myobject_248120",text="Full Proxy")#プロクシ作成
        active = cols.row(align=True)
        active.operator("object.myobject_199238",text="Lamp Proxy")#Lamp Proxy
        active = cols.row(align=True)
        active.operator("object.myobject_286013",text="複製を実体化")#複製を実体化
        active = cols.row(align=True)
        active.operator("object.myobject_759926",icon="MESH_TORUS")
        active.operator("object.myobject_700665",icon="MESH_ICOSPHERE")
        active.operator("object.myobject_194057",icon="MESH_ICOSPHERE")
        active.operator("object.myobject_286488",icon="MESH_ICOSPHERE")


        active = cols.row(align=True)
        active.label(text="")

        active = cols.row(align=True)
        active.label(text="ペンディング",icon="PINNED")
        #クリアボタン
        active.operator("object.myobject_114105",icon="UNPINNED",text="")
        active = cols.column(align=True)

        #ペンディングされたUIの描画
        for uicat in pendings:
            uiitemList = uicategories[uicat]
            for item in uiitemList:
                #スキップ処理
                if item.mode == "none":
                    continue
            
                #if item.mode == "edit":
                    ##編集モード以外飛ばす
                    #if bpy.context.edit_object != None:
                    #    continue
            
                #縦横
                if item.type == "fix":
                    if item.direction == "vertical":
                        active = cols.column(align=True)
                    if item.direction == "horizontal":
                        active = active.row(align=True)
                    continue
            
                #描画
                if item.type == "label":
                    if item.icon != "":
                        active.label(text=item.label, icon=item.icon)
                    else:
                        active.label(text=item.label)
                if item.type == "button":
                    if item.icon != "":
                        active.operator(item.idname, icon=item.icon)
                    else:
                        active.operator(item.idname)





        active.label(text="メイン")
        for uicat in uicategories:
            uiitemList = uicategories[uicat]
            for item in uiitemList:
                #スキップ処理
                if item.mode == "none":
                    continue
            
                #if item.mode == "edit":
                    ##編集モード以外飛ばす
                    #if bpy.context.edit_object != None:
                    #    continue
            
                #縦横
                #if item.type == "fix":
                    #if item.direction == "vertical":
                    #    active = cols.column(align=True)
                    #if item.direction == "horizontal":
                    #    active = active.row(align=True)
                    #continue
            
                #描画
                if item.type == "label":
                    #通常はvertical。horizontalは続くボタンは""を指定。
                    if item.direction == "vertical":
                        active = cols.column(align=True)
                    if item.direction == "horizontal":
                        active = cols.column(align=True)
                        active = active.row(align=True)

                    if item.icon != "":
                        if item.idname != "":
                            active.operator(item.idname, icon=item.icon)
                        else:
                            active.label(text=item.label, icon=item.icon)
                        
                    else:
                        if item.idname != "":
                            active.operator(item.idname)
                        #else:
                        #    active.label(text=item.label)
                #if item.type == "button":
                #    if item.icon != "":
                #        active.operator(item.idname, icon=item.icon)
                #    else:
                #        active.operator(item.idname)



#UIカテゴリの実行部を外部化。いろいろ処理できるように。
def uicategory_execute(self):
    global dialog_uicat
    dialog_uicat = self.bl_label
    bpy.ops.object.dialog("INVOKE_DEFAULT")



#ペンディング用リスト。カテゴリを登録していく
#pendings = ["簡略化"]
pendings = []


########################################
#ペンディング
########################################
class MYOBJECT_30808(bpy.types.Operator):#ペンディング
    """ペンディング"""
    bl_idname = "object.myobject_30808"
    bl_label = "ペンディング"
    bl_options = {'REGISTER', 'UNDO'}
    icon = "PINNED"
    #ui自動登録はなし

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        global dialog_uicat
        global pendings
        pendings.append(dialog_uicat)
        return {'FINISHED'}
########################################


########################################
#クリア
########################################
class MYOBJECT_114105(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "object.myobject_114105"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}
    icon="UNPINNED"

    #ui自動登録はなし

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        global pendings
        pendings = []
        
        return {'FINISHED'}
########################################

















"""
テンプレ

############################################################################################################################
uiitem("")
############################################################################################################################


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    mode="","edit","none","all"


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

"""


#リストへのアペンドは初期化処理内でやってるからこれだけでラベル追加できる。
############################################################################################################################
############################################################################################################################
################################################################################
#UIカテゴリ
########################################
#ファイル
########################################
class CATEGORYBUTTON_111115(bpy.types.Operator):#ファイル
    """ファイル"""
    bl_idname = "object.categorybutton_111115"
    bl_label = "ファイル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ファイル",True)
    uiitem.button(bl_idname,bl_label,icon="BLENDER",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#保存
########################################
class MYOBJECT_490317(bpy.types.Operator):#保存
    """保存"""
    bl_idname = "object.myobject_490317"
    bl_label = "保存"
    bl_options = {'REGISTER', 'UNDO'}
    
    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="all")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        try:
            print(bpy.ops.wm.save_mainfile())
            pass
        except  :
            pass
        
        return {'FINISHED'}
########################################

########################################
#BGレンダ
########################################
class MYOBJECT_960554(bpy.types.Operator):#BGレンダ
    """BGレンダ"""
    bl_idname = "object.myobject_960554"
    bl_label = "BGレンダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #エッジオフ
        bpy.context.scene.render.use_edge_enhance = False

        #メイン
        blendfilepath = bpy.data.filepath
        blendname = os.path.splitext(os.path.basename(blendfilepath))[0]
        renderdir = os.path.dirname(blendfilepath) + os.sep + "tmp_render" + os.sep
        binpath = bpy.app.binary_path
        command = qq(binpath) + " -b " + qq(blendfilepath) + " -o " + qq(renderdir+blendname+"_") + " -F PNG -x 1 -f " + str(bpy.context.scene.frame_current)
        self.report({"INFO"},command)
        #os.system(command)
        #subprocess.call(command, shell=True)
        subprocess.Popen(command)

        return {'FINISHED'}
########################################

########################################
#+辺
########################################
class MYOBJECT_420416(bpy.types.Operator):#+辺
    """+辺"""
    bl_idname = "object.myobject_420416"
    bl_label = "+辺"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #エッジオフ
        bpy.context.scene.render.use_edge_enhance = True

        #メイン
        blendfilepath = bpy.data.filepath
        blendname = os.path.splitext(os.path.basename(blendfilepath))[0]
        renderdir = os.path.dirname(blendfilepath) + os.sep + "tmp_render" + os.sep
        binpath = bpy.app.binary_path
        command = qq(binpath) + " -b " + qq(blendfilepath) + " -o " + qq(renderdir+blendname+"_") + " -F PNG -x 1 -f " + str(bpy.context.scene.frame_current)
        self.report({"INFO"},command)
        #os.system(command)
        #subprocess.call(command, shell=True)
        subprocess.Popen(command)
        
        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#保存して閉じる
########################################
class MYOBJECT_669544(bpy.types.Operator):#保存して閉じる
    """保存して閉じる"""
    bl_idname = "object.myobject_669544"
    bl_label = "保存して閉じる"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUIT",mode="all")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        try:
            bpy.ops.wm.save_mainfile()
            pass
        except  :
            pass
        bpy.ops.wm.quit_blender()
        #if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
        #    bpy.ops.wm.quit_blender()
        #else:
        #    printf("ERROR")
        return {'FINISHED'}
########################################

########################################
#保存して開き直す
########################################
class MYOBJECT_559881(bpy.types.Operator):#保存して開き直す
    """保存して開き直す"""
    bl_idname = "object.myobject_559881"
    bl_label = "保存して開き直す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="all")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #try:
        #    bpy.ops.wm.save_mainfile()
        #    bpy.ops.wm.revert_mainfile(use_scripts=True)
        #    pass
        #except  :
        #    pass
        #bpy.ops.wm.revert_mainfile(use_scripts=True)
        #if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
        #    #bpy.ops.wm.revert_mainfile()
        #    pass
        #else:
        #    return {'CANCELLED'}

        bpy.ops.wm.save_mainfile()
        bpy.ops.wm.revert_mainfile("INVOKE_DEFAULT",use_scripts=True)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#100倍とか
########################################
class MYOBJECT_463064(bpy.types.Operator):#100倍
    """100倍"""
    bl_idname = "object.myobject_463064"
    bl_label = "100倍とか"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        camera = bpy.context.scene.camera
        camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
        camera.rotation_euler[0] = 0.8746716380119324
        camera.rotation_euler[1] = -2.7369874260330107e-06
        camera.rotation_euler[2] = 2.5201363563537598
        
        bpy.ops.transform.resize(value=(10000, 10000, 10000), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}
########################################

########################################
#0.01倍
########################################
class MYOBJECT_159343(bpy.types.Operator):#0.01倍
    """0.0001倍"""
    bl_idname = "object.myobject_159343"
    bl_label = "0.01倍"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        camera = bpy.context.scene.camera
        camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
        camera.rotation_euler[0] = 0.8746716380119324
        camera.rotation_euler[1] = -2.7369874260330107e-06
        camera.rotation_euler[2] = 2.5201363563537598
        
        bpy.ops.transform.resize(value=(0.01, 0.01,0.01), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.view3d.view_selected()
        
        return {'FINISHED'}
########################################

########################################
#カメラだけ
########################################
class MYOBJECT_607395(bpy.types.Operator):#カメラだけ
    """カメラだけ"""
    bl_idname = "object.myobject_607395"
    bl_label = "カメラだけ"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        camera = bpy.context.scene.camera
        camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
        camera.rotation_euler[0] = 1
        camera.rotation_euler[1] = 0
        camera.rotation_euler[2] = -1
        
        bpy.ops.view3d.view_selected()
        
        return {'FINISHED'}
########################################

########################################
#いろいろ処理
########################################
class MYOBJECT_227575(bpy.types.Operator):#いろいろ処理
    """いろいろ処理"""
    bl_idname = "object.myobject_227575"
    bl_label = "いろいろ処理"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.camera.data.clip_end = 100000
        
        camera = bpy.context.scene.camera
        camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
        camera.rotation_euler[0] = 1
        camera.rotation_euler[1] = 0
        camera.rotation_euler[2] = -1
        
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#メモ設置
########################################
class MYOBJECT_350101(bpy.types.Operator):#メモ設置
    """メモ設置"""
    bl_idname = "object.myobject_350101"
    bl_label = "メモ設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_EMPTY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, view_align=False, location=bpy.context.space_data.cursor_location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.rotation_euler[1] = 3.14159
        obj.show_name = True
        obj.show_x_ray = True
        obj.name = "MEMO:"
        obj.location[2] += 1

        #右上レイヤーにまとめる
        obj.layers[9] = True
        obj.layers[0] = False
        bpy.context.scene.layers[9] = True

        #グループ化
        if "MEMO" not in bpy.data.groups:
            bpy.ops.group.create(name="MEMO")
        else:
            bpy.data.groups["MEMO"].objects.link(obj)
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#カルテレンダ
########################################
class MYOBJECT_317755(bpy.types.Operator):#カルテレンダ
    """カルテレンダ"""
    bl_idname = "object.myobject_317755"
    bl_label = "カルテレンダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #ジオメトリの選択
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        geo = bpy.context.scene.objects.active
        
        
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        #ゼロ位置に
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        
        #カメラ位置を設定
        cam = bpy.context.scene.camera
#        cam.data.lens = 100
        
#        cam.location[0] = 0
#        cam.location[1] = -7.66724
#        cam.location[2] = 1.58621
#        cam.rotation_euler[0] = -1.5708
#        cam.rotation_euler[1] = 3.14159
#        cam.rotation_euler[2] = 3.14159
#        cam.rotation_mode = 'XYZ'
        
#        cam.data.shift_x = 0
#        cam.data.shift_y = -0.188
        
        
        #レンダ準備
        bpy.context.scene.render.use_shadows = False
        bpy.context.scene.render.use_raytrace = False
        bpy.context.scene.render.use_textures = True
        bpy.context.scene.render.use_antialiasing = False
        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
        bpy.context.scene.render.layers["RenderLayer"].use_freestyle = False
        bpy.context.scene.render.use_freestyle = False
        bpy.context.scene.render.use_edge_enhance = False
        bpy.context.scene.render.edge_threshold = 255
        
        dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "")
#        name = bpy.path.display_name_from_filepath(bpy.data.filepath)
        pathbase = dir + os.sep + "render" + os.sep + "karte_"
        
        #正面
        geo.rotation_euler[0] = 0
        geo.rotation_euler[1] = 0
        geo.rotation_euler[2] = 0
        bpy.context.scene.render.filepath = pathbase + "front.png"
        bpy.ops.render.render(write_still=True)
        
        
        
        #背面
        geo.rotation_euler[2] = -3.14159
        bpy.ops.object.location_clear()
        bpy.context.scene.render.filepath = pathbase + "back.png"
        bpy.ops.render.render(write_still=True)
        
        #左側
        #cam.data.shift_x = 0.125
        geo.rotation_euler[2] = -1.5708/2
        bpy.ops.object.location_clear()
        bpy.context.scene.render.filepath = pathbase + "left.png"
        bpy.ops.render.render(write_still=True)
        
        
        #右側
        #cam.data.shift_x = -0.125
        geo.rotation_euler[2] = 1.5708/2
        bpy.ops.object.location_clear()
        bpy.context.scene.render.filepath = pathbase + "right.png"
        bpy.ops.render.render(write_still=True)
        
        
#        #トップ
#        cam.data.shift_x = 0
#        cam.data.shift_y = -0.125
#        #現在の高さZとジオメトリまでの距離Yたせば同じ距離感の頭までの距離になるぞ。
##        cam.location[0] = 0
#        cam.location[1] = (cam.location[2] + (cam.location[1] * -1)) * -1
#        cam.location[2] = 0
#        geo.rotation_euler[0] = 1.5708
#        geo.rotation_euler[1] = 0
#        geo.rotation_euler[2] = 0
#        bpy.ops.object.location_clear()
#        bpy.context.scene.render.filepath = pathbase + "top.png"
#        bpy.ops.render.render(write_still=True)
        
        
        
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        
        return {'FINISHED'}
########################################


########################################
#VRExport
########################################
class MYOBJECT_871849(bpy.types.Operator):#VRExport
    """VRExport"""
    bl_idname = "object.myobject_871849"
    bl_label = "VRExport"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #basepath = bpy.data.filepath

        ##現状保存
        #bpy.ops.wm.save_mainfile()

        #deselect()

        ##いらないものの削除
        #delete(match("ConstructionArea"))
        #delete(match("Grid_"))
        
        #deselect()

        #for obj in bpy.data.objects:
        #    obj.hide = False

        ##非表示レイヤー削除
        ##レイヤー表示を反転して全選択削除してもどす？
        ##オブジェクトが表示レイヤーをもってれば除外する
        ##layers = bpy.context.scene.layers
        ##dellist = []
        ##for obj in bpy.data.objects:
        ##    delflag = True
        ##    for n in range(0,20):
        ##        if obj.layers[n] == True:
        ##            if layers[n] == True:
        ##                delflag = False
        ##                break
        ##    if delflag:
        ##        dellist.append(obj)

        ##for n in range(0,20):
        ##    bpy.context.scene.layers[n] = True

        ##delete(dellist)
        #for n in range(0,20):
        #    bpy.context.scene.layers[n] = not bpy.context.scene.layers[n]
        #bpy.ops.object.select_all(action='SELECT')
        #delete(get_selected_list())
        #for n in range(0,20):
        #    bpy.context.scene.layers[n] = not bpy.context.scene.layers[n]
        

        ##mod適用
        #deselect()
        #for obj in bpy.data.objects:
        #    if obj.type == "MESH":
        #        obj.select = True
        #apply_mods()
        #deselect()

        #bpy.ops.object.select_all(action='SELECT')
        #reject_notmesh()
        #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


        #deselect()
        #for obj in bpy.data.objects:
        #    #テキストも重くなるのでいらない
        #    if obj.type == "FONT":
        #        obj.select = True

        #    #非表示オブジェクト削除
        #    if obj.type == "MESH":
        #        if obj.draw_type == "WIRE" or obj.draw_type == "BOUNDS":
        #            obj.select = True
        #    #if obj.hide == True:
        #    #    obj.hide = False
        #    #    obj.select = True



        #delete(get_selected_list())

        #シェルでコピーしたほうがいいんじゃね？
        #bpy.ops.wm.save_mainfile(filepath=fujiwara_toolbox.conf.maintools_vrexportpath)

        #####

        #非レンダオブジェクトを選択から除外
        selection = get_selected_list()
        for obj in selection:
            if obj.hide_render:
                obj.select = False

        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        #objで出す方がマシだ
        bpy.ops.export_scene.obj(filepath= fujiwara_toolbox.conf.maintools_vrexportdir + os.sep + "VRRoom.obj", use_selection=True)


        #出力フォルダを開く
        os.system("EXPLORER " + fujiwara_toolbox.conf.maintools_vrexportdir)
        ##time.sleep(5)
        #bpy.ops.wm.open_mainfile(filepath=basepath)

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





############################################################################################################################
uiitem("tmp.fbx")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#インポート
########################################
class MYOBJECT_174609(bpy.types.Operator):#fbxインポート
    """fbxインポート"""
    bl_idname = "object.myobject_174609"
    bl_label = "fbxインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.import_scene.fbx(filepath="tmp.fbx",automatic_bone_orientation=True)
        return {'FINISHED'}
########################################
########################################
#fbxエクスポート（選択メッシュ）
########################################
class MYOBJECT_87061(bpy.types.Operator):#fbxエクスポート（選択メッシュ）
    """fbxエクスポート（選択メッシュ）"""
    bl_idname = "object.myobject_87061"
    bl_label = "fbxエクスポート（選択メッシュ）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.export_scene.fbx(filepath="tmp.fbx",check_existing=False,use_selection=True)
        bpy.ops.object.delete()
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#3dcoatエクスポート
########################################
class MYOBJECT_822477(bpy.types.Operator):#3dcoatエクスポート
    """3dcoatエクスポート"""
    bl_idname = "object.myobject_822477"
    bl_label = "3dcoatエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #objじゃないとダメ
        #from blender
        #帰ってくるとき、原点がグローバル0になってしまうので、複製系は適用してしまう。
        bpy.context.scene.objects.active.select = True
        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
        #名前、.001とかが事故るのでリネームする
        for obj in selected:
            obj.name = obj.name.replace(".","")
        
        #まずはトランスフォームを適用する
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #100倍で出して0.01倍で取り込む。
        bpy.ops.export_scene.obj(filepath="tmp3dcoat.obj",check_existing=False,axis_forward='-Z', axis_up='Y',use_selection=True, global_scale=100.0, use_mesh_modifiers=False)
        
        #オリジナルを識別できるようにリネーム
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                obj.name = obj.name + "_3dcoatexported"
        
        
        
        return {'FINISHED'}
########################################


########################################
#3dcoatインポート
########################################
class MYOBJECT_189112(bpy.types.Operator):#3dcoatインポート
    """3dcoatインポート"""
    bl_idname = "object.myobject_189112"
    bl_label = "3dcoatインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #3dcoat
        bpy.ops.import_scene.obj(filepath="tmp3dcoat.obj", axis_forward='-Z', axis_up='Y')
        #名前変える
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                #blenderに追加されたMESH名を除去する
                obj.name = obj.name.split("_")[0]
                obj.name = obj.name + "_3dcoatimported"
        
        #スケール調整
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               obj.scale = (0.01,0.01,0.01)
               bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #exportedのメッシュをimportedの内容にする
        for target in bpy.data.objects:
            if target.type == "MESH":
                if "_3dcoatexported" in target.name:
                    for source in bpy.context.selected_objects:
                        if source.name.replace("_3dcoatimported","") == target.name.replace("_3dcoatexported",""):
                            target.data = source.data.copy()
                            #ついでに原点を重心に
                            #bpy.context.scene.objects.active = target
                            #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS',
                            #center='MEDIAN')
                            #importedの削除
                            #bpy.context.scene.objects.active = source
                            #bpy.ops.object.delete(use_global=False)
        
        for target in bpy.data.objects:
            if target.type == "MESH":
                if "_3dcoatexported" in target.name:
                    #exportedの名前を消す
                    target.name = target.name.replace("_3dcoatexported","")
                    #ついでに原点を重心に
                    #bpy.context.scene.objects.active = target
                    #bpy.ops.object.transform_apply(location=True,
                    #rotation=True, scale=True)
                    #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS',
                    #center='MEDIAN')
        
        #importedを消す
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if "_3dcoatimported" in obj.name:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.delete(use_global=False)
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#posi.objエクスポート
########################################
class MYOBJECT_505642(bpy.types.Operator):#posi.objエクスポート
    """posi.objエクスポート"""
    bl_idname = "object.myobject_505642"
    bl_label = "posi.objエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.export_scene.obj(filepath="posi.obj",check_existing=False,use_selection=True)
        
        return {'FINISHED'}
########################################


########################################
#nega.objエクスポート
########################################
class MYOBJECT_896828(bpy.types.Operator):#nega.objエクスポート
    """nega.objエクスポート"""
    bl_idname = "object.myobject_896828"
    bl_label = "nega.objエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.export_scene.obj(filepath="nega.obj",check_existing=False,use_selection=True)
        
        return {'FINISHED'}
########################################


########################################
#posi.objインポート
########################################
class MYOBJECT_229893(bpy.types.Operator):#posi.objインポート
    """posi.objインポート"""
    bl_idname = "object.myobject_229893"
    bl_label = "posi.objインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.import_scene.obj(filepath="posi.obj")
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#簡略化
########################################
class CATEGORYBUTTON_520749(bpy.types.Operator):#簡略化
    """簡略化"""
    bl_idname = "object.categorybutton_520749"
    bl_label = "簡略化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("簡略化",True)
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オフ
########################################
class MYOBJECT_759926(bpy.types.Operator):#オフ
    """オフ"""
    bl_idname = "object.myobject_759926"
    bl_label = "オフ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_TORUS",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.render.use_simplify = False
        
        return {'FINISHED'}
########################################


########################################
#Subdiv 2
########################################
class MYOBJECT_700665(bpy.types.Operator):#Subdiv 2
    """Subdiv 2"""
    bl_idname = "object.myobject_700665"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        
        return {'FINISHED'}
########################################


########################################
#Subdiv 1
########################################
class MYOBJECT_194057(bpy.types.Operator):#Subdiv 1
    """Subdiv 1"""
    bl_idname = "object.myobject_194057"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 1
        
        return {'FINISHED'}
########################################



########################################
#Subdiv 0
########################################
class MYOBJECT_286488(bpy.types.Operator):#Subdiv 0
    """Subdiv 0"""
    bl_idname = "object.myobject_286488"
    bl_label = "0"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0
        
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#レンダ解像度化
########################################
class MYOBJECT_69698(bpy.types.Operator):#レンダ解像度化
    """レンダ解像度化"""
    bl_idname = "object.myobject_69698"
    bl_label = "レンダ解像度化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj. modifiers:
                    if mod.type == "SUBSURF":
                        if mod.levels > mod.render_levels:
                            mod.render_levels = mod.levels
                        else:
                            mod.levels = mod.render_levels
        
        
        
        
        return {'FINISHED'}
########################################


















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#選択・操作
########################################
class CATEGORYBUTTON_200803(bpy.types.Operator):#選択・操作
    """選択・操作"""
    bl_idname = "object.categorybutton_200803"
    bl_label = "選択・操作"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("選択・操作",True)
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#親子
########################################
class MYOBJECT_24259(bpy.types.Operator):#親子
    """親子"""
    bl_idname = "object.myobject_24259"
    bl_label = "親子"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        objects = get_selected_list()
        targets = []
        for obj in objects:
            activate(obj)
            mode("OBJECT")
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            targets.extend(get_selected_list())

        targets.extend(objects)

        for obj in targets:
            obj.select = True

        #for obj in bpy.data.objects:
        #    obj.select = False
        #obj = bpy.context.scene.objects.active
        #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #obj.select = True
        return {'FINISHED'}
########################################

########################################
#親子→ローカルビュー
########################################
class MYOBJECT_96321(bpy.types.Operator):#親子→ローカルビュー
    """親子→ローカルビュー"""
    bl_idname = "object.myobject_96321"
    bl_label = "親子→ローカルビュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #for obj in bpy.data.objects:
        #    obj.select = False
        #obj = bpy.context.scene.objects.active
        #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #obj.select = True
        bpy.ops.object.myobject_24259()

        bpy.ops.view3d.localview()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#親子コピー
########################################
class MYOBJECT_55567(bpy.types.Operator):#親子コピー
    """親子コピー"""
    bl_idname = "object.myobject_55567"
    bl_label = "親子コピー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="COPYDOWN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_24259()
        bpy.ops.view3d.copybuffer()
        
        return {'FINISHED'}
########################################

########################################
#＆ペースト
########################################
class MYOBJECT_971178(bpy.types.Operator):#＆ペースト
    """＆ペースト"""
    bl_idname = "object.myobject_971178"
    bl_label = "＆ペースト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_55567()
        bpy.ops.view3d.pastebuffer()


        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





########################################
#親子削除
########################################
class MYOBJECT_975985(bpy.types.Operator):#親子削除
    """親子削除"""
    bl_idname = "object.myobject_975985"
    bl_label = "親子削除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PANEL_CLOSE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_24259()
        bpy.ops.object.delete(use_global=False)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#グループ
########################################
class MYOBJECT_764181(bpy.types.Operator):#グループ
    """グループ"""
    bl_idname = "object.myobject_764181"
    bl_label = "グループ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="ROTATECOLLECTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.select_grouped(type='GROUP')
        
        return {'FINISHED'}
########################################

########################################
#マテリアル未割り当て
########################################
class MYOBJECT_490584(bpy.types.Operator):#マテリアル未割り当て
    """マテリアル未割り当て"""
    bl_idname = "object.myobject_490584"
    bl_label = "マテリアル未割り当て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SOLID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            obj.select = False
        
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.active_material == None:
                    obj.select = True
        
        
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




########################################
#選択物のレイヤーだけ表示してコピー
########################################
class MYOBJECT_129690(bpy.types.Operator):#選択物のレイヤーだけ表示してコピー
    """選択物のレイヤーだけ表示してコピー"""
    bl_idname = "object.myobject_129690"
    bl_label = "選択物のレイヤーだけ表示してコピー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #一旦全部非表示
        for n in range(0,20):
            bpy.context.scene.layers[n] = False
        
        #選択オブジェクトの表示を反映
        for obj in bpy.data.objects:
            if obj.select:
                for n in range(0,20):
                    if obj.layers[n]:
                        bpy.context.scene.layers[n] = True
        
        #選択解除
        for obj in bpy.data.objects:
            obj.select = False
        
        #全選択
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.view3d.copybuffer()
        
        return {'FINISHED'}
########################################




########################################
#なにかあるレイヤーだけを全表示
########################################
class MYOBJECT_124884(bpy.types.Operator):#なにかあるレイヤーだけを全表示
    """なにかあるレイヤーだけを全表示"""
    bl_idname = "object.myobject_124884"
    bl_label = "なにかあるレイヤーだけを全表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #一旦全部非表示
        for n in range(0,20):
            bpy.context.scene.layers[n] = False
        
        #選択オブジェクトの表示を反映
        for obj in bpy.data.objects:
            for n in range(0,20):
                if obj.layers[n]:
                    bpy.context.scene.layers[n] = True
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ペースト・表示
########################################
class MYOBJECT_47465(bpy.types.Operator):#ペースト・表示
    """ペースト・表示"""
    bl_idname = "object.myobject_47465"
    bl_label = "ペースト・表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PASTEFLIPDOWN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.view3d.pastebuffer()
        for obj in bpy.data.objects:
            if obj.select:
                for n in range(0, 19):
                    if obj.layers[n] == True:
                        bpy.context.scene.layers[n] = True
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#カメラ範囲外を選択
########################################
class MYOBJECT_770418(bpy.types.Operator):#カメラ範囲外を選択
    """カメラ範囲外を選択"""
    bl_idname = "object.myobject_770418"
    bl_label = "カメラ範囲外を選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        selection = get_selected_list()
        for obj in selection:
            if checkIfIsInCameraView(obj):
                obj.select = False

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#原点ツール
########################################
class CATEGORYBUTTON_421353(bpy.types.Operator):#原点ツール
    """原点ツール"""
    bl_idname = "object.categorybutton_421353"
    bl_label = "原点ツール"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("原点ツール",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_EMPTY",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#カーソルに設置
########################################
class MYOBJECT_551555(bpy.types.Operator):#カーソルに設置
    """カーソルに設置"""
    bl_idname = "object.myobject_551555"
    bl_label = "カーソルに設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        loc = bpy.context.space_data.cursor_location
        if "原点ピボット" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            obj = bpy.context.scene.objects.active
            obj.name = "原点ピボット"
            obj.show_name = True
            obj.show_x_ray = True
            obj.empty_draw_type = 'ARROWS'
            obj.empty_draw_size = 0.5
        else:
            obj = bpy.data.objects["原点ピボット"]
            obj.hide = False
            obj.location = loc
        
        for tmp in bpy.context.selected_objects:
            tmp.select = False
        
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        return {'FINISHED'}
########################################

########################################
#オブジェクトに設置
########################################
class MYOBJECT_980669(bpy.types.Operator):#オブジェクトに設置
    """オブジェクトに設置"""
    bl_idname = "object.myobject_980669"
    bl_label = "オブジェクトに設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        loc = bpy.context.scene.objects.active.location
        bpy.context.space_data.cursor_location = loc
        if "原点ピボット" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            obj = bpy.context.scene.objects.active
            obj.name = "原点ピボット"
            obj.show_name = True
            obj.show_x_ray = True
            obj.empty_draw_type = 'ARROWS'
            obj.empty_draw_size = 0.5
        else:
            obj = bpy.data.objects["原点ピボット"]
            obj.hide = False
            obj.location = loc
        
        for tmp in bpy.context.selected_objects:
            tmp.select = False
        
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#オブジェクトをピボットに移動
########################################
class MYOBJECT_145460(bpy.types.Operator):#オブジェクトをピボットに移動
    """オブジェクトをピボットに移動"""
    bl_idname = "object.myobject_145460"
    bl_label = "オブジェクトをピボットに移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="NLA_PUSHDOWN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.objects.active.location = bpy.data.objects["原点ピボット"].location
        
        return {'FINISHED'}
########################################




########################################
#ピボットに原点を移動
########################################
class MYOBJECT_808575(bpy.types.Operator):#ピボットに原点を移動
    """ピボットに原点を移動"""
    bl_idname = "object.myobject_808575"
    bl_label = "ピボットに原点を移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EMPTY_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.cursor_location = bpy.data.objects["原点ピボット"].location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#原点を下に（選択物）
########################################
class MYOBJECT_947695(bpy.types.Operator):#原点を下に（選択物）
    """原点を下に（選択物）"""
    bl_idname = "object.myobject_947695"
    bl_label = "原点を下に（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="TRIA_DOWN_BAR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        objlist = []
        for obj in bpy.context.selected_objects:
            objlist.append(obj)
        
        for obj in bpy.context.selected_objects:
            obj.select = False
        
        for obj in objlist:
            bpy.context.scene.objects.active = obj
            obj.select = True
        
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bottom = 1000
            for v in obj.data.vertices:
                if v.co.z < bottom:
                    bottom = v.co.z
            bpy.context.space_data.cursor_location[2] = bottom
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.select = False
        
        for obj in objlist:
            obj.select = True
        
        return {'FINISHED'}
########################################
########################################
#重心下に
########################################
class MYOBJECT_183554(bpy.types.Operator):#重心下に
    """重心下に"""
    bl_idname = "object.myobject_183554"
    bl_label = "重心下に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        objlist = get_selected_list()
        deselect()
        
        for obj in objlist:
            bpy.context.scene.objects.active = obj
            obj.select = True
        
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bottom = 1000
            for v in obj.data.vertices:
                if v.co.z < bottom:
                    bottom = v.co.z
            bpy.context.space_data.cursor_location[2] = bottom
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.select = False
        
        for obj in objlist:
            obj.select = True
        
        return {'FINISHED'}
########################################





#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



########################################
#原点X=0
########################################
class MYOBJECT_463922(bpy.types.Operator):#原点X=0
    """原点X=0"""
    bl_idname = "object.myobject_463922"
    bl_label = "原点X=0"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        targets = get_selected_list()
        for obj in targets:
            deselect()
            activate(obj)
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.context.space_data.cursor_location[0] = 0
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        select(targets)
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#カーソルZを0に
########################################
class MYOBJECT_98727(bpy.types.Operator):#カーソルZを0に
    """カーソルZを0に"""
    bl_idname = "object.myobject_98727"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.cursor_location[2] = 0
        
        return {'FINISHED'}
########################################





########################################
#オブジェクトのZを0に
########################################
class MYOBJECT_109728(bpy.types.Operator):#オブジェクトのZを0に
    """オブジェクトのZを0に"""
    bl_idname = "object.myobject_109728"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.location[2] = 0
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#選択頂点を原点に
########################################
class MYOBJECT_753369(bpy.types.Operator):#選択頂点を原点に
    """選択頂点を原点に"""
    bl_idname = "object.myobject_753369"
    bl_label = "選択頂点を原点に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EDITMODE_HLT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        if obj.mode != "EDIT":
            self.report({"INFO"},"編集モードで押して下さい")
            return {'CANCELLED'}
        
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        return {'FINISHED'}
########################################











#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#スーパー視点
########################################
class CATEGORYBUTTON_413853(bpy.types.Operator):#スーパー視点
    """スーパー視点"""
    bl_idname = "object.categorybutton_413853"
    bl_label = "スーパー視点"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("スーパー視点",True)
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_OFF",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




def super_view(direction):
        base = active()

        target = base
        super = target
        #とりあえず最大50階層
        for n in range(0,50):
            if target.parent != None:
                target = target.parent
                super = target
            else:
                break

        activate(super)
        bpy.ops.view3d.viewnumpad(type=direction, align_active=True)
        activate(base)

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#
########################################
class MYOBJECT_202399a(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_202399a"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_202399b(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_202399b"
    bl_label = "上"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("TOP")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_202399c(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_202399c"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#左
########################################
class MYOBJECT_248412d(bpy.types.Operator):#サイド
    """一番上の階層のオブジェクトに対してビューを設定"""
    bl_idname = "object.myobject_248412d"
    bl_label = "左"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("LEFT")
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_779140e(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_779140e"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_779140f(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_779140f"
    bl_label = "右"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("RIGHT")
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#
########################################
class MYOBJECT_309675g(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_309675g"
    bl_label = "前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("FRONT")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_309675h(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_309675h"
    bl_label = "下"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("BOTTOM")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class MYOBJECT_309675i(bpy.types.Operator):#
    """"""
    bl_idname = "object.myobject_309675i"
    bl_label = "後"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        super_view("BACK")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#マテリアル
########################################
class CATEGORYBUTTON_798012(bpy.types.Operator):#マテリアル
    """マテリアル"""
    bl_idname = "object.categorybutton_798012"
    bl_label = "マテリアル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("マテリアル",True)
    uiitem.button(bl_idname,bl_label,icon="SMOOTH",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#全て影なし
########################################
class MYOBJECT_134463(bpy.types.Operator):#全て影なし
    """全て影なし"""
    bl_idname = "object.myobject_134463"
    bl_label = "全て影なし"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SOLID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for mat in bpy.data.materials:
            mat.use_shadeless = True
        for obj in bpy.data.objects:
            obj.show_wire = True
        bpy.context.space_data.show_floor = False
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        return {'FINISHED'}
########################################


########################################
#全て影あり
########################################
class MYOBJECT_594225(bpy.types.Operator):#全て影あり
    """全て影あり"""
    bl_idname = "object.myobject_594225"
    bl_label = "全て影あり"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SMOOTH",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for mat in bpy.data.materials:
            mat.use_shadeless = False
        for obj in bpy.data.objects:
            obj.show_wire = False
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#全てシングル化
########################################
class MYOBJECT_386533(bpy.types.Operator):#全てシングル化
    """全てシングル化"""
    bl_idname = "object.myobject_386533"
    bl_label = "全てシングル化"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.make_single_user(type='ALL', object=False, obdata=False, material=True, texture=False, animation=False)
        
        return {'FINISHED'}
########################################


########################################
#透過無効化（選択物）
########################################
class MYOBJECT_867349(bpy.types.Operator):#透過無効化（選択物）
    """透過無効化（選択物）"""
    bl_idname = "object.myobject_867349"
    bl_label = "透過無効化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for slot in obj.material_slots:
                mat = slot.material
                if "裏ポリエッジ" in mat.name:
                    continue
                mat.use_transparency = False
        
        
        return {'FINISHED'}
########################################
########################################
#有効化（選択物）
########################################
class MYOBJECT_748672(bpy.types.Operator):#有効化（選択物）
    """有効化（選択物）"""
    bl_idname = "object.myobject_748672"
    bl_label = "有効化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for slot in obj.material_slots:
                mat = slot.material
                mat.use_transparency = True
                if "裏ポリエッジ" in mat.name:
                    mat.transparency_method = 'Z_TRANSPARENCY'
                else:
                    mat.transparency_method = 'RAYTRACE'

        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#Material Utils
########################################
class MYOBJECT_110074(bpy.types.Operator):#Material Utils
    """Materials Utilsの呼び出し"""
    bl_idname = "object.myobject_110074"
    bl_label = "Materials Utils"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.wm.call_menu(name="VIEW3D_MT_master_material")
        return {'FINISHED'}
########################################

########################################
#無マテリアルに白を割り当て
########################################
class MYOBJECT_998634(bpy.types.Operator):#無マテリアルに白を割り当て
    """無マテリアルに白を割り当て"""
    bl_idname = "object.myobject_998634"
    bl_label = "無マテリアルに白を割り当て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
    #アサイン用マテリアルの作成
        #mat = bpy.data.materials.new(name="whitemat")
        #mat.diffuse_color=(1,1,1)
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            if len(obj.material_slots) == 0:
                matname = sbsname(obj.name)

                #既にあるマテリアルが外れてるだけだったらそれを返す
                if matname in bpy.data.materials:
                    mat = bpy.data.materials[matname]
                else:
                    #substance上で.が_に変換されて都合が悪いので除去しておく
                    mat = bpy.data.materials.new(name=matname)#substanceとの連携用にオブジェクト名でマテリアル作る
                    mat.diffuse_color=(1,1,1)
                #マテリアルスロットがゼロだった
                obj.data.materials.append(mat)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("ノード")
############################################################################################################################

########################################
#ベースセットアップ
########################################
class MYOBJECT_266402(bpy.types.Operator):#ベースセットアップ
    """ベースセットアップ"""
    bl_idname = "object.myobject_266402"
    bl_label = "ベースセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mat = active().active_material

        #既にノードがオンの場合データ消えるとマズいから警告だして終了する
        if mat.use_nodes:
            self.report({"WARNING"},"既にノードが設定されています")
            return {'CANCELLED'}

        mat.use_nodes = True
        mat.use_shadeless = True
        tree = mat.node_tree
        links = tree.links

        #ノードのクリア
        for node in tree.nodes:
            tree.nodes.remove(node)

        #マテリアルノード
        n_mat = tree.nodes.new("ShaderNodeMaterial")
        #自身のマテリアルを指定
        n_mat.material = mat
        n_mat.location = (0,200)

        #出力
        n_out = tree.nodes.new("ShaderNodeOutput")
        n_out.location = (500,200)


        #接続
        tree.links.new(n_mat.outputs["Color"], n_out.inputs["Color"])


        return {'FINISHED'}
########################################

#########################################
##モノクロ化
#########################################
#class MYOBJECT_324645(bpy.types.Operator):#モノクロ化
#    """モノクロ化"""
#    bl_idname = "object.myobject_324645"
#    bl_label = "モノクロ化"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        objects = get_selected_list()
#        for obj in objects:
#            if obj.type != "MESH":
#                continue
#            if len(obj.data.materials) == 0:
#                mat = bpy.data.materials.new(name="モノクロマテリアル")
#                obj.data.materials.append(mat)
#            for mat in obj.data.materials:
#                #既にノードがオンの場合データ消えるとマズいから警告だして終了する
#                #if mat.use_nodes:
#                #    continue
#                #→破棄でいいや
#                #裏ポリはスキップ！！
#                if "裏ポリエッジ" in mat.name:
#                    continue
                
#                mat.use_nodes = True
#                mat.use_shadeless = True
#                tree = mat.node_tree
#                links = tree.links

#                #ノードのクリア
#                for node in tree.nodes:
#                    tree.nodes.remove(node)



#                ng_mono = nodegroup_instance(tree, append_nodetree("二値・グレー化"))
#                ng_beta = nodegroup_instance(tree, append_nodetree("ベタ影二値"))




#                #マテリアルノード
#                n_mat = tree.nodes.new("ShaderNodeMaterial")
#                #自身のマテリアルを指定
#                n_mat.material = mat
#                n_mat.location = (0,200)

#                #出力
#                n_out = tree.nodes.new("ShaderNodeOutput")
#                n_out.location = (500,200)


#                #接続
#                #マテリアル→グレー
#                tree.links.new(n_mat.outputs["Color"], ng_mono.inputs["グレー化"])
#                #マテリアル→ベタ影
#                tree.links.new(n_mat.outputs["Color"], ng_beta.inputs["Color"])
#                #ベタ影→二値
#                tree.links.new(ng_beta.outputs["Color"], ng_mono.inputs["二値化"])
                
#                #二値→アウトプット
#                tree.links.new(ng_mono.outputs["Color"], n_out.inputs["Color"])

#                #アルファ
#                tree.links.new(n_mat.outputs["Alpha"], n_out.inputs["Alpha"])
#                pass
        
#        return {'FINISHED'}
#########################################



########################################
#漫画シェーダ
########################################
class MYOBJECT_117769(bpy.types.Operator):#漫画シェーダ
    """漫画シェーダ"""
    bl_idname = "object.myobject_117769"
    bl_label = "漫画シェーダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        objects = get_selected_list()
        for obj in objects:
            if obj.type != "MESH":
                continue
            if len(obj.data.materials) == 0:
                mat = bpy.data.materials.new(name="モノクロマテリアル")
                obj.data.materials.append(mat)
            for mat in obj.data.materials:
                #既にノードがオンの場合データ消えるとマズいから警告だして終了する
                #if mat.use_nodes:
                #    continue
                #→破棄でいいや
                #裏ポリはスキップ！！
                if "裏ポリエッジ" in mat.name:
                    continue
                
                mat.use_shadeless = True
                ntu = NodetreeUtils(mat)
                ntu.activate()
                ntu.cleartree()

                ng_comic = ntu.group_instance(append_nodetree("漫画シェーダ"))

                #マテリアルノード
                n_mat = ntu.add("ShaderNodeMaterial","Material")
                #自身のマテリアルを指定
                n_mat.material = mat

                #出力
                n_out = ntu.add("ShaderNodeOutput","Output")

                #接続
                ntu.link(n_mat.outputs["Color"], ng_comic.inputs["Color"])
                ntu.link(n_mat.outputs["Normal"], ng_comic.inputs["Normal"])

                ntu.link(ng_comic.outputs["Color"], n_out.inputs["Color"])

                ntu.link(n_mat.outputs["Alpha"], n_out.inputs["Alpha"])


                pass
        select(objects)
        return {'FINISHED'}
########################################


















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#Render
########################################
class CATEGORYBUTTON_959029(bpy.types.Operator):#Render
    """Render"""
    bl_idname = "object.categorybutton_959029"
    bl_label = "Render"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("Render",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_CAMERA",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#############################################################################################################################
#uiitem("レンダ設定")
#############################################################################################################################

#########################################
##カメラ外を非レンダ化
#########################################
#class MYOBJECT_881058(bpy.types.Operator):#カメラ外を非レンダ化
#    """カメラ外を非レンダ化*テスト"""
#    bl_idname = "object.myobject_881058"
#    bl_label = "カメラ外を非レンダ化*テスト"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        for obj in get_selected_list():
#            if not checkLocationisinCameraView(obj.matrix_world * obj.matrix_basis.inverted() * obj.location):
#                if "hide_render_basestate" not in obj:
#                    obj["hide_render_basestate"] = obj.hide_render
#                obj.hide_render = True
#                obj.hide = True


#        return {'FINISHED'}
#########################################

############################################################################################################################
uiitem("OpenGLレンダ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

def active_gpbrush():
    return bpy.context.scene.tool_settings.gpencil_brushes.active

def gpline_change(gplayer, value):
    #linewidth = bpy.context.scene.tool_settings.gpencil_brushes.active.line_width
    f = bpy.context.scene.frame_current

    if len(gplayer.frames) == 0:
        return

    for frame in gplayer.frames:
        if frame.frame_number == f:
            for stroke in frame.strokes:
                if hasattr(stroke,"line_width"):
                    stroke.line_width = value

    #gplayer.line_change = value
    #bpy.ops.gpencil.stroke_apply_thickness()
    #→これは結局stroke.line_widthに値が反映されてる




########################################
#GLレンダ（ビューポート）
########################################
class MYOBJECT_979047(bpy.types.Operator):#GLレンダ（ビューポート）
    """GLレンダ（ビューポート）"""
    bl_idname = "object.myobject_979047"
    bl_label = "GLレンダ（ビューポート）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        #bpy.context.space_data.fx_settings.use_ssao = False

        #カメラビュー
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        #参考：bpy.data.screens[0].areas[1].spaces[0].local_view

        #グリペンレイヤ
        gplayers = bpy.context.scene.grease_pencil.layers
        if "下書き" in gplayers:
            bpy.context.scene.grease_pencil.layers["下書き"].hide = True

        #gpcurrent = bpy.context.scene.grease_pencil.layers.active

        ##線幅
        for gplayer in gplayers:
            if not gplayer.hide:
                gpline_change(gplayer, 20)

        #for gplayer in gplayers:
        #    gplayer.line_change = 10

        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        renderdir = dir + os.sep + "render" + os.sep 
        renderpath = renderdir + selfname + "_layerAll_OpenGL.png"
        bpy.context.scene.render.filepath = renderpath

        bpy.ops.render.opengl("INVOKE_DEFAULT",view_context=True,write_still=True)
        #bpy.ops.render.opengl(view_context=False,write_still=True)

        #for gplayer in gplayers:
        #    if not gplayer.hide:
        #        bpy.context.scene.grease_pencil.layers.active = gplayer
        #        gpline_change(gplayer,-10)
        #        gpline_change(gplayer,-10)
        #        gpline_change(gplayer,-10)
        #        gpline_change(gplayer,-10)

        #for gplayer in gplayers:
        #    gplayer.line_change = -10

        #bpy.context.scene.grease_pencil.layers.active = gpcurrent

        return {'FINISHED'}
########################################



########################################
#GLレンダMASK
########################################
class MYOBJECT_171760(bpy.types.Operator):#GLレンダMASK
    """GLレンダMASK用"""
    bl_idname = "object.myobject_171760"
    bl_label = "GLレンダMASK"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'MATERIAL'

        #カメラビュー
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"

        #グリペンレイヤオフ
        gplayers = bpy.context.scene.grease_pencil.layers
        for gpl in gplayers:
            gpl.hide = True
        #if "下書き" in gplayers:
        #    bpy.context.scene.grease_pencil.layers["下書き"].hide = True

        #背景非表示
        for i in range(10,15):
            bpy.context.scene.layers[i] = False


        ##線幅
        for gplayer in gplayers:
            if not gplayer.hide:
                gpline_change(gplayer, 20)

        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        renderdir = dir + os.sep + "render" + os.sep 
        renderpath = renderdir + selfname + "_layerAll_OpenGLforMASK.png"
        bpy.context.scene.render.filepath = renderpath

        bpy.ops.render.opengl("INVOKE_DEFAULT",view_context=True,write_still=True)
        
        return {'FINISHED'}
########################################








########################################
#線幅を戻す
########################################
class MYOBJECT_347064(bpy.types.Operator):#線幅を戻す
    """線幅を戻す"""
    bl_idname = "object.myobject_347064"
    bl_label = "線幅を戻す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #線幅戻す
        gplayers = bpy.context.scene.grease_pencil.layers
        for gplayer in gplayers:
            if not gplayer.hide:
                gpline_change(gplayer, active_gpbrush().line_width)
        
        return {'FINISHED'}
########################################













#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


def construct_comiccomposit():
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_specular = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_shadow = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_combined = True
    bpy.context.scene.render.use_textures = True
    bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
    bpy.context.scene.render.edge_threshold = 255

    #レンダーレイヤー設定
    rl = bpy.context.scene.render.layers[0]
    rl.use_pass_color = True
    rl.use_pass_specular = True
    rl.use_pass_diffuse = True
    rl.use_pass_shadow = True
    rl.use_edge_enhance = False


    ntree = NodetreeUtils(bpy.context.scene)
    ntree.activate()
    ntree.cleartree()

    nRenderLayers = NodeUtils(ntree.add("CompositorNodeRLayers","RenderLayers"))
    nCompositeOutput = NodeUtils(ntree.add("CompositorNodeComposite", "Composite"))
    ngComic = append_nodetree("漫画コンポジットモノクロ")
    ngiComic = NodeUtils(ntree.group_instance(ngComic))


    #接続
    ntree.link(nRenderLayers.output("Color"), ngiComic.input("Color"))
    ntree.link(nRenderLayers.output("Image"), ngiComic.input("Diffuse"))
    ntree.link(nRenderLayers.output("Specular"), ngiComic.input("Specular"))
    #ntree.link(nRenderLayers.output("Shadow"), ngiComic.input("Shadow"))

    ntree.link(ngiComic.output("Image"), nCompositeOutput.input("Image"))

    ntree.link(nRenderLayers.output("Alpha"), nCompositeOutput.input("Alpha"))
        

############################################################################################################################
uiitem("漫画コンポジット")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#コンポジット構築のみ
########################################
class MYOBJECT_505834(bpy.types.Operator):#コンポジット構築のみ
    """コンポジット構築のみ"""
    bl_idname = "object.myobject_505834"
    bl_label = "コンポジット構築のみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        construct_comiccomposit()
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#プレビュー
########################################
class MYOBJECT_258524(bpy.types.Operator):#プレビュー
    """ビューポートでプレビュー"""
    bl_idname = "object.myobject_258524"
    bl_label = "プレビュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        construct_comiccomposit()
        bpy.context.scene.render.resolution_percentage = 25
        #bpy.ops.wm.save_mainfile()
        bpy.ops.render.render("INVOKE_DEFAULT",use_viewport=True)
        #exec_externalutils("fullrender.py")
        
        return {'FINISHED'}
########################################

#########################################
##フルレンダ
#########################################
#class MYOBJECT_185402(bpy.types.Operator):#フルレンダ
#    """バックグラウンドでフルレンダ"""
#    bl_idname = "object.myobject_185402"
#    bl_label = "フルレンダ"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        construct_comiccomposit()
#        bpy.context.scene.render.resolution_percentage = 100
#        bpy.ops.wm.save_mainfile()
#        exec_externalutils("fullrender.py")

#        #bpy.ops.render.render("INVOKE_DEFAULT",use_viewport=True)

#        return {'FINISHED'}
#########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("RenderGroup")
############################################################################################################################









"""
レンダグループ
・割当
    単一のレンダグループに割り当てる
    RenderGroup.NNN
    既に割り当てられてる場合は一旦解除する
    グループ解除して毎回新規グループ割当、でいいのでは？→勝手にナンバリングされる

    bpy.ops.group.create(name="RenderGroup")

    グループ解除はグループのほうから辿ってリンク解除していったほうがいいかも


    ----------------------------------------
    カスタムプロパティにレンダグループを保持させる。
    obj["RenderGroup"] = グループ名
    アンリンク時にグループ名を除去する。
    プロパティないときのためにtryでやったほうがいいかも。


"""

def unlink_RenderGroup(self,objects):
    if objects == None:
        return

    if type(objects) == "list":
        if len(objects) == 0:
            return

    if type(objects) == bpy.types.Object:
        tmp = []
        tmp.append(objects)
        objects = tmp

    for group in bpy.data.groups:
        self.report({"INFO"},str(group))

        if "RenderGroup" not in group.name:
            continue

        #RenderGroupだった
        #該当オブジェクトを全てアンリンクする
        for obj in objects:
            if obj.name in group.objects:
                group.objects.unlink(obj)

                try:
                    obj["RenderGroup"] = ""
                    pass
                except :
                    pass
    pass
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#RenderGroup
########################################
class MYOBJECT_716795(bpy.types.Operator):#RenderGroup
    """RenderGroup"""
    bl_idname = "object.myobject_716795"
    bl_label = "RenderGroup"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #カメラ・ランプを除外
        for obj in bpy.context.selected_objects:
            if obj.type == "CAMERA" or obj.type == "LAMP":
                obj.select = False

        objects = get_selected_list()
        unlink_RenderGroup(self,objects)
        bpy.ops.group.create(name="RenderGroup")

        #カスタムプロパティに保持
        groupname = ""
        for group in bpy.data.groups:
            if "RenderGroup" in group.name:
                if objects[0].name in group.objects:
                    groupname = group.name
                    break

        for obj in objects:
            obj["RenderGroup"] = groupname
        return {'FINISHED'}
########################################

########################################
#親子・連続指定用
########################################
class MYOBJECT_985143(bpy.types.Operator):#親子・連続指定用
    """親子・連続指定用"""
    bl_idname = "object.myobject_985143"
    bl_label = "親子・連続指定用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_24259()
        bpy.ops.object.myobject_716795()
        #隠す
        for obj in bpy.context.selected_objects:
            obj.hide = True

        deselect()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#プロパティから再構成
########################################
class MYOBJECT_880927(bpy.types.Operator):#プロパティから再構成
    """プロパティから再構成"""
    bl_idname = "object.myobject_880927"
    bl_label = "プロパティから再構成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        targets = get_selected_list()
        #親子選択
        bpy.ops.object.myobject_24259()
        for obj in targets:
            obj.select = True
        targets = get_selected_list()


        groupnames = set()
        for target in targets:
            try:
                groupnames.add(target["RenderGroup"])
                pass
            except  :
                pass

        for groupname in groupnames:
            deselect

            for obj in targets:
                try:
                    if obj["RenderGroup"] == groupname:
                        obj.select = True
                    pass
                except  :
                    pass
            #レンダグループ
            bpy.ops.object.myobject_716795()
            pass

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#クリア
########################################
class MYOBJECT_275643(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "object.myobject_275643"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        objects = get_selected_list()
        unlink_RenderGroup(self,objects)
        
        return {'FINISHED'}
########################################


########################################
#割り当て済みを隠す
########################################
class MYOBJECT_824105(bpy.types.Operator):#割り当て済みを隠す
    """割り当て済みを隠す"""
    bl_idname = "object.myobject_824105"
    bl_label = "割り当て済みを隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_OFF",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        for group in bpy.data.groups:
            if "RenderGroup" in group.name:
                for obj in group.objects:
                    obj.hide = True

        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#レイヤー
########################################
class CATEGORYBUTTON_845862(bpy.types.Operator):#レイヤー
    """レイヤー"""
    bl_idname = "object.categorybutton_845862"
    bl_label = "レイヤー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("レイヤー",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


"""
    リンクのパスに該当文字列があったら、特定レイヤーに割り振る、というかんじ。
    5-9
    15-19
    は自由レイヤー領域ということで無視。
    ☆range（開始値,終了値+1）
LayerConstitution[""] = range(,)



    レイヤー順、
    エフェクト
    プロップ
    キャラ
    背景
    にほんとはしたい？
    
    レイヤー重ね順から考えてほんとは後ろからつめていきたい。
    後ろづめ機能いる。

    エフェクト、プロップ、キャラと同じレイヤーにしたい場合とわけたい場合
    背景、わけたい場合

    どうするか

    あーあとカテゴリ外、邪魔だからどけてる可能性もあるのか…


    選択物オートレイヤー！
    と、カテゴリで選択
"""

class LayerCategory():
    LayerConstitution = {}
    #LayerConstitution["エフェクト"] = range(0,5)
    #LayerConstitution["プロップ"] = range(0,5)
    #LayerConstitution["キャラ"] = range(0,5)
    #LayerConstitution["背景"] = range(10,15)
    LayerConstitution["エフェクト"] = [0]
    LayerConstitution["プロップ"] = [0]
    LayerConstitution["キャラ"] = [0]
    LayerConstitution["背景"] = range(10,15)

    LayerConstitution["非表示エフェクト"] = [15]
    LayerConstitution["非表示プロップ"] = [16]
    LayerConstitution["非表示キャラ"] = [17]
    LayerConstitution["非表示背景"] = [18]

    CategoryObjects = {}

    def __init__(self):
        for key in self.LayerConstitution.keys():
            self.CategoryObjects[key] = self.getObjects(key)
        return

    def isinCategory(self,obj, category):
        linkedpath = checkLink(obj)
        if linkedpath is None:
            return False
        if category in linkedpath:
            return True
        return False

    def getObjects(self,category):
        result = []
        for obj in bpy.data.objects:
            if self.isinCategory(obj, category):
                result.append(obj)
        return result

    def layerstoindexlist(self,layers):
        indexlist = []
        for i in range(0,20):
            if layers[i]:
                indexlist.append(i)
        return indexlist

    def layersfromIndexList(self,indexlist):
        layers = [False for i in range(20)]
        for i in indexlist:
            layers[i] = True
        return layers

    #リスト内に、対象レンジ内のアイテムがあるかチェック
    def checklistHasinrangeItem(self,list,targetrange):
        for item in list:
            if item in targetrange:
                return True
        return False

    def isValidLayer(self,obj,category,blendops=None):
        #自由レイヤー以外のカテゴリ外レイヤーにいたらFalse。
        #カテゴリレイヤーにいなくてもFalse

        objlayers = self.layerstoindexlist(obj.layers)

        incategory = False
        for i in objlayers:
            if i in self.LayerConstitution[category]:
                incategory = True
                break;

        outofcategory = False
        #全レンジから適合カテゴリを除外したのがアウトレンジ
        outrange = []
        outrange.extend(range(0,5))
        outrange.extend(range(10,15))
        for i in self.LayerConstitution[category]:
            outrange.remove(i)

        for i in outrange:
            if i in objlayers:
                outofcategory = True

        if blendops is not None:
            if not incategory:
                blendops.report({"ERROR"},"カテゴリ範囲内に不在："+category)
                blendops.report({"ERROR"},obj.name)
            elif outrange:
                blendops.report({"WARNING"},"カテゴリ範囲外に発見："+category)
                blendops.report({"WARNING"},obj.name)

        return (incategory, outrange)

    def checkall(self, blendops):
        #チェックを走らせる
        for key in self.LayerConstitution.keys():
            for obj in self.CategoryObjects[key]:
                self.isValidLayer(obj, key, blendops)
    
    #オブジェクトが所属してるカテゴリを返す
    def get_category(self,obj):
        if checkLink(obj) == None:
            return None
        for key in self.LayerConstitution.keys():
            if self.isinCategory(obj,key):
                return key
        return None

    #オブジェクトをそのカテゴリに送る
    #レイヤーオフセットは引数で指定できるように、一応しておく
    def tocategory(self,obj,category,offset=0):
        objlayers = self.layerstoindexlist(obj.layers)

        if self.checklistHasinrangeItem(objlayers,self.LayerConstitution[category]):
            #既にレンジ内にレイヤーがある。のでキャンセル
            #と思ったけど、レンジ外は非表示にしとかないとめんどくさい
            for i in range(20):
                if i not in self.LayerConstitution[category]:
                    obj.layers[i] = False
            return

        index = self.LayerConstitution[category][0]

        if index+offset in self.LayerConstitution[category]:
            index = index+offset

        indexlist = [index]
        obj.layers = self.layersfromIndexList(indexlist)

    #レイヤー位置がマズいものを直す
    #選択物をいきなりカテゴライズしてしまえばそもそもカテゴリ内チェックする必要なかったのでは？
    #def correct(self,obj,category,blendops=None):
    #    incategory, outrange = self.isValidLayer(obj, category, blendops)
    #    if not incategory:
    #        self.tocategory(obj,category)
    #        pass
    #    pass

    def hideemptylayer(self):
        found = [False for i in range(20)]
        for obj in bpy.context.visible_objects:
            if obj.is_library_indirect:
                continue
            for i in range(20):
                if obj.layers[i]:
                    found[i] = True
        bpy.context.scene.layers = found

        pass

    def correct(self,targetlist):
        for obj in targetlist:
            for key in self.LayerConstitution.keys():
                if obj in self.CategoryObjects[key]:
                    self.tocategory(obj,key)

        #メッシュオブジェクト用。
        #特定文字列を検索してそれも指定カテゴリに送る
        meshlist = find_list("result", targetlist)
        for obj in meshlist:
            if obj.type == "MESH":
                self.tocategory(obj, "キャラ")
        
        self.hideemptylayer()



########################################
#構成チェック
########################################
class MYOBJECT_822286(bpy.types.Operator):#構成チェック
    """構成チェック"""
    bl_idname = "object.myobject_822286"
    bl_label = "構成チェック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        lc = LayerCategory()
        lc.checkall(self)
        
        return {'FINISHED'}
########################################


########################################
#カテゴリに移動（選択物）
########################################
class MYOBJECT_630218(bpy.types.Operator):#カテゴリに移動（選択物）
    """カテゴリに移動（選択物）"""
    bl_idname = "object.myobject_630218"
    bl_label = "カテゴリに移動（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        lc = LayerCategory()
        lc.correct(selection)
        
        return {'FINISHED'}
########################################



########################################
#カテゴリに移動（表示全部）
########################################
class MYOBJECT_113350(bpy.types.Operator):#カテゴリに移動（表示全部）
    """カテゴリに移動（表示全部）"""
    bl_idname = "object.myobject_113350"
    bl_label = "カテゴリに移動（表示全部）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        lc = LayerCategory()
        lc.correct(bpy.context.visible_objects)
        
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#キャラ手前
########################################
class MYOBJECT_748000(bpy.types.Operator):#キャラ手前
    """キャラ手前"""
    bl_idname = "object.myobject_748000"
    bl_label = "手前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(0)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class MYOBJECT_547202(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "object.myobject_547202"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(1)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class MYOBJECT_892615(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "object.myobject_892615"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(2)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class MYOBJECT_60203(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "object.myobject_60203"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(3)
        
        return {'FINISHED'}
########################################

########################################
#キャラ奥
########################################
class MYOBJECT_951016(bpy.types.Operator):#キャラ奥
    """キャラ奥"""
    bl_idname = "object.myobject_951016"
    bl_label = "奥"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(4)
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#背景手前
########################################
class MYOBJECT_977845(bpy.types.Operator):#背景手前
    """背景手前"""
    bl_idname = "object.myobject_977845"
    bl_label = "手前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(10)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class MYOBJECT_782024(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "object.myobject_782024"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(11)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class MYOBJECT_288468(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "object.myobject_288468"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(12)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class MYOBJECT_546419(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "object.myobject_546419"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(13)
        
        return {'FINISHED'}
########################################

########################################
#背景奥
########################################
class MYOBJECT_844075(bpy.types.Operator):#背景奥
    """背景奥"""
    bl_idname = "object.myobject_844075"
    bl_label = "奥"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(14)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ストック
########################################
class MYOBJECT_165238(bpy.types.Operator):#ストック
    """ストック"""
    bl_idname = "object.myobject_165238"
    bl_label = "ストック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(15)
        bpy.context.scene.layers[15] = False

        
        return {'FINISHED'}
########################################

########################################
#2
########################################
class MYOBJECT_377137(bpy.types.Operator):#2
    """2"""
    bl_idname = "object.myobject_377137"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(16)
        bpy.context.scene.layers[16] = False
        
        return {'FINISHED'}
########################################

########################################
#3
########################################
class MYOBJECT_21253(bpy.types.Operator):#3
    """3"""
    bl_idname = "object.myobject_21253"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(17)
        bpy.context.scene.layers[17] = False

        return {'FINISHED'}
########################################

########################################
#4
########################################
class MYOBJECT_870290(bpy.types.Operator):#4
    """4"""
    bl_idname = "object.myobject_870290"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(18)
        bpy.context.scene.layers[18] = False

        return {'FINISHED'}
########################################

########################################
#5
########################################
class MYOBJECT_255842(bpy.types.Operator):#5
    """5"""
    bl_idname = "object.myobject_255842"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        setlayer(19)
        bpy.context.scene.layers[19] = False
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("背景に移動してそのレイヤーを表示")
############################################################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#1
########################################
class MYOBJECT_720458(bpy.types.Operator):#1
    """1"""
    bl_idname = "object.myobject_720458"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = 10
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False

        

        
        return {'FINISHED'}
########################################

########################################
#2
########################################
class MYOBJECT_756530(bpy.types.Operator):#2
    """2"""
    bl_idname = "object.myobject_756530"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = 11
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################

########################################
#3
########################################
class MYOBJECT_589552(bpy.types.Operator):#3
    """3"""
    bl_idname = "object.myobject_589552"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = 12
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        return {'FINISHED'}
########################################

########################################
#4
########################################
class MYOBJECT_352073(bpy.types.Operator):#4
    """4"""
    bl_idname = "object.myobject_352073"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = 13
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################

########################################
#5
########################################
class MYOBJECT_283776(bpy.types.Operator):#5
    """5"""
    bl_idname = "object.myobject_283776"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = 14
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("背景を別ファイルに分離")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#分離
########################################
class MYOBJECT_436578(bpy.types.Operator):#分離
    """分離"""
    bl_idname = "object.myobject_436578"
    bl_label = "分離"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        basepath = bpy.data.filepath
        baselayers = []
        for i in range(20):
            baselayers.append(bpy.context.scene.layers[i])

        if "bg.blend" in basepath:
            self.report({"WARNING"},"背景ファイルです。")
            return {"CANCELLED"}


        #オリジナル保存
        dir = os.path.dirname(basepath) + os.sep + "orig"
        if not os.path.exists(dir):
            os.mkdir(dir)
        name = os.path.splitext(os.path.basename(basepath))[0]
        blendpath = dir + os.sep + name + ".blend"
        bpy.ops.wm.save_as_mainfile(filepath=blendpath,copy=True)





        #背景用ファイル
        dir = os.path.dirname(basepath)
        name = os.path.splitext(os.path.basename(basepath))[0]
        blendpath = dir + os.sep + name + "bg.blend"

        if os.path.exists(blendpath):
            self.report({"WARNING"},"既に分離されたファイルがあります。")
            return {"CANCELLED"}

        #背景だけ表示
        layers = [False for i in range(20)]
        for i in range(10,15):
            layers[i] = True

        bpy.context.scene.layers = layers
        bpy.ops.wm.save_as_mainfile(filepath=blendpath,copy=True)



        #背景消してオリジナル保存
        bpy.ops.object.select_all(action='SELECT')
        for obj in bpy.data.objects:
            if obj.type == "CAMERA":
                obj.select = False
        bpy.ops.object.delete(use_global=False)

        bpy.context.scene.layers = baselayers


        bpy.ops.wm.save_as_mainfile(filepath=basepath)


        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#本体を開く
########################################
class MYOBJECT_857359(bpy.types.Operator):#本体を開く
    """本体を開く"""
    bl_idname = "object.myobject_857359"
    bl_label = "本体を開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        basepath = bpy.data.filepath
        if "bg.blend" not in basepath:
            self.report({"WARNING"},"本体ファイルです。")
            return {"CANCELLED"}

        blendpath = basepath.replace("bg.blend", ".blend")
        if not os.path.exists(blendpath):
            self.report({"WARNING"},"ファイルが存在しません。")
            return {"CANCELLED"}

        subprocess.Popen("EXPLORER " + blendpath)
        
        return {'FINISHED'}
########################################







########################################
#背景を開く
########################################
class MYOBJECT_348653(bpy.types.Operator):#背景を開く
    """背景を開く"""
    bl_idname = "object.myobject_348653"
    bl_label = "背景を開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        basepath = bpy.data.filepath
        if "bg.blend" in basepath:
            self.report({"WARNING"},"背景ファイルです。")
            return {"CANCELLED"}

        blendpath = basepath.replace(".blend", "bg.blend")
        if not os.path.exists(blendpath):
            self.report({"WARNING"},"ファイルが存在しません。")
            return {"CANCELLED"}

        subprocess.Popen("EXPLORER " + blendpath)
        
        
        return {'FINISHED'}
########################################


















############################################################################################################################
#クイック中心
############################################################################################################################
########################################
#中点
########################################
class MYOBJECT_995874(bpy.types.Operator):#中点
    """変形中心を中点"""
    bl_idname = "object.myobject_995874"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="none")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        #グリッドスナップ
        bpy.ops.object.myobject_357169()
        
        return {'FINISHED'}
########################################


########################################
#頂点に
########################################
class MYOBJECT_59910(bpy.types.Operator):#頂点に
    """3Dカーソルを設置して変形の中心に"""
    bl_idname = "object.myobject_59910"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="none")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #コンテキストに応じてカーソルを設置
        obj = bpy.context.scene.objects.active

#        if obj.type == "MESH":
#
#
#        if obj.data.is_editmode:
#            for vert in obj.data.vertices:
#                if vert.select:
#                    bpy.ops.view3d.snap_cursor_to_selected()
#                    break;
        ##スナップしないほうが便利
        #bpy.ops.view3d.snap_cursor_to_selected()
        bpy.context.space_data.pivot_point = 'CURSOR'
        
        #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
################################################################################
#UIカテゴリ
########################################
#素体
########################################
class CATEGORYBUTTON_861028(bpy.types.Operator):#素体
    """素体"""
    bl_idname = "object.categorybutton_861028"
    bl_label = "素体"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("素体",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





############################################################################################################################
uiitem("素体")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#素体追加
########################################
class MYOBJECT_707900(bpy.types.Operator):#素体追加
    """素体追加"""
    bl_idname = "object.myobject_707900"
    bl_label = "追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        import fjw_AssetManager
        fjw_AssetManager.mode = "append"
        fjw_AssetManager.dirtoopen = assetdir + "\\素体\\"
        bpy.ops.file.amfilebrowser("INVOKE_DEFAULT")
        
        

        return {'FINISHED'}
########################################


#置換用
class SPIFileBrowser(bpy.types.Operator):
    """Test File Browser"""
    bl_idname = "file.spifilerowser"
    bl_label = "アセット読み込み"

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


    @classmethod
    def poll(cls, context):
        return True



    #対象名群
    targetnames = []


    #dest
    dest = {}
    dest_objects = []
    dest_geo = None
    def setup_dest_objects(self):
        self.dest_objects = []

        #対象オブジェクトをソースリストに入れる。
        self.dest_geo = bpy.context.scene.objects.active
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        self.dest_objects.append(self.dest_geo)
        for obj in bpy.context.selected_objects:
            self.dest_objects.append(obj)

        #登録先の初期化
        self.dest = {}

        #オブジェクトの登録処理
        for targetname in self.targetnames:
            self.append_dest(targetname)


    def append_dest(self, name):
        for obj in self.dest_objects:
            if name in obj.name:
                self.dest[name] = obj
                break

        return

    #src
    src = {}
    src_objects = []

    #現在選択されているオブジェクトをそのまま処理するので注意
    def setup_src_objects(self):
        self.src_objects = []

        for obj in bpy.context.selected_objects:
            self.src_objects.append(obj)

        self.src = {}

        #オブジェクトの登録処理
        for targetname in self.targetnames:
            self.append_src(targetname)

    def append_src(self, name):
        for obj in self.src_objects:
            if name in obj.name:
                self.src[name] = obj
                break

    #位置・回転・ポーズの転送
    def transfer(self, targetname):
        if targetname not in self.src or targetname not in self.dest:
            return

        sobj = self.src[targetname]
        dobj = self.dest[targetname]

        if sobj is None or dobj is None:
            return

        sobj.location = dobj.location
        sobj.rotation_euler = dobj.rotation_euler

        self.report({"INFO"},"sobj:"+sobj.name+" dobj:"+dobj.name)

        if sobj.type == "ARMATURE" and dobj.type == "ARMATURE":
            #ポーズのコピー
            #ポーズのコピー
            mode("OBJECT")
            activate(dobj)
            mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.copy()

            mode("OBJECT")
            activate(sobj)
            mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.paste(flipped=False)


    def transfer_all(self):
        for targetname in self.targetnames:
            self.transfer(targetname)


    def get_geo(self):
        geo = None

        targets = []
        targets.append("Geometry")
        targets.append("geometry")
        targets.append("ジオメトリ")

        for target in targets:
            if target in self.src:
                geo = self.src[target]
                break

        #for obj in self.src_objects:
        #    if( "Geometry" in obj.name or
        #        "geometry"in obj.name or
        #        "ジオメトリ" in obj.name

        #        ):
        #        geo = obj
        #        break


        return geo

    def execute(self, context):
        self.targetnames = []
        self.targetnames.append("geo")
        self.targetnames.append("ジオメトリ")
        self.targetnames.append("素体アーマチュア")
        self.targetnames.append("ArmatureController")
        self.targetnames.append("手コントローラ右")
        self.targetnames.append("手コントローラ左")
        self.targetnames.append("右手")
        self.targetnames.append("左手")
        self.targetnames.append("右足")
        self.targetnames.append("左足")

        self.setup_dest_objects()


        for obj in self.dest:
            if obj == None:
                self.report({"INFO"},"不完全なモデルなので結果が異常な可能性があります。:src")

        deselect()

        #アペンドする
        for file in self.files:
            with bpy.data.libraries.load(self.directory + "\\" + file.name, link=False, relative=True) as (data_from, data_to):
                data_to.objects = data_from.objects
                print(data_to.objects)

            for obj in data_to.objects:
                if obj.type == "CAMERA":
                    continue
                if obj.type == "LAMP":
                    continue
                if obj.parent != None:
                    if obj.parent.type == "CAMERA":
                        continue
                bpy.context.scene.objects.link(obj)
                obj.select = True

        self.report({"INFO"},self.filepath)
        
        #アペンドしたオブジェクトをソースリストに入れる。
        self.setup_src_objects()

        for obj in self.src:
            if obj == None:
                self.report({"INFO"},"不完全なモデルなので結果が異常な可能性があります。:src")


        deselect()


        #アペンド終わったので適用していく。
        self.transfer_all()

        deselect()


        #destの削除
        for obj in self.dest_objects:
            obj.select = True
            bpy.context.scene.objects.active = obj
        bpy.ops.object.delete(use_global=False)

        #bpy.context.scene.objects.active = self.src["geo"]
        #self.src["geo"].select = True
        geo = self.get_geo()
        try:
            activate(geo)
            geo.select = True
            pass
        except:
            pass

        #無操作で更新
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

        ##デバッグ用レポート
        #self.report({"INFO"},"src")
        #for obj in self.src_objects:
        #    if obj == None:
        #        continue
        #    self.report({"INFO"},obj.name)
        #self.report({"INFO"},"dest")
        #for obj in self.dest_objects:
        #    if obj == None:
        #        continue
        #    self.report({"INFO"},obj.name)

        #ヘアトラッカ設定
        bpy.ops.object.myobject_815238()

        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = assetdir + "\素体"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

bpy.utils.register_class(SPIFileBrowser)

########################################
#素体置換
########################################
class MYOBJECT_157507(bpy.types.Operator):#スワップ削除
    """素体置換"""
    bl_idname = "object.myobject_157507"
    bl_label = "素体置換"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        geo = None
        for obj in bpy.context.selected_objects:
            if "ジオメトリ" in obj.name:
                geo = obj
                break

        #選択解除
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = geo

        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        bpy.ops.file.spifilerowser("INVOKE_DEFAULT")

        return {'FINISHED'}
########################################









class LPIFileBrowser(bpy.types.Operator):
    """Test File Browser"""
    bl_idname = "file.lpifilerowser"
    bl_label = "アセット読み込み"

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        """
          ファイル名+ArmatureControllerのアクションをアペンドして、
          指定したジオメトリ内のArmatureControllerのアクションに設定、
          全ボーンを選択してポーズを適用
        """
        geo = bpy.context.scene.objects.active
        
        
        for obj in bpy.data.objects:
            obj.select = False
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        
        amcont = None
        for obj in bpy.context.selected_objects:
            if "ArmatureController" in obj.name:
                amcont = obj
                break
        
        
        #アクションをアペンドする
        
        actname = ""
        fname = ""
        for file in self.files:
            self.report({"INFO"},str(file))
            self.report({"INFO"},file.name)
            _directory = self.directory + os.sep + file.name + os.sep + "Action" + os.sep
            fname = file.name
            actname = file.name.replace(".blend", "") + "ArmatureController"
            _filename = actname
            _filepath = _directory + _filename
            self.report({"INFO"},_directory)
            self.report({"INFO"},_filename)
            self.report({"INFO"},_filepath)
            bpy.ops.wm.append(filepath=_filepath, filename=_filename, directory=_directory)

        self.report({"INFO"},self.filepath)
        
        #ポーズを適用する
        bpy.context.scene.objects.active = amcont
        amcont.pose_library = bpy.data.actions[actname]
        
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.poselib.apply_pose(pose_index=0)
        bpy.ops.pose.select_all(action='DESELECT')
        
        #もしテンポラリフォルダからの利用だったら、通常階層に移動する。
        if "テンポラリ" in self.directory:
            shutil.move(self.directory + fname,assetdir + r"\素体\ポージングプール" + os.sep + fname)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = assetdir + r"\素体\ポージングプール"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

bpy.utils.register_class(LPIFileBrowser)

########################################
#Libポーズ適用
########################################
class MYOBJECT_940955(bpy.types.Operator):#Libポーズ適用
    """Libポーズ適用"""
    bl_idname = "object.myobject_940955"
    bl_label = "Libポーズ適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        geo = None
        for obj in bpy.context.selected_objects:
            if "ジオメトリ" in obj.name:
                geo = obj
                break

        #選択解除
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = geo

        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        bpy.ops.file.lpifilerowser("INVOKE_DEFAULT")
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#素体抽出
########################################
class MYOBJECT_319683(bpy.types.Operator):#素体抽出
    """素体抽出"""
    bl_idname = "object.myobject_319683"
    bl_label = "ポーズ抽出展開"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        returnpath = bpy.data.filepath
        
        #現状保存→は、しないほうがいい。
#        bpy.ops.wm.save_mainfile()
        
        geo = bpy.context.scene.objects.active
        
        dir = assetdir + r"\素体\ポージングプール\テンポラリ"
        extractdir = dir
        
        dt = datetime.datetime.now()
        dtstr = dt.strftime("%Y%m%d%H%M%S")
        
        exstractpath = extractdir + os.sep + dtstr + ".blend"
        if not os.path.exists(extractdir):
            os.mkdir(extractdir)
        
        
        #選択解除
        for obj in bpy.data.objects:
           obj.select = False
        
        
        #素体ジオメトリ以下を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        geo.select = True
        

        #ポーズライブラリを登録
        for obj in bpy.context.selected_objects:
            if "ArmatureController" in obj.name:
                bpy.context.scene.objects.active = obj
                
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.poselib.new()
                #ポーズライブラリ名を、日時＋ArmatureControllerに。
                obj.pose_library.name = dtstr + "ArmatureController"
                #ポーズ登録
                bpy.ops.poselib.pose_add(frame=1)
                
                break

        bpy.context.scene.objects.active = geo


        #オブジェクトリストに入れる
        objlist = []
        for obj in bpy.context.selected_objects:
            objlist.append(obj)
        
        
        
        #選択解除
        for obj in bpy.data.objects:
           obj.select = False
        
        #リストにないものを削除
        for obj in bpy.data.objects:
            if obj not in objlist:
                obj.select = True
        bpy.ops.object.delete(use_global=False)
        
        
        
        #表示を整える
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'SOLID'
        
        #ポーズに出力
        bpy.ops.wm.save_mainfile(filepath=exstractpath)
        #開き直す
        bpy.ops.wm.open_mainfile(filepath=returnpath)
        
        
        
        
        
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ヘアトラッカ設定
########################################
class MYOBJECT_815238(bpy.types.Operator):#ヘアトラッカ設定
    """ヘアトラッカ設定"""
    bl_idname = "object.myobject_815238"
    bl_label = "ヘアトラッカ設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                for bone in obj.pose.bones:
                    if "HairTrackTarget" in bone.name:
                        for constraint in bone.constraints:
                            if constraint.type == "COPY_LOCATION":
                                constraint.target = bpy.context.scene.camera

        return {'FINISHED'}
########################################


########################################
#カメラ目線
########################################
class MYOBJECT_68972(bpy.types.Operator):#カメラ目線
    """カメラ目線"""
    bl_idname = "object.myobject_68972"
    bl_label = "カメラ目線"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #ヘアトラッカーがカメラと同じ位置なのを利用　ってあー3Dカーソルでもよかった？
        obj = active()
        if obj.type == "ARMATURE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            for bone in obj.pose.bones:
                if "EyeTarget" in bone.name:
                    obj.data.bones.active = obj.data.bones[bone.name]
                    cpyloc = None
                    for constraint in bone.constraints:
                        if constraint.type == "COPY_LOCATION":
                            cpyloc = constraint
                    if cpyloc == None:
                        bpy.ops.pose.constraint_add(type='COPY_LOCATION')
                        for constraint in bone.constraints:
                            if constraint.type == "COPY_LOCATION":
                                cpyloc = constraint
                    cpyloc.target = bpy.context.scene.camera
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#ランプ
########################################
class CATEGORYBUTTON_14843(bpy.types.Operator):#ランプ
    """ランプ"""
    bl_idname = "object.categorybutton_14843"
    bl_label = "ランプ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ランプ",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LAMP",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#SUN設置
########################################
class MYOBJECT_96315(bpy.types.Operator):#SUN設置
    """SUN設置"""
    bl_idname = "object.myobject_96315"
    bl_label = "SUN設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LAMP_SUN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mode("OBJECT")
        bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False, location=(0, -6, 6), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.rotation_euler[0] = 0.691299
        obj.rotation_euler[1] = 0
        obj.rotation_euler[2] = 0.487015
        obj.data.shadow_method = 'RAY_SHADOW'

        
        
        return {'FINISHED'}
########################################


########################################
#屋内用ロングランプ
########################################
class MYOBJECT_831406(bpy.types.Operator):#屋内用ロングランプ
    """屋内用ロングランプ"""
    bl_idname = "object.myobject_831406"
    bl_label = "屋内用ロングランプ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mode("OBJECT")
        cursor = bpy.context.space_data.cursor_location
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=cursor, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.data.distance = 500
        obj.data.shadow_method = 'RAY_SHADOW'
        obj.data.use_specular = False

        
        return {'FINISHED'}
########################################

########################################
#カメラにポイント設置
########################################
class MYOBJECT_47170(bpy.types.Operator):#カメラにポイント設置
    """カメラにポイント設置"""
    bl_idname = "object.myobject_47170"
    bl_label = "カメラにポイント設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CAMERA_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mode("OBJECT")
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=bpy.context.scene.camera.location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ボトムバックライト
########################################
class MYOBJECT_770473(bpy.types.Operator):#ボトムバックライト
    """ボトムバックライト"""
    bl_idname = "object.myobject_770473"
    bl_label = "ボトムバックライト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = active()
        deselect()
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=target.location, layers=target.layers)
        lamp = active()
        activate(target)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        deselect()
        activate(lamp)
        bpy.ops.object.transforms_to_deltas(mode='LOC')
        lamp.location = (0,0.35,-0.35)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#環境照明
########################################
class MYOBJECT_648653(bpy.types.Operator):#環境照明
    """環境照明"""
    bl_idname = "object.myobject_648653"
    bl_label = "環境照明"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.world.light_settings.use_environment_light = True
        bpy.context.scene.world.light_settings.environment_energy = 0.1

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ライト正規化
########################################
class MYOBJECT_550719(bpy.types.Operator):#ライト正規化
    """ライト正規化　+アクティブオブジェクトのみドロップシャドウをつける"""
    bl_idname = "object.myobject_550719"
    bl_label = "ライト正規化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type != "LAMP":
                obj.select = False
        
        count = len(bpy.context.selected_objects)
        power = 1 / count
        for obj in bpy.context.selected_objects:
            obj.data.energy = power
            obj.data.shadow_method = 'NOSHADOW'

        bpy.context.scene.objects.active.data.shadow_method = 'RAY_SHADOW'


        return {'FINISHED'}
########################################


########################################
#ランプ全レイヤ化
########################################
class MYOBJECT_682004(bpy.types.Operator):#ランプ全レイヤ化
    """ランプ全レイヤ化"""
    bl_idname = "object.myobject_682004"
    bl_label = "ランプ全レイヤ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        layers = bpy.context.scene.layers
        for obj in bpy.data.objects:
            if obj.type == "LAMP":
                for l in range(0,19):
                    if layers[l]:
                        obj.layers[l] = True



        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#カスタムプロパティ
########################################
class CATEGORYBUTTON_712442(bpy.types.Operator):#カスタムプロパティ
    """カスタムプロパティ"""
    bl_idname = "object.categorybutton_712442"
    bl_label = "カスタムプロパティ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("カスタムプロパティ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################








#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#グループ情報を回収
########################################
class MYOBJECT_454471(bpy.types.Operator):#グループ情報を回収
    """グループ情報を回収"""
    bl_idname = "object.myobject_454471"
    bl_label = "グループ情報を回収"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #まず全部除去
        for obj in bpy.data.objects:
            if "Groups" in obj:
                del obj["Groups"]

        for group in bpy.data.groups:
            for obj in group.objects:
                prop = []
                #カスタムプロパティの確認
                if "Groups" in obj:
                    prop = obj["Groups"]
                prop.append(group.name)

                obj["Groups"] = prop

        return {'FINISHED'}
########################################

########################################
#グループ再生
########################################
class MYOBJECT_490616(bpy.types.Operator):#グループ再生
    """グループ再生"""
    bl_idname = "object.myobject_490616"
    bl_label = "グループ再生"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#Trackto:CAMERA
########################################
class MYOBJECT_372481(bpy.types.Operator):#Trackto:CAMERA
    """カスタムプロパティでTrackto:CAMERAをもつものに-Yのカメラトラックをつける"""
    bl_idname = "object.myobject_372481"
    bl_label = "Trackto:CAMERA"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            if "TrackTo" in obj:
                if obj["TrackTo"] == "CAMERA":
                    con = obj.constraints.new('DAMPED_TRACK')
                    con.track_axis = 'TRACK_NEGATIVE_Y'
                    con.target = bpy.context.scene.camera
                    pass

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



































############################################################################################################################
#スナップ
############################################################################################################################
########################################
#グリッドスナップ
########################################
class MYOBJECT_357169(bpy.types.Operator):#グリッドスナップ
    """グリッドスナップ"""
    bl_idname = "object.myobject_357169"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_GRID",mode="none")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'INCREMENT'
        bpy.context.scene.tool_settings.use_snap_grid_absolute = True
        
        return {'FINISHED'}
########################################

########################################
#面スナップ
########################################
class MYOBJECT_911158(bpy.types.Operator):#面スナップ
    """面スナップ"""
    bl_idname = "object.myobject_911158"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_FACE",mode="none")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'FACE'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        
        return {'FINISHED'}
########################################

########################################
#辺スナップ
########################################
class MYOBJECT_993743(bpy.types.Operator):#辺スナップ
    """辺スナップ"""
    bl_idname = "object.myobject_993743"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'EDGE'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        
        return {'FINISHED'}
########################################


########################################
#頂点スナップ
########################################
class MYOBJECT_33358(bpy.types.Operator):#頂点スナップ
    """頂点スナップ"""
    bl_idname = "object.myobject_33358"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_VERTEX",mode="none")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        return {'FINISHED'}
########################################










#http://blenderartists.org/forum/showthread.php?337445-Add-on-rRMB-Menu
def SetLocalTransformRotation(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'
    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        empty_exists, source_empty = GetSourceEmpty(context)
  
        if amount_selected > 1:
        
            # bpy.ops.object.transform_apply works on all the selected objects, but we
            # don't want that.
            #So deselect all first, and later reselect all again.
            original_selected_objects = bpy.context.selected_objects
            
            for i in bpy.context.selected_objects:
                i.select = False

            #Loop through all the objects which were previously selected
            for i in original_selected_objects:

                #Only set the object if the current object is not the active object at the
                #same time
                if context.active_object != i:
                
                    i.select = True
                    
                    i.rotation_mode = 'QUATERNION'
                    
                    #Store the start rotation of the selected object
                    rotation_before = i.matrix_world.to_quaternion()
                    
                    #Remove any parents.  If an Object is a child of another object, the
                    #Local Transform orientation settings will be messed up
                    RemoveParent(context, i)

                    #Align the rotation of the selected object with the rotation of the active
                    #object
                    bpy.ops.transform.transform(mode='ALIGN')
                    
                    #Store the rotation of the selected object after it has been rotated
                    rotation_after = i.matrix_world.to_quaternion()
                    
                    #Calculate the difference in rotation from before to after the rotation
                    rotation_difference = rotation_before.rotation_difference(rotation_after)

                    #Rotate the object the opposite way as done with the ALIGN function
                    i.rotation_quaternion = rotation_difference.inverted()
                    
                    
                    obj = context.active_object 
                    context.scene.objects.active = i
                    obj.select = False
                    
                   
                    #Align the local rotation of all the selected objects with the global
                    #world orientation
                    bpy.ops.object.transform_apply(rotation = True)
                    
                    obj.select = True
                    context.scene.objects.active = obj
                    
                    #Set the roation of the selected object to the rotation of the active
                    #object
                    i.rotation_quaternion = context.active_object.matrix_world.to_quaternion()
                    
                    #Deselect again
                    i.select = False
                    
            #restore selected objects
            for i in original_selected_objects:
                i.select = True        

        if(amount_selected == 1) and (empty_exists == True) and IsMatrixRightHanded(source_empty.matrix_world):
        
            context.active_object.rotation_mode = 'QUATERNION' 
            
            #Store the start rotation of the selected object
            rotation_before = context.active_object.matrix_world.to_quaternion()
            
            RemoveParent(context, context.active_object)
   
            obj = context.active_object        
            source_empty.select = True 
            context.scene.objects.active = source_empty
            
            #Align the rotation of the selected object with the rotation of the active
            #object
            bpy.ops.transform.transform(mode='ALIGN')
            
            #Set the Object to active
            source_empty.select = False
            context.scene.objects.active = obj 
            
            #Store the rotation of the selected object after it has been rotated
            rotation_after = context.active_object.matrix_world.to_quaternion()
            
            #Calculate the difference in rotation from before to after the rotation
            rotation_difference = rotation_before.rotation_difference(rotation_after)

            #Rotate the object the opposite way as done with the ALIGN function
            context.active_object.rotation_quaternion = rotation_difference.inverted()

            #Align the local rotation of the selected object with the global world
            #orientation
            bpy.ops.object.transform_apply(rotation = True)

            #Set the rotation of the selected object to the rotation of the active
            #object
            context.active_object.rotation_quaternion = source_empty.matrix_world.to_quaternion()


def GetSourceEmpty(context):

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        if amount_selected == 1:
    
            #Check whether the active object has an empty
            name = "Empty." + context.active_object.name
            try:
                obj = bpy.data.objects[name]
            except KeyError:
                return False, bpy.ops.object
            else:        
                return True, obj
                
        if amount_selected > 1:
            return True, context.active_object
            
    else:
        return False, bpy.ops.object

def IsMatrixRightHanded(mat):

    x = mat.col[0].to_3d()
    y = mat.col[1].to_3d()
    z = mat.col[2].to_3d()
    check_vector = x.cross(y)
    
    #If the coordinate system is right handed, the angle between z and
    #check_vector
    #should be 0, but we will use 0.1 to take rounding errors into account
    angle = z.angle(check_vector)
    
    if angle <= 0.1:
        return True
    else:
        errorStorage.SetError(ErrorMessage.not_right_handed)
        return False

def RemoveParent(context, obj):

    #Remove any parents.  If an Object is a child of another object, the
    #Local Transform orientation settings will be messed up if it is changed
    active_obj = context.active_object
    bpy.context.scene.objects.active = obj
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.context.scene.objects.active = active_obj


class RAlignOrientationToSelection(bpy.types.Operator):
    '''Tooltip'''
    bl_description = "Align object's orientation to the selected elements."
    bl_idname = "object.ralign_orientation_to_selection"
    bl_label = "Align Orientation To Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        obj_type = obj.type
        # return(obj and obj_type in {'MESH', 'CURVE', 'SURFACE', 'ARMATURE', 'FONT',
        # 'LATTICE'} and context.mode == 'OBJECT')
        return(obj and obj_type in {'MESH'})

    def execute(self, context):

        selected = context.selected_objects
        obj = context.active_object
        objects = bpy.data.objects
        storeCursorX = context.space_data.cursor_location.x
        storeCursorY = context.space_data.cursor_location.y
        storeCursorZ = context.space_data.cursor_location.z

        #Create custom orientation
        bpy.context.space_data.transform_orientation = 'NORMAL'
        bpy.ops.transform.create_orientation(name="rOrientation", use=True, overwrite=True)
        bpy.ops.view3d.snap_cursor_to_selected()

        #Exit to Object Mode
        bpy.ops.object.editmode_toggle()

        #1st Layer visibility
        first_layer_was_off = False

        if bpy.context.scene.layers[0] != True:

            first_layer_was_off = True
            bpy.context.scene.layers[0] = True


        #Add empty aligned to the orientation
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = context.selected_objects
        bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='rOrientation', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

        #Copy Rotation from empty
        obj.select = True
        SetLocalTransformRotation(context)

        #Delete empty
        bpy.ops.object.select_all(action='DESELECT')
        for obj in empty:
            obj.select = True
        bpy.ops.object.delete()

        #Restore state
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select = True
        bpy.context.scene.objects.active = obj
        context.space_data.cursor_location.x = storeCursorX
        context.space_data.cursor_location.y = storeCursorY
        context.space_data.cursor_location.z = storeCursorZ

        if first_layer_was_off:

            bpy.context.scene.layers[0] = False

        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}















































#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#MOD
########################################
class CATEGORYBUTTON_812057(bpy.types.Operator):#MOD
    """MOD"""
    bl_idname = "object.categorybutton_812057"
    bl_label = "MOD"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("MOD",True)
    uiitem.button(bl_idname,bl_label,icon="MODIFIER",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################










#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#適用（選択物）
########################################
class MYOBJECT_557231(bpy.types.Operator):#適用（選択物）
    """適用（選択物）"""
    bl_idname = "object.myobject_557231"
    bl_label = "mod適用（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #for obj in bpy.data.objects:
        #    if obj.select == True :
        #        bpy.context.scene.objects.active = obj
        #        for mod in obj.modifiers:
        #            try:
        #                bpy.ops.object.modifier_apply(modifier=mod.name)
        #            except:
        #                #ダメだったのでmod除去
        #                bpy.ops.object.modifier_remove(modifier=mod.name)
        for obj in get_selected_list():
            activate(obj)
            for mod in obj.modifiers:
                if "裏ポリエッジ" in mod.name:
                    continue
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except:
                    #ダメだったのでmod除去
                    bpy.ops.object.modifier_remove(modifier=mod.name)        
        


        
        return {'FINISHED'}
########################################





########################################
#複製系だけ適用（選択物）
########################################
class MYOBJECT_661107(bpy.types.Operator):#複製系だけ適用（選択物）
    """複製系だけ適用（選択物）"""
    bl_idname = "object.myobject_661107"
    bl_label = "複製系だけ適用（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return {'FINISHED'}
########################################


########################################
#適用・隠す
########################################
class MYOBJECT_234815(bpy.types.Operator):#適用・隠す
    """適用・隠す"""
    bl_idname = "object.myobject_234815"
    bl_label = "適用・隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if (obj.type == "MESH"):
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    #if (mod.type == "MIRROR")||(mod.type == "SUBSURF")||(mod.type ==
                    #"SHRINKWRAP")||(mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                obj.hide = True
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#厚み用拡縮適用
########################################
class MYOBJECT_474026(bpy.types.Operator):#厚み用拡縮適用
    """厚み用拡縮適用"""
    bl_idname = "object.myobject_474026"
    bl_label = "厚み用拡縮適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in get_selected_list():
            if not ismesh(obj):
                continue

            for mod in obj.modifiers:
                if mod.type == "SOLIDIFY":
                    mod.thickness *= obj.scale[0]

            pass
        
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ミラー")
############################################################################################################################

########################################
#ミラー左右分離（選択物）
########################################
class MYOBJECT_757415(bpy.types.Operator):#ミラー左右分離（選択物）
    """ミラー左右分離（選択物）"""
    bl_idname = "object.myobject_757415"
    bl_label = "ミラー左右分離（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_WIREFRAME",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #編集時にfaceいじるにはbmeshを使う必要がある。
        #bmeshについてはこれ↓あと、TextEditorにサンプルコードというかテンプレがある。
        #http://blender.stackexchange.com/questions/2776/how-to-read-vertices-of-quad-faces-using-python-api
        #一応参考
        #http://blenderartists.org/forum/showthread.php?207542-Selecting-a-face-through-the-API&highlight=ow%20do%20I%20select/deselect%20vertices/edges/faces%20with%20python
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                #各種mod適用
                for mod in obj.modifiers:
                    if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if (mod.type == "MIRROR") or (mod.type == "SHRINKWRAP"):
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                
                #グローバル座標
                #http://blenderscripting.blogspot.jp/2013/03/world-coordinates-from-local-coordinates.html
                #om = obj.matrix_world
                
                
                bpy.ops.object.mode_set(mode = 'EDIT') 
                data = obj.data
                bm = bmesh.from_edit_mesh(data)
                bm.faces.active = None
                X = 0
                Y = 1
                Z = 2
                selectflag = False
                #選択リフレッシュ
                for v  in bm.verts:
                    v.select = False
                for e in bm.edges:
                    e.select = False
                for f in bm.faces:
                    f.select = False
                for face in bm.faces:
                    for v in face.verts:
                        if(v.co[X] < 0):
                            face.select = True
                            selectflag = True
                            continue
                for edge in bm.edges:
                    for v in edge.verts:
                        if(v.co[X] < 0):
                            edge.select = True
                            selectflag = True
                            continue
                for v in bm.verts:
                       if(v.co[X] < 0):
                           v.select = True
                           selectflag = True
                           continue
                bmesh.update_edit_mesh(data)
                if selectflag:
                    bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode = 'OBJECT')
        
        #↓先に原点を移動してしまうと、それを参照しているオブジェクトのミラーとかがズレてしまうので最後にやる。
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#X-でミラー化
########################################
class MYOBJECT_900279(bpy.types.Operator):#X-でミラー化
    """X-でミラー化"""
    bl_idname = "object.myobject_900279"
    bl_label = "X-でミラー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            meshu = MeshUtils(obj)
            meshu.select_byaxis("-X")
            mode("EDIT")
            meshu.delete()
            
            modu = Modutils(obj)
            modu.add("Local Mirror", "MIRROR")
            modu.sort()

        return {'FINISHED'}
########################################

########################################
#X+でミラー化
########################################
class MYOBJECT_734909(bpy.types.Operator):#X+でミラー化
    """X+でミラー化"""
    bl_idname = "object.myobject_734909"
    bl_label = "X+でミラー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            meshu = MeshUtils(obj)
            meshu.select_byaxis("+X")
            meshu.delete()
            
            modu = Modutils(obj)
            modu.add("Local Mirror", "MIRROR")
            modu.sort()
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#ペアレントミラー
########################################
class MYOBJECT_892110(bpy.types.Operator):#ペアレントミラー
    """ペアレントミラー"""
    bl_idname = "object.myobject_892110"
    bl_label = "ペアレントミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        #ミラー
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                bpy.ops.object.modifier_add(type='MIRROR')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.mirror_object = target
                mod.name = "Parented Mirror"

                ##片面化
                #meshu = MeshUtils(obj)
                #if obj.location[0] < 0:
                #    meshu.select_byaxis("-X",True,target.location)
                #else:
                #    meshu.select_byaxis("+X",True,target.location)
                #mode("EDIT")
                #meshu.delete()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        
        return {'FINISHED'}
########################################


########################################
#ターゲットミラー
########################################
class MYOBJECT_553492(bpy.types.Operator):#ターゲットミラー
    """ターゲットミラー"""
    bl_idname = "object.myobject_553492"
    bl_label = "ターゲットミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        target = bpy.context.scene.objects.active
        #ミラー
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                if obj != target:
                    modu = Modutils(obj)
                    mod = modu.add("Target Mirror","MIRROR")
                    mod.mirror_object = target
                    modu.move_top(mod)

                    ##片面化
                    #meshu = MeshUtils(obj)
                    #if obj.location[0] < 0:
                    #    meshu.select_byaxis("-X",True,target.location)
                    #else:
                    #    meshu.select_byaxis("+X",True,target.location)
                    #mode("EDIT")
                    #meshu.delete()
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################


########################################
#P・Tミラー除去
########################################
class MYOBJECT_17104(bpy.types.Operator):#ターゲットミラー除去
    """P・Tミラー除去"""
    bl_idname = "object.myobject_17104"
    bl_label = "P・Tミラー除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in get_selected_list():
            modu = Modutils(obj)
            modu.remove_byname("Target Mirror")
            modu.remove_byname("Parented Mirror")


        return {'FINISHED'}
########################################

########################################
#ミラー適用
########################################
class MYOBJECT_239793(bpy.types.Operator):#ミラー適用
    """ミラー適用"""
    bl_idname = "object.myobject_239793"
    bl_label = "ミラー適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            for n in range(10):
                mod_mirr = modu.find_bytype("MIRROR")
                if mod_mirr == None:
                    break
                modu.apply(mod_mirr)
        
        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("ペアレントmod")
############################################################################################################################









########################################
#ペアレントラップ
########################################
class MYOBJECT_519944(bpy.types.Operator):#ペアレントラップ
    """ペアレントラップ"""
    bl_idname = "object.myobject_519944"
    bl_label = "ペアレントラップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SHRINKWRAP",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        #ラップ
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.target = target
                mod.wrap_method = 'PROJECT'
                mod.use_positive_direction = True
                mod.use_negative_direction = True
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        
        
        return {'FINISHED'}
########################################



########################################
#ペアレント装甲
########################################
class MYOBJECT_907335(bpy.types.Operator):#ペアレント装甲
    """ペアレント装甲"""
    bl_idname = "object.myobject_907335"
    bl_label = "ペアレント装甲"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #ラップ
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.target = target
                #厚み
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.thickness = -0.05
        
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




########################################
#ペアレントメッシュデフォーム
########################################
class MYOBJECT_449421(bpy.types.Operator):#ペアレントメッシュデフォーム
    """シュリンクラップは適用。"""
    bl_idname = "object.myobject_449421"
    bl_label = "ペアレントメッシュデフォーム6"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MESHDEFORM",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj != target:
                    #exists = False
                    ##メッシュデフォームがなかったらかける
                    #for mod in obj.modifiers:
                    #    if mod.type == "MESH_DEFORM":
                    #        exists = True
                    #        break
                    #if not exists:

                        mod_md = None
                        #存在したらそれを使う
                        for mod in obj.modifiers:
                            if mod.type == "MESH_DEFORM":
                                mod_md = mod

                        #まずはシュリンクラップの適用
                        for mod in obj.modifiers:
                            if mod.type == "SHRINKWRAP":
                                bpy.ops.object.modifier_apply(modifier=mod.name)
                        #メッシュデフォームかける
                        bpy.context.scene.objects.active = obj
                        if mod_md == None:
                            bpy.ops.object.modifier_add(type='MESH_DEFORM')
                            last = len(obj.modifiers) - 1
                            mod = obj.modifiers[last]
                            mod_md = mod
                            mod_n = last
                            #一番上にもっていく。mirrorより後。
                            for i in range(mod_n - 1, -1, -1):
                                if obj.modifiers[i].type == "MIRROR":
                                    break
                                else:
                                    bpy.ops.object.modifier_move_up(modifier=mod.name)

                        modu = Modutils(obj)
                        modu.sort()


                        #バインド
                        #精度6
                        mod_md.precision = 6
                        mod_md.object = target
                        bpy.ops.object.meshdeform_bind(modifier=mod_md.name)
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        
        
        
        
        return {'FINISHED'}
########################################
########################################
#5
########################################
class MYOBJECT_384891(bpy.types.Operator):#5
    """5"""
    bl_idname = "object.myobject_384891"
    bl_label = "精度5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj != target:
                        mod_md = None
                        #存在したらそれを使う
                        for mod in obj.modifiers:
                            if mod.type == "MESH_DEFORM":
                                mod_md = mod

                        #まずはシュリンクラップの適用
                        for mod in obj.modifiers:
                            if mod.type == "SHRINKWRAP":
                                bpy.ops.object.modifier_apply(modifier=mod.name)
                        #メッシュデフォームかける
                        bpy.context.scene.objects.active = obj
                        if mod_md == None:
                            bpy.ops.object.modifier_add(type='MESH_DEFORM')
                            last = len(obj.modifiers) - 1
                            mod = obj.modifiers[last]
                            mod_md = mod
                            mod_n = last
                            #一番上にもっていく。mirrorより後。
                            for i in range(mod_n - 1, -1, -1):
                                if obj.modifiers[i].type == "MIRROR":
                                    break
                                else:
                                    bpy.ops.object.modifier_move_up(modifier=mod.name)

                        modu = Modutils(obj)
                        modu.sort()

                        #バインド
                        #精度5
                        mod_md.precision = 5
                        mod_md.object = target
                        bpy.ops.object.meshdeform_bind(modifier=mod_md.name)
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#バインド解除
########################################
class MYOBJECT_44204(bpy.types.Operator):#バインド解除
    """バインド解除"""
    bl_idname = "object.myobject_44204"
    bl_label = "バインド解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        if mod.is_bound:
                            bpy.ops.object.meshdeform_bind(modifier=mod.name)
        
        return {'FINISHED'}
########################################



########################################
#デフォーム適用
########################################
class MYOBJECT_766913(bpy.types.Operator):#デフォーム適用
    """デフォーム適用"""
    bl_idname = "object.myobject_766913"
    bl_label = "デフォーム適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return {'FINISHED'}
########################################









########################################
#全て再バインド
########################################
class MYOBJECT_860977(bpy.types.Operator):#全て再バインド
    """メッシュデフォーム全て再バインド"""
    bl_idname = "object.myobject_860977"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #for obj in bpy.context.selected_objects:
        #    if obj.type == "MESH":
        #        bpy.context.scene.objects.active = obj
        #        for mod in obj.modifiers:
        #            if mod.type == "MESH_DEFORM":
        #                if mod.is_bound:
        #                    bpy.ops.object.meshdeform_bind(modifier=mod.name)
        #                bpy.ops.object.meshdeform_bind(modifier=mod.name)
        for obj in get_selected_list("MESH"):
            activate(obj)
            for mod in obj.modifiers:
                if mod.type == "MESH_DEFORM":
                    if mod.is_bound:
                        bpy.ops.object.meshdeform_bind(modifier=mod.name)
                    bpy.ops.object.meshdeform_bind(modifier=mod.name)
        
       
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("その他")
############################################################################################################################


########################################
#カーブにアタッチ
########################################
class MYOBJECT_531573(bpy.types.Operator):#カーブにアタッチ
    """カーブにアタッチ"""
    bl_idname = "object.myobject_531573"
    bl_label = "カーブにアタッチ（シングル）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        curve = None
        mesh = None
        for obj in get_selected_list():
            if obj.type == "CURVE":
                curve = obj
            if obj.type == "MESH":
                mesh = obj

        #メッシュの拡縮適用
        deselect()
        activate(mesh)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


        #カーブをスプラインごとに分離する
        deselect()
        activate(curve)

        #カーブのベベルをゼロに
        curve.data.bevel_depth = 0

        #セパレートするごとにスプラインのインデックスかわってんじゃないの？
        splines = curve.data.splines
        for i in range(len(splines) - 1):
            mode("EDIT")
            spline = splines[1]

            #個別分離
            bpy.ops.curve.select_all(action='DESELECT')
            for point in spline.points:
                point.select = True
            if spline.type == "BEZIER":
                for bzp in spline.bezier_points:
                    bzp.select_control_point = True
            bpy.ops.curve.separate()
            mode("OBJECT")
            mode("EDIT")



        #mode("EDIT")
        #for index, spline in enumerate(curve.data.splines):
        #    #0番は残す
        #    if index == 0:
        #        continue

        #    #個別分離
        #    bpy.ops.curve.select_all(action='DESELECT')
        #    for point in spline.points:
        #        point.select = True
        #    if spline.type == "BEZIER":
        #        for bzp in spline.bezier_points:
        #            bzp.select_control_point = True
        #    bpy.ops.curve.separate()
        mode("OBJECT")
        curves = get_selected_list()

        #元オブジェクト名でグループ化
        group(curve.name)

        objs = []

        #あらかじめ複製を作成する
        for index, curve in enumerate(curves):
            #if index == 0:
            #    objs.append(mesh)
            #    continue
            deselect()
            activate(mesh)
            #リンク複製
            bpy.ops.object.duplicate(linked=True)
            objs.append(active())

        #オブジェクトを複製してアタッチしてく
        for index, curve in enumerate(curves):
            obj = objs[index]

            deselect()
            #トランスフォームをあわせる
            activate(obj)
            obj.location = curve.location
            obj.rotation_euler = curve.rotation_euler
            
            mod_arr = add_mod("ARRAY")
            mod_arr.fit_type = "FIT_CURVE"
            mod_arr.curve = curve

            mod_crv = add_mod("CURVE")
            mod_crv.object = curve

            #グループ・ペアレント
            group(mesh.name)

            activate(curve)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)



        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#オープンエッジの線画化
########################################
class MYOBJECT_141722(bpy.types.Operator):#オープンエッジの線画化
    """オープンエッジの線画化"""
    bl_idname = "object.myobject_141722"
    bl_label = "オープンエッジの線画化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        deselect()

        for obj in selection:
            if obj.type != "MESH":
                continue
            #オープンエッジの分離
            activate(obj)
            mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')
            mode("OBJECT")

            target = None
            for tmp_target in get_selected_list():
                if tmp_target != obj:
                    target = tmp_target
            target.name = obj.name + "_openedgeline"

            deselect()

            #スキンで線画化
            activate(target)
            #モディファイアをすべて除去
            target.modifiers.clear()
            #マテリアルをすべて除去
            target.data.materials.clear()
            
            #黒マテリアルの割当
            mat = None
            if "主線黒" in bpy.data.materials:
                mat = bpy.data.materials["主線黒"]
            else:
                mat = bpy.data.materials.new(name="主線黒")
                mat.diffuse_color = (0, 0, 0)
                mat.use_shadeless = True
            target.data.materials.append(mat)

            #スキンモディファイア
            bpy.ops.object.modifier_add(type='SKIN')
            mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.skin_root_mark()
            ssize = 0.0025
            bpy.ops.transform.skin_resize(value=(ssize, ssize, ssize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            mode("OBJECT")

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#MOD整列
########################################
class MYOBJECT_288910(bpy.types.Operator):#MOD整列
    """MOD整列"""
    bl_idname = "object.myobject_288910"
    bl_label = "MOD整列"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in get_selected_list():
            if obj.type != "MESH":
                continue
    
            modu = Modutils(obj)
            modu.sort()



        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




############################################################################################################################
uiitem("BoolToolカスタム")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#Differnce
########################################
class MYOBJECT_476244(bpy.types.Operator):#Differnce
    """Differnce"""
    bl_idname = "object.myobject_476244"
    bl_label = "Differnce"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_BOOLEAN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.btool.boolean_diff()
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.context.active_object.select = False
        for obj in bpy.context.selected_objects:
            obj.hide_render = True
        
        
        return {'FINISHED'}
########################################


########################################
#Differnce→隠す
########################################
class MYOBJECT_691601(bpy.types.Operator):#Differnce→隠す
    """Differnce→隠す"""
    bl_idname = "object.myobject_691601"
    bl_label = "Differnce→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.btool.boolean_diff()
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.context.active_object.select = False
        for obj in bpy.context.selected_objects:
            obj.hide_render = True
        bpy.ops.object.hide_view_set(unselected=False)
        
        return {'FINISHED'}
########################################


########################################
#Union(Direct)
########################################
class MYOBJECT_69194(bpy.types.Operator):#Union(Direct)
    """Union(Direct)"""
    bl_idname = "object.myobject_69194"
    bl_label = "Union(Direct)"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_EDGESPLIT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.btool.boolean_union_direct()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#バウンド非表示
########################################
class MYOBJECT_757208(bpy.types.Operator):#バウンド非表示
    """バウンド非表示"""
    bl_idname = "object.myobject_757208"
    bl_label = "バウンド非表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.draw_type == 'BOUNDS':
                obj.hide = True
        
        
        
        
        return {'FINISHED'}
########################################

########################################
#bool再計算
########################################
class MYOBJECT_6352(bpy.types.Operator):#bool再計算
    """bool再計算"""
    bl_idname = "object.myobject_6352"
    bl_label = "bool再計算"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.object.select_all(action='DESELECT')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("便利")
############################################################################################################################
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#裏ポリ+ベベルエッジ
########################################
class MYOBJECT_972011(bpy.types.Operator):#裏ポリ+ベベルエッジ
    """裏ポリ+ベベルエッジ"""
    bl_idname = "object.myobject_972011"
    bl_label = "裏ポリ+ベベルエッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_318722()
        bpy.ops.object.myobject_60327()
        
        return {'FINISHED'}
########################################

########################################
#オノマトペ白フチ
########################################
class MYOBJECT_357209(bpy.types.Operator):#オノマトペ白フチ
    """オノマトペ白フチ"""
    bl_idname = "object.myobject_357209"
    bl_label = "オノマトペ白フチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_737497()
        bpy.ops.object.myobject_788766()
        selection = get_selected_list()
        for obj in selection:
            mat = obj.material_slots[0].material
            mat.diffuse_color = (0,0,0)
            mat.use_shadeless = True

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#エッジ適用
########################################
class MYOBJECT_793633(bpy.types.Operator):#エッジ適用
    """エッジ適用"""
    bl_idname = "object.myobject_793633"
    bl_label = "エッジ適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            
            mod = modu.find("ベベルエッジ")
            modu.apply(mod)

            mod = modu.find("裏ポリエッジ")
            modu.apply(mod)


        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------







def urapolimat_index(obj):
    mat = append_material("裏ポリエッジ")
    #デフォルトマテリアルの設置
    if len(obj.data.materials) == 0:
        dmat = bpy.data.materials.new("default")
        obj.data.materials.append(dmat)

    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    matindex = obj.data.materials.find(mat.name)
    return matindex

def urapoliwhitemat_index(obj):
    mat = append_material("裏ポリエッジ白")
    #デフォルトマテリアルの設置
    if len(obj.data.materials) == 0:
        dmat = bpy.data.materials.new("default")
        obj.data.materials.append(dmat)

    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    matindex = obj.data.materials.find(mat.name)
    return matindex

############################################################################################################################
uiitem("裏ポリエッジ")
############################################################################################################################
edgewidth = 0.001

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#裏ポリエッジ付加
########################################
class MYOBJECT_318722(bpy.types.Operator):#裏ポリエッジ付加
    """裏ポリエッジ付加"""
    bl_idname = "object.myobject_318722"
    bl_label = "裏ポリエッジ付加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()


        for obj in selection:
            if "裏ポリエッジ" not in obj.modifiers:
                modu = Modutils(obj)
                matindex = urapolimat_index(obj)

                mod = modu.find("裏ポリエッジ")
                if mod is None:
                    mod = modu.add("裏ポリエッジ", "SOLIDIFY")
                mod.thickness = edgewidth
                mod.offset = 1
                mod.vertex_group = "裏ポリウェイト"
                mod.thickness_vertex_group = 0.1
                mod.use_flip_normals = True
                mod.use_quality_normals = True
                mod.material_offset = matindex
                mod.material_offset_rim = matindex
                modu.sort()
            pass
        
        return {'FINISHED'}
########################################

########################################
#裏ポリ白
########################################
class MYOBJECT_737497(bpy.types.Operator):#裏ポリ白
    """裏ポリ白"""
    bl_idname = "object.myobject_737497"
    bl_label = "裏ポリ白"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()


        for obj in selection:
            if "裏ポリエッジ" not in obj.modifiers:
                modu = Modutils(obj)
                matindex = urapoliwhitemat_index(obj)

                mod = modu.find("裏ポリエッジ")
                if mod is None:
                    mod = modu.add("裏ポリエッジ", "SOLIDIFY")
                mod.thickness = edgewidth
                mod.offset = 1
                mod.vertex_group = "裏ポリウェイト"
                mod.thickness_vertex_group = 0.1
                mod.use_flip_normals = True
                mod.use_quality_normals = True
                mod.material_offset = matindex
                mod.material_offset_rim = matindex
                modu.sort()
            pass
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

#########################################
##1/2
#########################################
#class MYOBJECT_791523(bpy.types.Operator):#1/2
#    """1/2"""
#    bl_idname = "object.myobject_791523"
#    bl_label = "1/2"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        reject_notmesh()
#        selection = get_selected_list()

#        for obj in selection:
#            if "裏ポリエッジ" in obj.modifiers:
#                mod = obj.modifiers["裏ポリエッジ"]
#                mod.thickness *= 0.5

#        return {'FINISHED'}
#########################################


########################################
#1mm
########################################
class MYOBJECT_892991(bpy.types.Operator):#1mm
    """1mm"""
    bl_idname = "object.myobject_892991"
    bl_label = "1mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            modu = Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.001
        
        return {'FINISHED'}
########################################
########################################
#2mm
########################################
class MYOBJECT_793908(bpy.types.Operator):#2mm
    """2mm"""
    bl_idname = "object.myobject_793908"
    bl_label = "2mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            modu = Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.002
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.002

        
        return {'FINISHED'}
########################################






########################################
#5mm
########################################
class MYOBJECT_401033(bpy.types.Operator):#5mm
    """5mm"""
    bl_idname = "object.myobject_401033"
    bl_label = "5mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            modu = Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.005
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.005
        
        return {'FINISHED'}
########################################



########################################
#1cm
########################################
class MYOBJECT_788766(bpy.types.Operator):#1cm
    """1cm"""
    bl_idname = "object.myobject_788766"
    bl_label = "1cm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            modu = Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.01
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.01
        
        return {'FINISHED'}
########################################







#########################################
##*2
#########################################
#class MYOBJECT_886958(bpy.types.Operator):#*2
#    """*2"""
#    bl_idname = "object.myobject_886958"
#    bl_label = "*2"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        reject_notmesh()
#        selection = get_selected_list()

#        for obj in selection:
#            if "裏ポリエッジ" in obj.modifiers:
#                mod = obj.modifiers["裏ポリエッジ"]
#                mod.thickness *= 2
        
#        return {'FINISHED'}
#########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#表示
########################################
class MYOBJECT_513603(bpy.types.Operator):#表示
    """表示"""
    bl_idname = "object.myobject_513603"
    bl_label = "表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                mod = obj.modifiers["裏ポリエッジ"]
                mod.show_viewport = True

        
        return {'FINISHED'}
########################################






########################################
#非表示
########################################
class MYOBJECT_14967(bpy.types.Operator):#非表示
    """非表示"""
    bl_idname = "object.myobject_14967"
    bl_label = "非表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                mod = obj.modifiers["裏ポリエッジ"]
                mod.show_viewport = False
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




########################################
#除去
########################################
class MYOBJECT_290695(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "object.myobject_290695"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()


        for obj in selection:
            activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                bpy.ops.object.modifier_remove(modifier="裏ポリエッジ")


        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ベベル")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ベベルエッジ
########################################
class MYOBJECT_60327(bpy.types.Operator):#ベベルエッジ
    """ベベルエッジ"""
    bl_idname = "object.myobject_60327"
    bl_label = "ベベルエッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            mbevel = modu.find("ベベルエッジ")
            if mbevel is None:
                mbevel = modu.add("ベベルエッジ", "BEVEL")
            mbevel.width = 0.002
            mbevel.use_clamp_overlap = False
            mbevel.use_clamp_overlap = True
            mbevel.material = urapolimat_index(obj)
            mbevel.limit_method = 'ANGLE'
            modu.sort()
        
        return {'FINISHED'}
########################################


########################################
#除去
########################################
class MYOBJECT_312642(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "object.myobject_312642"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            modu.remove_byname("ベベルエッジ")
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("辺分離")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#分離エッジ
########################################
class MYOBJECT_115887(bpy.types.Operator):#辺分離ソリッド
    """分離エッジ"""
    bl_idname = "object.myobject_115887"
    bl_label = "分離エッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            if modu.find("分離エッジ_EDGE_SPLIT") == None:
                msplit = modu.add("分離エッジ_EDGE_SPLIT","EDGE_SPLIT")
            if modu.find("分離エッジ_SOLIDIFY") == None:
                msolid = modu.add("分離エッジ_SOLIDIFY", "SOLIDIFY")
                msolid.thickness = 0.005
                msolid.offset = 1
                msolid.material_offset_rim = urapolimat_index(obj)
            modu.sort()

        return {'FINISHED'}
########################################

########################################
#除去
########################################
class MYOBJECT_693073(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "object.myobject_693073"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        for obj in selection:
            modu = Modutils(obj)
            modu.remove_byname("分離エッジ_EDGE_SPLIT")
            modu.remove_byname("分離エッジ_SOLIDIFY")
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("便利")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#低subsurf化（選択物）
########################################
class MYOBJECT_962587(bpy.types.Operator):#低subsurf化（選択物）
    """低subsurf化（選択物）"""
    bl_idname = "object.myobject_962587"
    bl_label = "低subsurf化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()
        for obj in selection:
            deselect()
            activate(obj)
            bpy.ops.object.shade_smooth()

            #自動スムーズはものによってかえたほうがいい
            #obj.data.use_auto_smooth = True
            #obj.data.auto_smooth_angle = 0.523599

            modu = Modutils(obj)
            subsurfs = modu.find_bytype_list("SUBSURF")

            for subsurf in subsurfs:
                subsurf.levels = 2
                subsurf.render_levels = 2

        select(selection)
        return {'FINISHED'}
########################################
























#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
################################################################################
#UIカテゴリ
########################################
#メッシュ
########################################
class CATEGORYBUTTON_813381(bpy.types.Operator):#メッシュ
    """メッシュ"""
    bl_idname = "object.categorybutton_813381"
    bl_label = "メッシュ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("メッシュ",True)
    uiitem.button(bl_idname,bl_label,icon="MESH_DATA",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################







############################################################################################################################
uiitem("最高描画タイプ")
############################################################################################################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#バウンド
########################################
class MYOBJECT_630367(bpy.types.Operator):#バウンド
    """バウンド"""
    bl_idname = "object.myobject_630367"
    bl_label = "バウンド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        objs = get_selected_list()

        for obj in objs:
            obj.draw_type = "BOUNDS"

        return {'FINISHED'}
########################################

########################################
#ワイヤー
########################################
class MYOBJECT_65984(bpy.types.Operator):#ワイヤー
    """ワイヤー"""
    bl_idname = "object.myobject_65984"
    bl_label = "ワイヤー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        objs = get_selected_list()

        for obj in objs:
            obj.draw_type = "WIRE"
        
        return {'FINISHED'}
########################################

########################################
#テクスチャ
########################################
class MYOBJECT_691590(bpy.types.Operator):#テクスチャ
    """テクスチャ"""
    bl_idname = "object.myobject_691590"
    bl_label = "テクスチャ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        objs = get_selected_list()

        for obj in objs:
            obj.draw_type = "TEXTURED"
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("UV")
############################################################################################################################
########################################
#スマートUV投影（各選択物）
########################################
class MYOBJECT_339338(bpy.types.Operator):#スマートUV投影（各選択物）
    """スマートUV投影（各選択物）"""
    bl_idname = "object.myobject_339338"
    bl_label = "スマートUV投影（各選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        for obj in get_selected_list():
            activate(obj)
            mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.reset()
            bpy.ops.uv.smart_project()
            mode("OBJECT")
        return {'FINISHED'}
########################################






########################################
#ライトマップパック展開（各選択物）
########################################
class MYOBJECT_719855(bpy.types.Operator):#ライトマップパック展開（各選択物）
    """ライトマップパック展開（各選択物）"""
    bl_idname = "object.myobject_719855"
    bl_label = "ライトマップパック展開（各選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        for obj in get_selected_list():
            activate(obj)
            bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=2048, PREF_BOX_DIV=12, PREF_MARGIN_DIV=0.1)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("メッシュ")
############################################################################################################################

########################################
#境界クリース
########################################
class MYOBJECT_676177(bpy.types.Operator):#境界クリース
    """境界クリース"""
    bl_idname = "object.myobject_676177"
    bl_label = "境界クリース"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.edge_crease(value=1)
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#自動スムーズ
########################################
class MYOBJECT_31891(bpy.types.Operator):#自動スムーズ
    """自動スムーズ"""
    bl_idname = "object.myobject_31891"
    bl_label = "自動スムーズ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.shade_smooth()

        for obj in get_selected_list("MESH"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 0.523599


        
        return {'FINISHED'}
########################################


########################################
#法線を反転
########################################
class MYOBJECT_795120(bpy.types.Operator):#法線を反転
    """法線を反転"""
    bl_idname = "object.myobject_795120"
    bl_label = "法線を反転"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.flip_normals()
                bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ペラポリ準備
########################################
class MYOBJECT_996345(bpy.types.Operator):#ペラポリ準備
    """ペラポリ準備"""
    bl_idname = "object.myobject_996345"
    bl_label = "ペラポリ準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        obj = active()
        modu = Modutils(obj)
        
        mod = modu.add("Local Mirror", "MIRROR")
        mod.use_clip = True

        mod = modu.add("Solidify", "SOLIDIFY")
        mod.thickness = 0.005
        mod.use_even_offset = True


        return {'FINISHED'}
########################################
















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("メッシュアクション")
############################################################################################################################

########################################
#複製分離
########################################
class MYOBJECT_635930(bpy.types.Operator):#複製分離
    """複製分離"""
    bl_idname = "object.myobject_635930"
    bl_label = "複製分離"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="edit")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        baselist = []
        for obj in bpy.data.objects:
            baselist.append(obj)
        
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        
        bpy.ops.object.editmode_toggle()
        
        for obj in bpy.data.objects:
            if obj not in baselist:
                #新しいオブジェクト
                bpy.context.scene.objects.active = obj
                bpy.ops.object.editmode_toggle()
                break
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#装甲化
########################################
class MYOBJECT_273555(bpy.types.Operator):#装甲化
    """装甲化"""
    bl_idname = "object.myobject_273555"
    bl_label = "装甲化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="edit")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        
        baseobj = bpy.context.scene.objects.active
        ArmorPlate = None
        
        #複製切り出し
        baselist = []
        for obj in bpy.data.objects:
            baselist.append(obj)
        
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        
        bpy.ops.object.editmode_toggle()
        
        for obj in bpy.data.objects:
            if obj not in baselist:
                #新しいオブジェクト
                ArmorPlate = obj
        #        bpy.context.scene.objects.active = obj
        #        bpy.ops.object.editmode_toggle()
                break
        
        #装甲化
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #既存の装甲・ラップmodの除去
                for mod in obj.modifiers:
                    if mod.type == "SHRINKWRAP" or mod.type == "SOLIDIFY" or mod.type == "BOOLEAN" or mod.type == "BEVEL":
                        bpy.ops.object.modifier_remove(modifier=mod.name)
                

                #ラップ→ないほうがいい
                #bpy.ops.object.modifier_add(type='SHRINKWRAP')
                #last = len(obj.modifiers) - 1
                #mod = obj.modifiers[last]
                #mod = add_mod('SHRINKWRAP')
                #mod.target = target
                #厚み
                mod = add_mod('SOLIDIFY')
                mod.thickness = -0.05
                mod.use_even_offset = True
                mod.use_quality_normals = True
                
                mod = add_mod('BEVEL')
                mod.width = 0.01
                mod.offset_type = 'WIDTH'

                #エッジにクリースつける
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.transform.edge_crease(value=1)
                objectmode()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        #bpy.context.scene.objects.active = ArmorPlate
        #連続できるようにする
        bpy.context.scene.objects.active = target
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.mesh_select_mode = [False,False,True]

        return {'FINISHED'}
########################################

########################################
#装甲化（内側）
########################################
class MYOBJECT_338159(bpy.types.Operator):#装甲化（内側）
    """装甲化（内側）"""
    bl_idname = "object.myobject_338159"
    bl_label = "装甲化（内側）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        baseobj = bpy.context.scene.objects.active
        ArmorPlate = None
        
        #複製切り出し
        baselist = []
        for obj in bpy.data.objects:
            baselist.append(obj)
        
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        
        bpy.ops.object.editmode_toggle()
        
        for obj in bpy.data.objects:
            if obj not in baselist:
                #新しいオブジェクト
                ArmorPlate = obj
        #        bpy.context.scene.objects.active = obj
        #        bpy.ops.object.editmode_toggle()
                break
        
        #装甲化
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #既存の装甲・ラップmodの除去
                for mod in obj.modifiers:
                    if mod.type == "SHRINKWRAP" or mod.type == "SOLIDIFY" or mod.type == "BOOLEAN" or mod.type == "BEVEL":
                        bpy.ops.object.modifier_remove(modifier=mod.name)
                

                #ラップ→ないほうがいい
                #bpy.ops.object.modifier_add(type='SHRINKWRAP')
                #last = len(obj.modifiers) - 1
                #mod = obj.modifiers[last]
                #mod = add_mod('SHRINKWRAP')
                #mod.target = target
                #厚み
                mod = add_mod('SOLIDIFY')
                mod.thickness = 0.05
                #mod.use_even_offset = True
                mod.use_quality_normals = True
                
                mod = add_mod('BEVEL')
                mod.width = 0.01
                mod.offset_type = 'WIDTH'

                #エッジにクリースつける
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.transform.edge_crease(value=1)
                objectmode()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        #bpy.context.scene.objects.active = ArmorPlate
        #連続できるようにする
        bpy.context.scene.objects.active = target
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.mesh_select_mode = [False,False,True]
        
        return {'FINISHED'}
########################################


########################################
#厚み反転
########################################
class MYOBJECT_351222(bpy.types.Operator):#厚み反転
    """厚み反転"""
    bl_idname = "object.myobject_351222"
    bl_label = "厚み反転"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        for obj in bpy.context.selected_objects:
            activate(obj)

            mod = get_mod('SOLIDIFY')
            if mod != None:
                mod.thickness *= -1

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------






########################################
#フチ厚み化
########################################
class MYOBJECT_813387(bpy.types.Operator):#フチ厚み化
    """フチ厚み化"""
    bl_idname = "object.myobject_813387"
    bl_label = "フチ厚み化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="edit")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        
        mod_solid = None
        found = False
        for mod in obj.modifiers:
            if mod.type == "SOLIDIFY":
                mod_solid = mod
                found = True
        
        if not found:
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            last = len(obj.modifiers) - 1
            mod = obj.modifiers[last]
            mod.thickness = -0.05
            mod_solid = mod
        
        mod_solid.use_flip_normals = True
        mod_solid.use_rim_only = True
        mod_solid.offset = 0

        
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        return {'FINISHED'}
########################################


########################################
#スキン化
########################################
class MYOBJECT_994469(bpy.types.Operator):#スキン化
    """スキン化"""
    bl_idname = "object.myobject_994469"
    bl_label = "スキン化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SKIN",mode="edit")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_635930()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.ops.transform.skin_resize(value=(0.1, 0.1, 0.1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#x*-1
########################################
class MYOBJECT_467890(bpy.types.Operator):#x*-1
    """x*-1"""
    bl_idname = "object.myobject_467890"
    bl_label = "x*-1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EMPTY_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
#        if bpy.context.scene.objects.active.type == "EMPTY":
#            base = bpy.context.scene.objects.active
#            bpy.ops.object.duplicate()
#
#            obj = bpy.context.scene.objects.active
#            bpy.ops.object.constraint_add(type='COPY_LOCATION')
#            bpy.ops.object.constraint_add(type='COPY_ROTATION')
#
#            for constraint in obj.constraints:
#                if constraint.type == "COPY_LOCATION":
#                    constraint.invert_x = True
#                    constraint.target = base
#                if constraint.type == "COPY_ROTATION":
#                    constraint.invert_x = False
#                    constraint.invert_y = True
#                    constraint.invert_z = True
#                    constraint.target = base
        bpy.context.object.scale[0] = -1
        
        return {'FINISHED'}
########################################

########################################
#gMirror
########################################
class MYOBJECT_681921(bpy.types.Operator):#gMirror
    """グループ化してミラーにする"""
    bl_idname = "object.myobject_681921"
    bl_label = "gMirror"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        import random
        groupname = "Group" + str(random.randrange(0,9999999999))
        bpy.ops.group.create(name=groupname)
        glayers = bpy.context.scene.objects.active.layers
        bpy.ops.object.group_instance_add(group=groupname, view_align=False, location=(0, 0, 0), layers=glayers)
        bpy.context.scene.objects.active.scale[0] = -1
        for obj in bpy.context.selected_objects:
            obj.select = False
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("オブジェクトモード")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#重複頂点を削除（選択物）
########################################
class MYOBJECT_559336(bpy.types.Operator):#重複頂点を削除（選択物）
    """重複頂点を削除（選択物）"""
    bl_idname = "object.myobject_559336"
    bl_label = "重複頂点を削除（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selection = get_selected_list()

        for obj in selection:
            activate(obj)
            meshu = MeshUtils(obj)
            meshu.selectall()
            meshu.remove_doubles()
        mode("OBJECT")
        return {'FINISHED'}
########################################





#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#トランスフォーム
########################################
class CATEGORYBUTTON_561346(bpy.types.Operator):#トランスフォーム
    """トランスフォーム"""
    bl_idname = "object.categorybutton_561346"
    bl_label = "トランスフォーム"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("トランスフォーム",True)
    uiitem.button(bl_idname,bl_label,icon="MANIPUL",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





########################################
#面に回転をあわせる
########################################
class MYOBJECT_272822(bpy.types.Operator):#面に回転をあわせる
    """面に回転をあわせる"""
    bl_idname = "object.myobject_272822"
    bl_label = "rRMB 面に回転をあわせる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_FACE",mode="edit")


    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.ralign_orientation_to_selection()
#        bpy.ops.transform.create_orientation()
#        bpy.ops.object.editmode_toggle()
#        bpy.context.space_data.transform_orientation = 'Face'
#        bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0,
#        0, 0), constraint_axis=(False, False, False),
#        constraint_orientation='Face', mirror=False, proportional='DISABLED',
#        proportional_edit_falloff='SMOOTH', proportional_size=1)
#        bpy.ops.object.transform_apply(location=False, rotation=True,
#        scale=True)
#        bpy.ops.transform.delete_orientation()
         
         
         
         
        return {'FINISHED'}
########################################

#########################################
##角度をきっちり
#########################################
#class MYOBJECT_908924(bpy.types.Operator):#角度をきっちり
#    """角度をきっちり"""
#    bl_idname = "object.myobject_908924"
#    bl_label = "角度をきっちり"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        rmode = bpy.context.object.rotation_mode
#        bpy.context.object.rotation_mode = 'XYZ'
#        obj = bpy.context.scene.objects.active
#        for n in range(0,3):
#            angle = math.degrees(obj.rotation_euler[n] )
#            if angle != 0:
#                if angle > 0:
#                    angle = angle - angle%90
#                else:
#                    angle = angle + angle%90
#            obj.rotation_euler[n] = math.radians(angle)
#
#        bpy.context.object.rotation_mode = rmode
#
#
#
#        return {'FINISHED'}
#########################################


############################################################################################################################
uiitem("複製反転")
############################################################################################################################

########################################
#ミラーリング
########################################
class MYOBJECT_698300(bpy.types.Operator):#ミラーリング
    """ミラーリング"""
    bl_idname = "object.myobject_698300"
    bl_label = "ミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])
        use_pivot_point_align = bpy.context.space_data.use_pivot_point_align

        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.context.space_data.pivot_point = 'CURSOR'

        #位置を反転→各オブジェクトごとにやらないと全体にかかる！
        #個別でやると今度は親子問題
        #bpy.context.space_data.use_pivot_point_align = True
        #for obj in selection:
        #    deselect()
        #    activate(obj)
        #    bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        #原点は3Dカーソル使って移動する！！

        #各オブジェクトを編集モードで反転
        #編集リスト
        editable = ["MESH","ARMATURE","CURVE"]

        for obj in selection:
            if obj.type in editable:
                deselect()
                activate(obj)
                obj.active_shape_key_index = 0

                #bpy.ops.view3d.snap_cursor_to_selected()
                mode("EDIT")
                
                #select_allがタイプによって違う
                if obj.type == "MESH":
                    bpy.ops.mesh.select_all(action="SELECT")
                if obj.type == "ARMATURE":
                    bpy.ops.armature.select_all(action="SELECT")
                if obj.type == "CURVE":
                    bpy.ops.curve.select_all(action="SELECT")

                #反転
                bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
                #法線反転
                if obj.type == "MESH":
                    bpy.ops.mesh.flip_normals()
                mode("OBJECT")

        #原点処理
        for obj in selection:
            deselect()
            activate(obj)
            bpy.ops.view3d.snap_cursor_to_selected()
            c = bpy.context.space_data.cursor_location
            bpy.context.space_data.cursor_location = (c[0]*-1,c[1],c[2])
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')



        select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        bpy.context.space_data.use_pivot_point_align = use_pivot_point_align



        #bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        #selection = get_selected_list()

        #current_pivot_point = bpy.context.space_data.pivot_point
        #current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])
        #use_pivot_point_align = bpy.context.space_data.use_pivot_point_align

        #bpy.context.space_data.cursor_location = (0,0,0)
        #bpy.context.space_data.pivot_point = 'CURSOR'

        ##位置を反転
        #bpy.context.space_data.use_pivot_point_align = True
        #bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

        ##各オブジェクトを編集モードで反転
        ##編集リスト
        #editable = ["MESH","ARMATURE","CURVE"]

        #for obj in selection:
        #    if obj.type in editable:
        #        deselect()
        #        activate(obj)
        #        bpy.ops.view3d.snap_cursor_to_selected()
        #        mode("EDIT")
                
        #        #select_allがタイプによって違う
        #        if obj.type == "MESH":
        #            bpy.ops.mesh.select_all(action="SELECT")
        #        if obj.type == "ARMATURE":
        #            bpy.ops.armature.select_all(action="SELECT")
        #        if obj.type == "CURVE":
        #            bpy.ops.curve.select_all(action="SELECT")

        #        #反転
        #        bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        #        mode("OBJECT")
        #select(selection)

        ##ピボット戻す
        #bpy.context.space_data.pivot_point = current_pivot_point        
        #bpy.context.space_data.cursor_location = current_cursor
        #bpy.context.space_data.use_pivot_point_align = use_pivot_point_align
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#グローバル X
########################################
class MYOBJECT_83454(bpy.types.Operator):#global X
    """グローバル X"""
    bl_idname = "object.myobject_83454"
    bl_label = "global X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        deselect()
        select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        select(roots)
        activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[0] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        deselect()
        delete([empty])

        select(selection)


        #bpy.context.space_data.pivot_point = 'CURSOR'
        #bpy.context.space_data.cursor_location = (0,0,0)
        #bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        #bpy.ops.transform.resize(value=(-1, 1, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#カーソル X
########################################
class MYOBJECT_334794(bpy.types.Operator):#カーソル X
    """カーソル X"""
    bl_idname = "object.myobject_334794"
    bl_label = "カーソル X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        deselect()
        select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        select(roots)
        activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[0] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        deselect()
        delete([empty])

        select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################


########################################
#Y
########################################
class MYOBJECT_168959(bpy.types.Operator):#Y
    """Y"""
    bl_idname = "object.myobject_168959"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        deselect()
        select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        select(roots)
        activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[1] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        deselect()
        delete([empty])

        select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################



########################################
#Z
########################################
class MYOBJECT_68739(bpy.types.Operator):#Z
    """Z"""
    bl_idname = "object.myobject_68739"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        deselect()
        select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        select(roots)
        activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[2] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        deselect()
        delete([empty])

        select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
















#
#############################################################################################################################
##ドラフト
#############################################################################################################################
#########################################
##アウトプット
#########################################
#class MYOBJECT_879787(bpy.types.Operator):#アウトプット
#    """アウトプット"""
#    bl_idname = "object.myobject_879787"
#    bl_label = "アウトプット"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("ドラフト");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        #http://python.civic-apps.com/date-format/
#        #bpy.context.scene.render.use_simplify = True
#        #bpy.context.scene.render.simplify_subdivision = 1
#        now = datetime.datetime.now()
#        nowstr = now.strftime("%Y%m%d%H%M%S")
#
#        bpy.ops.wm.save_mainfile(filepath="g:\\tmp\\log\\"+nowstr+".blend")
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.space_data.show_only_render = True
#        bpy.data.scenes["Scene"].render.filepath = "g:\\tmp\\tmp.png"
#        bpy.ops.render.opengl(animation=False, sequencer=False,
#        write_still=True, view_context=True)
#        bpy.data.scenes["Scene"].render.filepath =
#        "g:\\tmp\\log\\"+nowstr+".png"
#        bpy.ops.render.opengl(animation=False, sequencer=False,
#        write_still=True, view_context=True)
#        bpy.context.space_data.show_only_render = False
#        bpy.context.scene.render.resolution_percentage = 100
#        """
#        #そうだ！！GLレンダ！！！！
#        bpy.ops.wm.save_mainfile(filepath="c:\\tmp\\log\\"+nowstr+".blend")
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.scene.render.use_shadows = False
#        bpy.context.scene.render.use_raytrace = False
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_antialiasing = False
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_freestyle = False
#        bpy.context.scene.render.use_edge_enhance = False
#        bpy.context.scene.render.edge_threshold = 255
#        bpy.data.scenes["Scene"].render.filepath = "c:\\tmp\\tmp.png"
#        bpy.ops.render.render(write_still=True)
##        bpy.data.scenes["Scene"].render.filepath =
##        "c:\\tmp\\log\\"+nowstr+".png"
##        bpy.ops.render.render(write_still=True)
#        """
#
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#
#
#
#
#
#
#
#############################################################################################################################
##オリエンテーション
#############################################################################################################################
#########################################
##グローバル
#########################################
#class MYOBJECT_538468(bpy.types.Operator):#グローバル
#    """グローバル"""
#    bl_idname = "object.myobject_538468"
#    bl_label = "グローバル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("オリエンテーション");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'GLOBAL'
#
#        return {'FINISHED'}
#########################################
#
#########################################
##ローカル
#########################################
#class MYOBJECT_550536(bpy.types.Operator):#ローカル
#    """Sample Operator"""
#    bl_idname = "object.myobject_550536"
#    bl_label = "ローカル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'LOCAL'
#
#        return {'FINISHED'}
#########################################
#
#########################################
##ノーマル
#########################################
#class MYOBJECT_265618(bpy.types.Operator):#ノーマル
#    """ノーマル"""
#    bl_idname = "object.myobject_265618"
#    bl_label = "ノーマル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'NORMAL'
#
#        return {'FINISHED'}
#########################################


























#
#############################################################################################################################
##シーン
#############################################################################################################################
#########################################
##表示シーンを揃える
#########################################
#class MYOBJECT_708885(bpy.types.Operator):#表示シーンを揃える
#    """表示シーンを揃える"""
#    bl_idname = "object.myobject_708885"
#    bl_label = "表示シーンを揃える"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("シーン");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        scene = bpy.context.scene
#        for screen in bpy.data.screens:
#            screen.scene = scene
#        return {'FINISHED'}
#########################################
#




































#
#
#
#############################################################################################################################
##スナップ
#############################################################################################################################
#
#########################################
##選択→3Dカーソル
#########################################
#class MYOBJECT_553638(bpy.types.Operator):#選択→3Dカーソル
#    """選択→3Dカーソル"""
#    bl_idname = "object.myobject_553638"
#    bl_label = "選択→3Dカーソル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("スナップ");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
#
#        return {'FINISHED'}
#########################################
#
#
#########################################
##3Dカーソル→選択
#########################################
#class MYOBJECT_670764(bpy.types.Operator):#3Dカーソル→選択
#    """3Dカーソル→選択"""
#    bl_idname = "object.myobject_670764"
#    bl_label = "3Dカーソル→選択"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.ops.view3d.snap_cursor_to_selected()
#
#        return {'FINISHED'}
#########################################
#

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------















































################################################################################
#UIカテゴリ
########################################
#ペアレント
########################################
class CATEGORYBUTTON_445538(bpy.types.Operator):#ペアレント
    """ペアレント"""
    bl_idname = "object.categorybutton_445538"
    bl_label = "ペアレント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ペアレント",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オブジェクト
########################################
class MYOBJECT_227300(bpy.types.Operator):#オブジェクト
    """オブジェクト"""
    bl_idname = "object.myobject_227300"
    bl_label = "オブジェクト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################

########################################
#オブジェクト（Trans維持）
########################################
class MYOBJECT_413331(bpy.types.Operator):#オブジェクト（Trans維持）
    """オブジェクト（Trans維持）"""
    bl_idname = "object.myobject_413331"
    bl_label = "Trans維持"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#ボーン相対
########################################
class MYOBJECT_454489(bpy.types.Operator):#ボーン相対
    """ボーン相対"""
    bl_idname = "object.myobject_454489"
    bl_label = "ボーン相対"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="BONE_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='BONE_RELATIVE')
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################

########################################
#ボーン相対→隠す
########################################
class MYOBJECT_182276(bpy.types.Operator):#ボーン相対→隠す
    """ボーン相対→隠す"""
    bl_idname = "object.myobject_182276"
    bl_label = "→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='BONE_RELATIVE')
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.object.hide_view_set(unselected=False)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




########################################
#自動のウェイトで
########################################
class MYOBJECT_214836(bpy.types.Operator):#自動のウェイトで
    """自動のウェイトで"""
    bl_idname = "object.myobject_214836"
    bl_label = "自動のウェイトで"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        #アーマチュアを一番上にもってく
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                modslen = len(obj.modifiers)
                mod = obj.modifiers[modslen - 1]
                if mod.type == "ARMATURE":
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)
                    #mirrorはアーマチュアより上に。
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        for n in range(0,modslen):
                            bpy.ops.object.modifier_move_up(modifier=mod.   name)
        
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################


########################################
#自動のウェイトで→隠す
########################################
class MYOBJECT_214836a(bpy.types.Operator):#自動のウェイトで→隠す
    """自動のウェイトで→隠す"""
    bl_idname = "object.myobject_214836a"
    bl_label = "→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.object.hide_view_set(unselected=False)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------







########################################
#クリア
########################################
class MYOBJECT_307216(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "object.myobject_307216"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_LAMP",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_clear(type='CLEAR')
        
        return {'FINISHED'}
########################################

########################################
#クリア（Trans維持）
########################################
class MYOBJECT_855470(bpy.types.Operator):#クリア（Trans維持）
    """クリア（Trans維持）"""
    bl_idname = "object.myobject_855470"
    bl_label = "Trans維持"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_LAMP",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#
#
#############################################################################################################################
##トランスフォーム
#############################################################################################################################
#########################################
##X位置 0
#########################################
#class MYOBJECT_562777(bpy.types.Operator):#X位置 0
#    """トランスフォーム"""
#    bl_idname = "object.myobject_562777"
#    bl_label = "X位置 0"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("トランスフォーム");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        obj = bpy.context.scene.objects.active
#        obj.location[0] = 0
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#
#
#########################################
##回転X 90
#########################################
#class MYOBJECT_487092(bpy.types.Operator):#回転X 90
#    """回転X 90"""
#    bl_idname = "object.myobject_487092"
#    bl_label = "回転X 90"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        obj = bpy.context.scene.objects.active
#        obj.rotation_euler[0] = 1.5708
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#########################################
##-X位置コピー
#########################################
#class MYOBJECT_589282(bpy.types.Operator):#-X位置コピー
#    """-X位置コピー"""
#    bl_idname = "object.myobject_589282"
#    bl_label = "-X位置コピー"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        source = bpy.context.selected_objects[0]
#        target = bpy.context.scene.objects.active
#        target.location[0] = source.location[0] * -1
#        target.location[1] = source.location[1]
#        target.location[2] = source.location[2]
#
#        return {'FINISHED'}
#########################################









#対象のレイヤーをセット
def setlayer(l):
    bpy.context.scene.layers[l] = True
    for obj in bpy.context.selected_objects:
        obj.layers[l] = True
        for layer_n in range(0,19):
            if(layer_n != l):
                obj.layers[layer_n] = False
    
    refreshlayer()
    
    return



#オブジェクトのないレイヤーを非表示にする
def refreshlayer():
    layers = [False] * 20
    
    #現在非表示なものは表示しない、準備
    current_layers = [False] * 20
    for l in range(0,20):
        current_layers[l] = bpy.context.scene.layers[l]
    
    for obj in bpy.data.objects:
        for l in range(0,19):
            if(obj.layers[l]):
                layers[l] = True
    
    
    #現在非表示なものを非表示に
    for l in range(0,19):
        if(current_layers[l] == False):
            layers[l] = False
    
    bpy.context.scene.layers = layers
    
    return






























































#
#
#
#############################################################################################################################
##レンダー設定
#############################################################################################################################
#########################################
##プレビュー
#########################################
#class MYOBJECT_913578(bpy.types.Operator):#プレビュー
#    """プレビュー"""
#    bl_idname = "object.myobject_913578"
#    bl_label = "プレビュー"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("レンダー設定");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_shadows = True
#
#        return {'FINISHED'}
#########################################
#
#########################################
##フル
#########################################
#class MYOBJECT_852389(bpy.types.Operator):#フル
#    """フル"""
#    bl_idname = "object.myobject_852389"
#    bl_label = "フル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.render.resolution_percentage = 100
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_shadows = True
#
#        return {'FINISHED'}
#########################################






################################################################################
#UIカテゴリ
########################################
#アーマチュア
########################################
class CATEGORYBUTTON_446957(bpy.types.Operator):#アーマチュア
    """アーマチュア"""
    bl_idname = "object.categorybutton_446957"
    bl_label = "アーマチュア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("アーマチュア",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#スケール継承解除（選択ボーン）
########################################
class MYOBJECT_84927(bpy.types.Operator):#スケール継承解除（選択ボーン）
    """スケール継承解除（選択ボーン）"""
    bl_idname = "object.myobject_84927"
    bl_label = "スケール継承解除（選択ボーン）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.object.data.draw_type = 'STICK'
        
        #スケール継承の解除
        for bone in bpy.context.object.data.bones:
            if(bone.select == True):
                bone.use_inherit_scale = False
        
        
        
        return {'FINISHED'}
########################################

########################################
#スケール継承有効（選択ボーン）
########################################
class MYOBJECT_516332(bpy.types.Operator):#スケール継承有効（選択ボーン）
    """スケール継承有効（選択ボーン）"""
    bl_idname = "object.myobject_516332"
    bl_label = "スケール継承有効（選択ボーン）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.object.data.draw_type = 'STICK'
        
        #スケール継承の解除
        for bone in bpy.context.object.data.bones:
            if(bone.select == True):
                bone.use_inherit_scale = True
        
        
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#＜●＞コンストレイント
########################################
class MYOBJECT_618823(bpy.types.Operator):#＜●＞コンストレイント
    """＜●＞コンストレイント"""
    bl_idname = "object.myobject_618823"
    bl_label = "コンストレイント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_ON",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                        constraint.mute = False
        
        return {'FINISHED'}
########################################

########################################
#＜＿＞コンストレイント
########################################
class MYOBJECT_898623(bpy.types.Operator):#＜＿＞コンストレイント
    """＜＿＞コンストレイント"""
    bl_idname = "object.myobject_898623"
    bl_label = "コンストレイント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_OFF",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                        constraint.mute = True
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アーマチュアからスキンを作成
########################################
class MYOBJECT_742340(bpy.types.Operator):#アーマチュアからスキンを作成
    """アーマチュアからスキンを作成"""
    bl_idname = "object.myobject_742340"
    bl_label = "アーマチュアからスキンを作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if active().type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}

        armature_org = active()

        #############
        #アーマチュアからメッシュを生成
        #############

        #トランスフォームを反映するために複製して親子解除する
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        armature = active()
        bonedata = {}

        mode("POSE")

        #ポーズからとるとやっぱよくなかった。デフォルトから取るべき。
        armature.data.pose_position = 'REST'
        bones = armature.pose.bones
        #bones = armature.data.bones
        for bone in bones:
            bonedata[bone.name] = {"name":bone.name, "head":bone.head, "tail":bone.tail}

        mode("OBJECT")


        bpy.ops.object.add(type='MESH')
        obj = ob = bpy.context.object
        mesh = obj.data
        
        obj.location = armature.location
        obj.rotation_euler = armature.rotation_euler
        obj.scale = armature.scale

        #頂点・辺の生成
        for bname in bonedata:
            bdata = bonedata[bname]

            mesh.vertices.add(count=1)
            v0 = len(mesh.vertices) - 1
            v = mesh.vertices[v0]
            v.co = bdata["head"]

            mesh.vertices.add(count=1)
            v1 = len(mesh.vertices) - 1
            v = mesh.vertices[v1]
            v.co = bdata["tail"]

            mesh.edges.add(count=1)
            e = mesh.edges[len(mesh.edges) - 1]
            #辺の頂点指定は頂点のインデックス番号。
            e.vertices[0] = v0
            e.vertices[1] = v1

        #重複頂点を削除
        mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        #5mm
        bpy.ops.mesh.remove_doubles(threshold=0.005)
        mode("OBJECT")


        #複製したアーマチュアを削除
        delete([armature])

        deselect()
        activate(obj)
        obj.select = True

        #元アーマチュアにくくりつけておく
        activate(armature_org)
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


        #スキン
        activate(obj)
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        skinsize = 0.03
        bpy.ops.transform.skin_resize(value=(skinsize, skinsize, skinsize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.object.skin_root_mark()

        bpy.context.object.modifiers["Armature"].show_in_editmode = True

        obj.hide_render = True

        bpy.ops.object.modifier_add(type='SUBSURF')


        return {'FINISHED'}
########################################


########################################
#選択ボーン以外のウェイトを削除
########################################
class MYOBJECT_166889(bpy.types.Operator):#選択ボーン以外のウェイトを削除
    """選択ボーン以外のウェイトを削除"""
    bl_idname = "object.myobject_166889"
    bl_label = "選択ボーン以外のウェイトを削除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):

        tmp = get_selected_list("ARMATURE")
        if tmp.count == 0:
            return {'CANCELLED'}
        armatures = tmp

        tmp = get_selected_list("MESH")
        if tmp.count == 0:
            return {'CANCELLED'}
        meshes = tmp

        #選択されているボーンのリストを取得する
        
        armature_data = {}
        for arm in armatures:
            data = {}
            activate(arm)
            mode("POSE")
            for posebone in arm.pose.bones:
                data[posebone.bone.name] = posebone.bone.select
            armature_data[arm.name] = data

        #http://blender.stackexchange.com/questions/24170/vertex-groups-and-bone-weights-programmatically
        #http://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
        for mesh in meshes:

            #ウェイト割当で使うインデックスのリストを作成
            #今回はどれも全割当なのではじめにつくっとく
            vxIdList = []
            for idx, val in enumerate(mesh.data.vertices):
                vxIdList.append(idx)


            for armdata_name in armature_data:
                for vg in mesh.vertex_groups:
                    armdata = armature_data[armdata_name]
                    if vg.name in armdata:
                        if armdata[vg.name] == False:
                            #非選択ボーンなのでウェイトをゼロにする
                            vg.add(vxIdList, 0, "REPLACE")

        
        return {'FINISHED'}
########################################

########################################
#ウェイトボーン相対
########################################
class MYOBJECT_273078(bpy.types.Operator):#ウェイトボーン相対
    """ウェイトボーン相対"""
    bl_idname = "object.myobject_273078"
    bl_label = "ウェイトボーン相対"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #からのグループで割当
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.parent_set(type='ARMATURE_NAME')


        tmp = get_selected_list("ARMATURE")
        if tmp.count == 0:
            return {'CANCELLED'}
        armatures = tmp

        tmp = get_selected_list("MESH")
        if tmp.count == 0:
            return {'CANCELLED'}
        meshes = tmp

        #選択されているボーンのリストを取得する
        
        armature_data = {}
        for arm in armatures:
            data = {}
            activate(arm)
            mode("POSE")

            #アクティブ以外のウェイトとかいらないから他を非選択に
            activeposebone = arm.data.bones.active
            for posebone in arm.pose.bones:
                posebone.bone.select = False
            activeposebone.select = True

            for posebone in arm.pose.bones:
                data[posebone.bone.name] = posebone.bone.select
            armature_data[arm.name] = data

        #http://blender.stackexchange.com/questions/24170/vertex-groups-and-bone-weights-programmatically
        #http://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
        for mesh in meshes:

            #ウェイト割当で使うインデックスのリストを作成
            #今回はどれも全割当なのではじめにつくっとく
            vxIdList = []
            for idx, val in enumerate(mesh.data.vertices):
                vxIdList.append(idx)


            for armdata_name in armature_data:
                for vg in mesh.vertex_groups:
                    armdata = armature_data[armdata_name]
                    if vg.name in armdata:
                        if armdata[vg.name] == False:
                            #非選択ボーンなのでウェイトをゼロにする
                            vg.add(vxIdList, 0, "REPLACE")
                        else:
                            #選択ボーンはウェイト1
                            vg.add(vxIdList, 1, "REPLACE")
        
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("プロポーションエディット")
############################################################################################################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#準備
########################################
class MYOBJECT_964581(bpy.types.Operator):#準備
    """準備"""
    bl_idname = "object.myobject_964581"
    bl_label = "準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        ######################################################
        #準備
        ######################################################
        """
        ・コンストレイントの非表示
        ・全ボーンローテーション初期化→なしで
        """
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                    constraint.mute = True
        
        
        bpy.ops.pose.select_all(action='SELECT')
        #bpy.ops.pose.rot_clear()
        bpy.context.space_data.transform_orientation = 'LOCAL'
        
        #空移動でアップデート
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}
########################################



#########################################
##ポーズミラーリング
#########################################
class MYOBJECT_314879(bpy.types.Operator):#ポーズミラーリング
    """選択ボーンのポーズをミラーリング"""
    bl_idname = "object.myobject_314879"
    bl_label = "ポーズミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)

        return {'FINISHED'}
#########################################



def update_armaturesystem(self, context, mute_consraints):
    """
    シングルなアーマチュアとオブジェクトのペアではこれでよい、が、
    複数くくりつけてあるものをどうするかが問題。
    →childrenの中で、Armatureがついてる奴ピックアップすればいい！
    """
    #アーマチュアを選択して、あとは自動でやる
    if active().type != "ARMATURE":
        return

    armature = active()
    mode("OBJECT")
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    childrenall = get_selected_list()
    deselect()
    activate(armature)

    #コンストレイントを無効にする

    activate(armature)
    mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    if mute_consraints:
        for bone in armature.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                    constraint.mute = True

        
    mode("OBJECT")

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    deselect()


    targetobjects = []
    #アーマチュアmodがついている子をターゲットリストにいれる
    for obj in armature.children:
        if obj.type == "MESH":
            modu = Modutils(obj)
            arm = modu.find_bytype("ARMATURE")
            if arm != None:
                    targetobjects.append(obj)

    deformedobjects = []
    #! armature.childrenの中にcageの子とか含まれてない！
    for obj in childrenall:
        activate(obj)
        #self.report({"INFO"},obj.name)
        modu = Modutils(obj)
        #アーマチュアついてないのでミラーとメッシュデフォーム適用する
        meshdeforms = modu.find_bytype_list("MESH_DEFORM")
        for mod in meshdeforms:
            self.report({"INFO"},obj.name + " has MeshDeform")
            #ミラー適用
            mrrs = modu.find_bytype_list("MIRROR")
            for mrr in mrrs:
                bpy.ops.object.modifier_apply(modifier=mrr.name)

            deformedobjects.append([obj, mod.object])
            bpy.ops.object.modifier_apply(modifier=mod.name)

    #deformedobjects = list(set(deformedobjects))

    #cages = []



    ##ターゲット群をペアレント解除する
    deselect()
    for obj in targetobjects:
        obj.hide = False
    select(targetobjects)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    #for obj in targetobjects:
    #    bpy.context.scene.objects.active = obj
    #    obj.hide = False
    #    self.report({"INFO"},obj.name)
    #    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
    mode("OBJECT")

    mirrored_objects = []

    #オブジェクト側：mod適用
    for obj in targetobjects:
        activate(obj)
        modu = Modutils(obj)

        mrrs = modu.find_bytype_list("MIRROR")
        for mod in mrrs:
            mirrored_objects.append(obj)
            bpy.ops.object.modifier_remove(modifier=mod.name)

        arms = modu.find_bytype_list("ARMATURE")
        for mod in arms:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    #重複削除
    mirrored_objects = list(set(mirrored_objects))

    for obj in targetobjects:
        activate(obj)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        
    #アーマチュア側：デフォルトのポーズに適用
    activate(armature)
    mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.armature_apply()
    mode("OBJECT")
    #OK
        
        
        
    #再リンク
    #全部選択解除
    deselect()
        
    #アーマチュアとオブジェクトを選択
    select(targetobjects)
    armature.select = True
        
    #アーマチュアをアクティブオブジェクトに
    activate(armature)
    #空のウェイトでペアレント
    bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False, keep_transform=False)
    #オブジェクト側：アーマチュアを一番上にもってく
    #しまった！mirrorはアーマチュアより上になきゃいけない！！

    #ミラーのつけなおし
    for obj in mirrored_objects:
        activate(obj)
        modu = Modutils(obj)
        mrr = modu.add("Mirror","MIRROR")
        mrr.mirror_object = armature

    #mod順整列
    for obj in targetobjects:
        modu = Modutils(obj)
        modu.sort()

        #activate(obj)
        #modu = Modutils(obj)

        #mods = modu.find_bytype_list("ARMATURE")
        #for mod in mods:
        #    modu.move_top(mod)
        #mods = modu.find_bytype_list("MIRROR")
        #for mod in mods:
        #    modu.move_top(mod)
    

    #コンストレイントを有効にする
    activate(armature)
    mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    for bone in armature.pose.bones:
        if(armature.data.bones[bone.name].select == True):
            for constraint in bone.constraints:
                constraint.mute = False
    
    #メッシュデフォームのつけなおし
    for pair in deformedobjects:
        obj = pair[0]
        activate(obj)
        modu = Modutils(obj)
        mod = modu.add("MeshDeform","MESH_DEFORM")
        mod.object = pair[1]
        bpy.ops.object.meshdeform_bind(modifier=mod.name)
        modu.sort()


    #空移動でアップデート
    bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

########################################
#アップデート
########################################
class MYOBJECT_164873(bpy.types.Operator):#アップデート
    """アップデート"""
    bl_idname = "object.myobject_164873"
    bl_label = "アップデート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        ######################################################
        #後処理
        ######################################################
        update_armaturesystem(self, context, True)

        return {'FINISHED'}
########################################

########################################
#アップデート(C有効)
########################################
class MYOBJECT_164873a(bpy.types.Operator):#アップデート(C有効)
    """アップデート(コンストレイント有効)"""
    bl_idname = "object.myobject_164873a"
    bl_label = "アップデート(C有効)"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        ######################################################
        #後処理
        ######################################################
        update_armaturesystem(self, context, False)

        return {'FINISHED'}
########################################


#    def execute(self, context):
#        ######################################################
#        #後処理
#        ######################################################
        
#        """
#        シングルなアーマチュアとオブジェクトのペアではこれでよい、が、
#        複数くくりつけてあるものをどうするかが問題。
#        →childrenの中で、Armatureがついてる奴ピックアップすればいい！
#        """
#        #アーマチュアを選択して、あとは自動でやる
#        if bpy.context.scene.objects.active.type != "ARMATURE":
#            #self.report(type=‘WARNING’,message="アーマチュアを選択すること！")
#            return

#        armature = bpy.context.scene.objects.active


#        #コンストレイントを無効にする
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        for bone in bpy.context.object.pose.bones:
#            if(bpy.context.object.data.bones[bone.name].select == True):
#                for constraint in bone.constraints:
#                    constraint.mute = True

        
#        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#        bpy.ops.object.select_all(action='SELECT')
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
#        bpy.ops.object.select_all(action='DESELECT')

#        targetobjects = []
#        #アーマチュアmodがついている子をターゲットリストにいれる
#        for obj in armature.children:
#            if obj.type == "MESH":
#                for mod in obj.modifiers:
#                    if mod.type == "ARMATURE":
#                        targetobjects.append(obj)
#                        break
        
#        #ターゲット群をペアレント解除する
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            obj.hide = False
#            self.report({"INFO"},obj.name)
#            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
#        bpy.ops.object.mode_set(mode='OBJECT')

#        mirrored_objects = []

#        #オブジェクト側：アーマチュア適用
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            for mod in obj.modifiers:
#                if mod.type == "MIRROR":
#                    #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
#                    #bpy.ops.object.modifier_apply(modifier=mod.name)
#                    mirrored_objects.append(obj)
#                    bpy.ops.object.modifier_remove(modifier=mod.name)
#                if mod.type == "ARMATURE":
#                    #適用する
#                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')


        
#        #アーマチュア側：デフォルトのポーズに適用
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        bpy.ops.pose.armature_apply()
#        bpy.ops.object.mode_set(mode='OBJECT')
#        #OK
        
        
        
#        #再リンク
#        #全部選択解除
#        for obj in bpy.data.objects:
#            obj.select = False
        
        
#        #アーマチュアとオブジェクトを選択
#        armature.select = True
#        for obj in targetobjects:
#            obj.select = True
        
        
#        #アーマチュアをアクティブオブジェクトに
#        bpy.context.scene.objects.active = armature
#        #空のウェイトでペアレント
#        bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False, keep_transform=False)
##        bpy.ops.object.parent_set(type='ARMATURE_AUTO', xmirror=False,
##        keep_transform=False)
#        #オブジェクト側：アーマチュアを一番上にもってく
#        #しまった！mirrorはアーマチュアより上になきゃいけない！！

#        #ミラーのつけなおし
#        for obj in mirrored_objects:
#            activate(obj)
#            bpy.ops.object.modifier_add(type='MIRROR')
#            mod = getnewmod(obj)
#            mod.mirror_object = armature

#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            modslen = len(obj.modifiers)
#            mod = obj.modifiers[modslen - 1]
#            for n in range(0,modslen):
#                bpy.ops.object.modifier_move_up(modifier=mod.name)
#            #mirrorはアーマチュアより上に。
#            for mod in obj.modifiers:
#                if mod.type == "MIRROR":
#                    for n in range(0,modslen):
#                        bpy.ops.object.modifier_move_up(modifier=mod.name)
        
        
        
#        #コンストレイントを有効にする
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        for bone in bpy.context.object.pose.bones:
#            if(bpy.context.object.data.bones[bone.name].select == True):
#                for constraint in bone.constraints:
#                    constraint.mute = False
        
#        #空移動でアップデート
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

#        return {'FINISHED'}



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#アーマチュアユーティリティ
########################################
class CATEGORYBUTTON_744202(bpy.types.Operator):#アーマチュアユーティリティ
    """アーマチュアユーティリティ"""
    bl_idname = "object.categorybutton_744202"
    bl_label = "アーマチュアユーティリティ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("アーマチュアユーティリティ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

############################################################################################################################
uiitem("素体システム用リネーマ")
############################################################################################################################






########################################
#ジオメトリ
########################################
class MYOBJECT_244616(bpy.types.Operator):#ジオメトリ
    """素体ジオメトリ"""
    bl_idname = "object.myobject_244616"
    bl_label = "素体ジオメトリ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label

        return {'FINISHED'}
########################################

########################################
#素体アーマチュア
########################################
class MYOBJECT_589321(bpy.types.Operator):#素体アーマチュア
    """素体アーマチュア"""
    bl_idname = "object.myobject_589321"
    bl_label = "素体アーマチュア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#ArmatureController
########################################
class MYOBJECT_573567(bpy.types.Operator):#ArmatureController
    """ArmatureController"""
    bl_idname = "object.myobject_573567"
    bl_label = "ArmatureController"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#手コントローラ右
########################################
class MYOBJECT_285809(bpy.types.Operator):#手コントローラ右
    """手コントローラ右"""
    bl_idname = "object.myobject_285809"
    bl_label = "手コントローラ右"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#手コントローラ左
########################################
class MYOBJECT_431070(bpy.types.Operator):#手コントローラ左
    """手コントローラ左"""
    bl_idname = "object.myobject_431070"
    bl_label = "手コントローラ左"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#右手
########################################
class MYOBJECT_116809(bpy.types.Operator):#右手
    """右手"""
    bl_idname = "object.myobject_116809"
    bl_label = "右手"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#左手
########################################
class MYOBJECT_694161(bpy.types.Operator):#左手
    """左手"""
    bl_idname = "object.myobject_694161"
    bl_label = "左手"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#右足
########################################
class MYOBJECT_424374(bpy.types.Operator):#右足
    """右足"""
    bl_idname = "object.myobject_424374"
    bl_label = "右足"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#左足
########################################
class MYOBJECT_372755(bpy.types.Operator):#左足
    """左足"""
    bl_idname = "object.myobject_372755"
    bl_label = "左足"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        active().name = self.bl_label
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("標準ボーンリネーマ（Rigify準拠）")
############################################################################################################################




def bone_rename(bonename):
    arm = active()
    if arm.type != "ARMATURE":
        self.report({"INFO"},"アーマチュアを選択してください")
        return {'CANCELLED'}
    mode("EDIT")
    bone = arm.data.edit_bones.active
    bone.name = bonename



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#head
########################################
class MYOBJECT_851815(bpy.types.Operator):#head
    """head"""
    bl_idname = "object.myobject_851815"
    bl_label = "head"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#neck
########################################
class MYOBJECT_862554(bpy.types.Operator):#neck
    """neck"""
    bl_idname = "object.myobject_862554"
    bl_label = "neck"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#chest
########################################
class MYOBJECT_632665(bpy.types.Operator):#chest
    """chest"""
    bl_idname = "object.myobject_632665"
    bl_label = "chest"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#spine
########################################
class MYOBJECT_886883(bpy.types.Operator):#spine
    """spine"""
    bl_idname = "object.myobject_886883"
    bl_label = "spine"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#hips
########################################
class MYOBJECT_916888(bpy.types.Operator):#hips
    """hips"""
    bl_idname = "object.myobject_916888"
    bl_label = "hips"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#root
########################################
class MYOBJECT_324118(bpy.types.Operator):#root
    """root"""
    bl_idname = "object.myobject_324118"
    bl_label = "root"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#shoulder.R
########################################
class MYOBJECT_403000(bpy.types.Operator):#shoulder.R
    """shoulder.R"""
    bl_idname = "object.myobject_403000"
    bl_label = "shoulder.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


########################################
#shoulder.L
########################################
class MYOBJECT_779120(bpy.types.Operator):#shoulder.L
    """shoulder.L"""
    bl_idname = "object.myobject_779120"
    bl_label = "shoulder.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#upper_arm.R
########################################
class MYOBJECT_148790(bpy.types.Operator):#upper_arm.R
    """upper_arm.R"""
    bl_idname = "object.myobject_148790"
    bl_label = "upper_arm.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#upper_arm.L
########################################
class MYOBJECT_598468(bpy.types.Operator):#upper_arm.L
    """upper_arm.L"""
    bl_idname = "object.myobject_598468"
    bl_label = "upper_arm.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#forearm.R
########################################
class MYOBJECT_148513(bpy.types.Operator):#forearm.R
    """forearm.R"""
    bl_idname = "object.myobject_148513"
    bl_label = "forearm.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


########################################
#forearm.L
########################################
class MYOBJECT_928612(bpy.types.Operator):#forearm.L
    """forearm.L"""
    bl_idname = "object.myobject_928612"
    bl_label = "forearm.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#hand.R
########################################
class MYOBJECT_43548(bpy.types.Operator):#hand.R
    """hand.R"""
    bl_idname = "object.myobject_43548"
    bl_label = "hand.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#hand.L
########################################
class MYOBJECT_862708(bpy.types.Operator):#hand.L
    """hand.L"""
    bl_idname = "object.myobject_862708"
    bl_label = "hand.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#thigh.R
########################################
class MYOBJECT_474630(bpy.types.Operator):#thigh.R
    """thigh.R"""
    bl_idname = "object.myobject_474630"
    bl_label = "thigh.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################
########################################
#thigh.L
########################################
class MYOBJECT_550261(bpy.types.Operator):#thigh.L
    """thigh.L"""
    bl_idname = "object.myobject_550261"
    bl_label = "thigh.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#shin.R
########################################
class MYOBJECT_371561(bpy.types.Operator):#shin.R
    """shin.R"""
    bl_idname = "object.myobject_371561"
    bl_label = "shin.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#shin.L
########################################
class MYOBJECT_348617(bpy.types.Operator):#shin.L
    """shin.L"""
    bl_idname = "object.myobject_348617"
    bl_label = "shin.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#heel.R
########################################
class MYOBJECT_420903(bpy.types.Operator):#heel.R
    """heel.R"""
    bl_idname = "object.myobject_420903"
    bl_label = "heel.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#heel.L
########################################
class MYOBJECT_559040(bpy.types.Operator):#heel.L
    """heel.L"""
    bl_idname = "object.myobject_559040"
    bl_label = "heel.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#foot.R
########################################
class MYOBJECT_505403(bpy.types.Operator):#foot.R
    """foot.R"""
    bl_idname = "object.myobject_505403"
    bl_label = "foot.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#foot.L
########################################
class MYOBJECT_120526(bpy.types.Operator):#foot.L
    """foot.L"""
    bl_idname = "object.myobject_120526"
    bl_label = "foot.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#toe.R
########################################
class MYOBJECT_288663(bpy.types.Operator):#toe.R
    """toe.R"""
    bl_idname = "object.myobject_288663"
    bl_label = "toe.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#toe.L
########################################
class MYOBJECT_135779(bpy.types.Operator):#toe.L
    """toe.L"""
    bl_idname = "object.myobject_135779"
    bl_label = "toe.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################













#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("アーマチュア差し替え")
############################################################################################################################





########################################
#選択の形状をアクティブにあわせる
########################################
class MYOBJECT_729233(bpy.types.Operator):#選択の形状をアクティブにあわせる
    """選択の形状をアクティブにあわせる"""
    bl_idname = "object.myobject_729233"
    bl_label = "選択の形状をアクティブにあわせる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        source_arm = active()
        target_arm = None

        for obj in bpy.context.selected_objects:
            if obj != source_arm:
                target_arm = obj
                break

        if source_arm == None or source_arm.type != "ARMATURE" or target_arm == None or target_arm.type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}


        source_arm.data.pose_position = "REST"
        target_arm.data.pose_position = "REST"

        #Xミラー解除
        target_arm.data.use_mirror_x = False


        #ペアレント解除→システムごと差し替えるからしないほうがいい
        #mode("OBJECT")
        #deselect()
        #activate(target_arm)
        #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        #位置あわせ
        target_arm.location = source_arm.location

        #target_arm.location[1] = source_arm.location[1]
        #target_arm.location[2] = source_arm.location[2]

        activate(target_arm)
        mode("EDIT")

        bone_names = []

        for bone in target_arm.data.edit_bones:
            ##デフォルト名はスルー。どう対応してるかわかったもんじゃないから
            #if "Bone." in bone.name:
            #    continue
            bone_names.append(bone.name)
            self.report({"INFO"},bone.name)



        #形状をあわせる
        #ボーンの接続を全て切る
        #mode("OBJECT")
        #activate(target_arm)
        #mode("EDIT")
        #for bone in target_arm.data.edit_bones:
        #    bone.use_connect = False


        #とりあえず数値をあらかじめ取得してみる
        mode("OBJECT")
        activate(source_arm)
        mode("EDIT")
        source_data = {}
        for bone in source_arm.data.edit_bones:
            source_data[bone.name] = [copy.deepcopy(bone.head),copy.deepcopy(bone.tail)]
            self.report({"INFO"},"src:"+bone.name)

        mode("OBJECT")
        activate(target_arm)
        mode("EDIT")
        for bone_name in bone_names:
            #mode("OBJECT")
            #mode("EDIT")
            if bone_name not in target_arm.data.edit_bones:
                continue
            if bone_name not in source_data:
                continue

            #選択解除
            bpy.ops.armature.select_all(action='DESELECT')

            ebone = target_arm.data.edit_bones[bone_name]
            target_arm.data.edit_bones.active = ebone

            ebone.head = source_data[bone_name][0]
            ebone.tail = source_data[bone_name][1]

            self.report({"INFO"},"move:"+ebone.name+" 予定地名:"+bone_name+" 予定地:"+str(source_data[bone_name][0])+" 現在地:"+str(ebone.head))

        #Xミラー
        target_arm.data.use_mirror_x = True
        
        return {'FINISHED'}
########################################

########################################
#選択からアクティブへリターゲット
########################################
class MYOBJECT_546712(bpy.types.Operator):#選択からアクティブへリターゲット
    """選択からアクティブへリターゲット"""
    bl_idname = "object.myobject_546712"
    bl_label = "選択からアクティブへリターゲット"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        source_arm = None
        target_arm = active()
        
        #隠れてるものがあるとまずい。
        mode("OBJECT")
        bpy.ops.object.hide_view_clear()


        for obj in bpy.context.selected_objects:
            if obj != target_arm:
                source_arm = obj
                break

        if source_arm == None or source_arm.type != "ARMATURE" or target_arm == None or target_arm.type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}

        #ターゲットの子を全て削除
        deselect()
        activate(target_arm)
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #メッシュだけ
        for obj in get_selected_list():
            if obj.type != "MESH":
                obj.select = False
        delete(get_selected_list())


        #ソースの子を取得
        deselect()
        activate(source_arm)
        bpy.ops.object.select_grouped(type='CHILDREN')
        
        #オブジェクトのペアレント状態を保存する
        source_children_data = {}
        for obj in get_selected_list():
            #ペアレントはsource_armにきまってんのでペアレントオブジェクトの情報はいらない
            source_children_data[obj.name] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type}
            #self.report({"INFO"}, str(source_children_data[obj.name]))
        #ペアレント解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')



        #リターゲット
        #まずは通常ペアレントだけ
        self.report({"INFO"},str(source_children_data))
        for obj_data_name in source_children_data:
            obj_data = source_children_data[obj_data_name]
            deselect()
            #self.report({"INFO"},str(obj_data))
            obj = bpy.data.objects[obj_data["name"]]
            obj.select = True
            activate(target_arm)
            target_arm.select = True


            if obj_data["parent_type"] == "OBJECT":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            if obj_data["parent_type"] == "BONE":
                mode("POSE")
                #アクティブボーンの設定
                bones = active().data.bones
                if obj_data["parent_bone"] not in bones:
                    continue
                bones.active = bones[obj_data["parent_bone"]]
                #ペアレントつける
                bpy.ops.object.parent_set(type='BONE_RELATIVE')


                #obj.parent_type = "BONE"
                #obj.parent_bone = obj_data["parent_bone"]

        #mod設定
        for obj_data_name in source_children_data:
            obj_data = source_children_data[obj_data_name]
            deselect()
            obj = bpy.data.objects[obj_data["name"]]
            activate(obj)
            for mod in obj.modifiers:
                if mod.type == "MIRROR":
                    if mod.mirror_object == source_arm:
                        mod.mirror_object = target_arm
                if mod.type == "ARMATURE":
                        mod.object = target_arm

        #ポーズオン
        target_arm.data.pose_position = "POSE"
        source_arm.data.pose_position = "POSE"



        return {'FINISHED'}
########################################















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#BlenRigヘルパー
########################################
class CATEGORYBUTTON_456539(bpy.types.Operator):#BlenRigヘルパー
    """BlenRigヘルパー"""
    bl_idname = "object.categorybutton_456539"
    bl_label = "BlenRigヘルパー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("BlenRigヘルパー",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("アーマチュア")
############################################################################################################################

#バインドするならTrue。しないならFalse。
def blenrig_mdbinding(objects, bound):
    if "BlenRig_mdef_cage" in bpy.data.objects:
        cage = bpy.data.objects["BlenRig_mdef_cage"]
        #関連バインドの解除→選択物のみ。負荷軽減。
        for obj in objects:
            if obj.type == "MESH":
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        if mod.object == cage:
                            #バインド変更
                            if mod.is_bound != bound:
                                activate(obj)
                                bpy.ops.object.meshdeform_bind(modifier=mod.name)

    pass

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#体型編集
########################################
class MYOBJECT_545067(bpy.types.Operator):#体型編集
    """体型編集"""
    bl_idname = "object.myobject_545067"
    bl_label = "体型編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #バインド解除
        blenrig_mdbinding(get_selected_list(), False)

        bpy.context.scene.layers[10] = True
        bpy.context.scene.layers[11] = True

        rig = active()
        if rig.type != "ARMATURE":
            return {'CANCELLED'}


        #rig = None
        #for obj in bpy.data.objects:
        #    if "blenrig" in obj.name:
        #        rig = obj
        #rig = bpy.data.objects["biped_blenrig"]
        if rig != None:
            rig.show_x_ray = True
            activate(rig)
            mode("POSE")
            rig.data.reproportion = True

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#右側選択
########################################
class MYOBJECT_942054(bpy.types.Operator):#右側選択
    """右側選択"""
    bl_idname = "object.myobject_942054"
    bl_label = "右側選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.select_pattern(pattern="*_R")

        return {'FINISHED'}
########################################






########################################
#ミラーリング
########################################
class MYOBJECT_734967(bpy.types.Operator):#ミラーリング
    """ミラーリング"""
    bl_idname = "object.myobject_734967"
    bl_label = "ミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)

        return {'FINISHED'}
########################################

########################################
#左側選択
########################################
class MYOBJECT_384660(bpy.types.Operator):#左側選択
    """左側選択"""
    bl_idname = "object.myobject_384660"
    bl_label = "左側選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.select_pattern(pattern="*_L")

        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アクティブのグループのみ表示
########################################
class MYOBJECT_315193(bpy.types.Operator):#アクティブのグループのみ表示
    """アクティブのグループのみ表示"""
    bl_idname = "object.myobject_315193"
    bl_label = "アクティブのグループのみ表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.pose.select_grouped(type='GROUP')
        bpy.ops.pose.select_all(action='INVERT')
        bpy.ops.pose.hide(unselected=False)

        return {'FINISHED'}
########################################


########################################
#全て表示
########################################
class MYOBJECT_705250(bpy.types.Operator):#全て表示
    """全て表示"""
    bl_idname = "object.myobject_705250"
    bl_label = "全て表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.pose.reveal()

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#完了
########################################
class MYOBJECT_859280(bpy.types.Operator):#完了
    """完了"""
    bl_idname = "object.myobject_859280"
    bl_label = "完了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        current = active()
        mode("OBJECT")
        #armature = bpy.data.objects["biped_blenrig"]
        #cage = bpy.data.objects["BlenRig_mdef_cage"]
        #proxy = bpy.data.objects["BlenRig_proxy_model"]
        #armature = find("blenrig")
        if current.type != "ARMATURE":
            return {'CANCELLED'}
        armature = current
        cage = find("BlenRig_mdef_cage")
        proxy = find("BlenRig_proxy_model")

        ######################################################################
        #Childrenメッシュの下処理
        ######################################################################

        activate(armature)
        targetobjects = []
        targetobjects_data = {}
        #アーマチュアmodがついている子をターゲットリストにいれる
        for obj in armature.children:
            targetobjects.append(obj)
            targetobjects_data[obj.data] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type, "armature":False}
            if obj.type == "MESH":
                if obj == cage or obj == proxy:
                    continue


                for mod in obj.modifiers:
                    if mod.type == "ARMATURE":
                        targetobjects_data[obj.data] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type, "armature":True}
                        break

        #ターゲット群をペアレント解除する
        for obj in targetobjects:
            obj.hide = False
            deselect()
            activate(obj)
            self.report({"INFO"},obj.name)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        bpy.ops.object.mode_set(mode='OBJECT')
    

        mirrored_objects = []

        #オブジェクト側：アーマチュア適用
        for obj in targetobjects:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == "MIRROR":
                    mirrored_objects.append(obj)
                    #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                    #bpy.ops.object.modifier_apply(modifier=mod.name)
                    #むしろミラー除去
                    bpy.ops.object.modifier_remove(modifier=mod.name)
                if mod.type == "ARMATURE":
                    #適用する
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                        pass
                    except  :
                        self.report({"INFO"},"mod適用エラー："+obj.name+"/"+mod.name)
                        pass
        
        for obj in targetobjects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')



        #一旦Blenrigの処理へ

        ######################################################################
        #Blenrigパート
        ######################################################################
        #ケージのメッシュベイク
        if cage is not None:
            deselect()
            bpy.context.scene.layers[11] = True
            activate(cage)
            cage.select = True
            mode("OBJECT")
            bpy.ops.blenrig5.mesh_pose_baker()
            cage.select = False

        #プロクシのメッシュベイク
        if proxy is not None:
            deselect()
            bpy.context.scene.layers[1] = True
            activate(proxy)
            proxy.select = True
            mode("OBJECT")
            bpy.ops.blenrig5.mesh_pose_baker()

            bpy.context.scene.layers[1] = False

        #アーマチュアのベイク
        deselect()
        activate(armature)
        armature.select = True
        mode("POSE")
        bpy.ops.pose.reveal()
        bpy.ops.blenrig5.armature_baker()


        ######################################################################
        #Childrenメッシュの更新
        ######################################################################
        deselect()
        #アーマチュアとオブジェクトを選択

        #再ペアレント
        for obj_data_name in targetobjects_data:
            obj_data = targetobjects_data[obj_data_name]
            deselect()
            obj = bpy.data.objects[obj_data["name"]]
            obj.select = True
            activate(armature)
            armature.select = True


            if obj_data["parent_type"] == "OBJECT":
                if obj_data["armature"]:
                    bpy.ops.object.parent_set(type='ARMATURE_NAME')
                else:
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            if obj_data["parent_type"] == "BONE":
                activate(armature)
                mode("POSE")
                #アクティブボーンの設定
                bones = active().data.bones
                if obj_data["parent_bone"] not in bones:
                    continue
                bones.active = bones[obj_data["parent_bone"]]
                self.report({"INFO"},bones.active.basename)

                mode("POSE")
                self.report({"INFO"},"active:"+active().data.bones.active.basename)
                

                #オブジェクトレイヤーを全表示に
                current_objlayers = [True for i in range(32)]
                for i in range(32):
                    current_objlayers[i] = active().data.layers[i]
                #copy.deepcopy(active().data.layers)
                active().data.layers = [True for i in range(32)]


                #ペアレントつける
                bpy.ops.object.parent_set(type='BONE_RELATIVE')

                #オブジェクトレイヤーを戻す
                active().data.layers = current_objlayers


        ##空のウェイトでペアレント
        #armature.select = True
        ##select(targetobjects)
        #activate(armature)
        #bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False, keep_transform=False)

        #アーマチュアを一番上に
        for obj in targetobjects:
            if obj.type == "MESH":
                activate(obj)
                modslen = len(obj.modifiers)
                if modslen > 0:
                    #一番新しい奴＝アーマチュア
                    mod = obj.modifiers[modslen - 1]
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)


        #ミラーのつけなおし
        for obj in mirrored_objects:
            if obj.type == "MESH":
                activate(obj)
                bpy.ops.object.modifier_add(type='MIRROR')
                mod = getnewmod(obj)
                mod.mirror_object = armature

        #ミラーは一番上に。
        for obj in mirrored_objects:
            if obj.type == "MESH":
                activate(obj)
                modslen = len(obj.modifiers)
                if modslen > 0:
                    mod = obj.modifiers[modslen - 1]
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)



        ######################################################################
        #Blenrigパート
        ######################################################################
        activate(armature)
        armature.data.reproportion = False

        #再バインド
        #blenrig_mdbinding(armature.children, True)
        activate(current)

        return {'FINISHED'}
########################################




########################################
#再バインド
########################################
class MYOBJECT_115485(bpy.types.Operator):#再バインド
    """再バインド"""
    bl_idname = "object.myobject_115485"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        armature = bpy.data.objects["biped_blenrig"]
        blenrig_mdbinding(armature.children, True)
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("ケージ")
############################################################################################################################

"""
ケージ編集
ベイク
"""
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ケージスカルプト
########################################
class MYOBJECT_724488(bpy.types.Operator):#ケージスカルプト
    """ケージスカルプト。バインド操作は選択物のみ。"""
    bl_idname = "object.myobject_724488"
    bl_label = "ケージスカルプト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SCULPTMODE_HLT",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #ケージレイヤの表示
        bpy.context.scene.layers[11] = True
        
        mode("OBJECT")
        cage = bpy.data.objects["BlenRig_mdef_cage"]
        cage.select = True

        #バインドは一番上につくので、subdiv0にする
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0

        #関連バインドの解除→洗濯物のみ。負荷軽減。
        blenrig_mdbinding(get_selected_list(),False)

        reject_notmesh()
        localview()

        bpy.context.scene.layers[11] = True
        activate(cage)
        cage.draw_type = "TEXTURED"
        mode("SCULPT")

        return {'FINISHED'}
########################################

########################################
#完了
########################################
class MYOBJECT_371121(bpy.types.Operator):#完了
    """完了"""
    bl_idname = "object.myobject_371121"
    bl_label = "完了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        globalview()

        cage = bpy.data.objects["BlenRig_mdef_cage"]
        mode("OBJECT")
        activate(cage)
        mode("OBJECT")
        cage.draw_type = "WIRE"

        

        #関連再バインド
        blenrig_mdbinding(bpy.data.objects, True)
        activate(cage)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


















################################################################################
#UIカテゴリ
########################################
#VectorDisplacementモデル
########################################
class CATEGORYBUTTON_290440(bpy.types.Operator):#VectorDisplacementモデル
    """VectorDisplacementモデル"""
    bl_idname = "object.categorybutton_290440"
    bl_label = "VectorDisplacementモデル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("VectorDisplacementモデル",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




########################################
#セミオートインポート・セットアップ
########################################
class MYOBJECT_475352(bpy.types.Operator):#セミオートインポート・セットアップ
    """マップはtexturesにいれること"""
    bl_idname = "object.myobject_475352"
    bl_label = "オートインポート・セットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #objのインポート
        import bpy
        import os
        import re
        
        
        for obj in bpy.data.objects:
            obj.select = False
        
        dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "")
        
        files = os.listdir(dir)
        for file in files:
            if re.search(r"meta", file) is not None: continue
            if re.search(r"(fbx)|(FBX)|(obj)|(OBJ)|(lwo)|(LWO)",file) is not None :
                loaded = False
                if re.search(r"(fbx)|(FBX)",file) is not None :
                    bpy.ops.import_scene.fbx(filepath=file)
                    loaded = True
                if re.search(r"(obj)|(OBJ)",file) is not None :
                    bpy.ops.import_scene.obj(filepath=file)
                    loaded = True
                if re.search(r"(lwo)|(LWO)",file) is not None :
                    bpy.ops.import_scene.lwo(filepath=file)
                    loaded = True
                if loaded is False : continue
                #グループ化
                groupname = os.path.splitext(os.path.basename(file))[0]
                bpy.ops.group.create(name=groupname)
        
        
        #テクスチャの読み込み
        #dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "") + os.sep + "textures" + os.sep
        #やっぱtexturesめんどくさかった
        dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "") + os.sep
        
        files = os.listdir(dir)
        for file in files:
            print(dir + "\\" + file)
            if re.search(r"meta", file) is not None: continue
            if re.search(r"(exr)|(tif)|(tiff)|(jpg)|(png)",file) is not None :
                bpy.ops.image.open(filepath=dir + "\\" + file)
                img = bpy.data.images[file]
                bpy.ops.texture.new()
                #最後のテクスチャ
                lasttex = bpy.data.textures[len(bpy.data.textures) - 1]
                lasttex.name = file
                lasttex.image = img
                lasttex.use_clamp = False
        
        
        
        #modの準備
        for group in bpy.data.groups:
            for obj in group.objects:
                if obj.type == "MESH":
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_add(type='SUBSURF')
                    bpy.context.object.modifiers["Subsurf"].levels = 3
                    bpy.context.object.modifiers["Subsurf"].render_levels = 5
                    bpy.context.object.modifiers["Subsurf"].subdivision_type = 'CATMULL_CLARK'
                    bpy.ops.object.modifier_add(type='DISPLACE')
                    bpy.context.object.modifiers["Displace"].direction = 'RGB_TO_XYZ'
                    bpy.context.object.modifiers["Displace"].mid_level = 0
                    bpy.context.object.modifiers["Displace"].texture_coords = 'UV'
                    bpy.context.object.modifiers["Displace"].texture = bpy.data.textures[group.name + ".exr"]
                    bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
                    bpy.context.object.modifiers["CorrectiveSmooth"].use_only_smooth = True
        
        
        return {'FINISHED'}
########################################

########################################
#多重解像度モデル化
########################################
class MYOBJECT_954427(bpy.types.Operator):#多重解像度モデル化
    """多重解像度モデル化"""
    bl_idname = "object.myobject_954427"
    bl_label = "多重解像度モデル化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        targets = get_selected_list()
        for target in targets:
            bpy.context.scene.render.use_simplify = True
            bpy.context.scene.render.simplify_subdivision = 0
            deselect()
            activate(target)
            target.select = True
            #subdivレベルを得る
            div = 0
            for mod in target.modifiers:
                if mod.type == "SUBSURF":
                    if mod.render_levels > div:
                        mod.levels = mod.render_levels

                    div = mod.levels
            
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            newone = active()

            #mod削除
            for mod in newone.modifiers:
                bpy.ops.object.modifier_remove(modifier=mod.name)
            
            #多重解像度
            bpy.ops.object.modifier_add(type='MULTIRES')
            mod = getnewmod(newone)
            #分割
            for n in range(div):
                bpy.ops.object.multires_subdivide(modifier=mod.name)

            target.select = True
            bpy.context.scene.render.use_simplify = False
            #再形成
            bpy.ops.object.multires_reshape(modifier=mod.name)

            name = target.name
            #元のを削除
            deselect()
            target.select = True
            delete(get_selected_list())
            newone.name = name

        self.report({"INFO"},"完了")
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#MarvelousDesigner
########################################
class CATEGORYBUTTON_425599(bpy.types.Operator):#MarvelousDesigner
    """MarvelousDesigner"""
    bl_idname = "object.categorybutton_425599"
    bl_label = "MarvelousDesigner"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("MarvelousDesigner",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("オート")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


#バックグラウンドじゃキーフレーム挿入できないんだった…
#########################################
##オートアバターBG
#########################################
#class MYOBJECT_747942(bpy.types.Operator):#オートアバターBG
#    """オートアバターBG"""
#    bl_idname = "object.myobject_747942"
#    bl_label = "オートアバターBG"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.ops.wm.save_mainfile()
#        exec_externalutils("autoMDAvatar.py")
#        return {'FINISHED'}
#########################################







########################################
#オートアバター
########################################
class MYOBJECT_302662(bpy.types.Operator):#オートアバター
    """カメラ範囲内のbodyを自動でアバター出力して終了する"""
    bl_idname = "object.myobject_302662"
    bl_label = "オートアバター"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #だめっぽい
        #個々に別ラインでバックグラウンドやらせてもいいかも

        #ターゲットになるプロクシアーマチュアを選択している、という前提
        #dataを見ればいい　同一のアーマチュアデータを参照している、で同定する
        #selection = get_selected_list()

        #armdata = []

        #for obj in selection:
        #    if obj.type == "ARMATURE":
        #       armdata.append(obj.data.name)
        
        #print("armdata:****************")
        #print(armdata)
                      
        framejump(10)


        #MD作業ファイル準備
        bpy.ops.object.myobject_902822()

        #bpy.context.scene.layers[0] = True
        #for i in range(19):
        #    bpy.context.scene.layers[i+1] = False
        #for i in range(5):
        #    bpy.context.scene.layers[i] = True

        #mode("OBJECT")
        #bpy.ops.object.select_all(action='SELECT')
        #bpy.ops.object.duplicates_make_real(use_base_parent=True,use_hierarchy=True)
        #bpy.ops.object.make_local(type='SELECT_OBDATA')

        ##proxyの全削除
        #prxs = find_list("_proxy")
        #delete(prxs)


        #bpy.ops.object.select_all(action='SELECT')


        #selection = get_selected_list()
        #for obj in selection:
        #    if obj.type == "ARMATURE":
        #        if obj.data.name in armdata:
        #            targets.append(obj)
        #            print(obj.data.name)
        #deselect()
        #select(targets)
        #print(targets)
        #bpy.ops.object.fjw_set_key()
        #bpy.ops.wm.quit_blender()

        bpy.ops.object.select_all(action='SELECT')
        reject_notmesh()
        selection = get_selected_list()

        targets = []

        for obj in selection:
            if "Body" in obj.name:
                modu = Modutils(obj)
                armt = modu.find("Armature")
                if armt != None:
                    #カメラに映っているもののみに実行する。
                    if checkIfIsInCameraView(obj):
                        #targets.append(obj)
                        targets.append(armt.object)

        for obj in targets:
            if obj == None:
                continue
            deselect()
            activate(obj)
            if obj.type == "ARMATURE":
                bpy.ops.object.framejump_10()
                bpy.ops.object.fjw_set_key()
            #MDDataに出力
            #bpy.ops.object.myobject_347662()
        
        ##元ファイルを開き直してdone
        #    #subprocess.Popen("EXPLORER " + bpy.data.filepath)
        #    #ばーっとひらいてつぎつぎ、というやり方にする　ただとじる
        #    bpy.ops.wm.quit_blender()

        #終了
        bpy.ops.object.myobject_628306()

        return {'FINISHED'}
########################################



########################################
#オートインポート
########################################
class MYOBJECT_487662(bpy.types.Operator):#オートインポート
    """オートインポート"""
    bl_idname = "object.myobject_487662"
    bl_label = "オートインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #存在確認
        blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath) + os.sep + "MDData" + os.sep + blendname + os.sep

        if not os.path.exists(dir):
            return {'CANCELLED'}

        files = os.listdir(dir)
        for file in files:
            targetname = file

            if targetname in bpy.data.objects:
                obj = bpy.data.objects[targetname]
                arm = find_child_bytype(obj, "ARMATURE")
                if arm is not None:
                    mode("OBJECT")
                    deselect()
                    activate(arm)

                    mode("POSE")
                    armu = ArmatureUtils(arm)
                    geo = armu.GetGeometryBone()
                    armu.activate(geo)
                    mode("POSE")

                    #インポート
                    import_mdresult(self,dir+file+os.sep+"result.obj")

        ##存在確認
        #dir = os.path.dirname(bpy.data.filepath) + os.sep + "MDData" + os.sep
        #blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]

        #if not os.path.exists(dir):
        #    return {'CANCELLED'}

        #files = os.listdir(dir)
        #for file in files:
        #    if "_result" not in file:
        #        continue

        #    targetname = file
        #    targetname = targetname.replace("avatar_","")
        #    targetname = targetname.replace("_result","")
        #    targetname = targetname.replace(blendname+"_","")
        #    targetname = targetname.replace(".obj","")

        #    if targetname in bpy.data.objects:
        #        obj = bpy.data.objects[targetname]
        #        arm = find_child_bytype(obj, "ARMATURE")
        #        if arm is not None:
        #            mode("OBJECT")
        #            deselect()
        #            activate(arm)

        #            mode("POSE")
        #            armu = ArmatureUtils(arm)
        #            geo = armu.GetGeometryBone()
        #            armu.activate(geo)
        #            mode("POSE")

        #            #インポート
        #            import_mdresult(self,dir+file)

        return {'FINISHED'}
########################################





#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("セットアップ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#MD作業ファイル準備
########################################
class MYOBJECT_902822(bpy.types.Operator):#MD作業ファイル準備
    """MD作業ファイル準備"""
    bl_idname = "object.myobject_902822"
    bl_label = "MD作業ファイル準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "_MDWork" not in bpy.data.filepath:
            bpy.ops.object.fjw_openlinkedfolder()

            #bpy.ops.wm.save_mainfile()
            framejump(10)
            dir = os.path.dirname(bpy.data.filepath)
            name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
            blend_md = dir + os.sep + name + "_MDWork.blend"
            bpy.ops.wm.save_as_mainfile(filepath=blend_md)

            bpy.context.scene.layers[0] = True
            for i in range(19):
                bpy.context.scene.layers[i+1] = False
            for i in range(5):
                bpy.context.scene.layers[i] = True

            mode("OBJECT")
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.duplicates_make_real(use_base_parent=True,use_hierarchy=True)

            #proxyの全削除
            prxs = find_list("_proxy")
            delete(prxs)

        return {'FINISHED'}
########################################

########################################
#元を開く（別窓）
########################################
class MYOBJECT_179920(bpy.types.Operator):#元を開く（別窓）
    """元を開く（別窓）"""
    bl_idname = "object.myobject_179920"
    bl_label = "元を開く（別窓）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        path = bpy.data.filepath.replace("_MDWork","")
        subprocess.Popen("EXPLORER " + path)
        
        return {'FINISHED'}
########################################







########################################
#戻る
########################################
class MYOBJECT_401078(bpy.types.Operator):#戻る
    """戻る"""
    bl_idname = "object.myobject_401078"
    bl_label = "戻る"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LOOP_BACK",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "_MDWork" in bpy.data.filepath:
            path = bpy.data.filepath.replace("_MDWork","")
            #bpy.ops.wm.open_mainfile(filepath = path)
            #os.system(path)
            subprocess.Popen("EXPLORER " + path)
            os.remove(bpy.data.filepath)
            bpy.ops.wm.quit_blender()

        return {'FINISHED'}
########################################

########################################
#終了
########################################
class MYOBJECT_628306(bpy.types.Operator):#終了
    """終了"""
    bl_idname = "object.myobject_628306"
    bl_label = "終了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "_MDWork" in bpy.data.filepath:
            os.remove(bpy.data.filepath)
            bpy.ops.wm.quit_blender()
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#選択プロクシから転送
########################################
class MYOBJECT_360702(bpy.types.Operator):#選択プロクシから転送
    """選択プロクシから転送"""
    bl_idname = "object.myobject_360702"
    bl_label = "選択プロクシから転送"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="NLA_PUSHDOWN",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        armature = None
        proxy = None
        selection = get_selected_list()
        for obj in selection:
            if "_proxy" in obj.name:
                proxy = obj
            else:
                armature = obj

        #self.report({"INFO"},armature.name)
        #self.report({"INFO"},proxy.name)
        activate(armature)
        mode("POSE")
        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
        armature.animation_data.action = proxy.animation_data.action
        #currentframe = bpy.context.scene.frame_current
        #if armature is not None and proxy is not None:
        #    framejump(0)
        #    TransferPose(proxy, armature)
        #    framejump(5)
        #    TransferPose(proxy, armature)
        #    framejump(10)
        #    TransferPose(proxy, armature)
        #    framejump(15)
        #    TransferPose(proxy, armature)
        #    framejump(currentframe)
        #    pass

        return {'FINISHED'}
########################################















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("obj+PointCache")
############################################################################################################################


def export_mdavatar(self, dir, name, openfolder=True):
        #アクティブオブジェクトのみ。
        #メッシュ以外だったら戻る
        obj = active()
        if obj.type != "MESH":
            self.report({"INFO"},"")
            return {'CANCELLED'}

        if not os.path.exists(dir):
            os.makedirs(dir)

        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2

        #裏ポリエッジオフ
        for mod in obj.modifiers:
            if "裏ポリエッジ" in mod.name:
                mod.show_viewport = False

        #フレーム1に移動
        bpy.ops.screen.frame_jump(end=False)
        #obj出力
        #dir = "G:" + os.sep + "MarvelousDesigner" + os.sep
        #dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath= dir + name + ".obj", use_selection=True)

        #PointCache出力
        #bpy.ops.export_shape.pc2(filepath= dir + "avatar.pc2", check_existing=False, rot_x90=True, world_space=True, apply_modifiers=True, range_start=1, range_end=10, sampling='1')
        bpy.ops.export_shape.mdd(filepath= dir + name + ".mdd", fps=6,frame_start=1,frame_end=10)

        #結果用の空ファイルを作っておく
        f = open(dir+"result.obj","w")
        f.close()

        #出力フォルダを開く
        if openfolder:
            os.system("EXPLORER " + dir)


########################################
#アバター出力
########################################
class MYOBJECT_738210(bpy.types.Operator):#アバター出力
    """アバター出力"""
    bl_idname = "object.myobject_738210"
    bl_label = "アバター出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        export_mdavatar(self, fujiwara_toolbox.conf.MarvelousDesigner_dir, "avatar")
        return {'FINISHED'}
########################################


########################################
#MDDataに出力
########################################
class MYOBJECT_347662(bpy.types.Operator):#MDDataに出力
    """MDDataに出力"""
    bl_idname = "object.myobject_347662"
    bl_label = "MDDataに出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        dir = os.path.dirname(bpy.data.filepath) + os.sep + "MDData" + os.sep

        blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        root = get_root(active())

        name = "avatar_" + blendname + "_" + root.name

        export_mdavatar(self, dir, name, False)
        return {'FINISHED'}
########################################







########################################
#アバターのみ
########################################
class MYOBJECT_287546(bpy.types.Operator):#アバターのみ
    """アバターのみ"""
    bl_idname = "object.myobject_287546"
    bl_label = "アバターのみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #アクティブオブジェクトのみ。
        #メッシュ以外だったら戻る
        obj = active()
        if obj.type != "MESH":
            self.report({"INFO"},"")
            return {'CANCELLED'}

        bpy.ops.wm.save_mainfile()

        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2

        #裏ポリエッジオフ
        for mod in obj.modifiers:
            if "裏ポリエッジ" in mod.name:
                mod.show_viewport = False

        #フレーム1に移動
        bpy.ops.screen.frame_jump(end=False)
        #obj出力
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath= dir + "avatar.obj", use_selection=True)


        #出力フォルダを開く
        os.system("EXPLORER " + dir)
        
        return {'FINISHED'}
########################################

########################################
#プロップ出力
########################################
class MYOBJECT_341922(bpy.types.Operator):#プロップ出力
    """プロップ出力"""
    bl_idname = "object.myobject_341922"
    bl_label = "プロップ出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #アクティブオブジェクトのみ。
        #メッシュ以外だったら戻る
        obj = active()
        if obj.type != "MESH":
            self.report({"INFO"},"")
            return {'CANCELLED'}

        bpy.ops.wm.save_mainfile()

        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2

        #フレーム1に移動→しない！
        #bpy.ops.screen.frame_jump(end=False)
        #obj出力
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath= dir + "prop.obj", use_selection=True)


        #出力フォルダを開く
        os.system("EXPLORER " + dir)
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("フレーム毎obj")
############################################################################################################################

########################################
#アバター出力
########################################
class MYOBJECT_501373(bpy.types.Operator):#アバター出力
    """アバター出力"""
    bl_idname = "object.myobject_501373"
    bl_label = "アバター出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2

        targetobj = active()

        if targetobj.type == "EMPTY":
            if targetobj.dupli_group != None:
                dupliobjects = targetobj.dupli_group.objects
                for obj in dupliobjects:
                    #裏ポリエッジオフ
                    for mod in obj.modifiers:
                        if "裏ポリエッジ" in mod.name:
                            mod.show_viewport = False
                    #非表示オブジェクトをかたっぱしからunlink
                    if obj.hide_render:
                        dupliobjects.unlink(obj)

        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        #フレーム0
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=-1)
        #obj出力
        bpy.ops.export_scene.obj(filepath= dir + "avatar_0.obj", use_selection=True)

        #フレーム5
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=4)
        #obj出力
        bpy.ops.export_scene.obj(filepath= dir + "avatar_5.obj", use_selection=True)

        #フレーム10
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=9)
        #obj出力
        bpy.ops.export_scene.obj(filepath= dir + "avatar_10.obj", use_selection=True)

        #出力フォルダを開く
        os.system("EXPLORER " + dir)

        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------







############################################################################################################################
uiitem("ジェネラル")
############################################################################################################################

########################################
#base出力
########################################
class MYOBJECT_518498(bpy.types.Operator):#base出力
    """base出力"""
    bl_idname = "object.myobject_518498"
    bl_label = "base出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #アクティブオブジェクトをルートと仮定する
        #root = active()


        #現状保存
        bpy.ops.wm.save_mainfile()
        
        mode("OBJECT")
        
        #レイヤー全表示
        bpy.context.scene.layers = [True for n in range(20)]
        #複数親子選択
        bpy.ops.object.myobject_24259()


        selection = get_selected_list()

        deselect()
        
        #root.select = True
        ##ジオメトリのトランスフォームを解除
        #bpy.ops.object.location_clear()
        #bpy.ops.object.rotation_clear()
        
        #子アーマチュアを全てレスト位置に
        for obj in selection:
            if obj.type == "ARMATURE":
                obj.data.pose_position = 'REST'

        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)


        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in selection:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        try:
                            bpy.ops.object.modifier_apply(modifier=mod.name)
                            pass
                        except  :
                            pass
                        
                    if "裏ポリエッジ" in mod.name:
                        bpy.ops.object.modifier_remove(modifier=mod.name)
        ##親子解除
        #select(selection)
        #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2


        deselect()
        select(selection)
        reject_notmesh()
        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False
        #ノンレンダ除外
        for obj in bpy.context.selected_objects:
            if obj.hide_render == True:
                   obj.select = False




        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "base.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        
        return {'FINISHED'}
########################################



########################################
#poseTo出力
########################################
class MYOBJECT_178092(bpy.types.Operator):#poseTo出力
    """poseTo出力"""
    bl_idname = "object.myobject_178092"
    bl_label = "poseTo出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        root = active()

        #現状保存
        bpy.ops.wm.save_mainfile()
        
        mode("OBJECT")

        #レイヤー全表示
        bpy.context.scene.layers = [True for n in range(20)]
        #複数親子選択
        bpy.ops.object.myobject_24259()


        selection = get_selected_list()

        regist_pose("PoseTo",selection)
        activate(root)
        bpy.ops.wm.save_mainfile()
        mode("OBJECT")

        deselect()
        
        activate(root)
        root.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
#        bpy.ops.object.rotation_clear()
        
        #ジオメトリの子を選択
        select(selection)
        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)
        
        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in selection:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        try:
                            bpy.ops.object.modifier_apply(modifier=mod.name)
                            pass
                        except  :
                            pass
                        
                    if "裏ポリエッジ" in mod.name:
                        bpy.ops.object.modifier_remove(modifier=mod.name)
        #親子解除
        #for obj in bpy.context.selected_objects:
        #    bpy.context.scene.objects.active = obj
        #    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2


        deselect()
        select(selection)
        reject_notmesh()
        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False
        #ノンレンダ除外
        for obj in bpy.context.selected_objects:
            if obj.hide_render == True:
                   obj.select = False

        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "poseTo.obj", use_selection=True,)

        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        
        return {'FINISHED'}
########################################


def import_mdresult(self,resultpath):
        current = active()

        loc = Vector((0,0,0))
        qrot = Quaternion()

        #もしボーンが選択されていたらそのボーンにトランスフォームをあわせる
        if current.mode == "POSE":
            armu = ArmatureUtils(current)
            pbone = armu.poseactive()
            loc = current.matrix_world * pbone.location
            qrot = pbone.rotation_quaternion

            #boneはYupなので入れ替え
            loc = Vector((loc.x,loc.z*-1,loc.y))
            qrot = Quaternion((qrot.w, qrot.x, qrot.z*-1, qrot.y))

        mode("OBJECT")

        bpy.ops.import_scene.obj(filepath=resultpath)
        #インポート後処理
        #回転を適用
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        selection = get_selected_list()
        for obj in selection:
           if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
                #服はエッジ出ない方がいい　裏ポリで十分
                for slot in obj.material_slots:
                    mat = slot.material
                    mat.use_transparency = True
                    mat.transparency_method = 'RAYTRACE'


                obj.location = loc
                obj.rotation_quaternion = obj.rotation_quaternion * qrot
                obj.rotation_euler = obj.rotation_quaternion.to_euler()
        
                #読み先にレイヤーをそろえる
                obj.layers = current.layers
        
        #裏ポリエッジ付加
        bpy.ops.object.myobject_318722()


########################################
#インポート
########################################
class MYOBJECT_86482(bpy.types.Operator):#インポート
    """インポート"""
    bl_idname = "object.myobject_86482"
    bl_label = "インポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        import_mdresult(self,dir + "result.obj")

#        current = active()

#        loc = Vector((0,0,0))
#        qrot = Quaternion()

#        #もしボーンが選択されていたらそのボーンにトランスフォームをあわせる
#        if current.mode == "POSE":
#            armu = ArmatureUtils(current)
#            pbone = armu.poseactive()
#            loc = current.matrix_world * pbone.location
#            qrot = pbone.rotation_quaternion

#            #boneはYupなので入れ替え
#            loc = Vector((loc.x,loc.z*-1,loc.y))
#            qrot = Quaternion((qrot.w, qrot.x, qrot.z*-1, qrot.y))

#        #bpy.ops.view3d.snap_cursor_to_selected()
#        #loc = bpy.context.space_data.cursor_location
#        ##loc = current.location
#        #rot = current.rotation_euler
        
#        #append_nodetree("服　汎用システム")
#        #append_nodetree("二値・グレー化")

#        mode("OBJECT")

#        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
#        bpy.ops.import_scene.obj(filepath=dir + "result.obj")
#        #インポート後処理
#        #回転を適用
#        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

#        selection = get_selected_list()
#        for obj in selection:
#           if obj.type == "MESH":
#                bpy.context.scene.objects.active = obj
#                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
#                bpy.ops.mesh.remove_doubles()
#                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
#                #obj.layers = current.layers

#                #bpy.ops.object.modifier_add(type='SUBSURF')
#                #bpy.context.object.modifiers["Subsurf"].levels = 0
#                #bpy.context.object.modifiers["Subsurf"].render_levels = 2
#                for slot in obj.material_slots:
#                    mat = slot.material
#                    mat.use_transparency = False

#                obj.location = loc
#                obj.rotation_quaternion = obj.rotation_quaternion * qrot
#                obj.rotation_euler = obj.rotation_quaternion.to_euler()
        
#                #読み先にレイヤーをそろえる
#                obj.layers = current.layers
        
#        #いらんかも。
#        #for obj in selection:
#        #    if obj.type == "MESH":
#        #        activate(obj)

#        #        #マテリアルに服シェーダをアタッチする
#        #        if "服　汎用システム" in bpy.data.node_groups:
#        #            for mat in obj.data.materials:
#        #                ng_clothshader = bpy.data.node_groups["服　汎用システム"]

#        #                mat.use_nodes = True
#        #                mat.use_shadeless = True
#        #                tree = mat.node_tree
#        #                links = tree.links

#        #                #ノードのクリア
#        #                for node in tree.nodes:
#        #                    tree.nodes.remove(node)

#        #                #マテリアルノード
#        #                n_mat = tree.nodes.new("ShaderNodeMaterial")
#        #                #自身のマテリアルを指定
#        #                n_mat.material = mat
#        #                n_mat.location = (0,200)

#        #                n_group = tree.nodes.new("ShaderNodeGroup")
#        #                n_group.node_tree = ng_clothshader

#        #                #出力
#        #                n_out = tree.nodes.new("ShaderNodeOutput")
#        #                n_out.location = (500,200)


#        #                #接続
#        #                tree.links.new(n_mat.outputs["Color"], n_group.inputs["Color1"])
#        #                tree.links.new(n_group.outputs["Color"], n_out.inputs["Color"])


#                #回転をあわせる
##                obj.rotation_euler = rot
#                #位置をあわせる
#                #bpy.ops.transform.translate(value=(loc[0], loc[1], loc[2]), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#                #原点位置であってる　シミュレーションで問題でる？が、どうしようもない
        
        
#        #裏ポリエッジ付加
#        bpy.ops.object.myobject_318722()

            

#        #deselect()
#        #select(selection)
#        ##オープンエッジの線画化
#        #bpy.ops.object.myobject_141722()
#        #deselect()

#        #ジオメトリの子にする
#        #activate(current)
#        #bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
#        #オブジェクトを単一レイヤー化する
#        #for obj in bpy.data.objects:
#        #for obj in selection:
#        #    for l in range(19,0,-1):
#        #            obj.layers[l] = False
        
        return {'FINISHED'}
########################################



############################################################################################################################
uiitem("マテリアル")
############################################################################################################################

########################################
#インポート用マテリアルフォルダを開く
########################################
class MYOBJECT_902107(bpy.types.Operator):#インポート用マテリアルフォルダを開く
    """インポート用マテリアルフォルダを開く"""
    bl_idname = "object.myobject_902107"
    bl_label = "インポート用マテリアルフォルダを開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        dir = fujiwara_toolbox.conf.assetdir + os.sep + "ノード"
        os.system("EXPLORER " + dir)

        return {'FINISHED'}
########################################



########################################
#マテリアル・ノードクリンアップ
########################################
class MYOBJECT_56507(bpy.types.Operator):#マテリアル・ノードクリンアップ
    """マテリアル・ノードクリンアップ"""
    bl_idname = "object.myobject_56507"
    bl_label = "マテリアル・ノードクリンアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for nodetree in bpy.data.node_groups:
            if "服　汎用システム" in nodetree.name:
                bpy.data.node_groups.remove(nodetree,True)
        return {'FINISHED'}
########################################













############################################################################################################################
uiitem("旧素体システム")
############################################################################################################################

########################################
#base出力
########################################
class MYOBJECT_849795(bpy.types.Operator):#base出力
    """base出力。保存して開き直すので注意"""
    bl_idname = "object.myobject_849795"
    bl_label = "base出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        
        geo = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            obj.select = False
        
        geo.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        
        
        #ジオメトリの子を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #髪を除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if len(obj.material_slots) != 0:
                   if ("髪" in obj.material_slots[0].name) or ("hair" in obj.material_slots[0].name):
                       obj.select = False
        
        #書割除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.dimensions[0] == 0 or obj.dimensions[1] == 0 or obj.dimensions[2] == 0:
                   obj.select = False

        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False


        #子アーマチュアを全てレスト位置に
        for obj in bpy.context.selected_objects:
            if obj.type == "ARMATURE":
                obj.data.pose_position = 'REST'
                #素体だったらトランスフォーム解除
                #if "素体" in obj.name:
                #    bpy.context.scene.objects.active = obj
                #    bpy.ops.object.rotation_clear()

        #bpy.context.scene.objects.active = geo
        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)


        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        #親子解除
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "base.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        return {'FINISHED'}
########################################



#
#########################################
##poseRot0出力
#########################################
#class MYOBJECT_473205(bpy.types.Operator):#poseRot0出力
#    """poseRot0出力"""
#    bl_idname = "object.myobject_473205"
#    bl_label = "poseRot0出力"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
#            self.report({"INFO"},"素体ジオメトリを指定してください")
#            return {'FINISHED'}
#        #現状保存
#        bpy.ops.wm.save_mainfile()
#
#
#
#        geo = bpy.context.scene.objects.active
#
#        for obj in bpy.context.selected_objects:
#            obj.select = False
#
#        geo.select = True
#        #ジオメトリのトランスフォームを解除
#        bpy.ops.object.location_clear()
#        #まずは垂直だけ回転にする
##        geo.rotation_mode = 'XYZ'
##        geo.rotation_euler[0] = 0
##        geo.rotation_euler[1] = 0
#
##        rotto = geo.rotation_euler[2]
##        bpy.ops.object.rotation_clear()
##        bpy.ops.transform.rotate(value=rotto, axis=(0, 0, 1),
##        constraint_axis=(False, False, False),
##        constraint_orientation='LOCAL', mirror=False,
##        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
##        proportional_size=1)
#
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False,
#        True, False), constraint_orientation='LOCAL', mirror=False,
#        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
#        proportional_size=1, release_confirm=True)
#
#        #ジオメトリの子を選択
#        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
#        #髪を除外
#        for obj in bpy.context.selected_objects:
#           if obj.type == "MESH":
#               if ("髪" in obj.material_slots[0].name) or ("hair" in
#               obj.material_slots[0].name):
#                   obj.select = False
#
#        #子アーマチュアを全てレスト位置に
#        for obj in bpy.context.selected_objects:
#            if obj.type == "ARMATURE":
#                obj.data.pose_position = 'REST'
#
#        #全てシングル化
#        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True,
#        material=False, texture=False, animation=False)
#
#
#        #ミラーとアーマチュアの適用
#        #オブジェクト側：アーマチュア適用
#        for obj in bpy.context.selected_objects:
#            if obj.type == "MESH":
#                bpy.context.scene.objects.active = obj
#                for mod in obj.modifiers:
#                    if mod.type=="MIRROR":
#                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
#                        bpy.ops.object.modifier_apply (modifier=mod.name)
#                    if mod.type=="ARMATURE":
#                        #適用する
#                        self.report({"INFO"},obj.name + ":" + mod.name)
#                        bpy.ops.object.modifier_apply (modifier=mod.name)
#        #親子解除
#        for obj in bpy.context.selected_objects:
#            bpy.context.scene.objects.active = obj
#            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
#
#
#        #トランスフォームのアプライ
#        bpy.ops.object.transform_apply(location=False, rotation=False,
#        scale=True)
#        #ノーマルの再計算
#        bpy.ops.object.myobject_590395()
#
#        #簡略化2
#        bpy.context.scene.render.use_simplify = True
#        bpy.context.scene.render.simplify_subdivision = 2
#
#        bpy.ops.export_scene.obj(filepath="G:"+os.sep+"MarvelousDesigner"+os.sep+"poseRot0.obj",
#        use_selection=True,)
#
#        #開きなおし
#        bpy.ops.wm.revert_mainfile(use_scripts=True)
#        return {'FINISHED'}
#########################################
#




#########################################
##posenoRot出力
#########################################
#class MYOBJECT_424197(bpy.types.Operator):#posenoRot出力
#    """posenoRot出力"""
#    bl_idname = "object.myobject_424197"
#    bl_label = "posenoRot出力"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
#            self.report({"INFO"},"素体ジオメトリを指定してください")
#            return {'FINISHED'}
#        #現状保存
#        bpy.ops.wm.save_mainfile()
#
#
#
#        geo = bpy.context.scene.objects.active
#
#        for obj in bpy.context.selected_objects:
#            obj.select = False
#
#        geo.select = True
#        #ジオメトリのトランスフォームを解除
##        bpy.ops.object.location_clear()
#        bpy.ops.object.rotation_clear()
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False,
#        True, False), constraint_orientation='LOCAL', mirror=False,
#        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
#        proportional_size=1, release_confirm=True)
#
#
#        #ジオメトリの子を選択
#        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
#        #髪を除外
#        for obj in bpy.context.selected_objects:
#           if obj.type == "MESH":
#               if ("髪" in obj.material_slots[0].name) or ("hair" in
#               obj.material_slots[0].name):
#                   obj.select = False
#
#        #全てシングル化
#        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True,
#        material=False, texture=False, animation=False)
#
#        #ミラーとアーマチュアの適用
#        #オブジェクト側：アーマチュア適用
#        for obj in bpy.context.selected_objects:
#            if obj.type == "MESH":
#                bpy.context.scene.objects.active = obj
#                for mod in obj.modifiers:
#                    if mod.type=="MIRROR":
#                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
#                        bpy.ops.object.modifier_apply (modifier=mod.name)
#                    if mod.type=="ARMATURE":
#                        #適用する
#                        self.report({"INFO"},obj.name + ":" + mod.name)
#                        bpy.ops.object.modifier_apply (modifier=mod.name)
#        #親子解除
#        for obj in bpy.context.selected_objects:
#            bpy.context.scene.objects.active = obj
#            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
#
#        #トランスフォームのアプライ
#        bpy.ops.object.transform_apply(location=False, rotation=False,
#        scale=True)
#        #ノーマルの再計算
#        bpy.ops.object.myobject_590395()
#
#        #簡略化2
#        bpy.context.scene.render.use_simplify = True
#        bpy.context.scene.render.simplify_subdivision = 2
#
#        bpy.ops.export_scene.obj(filepath="G:"+os.sep+"MarvelousDesigner"+os.sep+"posenoRot.obj",
#        use_selection=True,)
#
#        #開きなおし
#        bpy.ops.wm.revert_mainfile(use_scripts=True)
#        return {'FINISHED'}
#########################################
#
#
#
#



"""
よくよく考えたらどうすんのこれ問題。

・ポーズの前後が反転していると、大変めんどくさい。前後が同じであれば、わりとなんとかなる。
→前後反転してたら一回反転してposeTo出して、インポート時にまた反転する
　のはいいんだけど、反転の判定ってどーしたらいいの～

→無理なきがするから手動でやる？

ジオメトリに回転がかかってる場合
・単純に位置をゼロにすると、地面を突き破ることが。
・かといってx,yだけゼロにする処理だと、zが大きい場合なんかにものすごい不都合。シーン内で飛び上がってる奴とか。




"""

#ポーズ登録
def regist_pose(pose_name="Pose", objects = None):
    if objects == None:
        obj = active()
        if obj.type != "ARMATURE":
            return

        mode("POSE")
        bpy.ops.pose.select_all(action='SELECT')
        try:
            newframe = obj.pose_library.frame_range[1]+1
            bpy.ops.poselib.pose_add(frame=newframe, name=pose_name)
        except:
            pass
    else:
        for obj in objects:
            activate(obj)
            if obj.type != "ARMATURE":
                continue

            mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')
            try:
                newframe = obj.pose_library.frame_range[1]+1
                bpy.ops.poselib.pose_add(frame=newframe, name=pose_name)
            except:
                pass
            pass
        pass
    mode("OBJECT")

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#中間ポーズ
########################################
class MYOBJECT_976064(bpy.types.Operator):#中間ポーズ
    """中間ポーズ"""
    bl_idname = "object.myobject_976064"
    bl_label = "中間ポーズ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        
        geo = bpy.context.scene.objects.active
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        for obj in bpy.context.selected_objects:
            activate(obj)
            regist_pose("中間ポーズ")
        deselect()
        activate(geo)
        bpy.ops.wm.save_mainfile()

        deselect()
        
        geo.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
#        bpy.ops.object.rotation_clear()
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        
        
        #ジオメトリの子を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #髪を除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if len(obj.material_slots) != 0:
                   if ("髪" in obj.material_slots[0].name) or ("hair" in obj.material_slots[0].name):
                       obj.select = False
        #書割除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.dimensions[0] == 0 or obj.dimensions[1] == 0 or obj.dimensions[2] == 0:
                   obj.select = False

        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False

        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)
        
        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        #親子解除
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "中間poseTo.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        
        return {'FINISHED'}
########################################


########################################
#反転中間ポーズ
########################################
class MYOBJECT_666595(bpy.types.Operator):#反転中間ポーズ
    """反転中間ポーズ"""
    bl_idname = "object.myobject_666595"
    bl_label = "反転中間ポーズ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        
        geo = bpy.context.scene.objects.active
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        for obj in bpy.context.selected_objects:
            activate(obj)
            regist_pose("中間ポーズ")
        activate(geo)
        bpy.ops.wm.save_mainfile()

        deselect()
        
        geo.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
        bpy.ops.transform.rotate(value=3.14159, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        
        #ジオメトリの子を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #髪を除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if ("髪" in obj.material_slots[0].name) or ("hair" in obj.material_slots[0].name):
                   obj.select = False
        #書割除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.dimensions[0] == 0 or obj.dimensions[1] == 0 or obj.dimensions[2] == 0:
                   obj.select = False


        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False

        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)
        
        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        #親子解除
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "中間poseTo.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#poseTo出力
########################################
class MYOBJECT_677880(bpy.types.Operator):#poseTo出力
    """poseTo出力"""
    bl_idname = "object.myobject_677880"
    bl_label = "poseTo出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        
        geo = bpy.context.scene.objects.active
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        for obj in bpy.context.selected_objects:
            activate(obj)
            regist_pose("PoseTo")
        activate(geo)
        bpy.ops.wm.save_mainfile()

        deselect()
        
        geo.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
#        bpy.ops.object.rotation_clear()
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        
        
        #ジオメトリの子を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #髪を除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if len(obj.material_slots) != 0:
                   if ("髪" in obj.material_slots[0].name) or ("hair" in obj.material_slots[0].name):
                       obj.select = False
        #書割除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.dimensions[0] == 0 or obj.dimensions[1] == 0 or obj.dimensions[2] == 0:
                   obj.select = False

        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False


        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)
        
        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        #親子解除
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "poseTo.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        return {'FINISHED'}
########################################



########################################
#反転poseTo出力
########################################
class MYOBJECT_425209(bpy.types.Operator):#反転poseTo出力
    """反転poseTo出力"""
    bl_idname = "object.myobject_425209"
    bl_label = "反転poseTo出力"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        #現状保存
        bpy.ops.wm.save_mainfile()
        
        
        
        geo = bpy.context.scene.objects.active
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        for obj in bpy.context.selected_objects:
            activate(obj)
            regist_pose("PoseTo")
        activate(geo)
        bpy.ops.wm.save_mainfile()

        deselect()
        
        geo.select = True
        #ジオメトリのトランスフォームを解除
        bpy.ops.object.location_clear()
        bpy.ops.transform.rotate(value=3.14159, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        
        #ジオメトリの子を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #髪を除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if ("髪" in obj.material_slots[0].name) or ("hair" in obj.material_slots[0].name):
                   obj.select = False
        #書割除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.dimensions[0] == 0 or obj.dimensions[1] == 0 or obj.dimensions[2] == 0:
                   obj.select = False

        #ワイヤーフレーム除外
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               if obj.draw_type == "WIRE":
                   obj.select = False


        
        #全てシングル化
        bpy.ops.object.make_single_user(type='ALL', object=True, obdata=True, material=False, texture=False, animation=False)
        
        #ミラーとアーマチュアの適用
        #オブジェクト側：アーマチュア適用
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if mod.type == "ARMATURE":
                        #適用する
                        self.report({"INFO"},obj.name + ":" + mod.name)
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        #親子解除
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        #ノーマルの再計算
        bpy.ops.object.myobject_590395()
        
        #簡略化2
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.export_scene.obj(filepath=dir + "poseTo.obj", use_selection=True,)
        
        #開きなおし
        bpy.ops.wm.revert_mainfile(use_scripts=True)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#インポート
########################################
class MYOBJECT_717368(bpy.types.Operator):#インポート
    """インポート"""
    bl_idname = "object.myobject_717368"
    bl_label = "インポート"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        geo = bpy.context.scene.objects.active
        loc = geo.location
        rot = geo.rotation_euler
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.import_scene.obj(filepath=dir + "result.obj")
        #インポート後処理
        #回転を適用
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = 0
                bpy.context.object.modifiers["Subsurf"].render_levels = 2
                for slot in obj.material_slots:
                    mat = slot.material
                    mat.use_transparency = False
        
        
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                #回転をあわせる
#                obj.rotation_euler = rot
                #位置をあわせる
                bpy.ops.transform.translate(value=(loc[0], loc[1], loc[2]), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        
        
        #ジオメトリの子にする
        bpy.context.scene.objects.active = geo
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        #オブジェクトを単一レイヤー化する
        for obj in bpy.data.objects:
            for l in range(19,0,-1):
                    obj.layers[l] = False
        return {'FINISHED'}
########################################



########################################
#反転インポート
########################################
class MYOBJECT_624042(bpy.types.Operator):#反転インポート
    """反転インポート"""
    bl_idname = "object.myobject_624042"
    bl_label = "反転インポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        geo = bpy.context.scene.objects.active
        loc = geo.location
        rot = geo.rotation_euler
        
        dir = fujiwara_toolbox.conf.MarvelousDesigner_dir
        bpy.ops.import_scene.obj(filepath=dir + "result.obj")
        #インポート後処理
        #回転を適用
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = 0
                bpy.context.object.modifiers["Subsurf"].render_levels = 2
                for slot in obj.material_slots:
                    mat = slot.material
                    mat.use_transparency = False
        
        
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                #回転をあわせる
#                obj.rotation_euler = rot
                #位置をあわせる
                bpy.ops.transform.translate(value=(loc[0], loc[1], loc[2]), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        
        
        #ジオメトリの子にする
        bpy.context.scene.objects.active = geo
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        #オブジェクトを単一レイヤー化する
        for obj in bpy.data.objects:
            for l in range(19,0,-1):
                    obj.layers[l] = False
        #反転処理
        bpy.ops.transform.rotate(value=3.14159, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#        bpy.ops.transform.translate(value=(loc[0], loc[1], loc[2]*-1),
#        constraint_axis=(False, False, False),
#        constraint_orientation='GLOBAL', mirror=False,
#        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
#        proportional_size=1)

        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#Substance/テクスチャ
########################################
class CATEGORYBUTTON_81935(bpy.types.Operator):#Substance/テクスチャ
    """Substance/テクスチャ"""
    bl_idname = "object.categorybutton_81935"
    bl_label = "Substance/テクスチャ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("Substance/テクスチャ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


############################################################################################################################
uiitem("選択からアクティブにベイク")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
def sbsname(basename):
    return basename.replace(".","_")

#def use_textures(obj,flag):
#    for mat in obj.data.materials:
#        for index,use_texture in mat.use_textures:
#            mat.use_textures[index] = flag


def remove_tex_identifier(name):
    name = re.sub("_curvature|_ambient_occlusion|_baseColor|_color|_diffuse|_Height|_Normal|_AO|_ambient_occlusion|_metallic|_roughness|_shadow","",name,0,re.IGNORECASE)
    return name

def get_texname(filepath):
    name = os.path.basename(filepath)
    name,ext = os.path.splitext(name)
    name = remove_tex_identifier(name)
    return name

def saveall_dirtyimages():
    for img in bpy.data.images:
        if img.is_dirty:
            if img.filepath == "":
                dir = os.path.dirname(bpy.data.filepath)
                name = get_texname(img.name)
                imgdir = dir + os.sep + name + "_textures" + os.sep
                if not os.path.exists(imgdir):
                    os.makedirs(imgdir)
                img.filepath = imgdir + img.name
            img.save()

#type: https://docs.blender.org/api/blender_python_api_2_78c_release/bpy.types.RenderSettings.html#bpy.types.RenderSettings.bake_type
def texture_bake(filepath, size, type, identifier):
    filename = os.path.basename(filepath)
    bakeobj = active()

    if filename in bpy.data.images:
        imgtobake = bpy.data.images[filename]
        imgtobake.scale(size,size)
    else:
        imgtobake = bpy.data.images.new(filename,size,size,True)

    #もしかしてここで一回imgを保存する必要がある？→正解！
    #imageはいじくる前にかならずsaveしないといけない！
    saveall_dirtyimages()

    #self.report({"INFO"},"image to bake:"+imgtobake.name)

    for uvface in bakeobj.data.uv_textures.active.data:
        uvface.image = imgtobake
    bakeobj.data.update()

    bpy.context.scene.render.bake_type = type
    bpy.context.scene.render.use_bake_selected_to_active = True
    bpy.context.scene.render.use_textures = True

    bpy.ops.object.bake_image()
    saveall_dirtyimages()



def bake_setup():
    bpy.ops.object.myobject_998634()#無マテリアルに白を割り当て
    bakeobj = active()

    #複製されてることを考慮して一旦マテリアルを外す
    bakeobj.data.materials.clear()

    objname = sbsname(bakeobj.name)
    bakedir = os.path.dirname(bpy.data.filepath)+os.sep+objname+"_textures"+os.sep

    #UV展開
    if len(bakeobj.data.uv_textures) == 0:
        mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        mode("OBJECT")

    return objname, bakedir

def autobake(size,type,identifier):
    objname,bakedir = bake_setup()
    bakepath = bakedir+objname+"_"+identifier+".png"
    texture_bake(bakepath,size,type,identifier)

def bake_ModelAppearance(size):
    bpy.context.scene.render.bake_distance = 0
    bpy.context.scene.render.bake_bias = 0.001
    bpy.context.scene.render.bake_margin = 16
    bpy.context.scene.render.use_bake_clear = True
    bpy.context.scene.render.use_bake_to_vertex_color = False
    bpy.context.scene.render.bake_quad_split = 'AUTO'

    autobake(size,"TEXTURE","baseColor")
    autobake(size,"DISPLACEMENT","Height")
    autobake(size,"NORMALS","Normal")

    bpy.ops.object.myobject_358608()#テクスチャ回収

    deselect()
    active().select = True



########################################
#2048
########################################
class MYOBJECT_458089(bpy.types.Operator):#2048
    """2048*2048px"""
    bl_idname = "object.myobject_458089"
    bl_label = "2048"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bake_ModelAppearance(2048)
        return {'FINISHED'}
########################################

########################################
#4096
########################################
#bpy.ops.object.myobject_264050() #4096
class MYOBJECT_264050(bpy.types.Operator):#4096
    """4096*4096px"""
    bl_idname = "object.myobject_264050"
    bl_label = "4096"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bake_ModelAppearance(4096)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("影をベイク")
############################################################################################################################

def set_sun_shadow(value):
    for lamp in bpy.data.lamps:
        if lamp.type == "SUN":
            lamp.use_shadow = value

def bake_shadow(size):
    bpy.context.scene.render.bake_distance = 0.001
    bpy.context.scene.render.bake_bias = 0.001
    bpy.context.scene.render.bake_margin = 16
    bpy.context.scene.render.use_bake_clear = True
    bpy.context.scene.render.use_bake_to_vertex_color = False
    bpy.context.scene.render.bake_quad_split = 'AUTO'

    set_sun_shadow(True)

    autobake(size,"SHADOW","Shadow")

    set_sun_shadow(False)

    bpy.ops.object.myobject_358608()#テクスチャ回収
    deselect()
    active().select = True

    pass

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#512
########################################
#bpy.ops.object.myobject_401784() #512
class MYOBJECT_401784(bpy.types.Operator):#512
    """512"""
    bl_idname = "object.myobject_401784"
    bl_label = "512"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bake_shadow(512)
        return {'FINISHED'}
########################################

########################################
#1024
########################################
#bpy.ops.object.myobject_442748() #1024
class MYOBJECT_442748(bpy.types.Operator):#1024
    """1024"""
    bl_idname = "object.myobject_442748"
    bl_label = "1024"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bake_shadow(1024)
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Substance")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#Substance Output
########################################
class MYOBJECT_596924(bpy.types.Operator):#Substance Output
    """Substance Output"""
    bl_idname = "object.myobject_596924"
    bl_label = "Substance Output"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        scrdir = os.path.dirname(__file__)
        sbssourcepath = scrdir + os.sep + "resources" + os.sep + "EMPTY.sbs"

        reject_notmesh()
        for obj in get_selected_list():
            #substance上で.が_に変換されて都合が悪いので除去しておく
            #obj.name = obj.name.replace(".","")

            dir = os.path.dirname(bpy.data.filepath)
            name = sbsname(obj.name)
            imgdir = dir + os.sep + name + "_textures" + os.sep
            if not os.path.exists(imgdir):
                os.makedirs(imgdir)

            #sbsファイルのコピー　あったらしない
            sbsdestpath = imgdir + name + ".sbs"
            if not os.path.exists(sbsdestpath):
                shutil.copyfile(sbssourcepath, sbsdestpath)
            deselect()
            activate(obj)
            if len(obj.data.uv_textures) == 0:
                mode("EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project()
                mode("OBJECT")

            bpy.ops.export_scene.obj(filepath=imgdir+name + ".obj",check_existing=False,use_selection=True,use_mesh_modifiers=False)
            #出力フォルダを開く
            os.system("EXPLORER " + imgdir)

        return {'FINISHED'}
########################################

########################################
#分離してSubstance Output
########################################
class MYOBJECT_539212(bpy.types.Operator):#分離してSubstance Output
    """分離してSubstance Output"""
    bl_idname = "object.myobject_539212"
    bl_label = "分離してSubstance Output"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        deselect()
        bpy.ops.mesh.separate(type='SELECTED')
        mode("OBJECT")

        bpy.ops.object.myobject_339338()#スマートUV投影（各選択物）

        for obj in get_selected_list():
            mat = bpy.data.materials.new(name=sbsname(obj.name))#substanceとの連携用にオブジェクト名でマテリアル作る
            mat.diffuse_color=(1,1,1)
            if len(obj.material_slots) == 0:
                obj.data.materials.append(mat)
            else:
                obj.material_slots[0].material = mat
        
        bpy.ops.object.myobject_596924()#Substance Output

        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#テクスチャ回収
########################################
class MYOBJECT_358608(bpy.types.Operator):#テクスチャ回収
    """テクスチャ回収"""
    bl_idname = "object.myobject_358608"
    bl_label = "テクスチャ回収"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        basedir = os.path.dirname(bpy.data.filepath)
        texfiles = []

        bpy.ops.object.myobject_998634()#無マテリアルに白を割り当て

        #テクスチャピックアップ
        for dirpath, dirs, files in os.walk(basedir):
            for file in files:
                name,ext = os.path.splitext(file)
                if re.search("bmp|png|jpg|jpeg", ext, re.IGNORECASE) is not None:
                    texfiles.append(dirpath+os.sep+file)

        images = []
        for texfile in texfiles:
            self.report({"INFO"},texfile)
            #Substanceのモデル情報はスルー
            if re.search("_curvature|_ambient_occlusion", texfile,re.IGNORECASE) is not None:
            #if re.search("_curvature", texfile,re.IGNORECASE) is not None:
                continue
            images.append(load_img(texfile))

        #basecolor類がはじめになるように並べ替える
        tmp = []
        for image in images:
            if re.search("_baseColor|_color|_diffuse", image.name,re.IGNORECASE) is not None:
                tmp.append(image)
                images.remove(image)
        #残りを足す
        tmp.extend(images)
        images = tmp

        for image in images:
            texname, ext = os.path.splitext(image.name)

            #テクスチャが存在する場合は既にマテリアル設定とかしてるはずなのでスルー
            if texname in bpy.data.textures:
                continue

            tex = bpy.data.textures.new(texname, "IMAGE")
            tex.image = image

            #Substance的命名規則で名前を得る
            #matname = texname.split("_")[0]
            #identifier=最後の_hogeを除去したものが名前
            matname = re.sub("_[a-zA-Z]+$", "", texname)
            mat = get_material(matname)
            

            texture_slot = mat.texture_slots.add()
            texture_slot.texture = tex

            if re.search("_baseColor|_color|_diffuse", tex.name,re.IGNORECASE) is not None:
                texture_slot.use_map_color_diffuse = True
                texture_slot.diffuse_color_factor = 1
                texture_slot.blend_type = 'MULTIPLY'
            if re.search("_Height|_Normal", tex.name,re.IGNORECASE) is not None:
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_normal = True
                texture_slot.normal_factor = 0.01
            if re.search("_AO|_ambient_occlusion", tex.name,re.IGNORECASE) is not None:
                texture_slot.use_map_color_diffuse = True
                texture_slot.diffuse_color_factor = 1
                texture_slot.blend_type = 'MULTIPLY'
            if re.search("_metallic", tex.name,re.IGNORECASE) is not None:
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_hardness = True
                texture_slot.hardness_factor = 1
            if re.search("_roughness", tex.name,re.IGNORECASE) is not None:
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_specular = True
                texture_slot.specular_factor = 1
            if re.search("_Shadow", tex.name,re.IGNORECASE) is not None:
                #作業中
                texture_slot.use_map_color_diffuse = True
                texture_slot.diffuse_color_factor = 1
                texture_slot.blend_type = 'MULTIPLY'

                


        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("調整")
############################################################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def settexdepth(value,objects):
    for obj in objects:
        for mat in obj.data.materials:
            for texture_slot in mat.texture_slots:
                if texture_slot is None:
                    continue
                if re.search("_Height", texture_slot.texture.name,re.IGNORECASE) is not None:
                    texture_slot.normal_factor = value


########################################
#デプス0.01
########################################
class MYOBJECT_819234(bpy.types.Operator):#デプス0.01
    """デプス0.01"""
    bl_idname = "object.myobject_819234"
    bl_label = "デプス0.01"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        settexdepth(0.01,get_selected_list())
        
        return {'FINISHED'}
########################################

########################################
#デプス1
########################################
class MYOBJECT_73453(bpy.types.Operator):#デプス1
    """デプス1"""
    bl_idname = "object.myobject_73453"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        settexdepth(1,get_selected_list())
        return {'FINISHED'}
########################################

########################################
#デプス5
########################################
class MYOBJECT_997104(bpy.types.Operator):#デプス5
    """デプス5"""
    bl_idname = "object.myobject_997104"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        settexdepth(5,get_selected_list())
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





################################################################################
#UIカテゴリ
########################################
#髪ツール
########################################
class CATEGORYBUTTON_739344(bpy.types.Operator):#髪ツール
    """髪ツール"""
    bl_idname = "object.categorybutton_739344"
    bl_label = "髪ツール"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("髪ツール",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#開きにする
########################################
class MYOBJECT_521395(bpy.types.Operator):#開きにする
    """開きにする"""
    bl_idname = "object.myobject_521395"
    bl_label = "開きにする"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #data.shape_keys = bpy.data.keys["Key.007"]みたいになってる
        #個別のシェイプキーは、
        #bpy.data.shape_keys["Key.007"].key_blocks["Flat"].mute = True
        #という形で、key_blocksに入っている
        active().data.shape_keys.eval_time = 10

        #アーマチュア非表示
        modu = Modutils(active())
        mod_armature = modu.find_bytype("ARMATURE")
        modu.hide(mod_armature)

        bpy.ops.view3d.viewnumpad(type="FRONT", align_active=True)
        
        
        return {'FINISHED'}
########################################

########################################
#立体化
########################################
class MYOBJECT_17323(bpy.types.Operator):#立体化
    """立体化"""
    bl_idname = "object.myobject_17323"
    bl_label = "立体化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        active().data.shape_keys.eval_time = 0
        
        #アーマチュア表示
        modu = Modutils(active())
        mod_armature = modu.find_bytype("ARMATURE")
        modu.show(mod_armature)

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#オブジェクト生成
########################################
class CATEGORYBUTTON_335613(bpy.types.Operator):#オブジェクト生成
    """オブジェクト生成"""
    bl_idname = "object.categorybutton_335613"
    bl_label = "オブジェクト生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("オブジェクト生成",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ランダム石生成
########################################
class MYOBJECT_104686(bpy.types.Operator):#ランダム石生成
    """ランダム石生成"""
    bl_idname = "object.myobject_104686"
    bl_label = "ランダム石生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mode("OBJECT")
        bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=cursor(), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        mode("EDIT")

        def rndv():
            rnd = random.randint(1,1000)
            print(rnd)
            bpy.ops.transform.vertex_random(normal=1,seed=rnd)

        bpy.ops.mesh.subdivide(number_cuts=3, smoothness=0)
        x = random.uniform(0.5,2)
        y = random.uniform(0.5,2)
        z = random.uniform(0.5,2)
        bpy.ops.transform.resize(value=(x,y,z), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


        for i in range(random.randint(1,50)):
            rndv()

        #bpy.ops.mesh.vertices_smooth(factor=1, repeat=1)
        bpy.ops.mesh.looptools_relax(input='selected', interpolation='cubic', iterations='10', regular=True)
        mode("OBJECT")

        #自動スムーズ
        bpy.ops.object.myobject_31891()


        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#物理
########################################
class CATEGORYBUTTON_984430(bpy.types.Operator):#物理
    """物理"""
    bl_idname = "object.categorybutton_984430"
    bl_label = "物理"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("物理",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




########################################
#ベイクリフレッシュ
########################################
class MYOBJECT_245059(bpy.types.Operator):#ベイクリフレッシュ
    """ベイクリフレッシュ"""
    bl_idname = "object.myobject_245059"
    bl_label = "ベイクリフレッシュ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0
        
        
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#Pin割当
########################################
class MYOBJECT_823626(bpy.types.Operator):#Pin割当
    """Pin割当"""
    bl_idname = "object.myobject_823626"
    bl_label = "Pin割当"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="edit")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.active_object
        if("Pin" not in obj.vertex_groups):
            bpy.ops.object.vertex_group_add()
            obj.vertex_groups[len(obj.vertex_groups) - 1].name = "Pin"
        
        
        obj.vertex_groups.active_index = obj.vertex_groups.find("Pin")
        bpy.ops.object.vertex_group_assign()
        
        
        
        
        
        return {'FINISHED'}
########################################

#########################################
##Total割当
#########################################
#class MYOBJECT_878504(bpy.types.Operator):#Total割当
#    """Total割当"""
#    bl_idname = "object.myobject_878504"
#    bl_label = "Total割当"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        for obj in bpy.context.selected_objects:
#            bpy.context.scene.objects.active = obj
#
#            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
#
#            if("Total" not in obj.vertex_groups):
#                bpy.ops.mesh.select_all(action='SELECT')
#                bpy.ops.object.vertex_group_add()
#                obj.vertex_groups[len(obj.vertex_groups)-1].name = "Total"
#
#
#            obj.vertex_groups.active_index = obj.vertex_groups.find("Total")
#            bpy.ops.object.vertex_group_assign()
#
#            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#        return {'FINISHED'}
#########################################
















########################################
#コリジョン用複製
########################################
class MYOBJECT_205157(bpy.types.Operator):#コリジョン用複製
    """コリジョン用複製"""
    bl_idname = "object.myobject_205157"
    bl_label = "コリジョン用複製"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        source = bpy.context.scene.objects.active
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        target = bpy.context.scene.objects.active
        target.name = source.name + "_Collision"
        target.draw_type = 'WIRE'
        target.hide_render = True
        #Armature以外削除
        for mod in target.modifiers:
            if mod.type != "ARMATURE":
                bpy.ops.object.modifier_remove(modifier=mod.name)
        
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        for mod in target.modifiers:
            if mod.type == "SHRINKWRAP":
                mod.target = source
                mod.offset = 0.005
                mod.use_keep_above_surface = True
        
        #コリジョン追加
        bpy.ops.object.modifier_add(type='COLLISION')
        
        
        return {'FINISHED'}
########################################

########################################
#サーフェスのオフセットを作成
########################################
class MYOBJECT_598876(bpy.types.Operator):#サーフェスのオフセットを作成
    """サーフェスのオフセットを作成"""
    bl_idname = "object.myobject_598876"
    bl_label = "サーフェスのオフセットを作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        source = bpy.context.scene.objects.active
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        target = bpy.context.scene.objects.active
        target.name = source.name + "_SurfaceOffset"
        target.draw_type = 'TEXTURED'
        #Armature以外削除
        for mod in target.modifiers:
            if mod.type != "ARMATURE":
                bpy.ops.object.modifier_remove(modifier=mod.name)
        
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        for mod in target.modifiers:
            if mod.type == "SHRINKWRAP":
                mod.target = source
                mod.offset = 0.01
                mod.use_keep_above_surface = True
        
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("キャラ用")
############################################################################################################################

########################################
#クロスを確定して髪準備
########################################
class MYOBJECT_482428(bpy.types.Operator):#クロスを確定して髪準備
    """クロスを確定して髪準備"""
    bl_idname = "object.myobject_482428"
    bl_label = "クロスを確定して髪準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()
        for obj in selection:
            if obj.type == "MESH":
                deselect()
                activate(obj)
                mod_cloth = None
                for mod in obj.modifiers:
                    if mod.type == "CLOTH":
                        mod_cloth = mod
                if mod_cloth is None:
                    continue

                #布適用
                bpy.ops.object.modifier_apply(modifier=mod_cloth.name)
                
                #パーティクル
                psetting = append_particlesetting("髪設定")
                bpy.context.object.hnMasterHairSystem = "髪設定"
                bpy.ops.particle.hairnet(meshKind="SHEET")


        return {'FINISHED'}
########################################


































################################################################################
#UIカテゴリ
########################################
#Plane
########################################
class CATEGORYBUTTON_814784(bpy.types.Operator):#Plane
    """Plane"""
    bl_idname = "object.categorybutton_814784"
    bl_label = "Plane"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("Plane",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################






########################################
#DPIを揃える
########################################
class MYOBJECT_718267(bpy.types.Operator):#DPIを揃える
    """DPIを揃える"""
    bl_idname = "object.myobject_718267"
    bl_label = "DPIを揃える"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        reject_notmesh()
        obj_active = active()

        ##板ポリじゃない奴を除外
        #for obj in bpy.context.selected_objects:
        #    if obj.dimensions[1] != 0 and obj.dimensions[2] != 0:
        #        obj.select = False
        #板ポリじゃない＝眼孔
        #正面からの縦横比をあわせるべきでは？
        #modオフにすればよかった…

        targets = get_selected_list()

        X = 0
        Y = 1
        Z = 2

        width = 0
        height = 1

        base_density = 1

        #縦横比をあわせる
        scaletargets = []
        for target in targets:
            self.report({"INFO"},"target:"+target.name)

            #modオフ
            for mod in target.modifiers:
                mod.show_viewport = False


            V = Y
            #縦軸どっちか
            #でかい方を縦に
            if target.dimensions[Y] < target.dimensions[Z]:
                V = Z

            #イメージを取得して縦横ピクセルを得る
            img = None
            if len(target.material_slots) == 0:
                continue
            mat = target.material_slots[0].material
            
            if len(mat.texture_slots) == 0:
                continue
            if mat.texture_slots[0] == None:
                continue
            tex = mat.texture_slots[0].texture
            if tex == None:
                continue

            img = tex.image
            if img == None:
                continue

            #イメージのサイズ
            #img.size[width]
            #img.size[height]

            #横＝1でやる density=密度
            density = img.size[width] / target.dimensions[X]

            if target == obj_active:
                base_density = density

            self.report({"INFO"},target.name +str(target.dimensions[X])+ "|" + " img" + str(img.size[width]) + " density" + str(density))

            ox = target.dimensions[X]
            if V == Y:
                oy = img.size[height] / density
                oz = target.dimensions[Z]
            else:
                oy = target.dimensions[Y]
                oz = img.size[height] / density
            target.dimensions = (ox,oy,oz)

            if target != obj_active:
                scaletargets.append(target)
        #base_densityを元に各オブジェクトのサイズをあわせる
        for target in scaletargets:
            V = Y
            #縦軸どっちか
            #でかい方を縦に
            if target.dimensions[Y] < target.dimensions[Z]:
                V = Z
            #target.scale = obj_active.scale
            #↑これじゃだめ
            #イメージを取得して縦横ピクセルを得る
            mat = target.material_slots[0].material
            tex = mat.texture_slots[0].texture
            img = tex.image

            #横＝1でやる density=密度
            density = base_density

            ox = img.size[width] / density
            if V == Y:
                oy = img.size[height] / density
                oz = target.dimensions[Z]
            else:
                oy = target.dimensions[Y]
                oz = img.size[height] / density
            target.dimensions = (ox,oy,oz)



        for target in targets:
            #modオン
            for mod in target.modifiers:
                mod.show_viewport = True


        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------







################################################################################
#UIカテゴリ
########################################
#その他
########################################
class CATEGORYBUTTON_207003(bpy.types.Operator):#その他
    """その他"""
    bl_idname = "object.categorybutton_207003"
    bl_label = "その他"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("その他",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


############################################################################################################################
uiitem("開発ヘルパ")
############################################################################################################################

########################################
#アクティブタイプ取得
########################################
class MYOBJECT_468766(bpy.types.Operator):#アクティブタイプ取得
    """アクティブタイプ取得"""
    bl_idname = "object.myobject_468766"
    bl_label = "アクティブタイプ取得"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        text = bpy.context.active_object.active_material.node_tree.nodes.active.bl_idname
        bpy.data.window_managers['WinMan'].clipboard = text
        
        return {'FINISHED'}
########################################






############################################################################################################################
uiitem("フィニッシング")
############################################################################################################################



########################################
#注意事項
########################################
class MYOBJECT_893322(bpy.types.Operator):#注意事項
    """バックアップを作ってから行うこと。他の3Dビューはとじること。"""
    bl_idname = "object.myobject_893322"
    bl_label = "注意事項"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################


########################################
#nゴンチェック
########################################
class MYOBJECT_342881(bpy.types.Operator):#nゴンチェック
    """nゴンチェック"""
    bl_idname = "object.myobject_342881"
    bl_label = "nゴンチェック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        reject_notmesh()
        selected = get_selected_list()

        targets = []
        for obj in selected:
            #if obj in ngon_ok:
            #    continue

            deselect()
            activate(obj)

                        #nゴンチェック
            flag_ngon = False
            polys = obj.data.polygons

            for poly in polys:
                if len(poly.vertices) > 4:
                    flag_ngon = True
                    break

            #ngonあった
            if flag_ngon:
                targets.append(obj)

        globalview()
        deselect()
        for target in targets:
            target.select = True

        localview()
        self.report({"INFO"},"これらのオブジェクトにNゴンが含まれているので簡略化オフでのルックを確認してください")

        return {'FINISHED'}
########################################

########################################
#モデル確定
########################################
class MYOBJECT_847775(bpy.types.Operator):#モデル確定
    """モデル確定"""
    bl_idname = "object.myobject_847775"
    bl_label = "モデル確定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        start = time.time()

        #subdiv0でbool非表示にしてから、オフ確定すればはやいはず
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0

        reject_notmesh()
        bpy.ops.object.duplicates_make_real()
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)



        selected = get_selected_list()

        #ブーリアン非表示で負荷へらす
        for obj in selected:
            activate(obj)
            for mod in obj.modifiers:
                if mod.type=="BOOLEAN":
                    mod.show_viewport = False

        bpy.context.scene.render.use_simplify = False
        apply_mods()


        elapsed_time = time.time() - start
        self.report({"INFO"},("elapsed_time:{0}".format(elapsed_time/60)) + "[min]")


        return {'FINISHED'}
########################################














########################################
#ポリゴン密度
########################################
class MYOBJECT_809008(bpy.types.Operator):#ポリゴン密度
    """ポリゴン密度"""
    bl_idname = "object.myobject_809008"
    bl_label = "ポリゴン密度"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = active()
        
        dim = obj.dimensions
        vol = dim.x * dim.y * dim.z

        polys = len(obj.data.polygons)
        for mod in obj.modifiers:
            if mod.type == "SUBSURF":
                a = 4**mod.levels
                polys *= a

        self.report({"INFO"}, obj.name+"面："+str(polys)+" 密度："+str(polys/vol))

        
        return {'FINISHED'}
########################################














############################################################################################################################
uiitem("FIX")
############################################################################################################################






########################################
#カメラとランプをレイヤ1に寄せる
########################################
class MYOBJECT_704935(bpy.types.Operator):#カメラとランプをレイヤ1に寄せる
    """カメラとランプをレイヤ1に寄せる"""
    bl_idname = "object.myobject_704935"
    bl_label = "カメラとランプをレイヤ1に寄せる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            if (obj.type == "CAMERA") or (obj.type == "LAMP"):
                for layer in obj.layers:
                    layer = False
                obj.layers[0] = True
        
        
        
        
        return {'FINISHED'}
########################################


############################################################################################################################
uiitem("ネームツール")
############################################################################################################################





def packimg():
    for img in bpy.data.images:
        if img != None:
            bpy.ops.image.pack({'edit_image': img},as_png=True)




########################################
#シングルユーザー化
########################################
class MYOBJECT_199389(bpy.types.Operator):#シングルユーザー化
    """シングルユーザー化"""
    bl_idname = "object.myobject_199389"
    bl_label = "シングルユーザー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=True, texture=True, animation=False)
        
        
        return {'FINISHED'}
########################################

########################################
#複製
########################################
class MYOBJECT_607832(bpy.types.Operator):#複製
    """複製"""
    bl_idname = "object.myobject_607832"
    bl_label = "複製生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.duplicate()
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=True, texture=True, animation=False)
        obj = bpy.context.active_object
        img = bpy.data.images.new(name = "img",width = 400,height = 400,alpha = True)
        img.generated_color = (0, 0, 0, 0)
        obj.active_material.active_texture.image = img
        
        return {'FINISHED'}
########################################







########################################
#保存
########################################
class MYOBJECT_490317a(bpy.types.Operator):#保存
    """保存"""
    bl_idname = "object.myobject_490317a"
    bl_label = "保存"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="all")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        packimg()
        bpy.ops.wm.save_mainfile()
        self.report({"INFO"},"saved")
        return {'FINISHED'}
########################################

########################################
#保存して閉じる
########################################
class MYOBJECT_669544a(bpy.types.Operator):#保存して閉じる
    """保存して閉じる"""
    bl_idname = "object.myobject_669544a"
    bl_label = "保存して閉じる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUIT",mode="all")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
            packimg()
            bpy.ops.wm.quit_blender()
        else:
            printf("ERROR")
        return {'FINISHED'}
########################################


########################################
#レンダリングのみトグル
########################################
class MYOBJECT_489145(bpy.types.Operator):#レンダリングのみトグル
    """レンダリングのみトグル"""
    bl_idname = "object.myobject_489145"
    bl_label = "レンダリングのみトグル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SCENE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if bpy.context.space_data.show_only_render:
            bpy.context.space_data.show_only_render = False
        else:
            bpy.context.space_data.show_only_render = True
        
        
        
        return {'FINISHED'}
########################################






########################################
#オブジェクトモード
########################################
class MYOBJECT_334541(bpy.types.Operator):#オブジェクトモード
    """オブジェクトモード"""
    bl_idname = "object.myobject_334541"
    bl_label = "オブジェクトモード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}
########################################





########################################
#通常ペン
########################################
class MYOBJECT_878021(bpy.types.Operator):#通常ペン
    """通常ペン"""
    bl_idname = "object.myobject_878021"
    bl_label = "通常ペン"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="IMAGE_ALPHA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.data.brushes["TexDraw"].color = (0, 0, 0)
        bpy.context.scene.tool_settings.unified_paint_settings.size = 1
        bpy.data.brushes["TexDraw"].strength = 1
        bpy.data.brushes["TexDraw"].use_pressure_strength = False
        bpy.data.brushes["TexDraw"].blend = 'MIX'
        
        return {'FINISHED'}
########################################


########################################
#消しゴム アルファ
########################################
class MYOBJECT_114451(bpy.types.Operator):#消しゴム アルファ
    """消しゴム　アルファ"""
    bl_idname = "object.myobject_114451"
    bl_label = "消しゴム　アルファ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SEQ_PREVIEW",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.context.scene.tool_settings.unified_paint_settings.size = 20
        bpy.data.brushes["TexDraw"].blend = 'ERASE_ALPHA'
        
        return {'FINISHED'}
########################################



########################################
#消しゴム 白
########################################
class MYOBJECT_125921(bpy.types.Operator):#消しゴム 白
    """消しゴム　白"""
    bl_idname = "object.myobject_125921"
    bl_label = "消しゴム　白"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATPLANE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.data.brushes["TexDraw"].color = (1, 1, 1)
        bpy.context.scene.tool_settings.unified_paint_settings.size = 20
        bpy.data.brushes["TexDraw"].blend = 'MIX'
        return {'FINISHED'}
########################################



########################################
#大ブラシ
########################################
class MYOBJECT_960402(bpy.types.Operator):#大ブラシ
    """大ブラシ"""
    bl_idname = "object.myobject_960402"
    bl_label = "大ブラシ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="INLINK",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.size = 150
        
        return {'FINISHED'}
########################################















############################################################################################################################
uiitem("テキスト")
############################################################################################################################
#########################################
##新規テキスト
#########################################
#class MYOBJECT_816263(bpy.types.Operator):#新規テキスト
#    """新規テキスト"""
#    bl_idname = "object.myobject_816263"
#    bl_label = "新規テキスト"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")

#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.ops.object.text_add(radius=1, view_align=False, enter_editmode=False, location=bpy.context.space_data.cursor_location, layers=layers(put_visible_last=True))
#        bpy.ops.object.myobject_757107()
#        return {'FINISHED'}
#########################################



########################################
#ヘルパー起動
########################################
class MYOBJECT_757107(bpy.types.Operator):#ヘルパー起動
    """ヘルパー起動"""
    bl_idname = "object.myobject_757107"
    bl_label = "ヘルパー起動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="BLENDER")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        import bpy
        import os
        
        if bpy.data.filepath == "":
            return
        
        dir = os.path.dirname(bpy.data.filepath)
        exefile = "日本語入力ヘルパー.exe"
        exefullpath = dir + os.sep + exefile
        
        if not os.path.exists(exefullpath):
            self.report({"INFO"},"ヘルパーが存在しません。")
            return {'FINISHED'}
        
#        os.system(exefullpath)
        subprocess.Popen(exefullpath)
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#日本語入力.txt
########################################
class MYOBJECT_542245(bpy.types.Operator):#日本語入力.txt
    """日本語入力.txt"""
    bl_idname = "object.myobject_542245"
    bl_label = "日本語入力.txt"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_FONT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if active() == None or active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}


        import bpy
        import os
        import codecs
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        text = ""
        
        
        #f = open(txtfullpath)
        f = codecs.open(txtfullpath, "r", "utf-8")
        text = f.read()
        f.close()
        
        obj = bpy.context.active_object
        if obj.type != "FONT" or obj.select == False:
            bpy.ops.object.text_add()
        
        obj = bpy.context.active_object
        
        
        obj.data.body = text.replace(text[0],"")
        
        self.report({"INFO"},text)
        
        
        
        #テキストを消す
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write("")
        f.close()
        return {'FINISHED'}
########################################

########################################
#流し込み
########################################
class MYOBJECT_46615(bpy.types.Operator):#流し込み
    """流し込み"""
    bl_idname = "object.myobject_46615"
    bl_label = "流し込み"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if active() == None or active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}

        import bpy
        import os
        import codecs
        import re
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        text = ""
        
        
        #f = open(txtfullpath)
        f = codecs.open(txtfullpath, "r", "utf-8")
        text = f.read()
        f.close()
        text = text.replace(text[0],"")

        obj = bpy.context.active_object
        if obj.type != "FONT" or obj.select == False:
            bpy.ops.object.text_add()
        

        obj = bpy.context.active_object
        base = obj
        
        #sep = "☆セパレータ☆"
        #texts = text.replace().split(sep)
        p = re.compile(r"\n{2,}")
        texts = p.split(text)

        #active().data.body = texts[0]

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        textobjs = []
        for text in texts:
            if text == "":
                continue

            deselect()
            obj = active()
            textobjs.append(obj)

            obj.data.body = text

            obj.select = True

            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            dup = active()
            deselect()

            dup.location[1] -= obj.dimensions[1]+obj.data.size

        deselect()
        delete(active())
        

        for textobj in textobjs:
            textobj.select = True
        
        activate(base)
        
        #テキストを消す
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write("")
        f.close()
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






########################################
#編集
########################################
class MYOBJECT_665745(bpy.types.Operator):#編集
    """編集"""
    bl_idname = "object.myobject_665745"
    bl_label = "編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EDIT",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if active() == None or active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}

        import bpy
        import os
        import codecs
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        
        
        obj = bpy.context.active_object
        if obj.type != "FONT":
            self.report({"INFO"},"非テキストオブジェクト。")
            return {'FINISHED'}
        
        text = obj.data.body
        
        #f = open(txtfullpath,"w")
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write(text)
        f.close()
        
        
        
        
        return {'FINISHED'}
########################################

########################################
#アクティブへまとめる
########################################
class MYOBJECT_352627(bpy.types.Operator):#アクティブへまとめる
    """アクティブへまとめる"""
    bl_idname = "object.myobject_352627"
    bl_label = "アクティブへまとめる"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = active()
        selected = get_selected_list()
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1, view_align=False, location=obj.location, layers=obj.layers)
        empty = active()

        for slc in selected:
            slc.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)



        return {'FINISHED'}
########################################







############################################################################################################################
uiitem("画像ファイル")
############################################################################################################################


########################################
#外部エディタで編集
########################################
class MYOBJECT_381157(bpy.types.Operator):#外部エディタで編集
    """外部エディタで編集"""
    bl_idname = "object.myobject_381157"
    bl_label = "外部エディタで編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
#        if len(bpy.context.selected_objects) > 20:
#            self.report({"INFO"},"多すぎ注意！！")
#            return {'FINISHED'}
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.active_material != None:
                    if obj.active_material.active_texture != None:
                        if obj.active_material.active_texture.image != None:
                            dir = os.path.dirname(bpy.data.filepath)
                            path = dir + os.sep + obj.active_material.active_texture.image.filepath.replace("//","")
                            bpy.ops.image.external_edit(filepath=path)
        
        
        
        return {'FINISHED'}
########################################

########################################
#選択リロード
########################################
class MYOBJECT_754499(bpy.types.Operator):#選択リロード
    """選択リロード"""
    bl_idname = "object.myobject_754499"
    bl_label = "選択リロード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.active_material != None:
                    if obj.active_material.active_texture != None:
                        if obj.active_material.active_texture.image != None:
                            bpy.ops.image.reload({"edit_image":obj.active_material.active_texture.image})
        
        
        return {'FINISHED'}
########################################






########################################
#リロード・開く
########################################
class MYOBJECT_980757(bpy.types.Operator):#リロード・開く
    """リロード・開く"""
    bl_idname = "object.myobject_980757"
    bl_label = "リロード・開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.myobject_754499()
        bpy.ops.object.myobject_381157()
        
        return {'FINISHED'}
########################################









#########################################
##全てリロード
#########################################
#class MYOBJECT_821048(bpy.types.Operator):#全てリロード
#    """全てリロード"""
#    bl_idname = "object.myobject_821048"
#    bl_label = "全てリロード"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        for obj in bpy.data.objects:
#            if obj.type == "MESH":
#                if obj.active_material != None:
#                    if obj.active_material.active_texture != None:
#                        if obj.active_material.active_texture.image != None:
#                            bpy.ops.image.reload({"edit_image":obj.active_material.active_texture.image})
#
#
#        return {'FINISHED'}
#########################################














############################################################################################################################
uiitem("その他")
############################################################################################################################



########################################
#ビューロックトグル
########################################
class MYOBJECT_938626(bpy.types.Operator):#ビューロックトグル
    """ビューロックトグル"""
    bl_idname = "object.myobject_938626"
    bl_label = "ロック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if bpy.context.space_data.lock_camera:
            bpy.context.space_data.lock_camera = False
        else:
            bpy.context.space_data.lock_camera = True
        
        return {'FINISHED'}
########################################

########################################
#LSing
########################################
class MYOBJECT_985887(bpy.types.Operator):#LSing
    """オブジェクトを単一レイヤー化する"""
    bl_idname = "object.myobject_985887"
    bl_label = "単レ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.data.objects:
            for l in range(19,0,-1):
                    obj.layers[l] = False
        
        
        
        return {'FINISHED'}
########################################

########################################
#オブジェクトを統合（グルーピング）
########################################
class MYOBJECT_482619(bpy.types.Operator):#オブジェクトを統合（グルーピング）
    """オブジェクトを統合（グルーピング）"""
    bl_idname = "object.myobject_482619"
    bl_label = "オブジェクトを統合（グルーピング）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        mesh_exists = False
        #メッシュがあればグループ統合、そうじゃなければ普通に統合。
        for obj in get_selected_list():
            if obj.type == "MESH":
                mesh_exists = True

        if mesh_exists:
            reject_notmesh()
        
            target = active()
            for obj in bpy.context.selected_objects:
                activate(obj)
                mode("EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_assign_new()
                vgroup = obj.vertex_groups[len(obj.vertex_groups) - 1]
                vgroup.name = obj.name
                mode("OBJECT")

                #subsurf以外のmodは適用するべき？

            activate(target)

        bpy.ops.object.join()
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------







########################################
#プロクシ作成
########################################
class MYOBJECT_b424289a(bpy.types.Operator):#プロクシ作成
    """プロクシ作成　自動キーフレームオン"""
    bl_idname = "object.myobject_b424289a"
    bl_label = "プロクシ作成"
    bl_options = {'REGISTER', 'UNDO'}

    #uiitem = uiitem()
    #uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #blenrig用プロクシの作成
        make_proxy("biped_blenrig")
        #roomtoolsのプロクシ作成（mapcontroller用）を実行
        bpy.ops.object.myobject_424289()

        #make_proxy_all()

        #プロクシ作るとキーフレームじゃないと保存されなかったりするので自動キーフレームうつ
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        
        #deselect()
        #pobj.select = True




        ##リンクデータのオブジェクト
        #inlinkobjects = pobj.dupli_group.objects
        
        #mp_name = ""
        #for obj in inlinkobjects:
        #    if "MapController" in obj.name:
        #        mp_name = obj.name
        #        break

        #if mp_name == "":
        #    self.report({"INFO"},"MapControllerがありません。")
        #    return {'CANCELLED'}

        #bpy.ops.object.proxy_make(object=mp_name)

        #mapcontroller = active()
        #map.select = True

        #bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        #bpy.ops.object.mode_set(mode='POSE', toggle=False)


        return {'FINISHED'}
########################################

########################################
#プロクシ作成（全）
########################################
class MYOBJECT_248120(bpy.types.Operator):#プロクシ作成（全）
    """プロクシ作成（全）"""
    bl_idname = "object.myobject_248120"
    bl_label = "Full Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #プロクシ＝アニメつけるってことだからオート記録オンに
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        linkobj = active()
        loc = linkobj.location
        objects = make_proxy_all()
        for obj in objects:
            if obj.type == "ARMATURE":
                obj.show_x_ray = True
        deselect()

        bpy.context.space_data.cursor_location = loc
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = active()
        empty.name = linkobj.name
        empty.rotation_euler = linkobj.rotation_euler

        select(objects)
        activate(empty)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        linked_objects = linkobj.dupli_group.objects
        #親子構造の反映
        for obj in objects:
            #プロクシ使う場合トランスフォームはロックした方が望ましい
            obj.lock_location = (True,True,True)
            obj.lock_rotation = (True,True,True)
            obj.lock_scale = (True,True,True)

            basename = obj.name.replace("_proxy", "").replace(get_linkedfilename(linkobj)+"/", "")
            baseobj = None
            if basename in linked_objects:
                baseobj = linked_objects[basename]
            else:
                continue

            self.report({"INFO"},"basename"+basename)

            if baseobj.parent == None:
                continue
            
            targetname = get_linkedfilename(linkobj) + "/" + baseobj.parent.name + "_proxy"
            is_found = False
            for tmp in bpy.data.objects:
                if targetname == tmp.name:
                    is_found = True
            if not is_found:
                continue
            #if targetname not in objects:
            #    continue

            self.report({"INFO"},"targetname"+targetname)

            targetobj = bpy.data.objects[targetname]

            deselect()
            obj.select = True
            activate(targetobj)
            #親子=オブジェクト
            if baseobj.parent_type == "OBJECT":
                mode("OBJECT")
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                pass
            #親子=ボーン
            if baseobj.parent_type == "BONE":
                mode("POSE")
                targetbonename = baseobj.parent_bone

                #ターゲットのアーマチュアレイヤー全部表示しないとだめ
                baselayers = [True for i in range(32)]
                for i in range(32):
                    baselayers[i] = targetobj.data.layers[i]
                targetobj.data.layers = [True for i in range(32)]
                targetobj.data.bones.active = targetobj.data.bones[targetbonename]
                bpy.ops.object.parent_set(type='BONE_RELATIVE')
                #レイヤー表示を戻す
                targetobj.data.layers = baselayers
                mode("OBJECT")
                pass



        return {'FINISHED'}
########################################


########################################
#Lamp Proxy
########################################
class MYOBJECT_199238(bpy.types.Operator):#Lamp Proxy
    """Lamp Proxy"""
    bl_idname = "object.myobject_199238"
    bl_label = "Lamp Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        linkobj = active()
        loc = linkobj.location
        objects = make_proxy_type("LAMP")
        deselect()

        for obj in objects:
            if obj == linkobj:
                continue
            obj.layers = bpy.context.scene.layers

        bpy.context.space_data.cursor_location = loc
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = active()
        empty.name = linkobj.name + "_Lamps"
        empty.rotation_euler = linkobj.rotation_euler

        select(objects)
        linkobj.select = False
        activate(empty)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        return {'FINISHED'}
########################################
























"""
オブジェクトID
    PARENTDATA_OBJECTID
ペアレントデータ
    PARENTDATA_DATA
"""

#すべてのペアレントデータを一旦削除する
def parentdata_deleteall():
    d = "PARENTDATA_OBJECTID"
    for obj in bpy.data.objects:
        if d in obj:
            del obj[d]
    pass

#すべてのオブジェクトにIDを割り当てる
def parentdata_identifyall():
    for obj in bpy.data.objects:
        obj["PARENTDATA_OBJECTID"] = str(random.randint(0,9999999))
    pass

#すべてのオブジェクトの親子情報を格納する
def parentdata_getparentdataall():
    for obj in bpy.data.objects:
        if obj.parent != None:
            obj["PARENTDATA_DATA"] = {"parent":obj.parent["PARENTDATA_OBJECTID"], "type":obj.parent_type, "bone":obj.parent_bone}
    pass


########################################
#ペアレントデータビルド
########################################
class MYOBJECT_95038(bpy.types.Operator):#ペアレントデータビルド
    """ペアレント情報をカスタムデータに格納する"""
    bl_idname = "object.myobject_95038"
    bl_label = "ペアレントデータビルド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        parentdata_deleteall()
        parentdata_identifyall()
        parentdata_getparentdataall()
        return {'FINISHED'}
########################################


#ペアレントデータから親子関係をビルドする
def parentdata_buildfromparentdata():
    mode("OBJECT")
    for obj in bpy.data.objects:
        deselect()

        #すでに親がある場合はスキップ
        if obj.parent != None:
            continue

        if "PARENTDATA_DATA" in obj:
            obj.select = True
            for target in bpy.data.objects:
                if "PARENTDATA_OBJECTID" in target:
                    if target["PARENTDATA_OBJECTID"] == obj["PARENTDATA_DATA"]["parent"]:
                        activate(target)
                        break
            
            if obj["PARENTDATA_DATA"]["type"] != "BONE":
                #維持してペアレント
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            else:
                #ボーン相対
                mode("POSE")
                #ターゲットのアーマチュアレイヤー全部表示しないとだめ
                baselayers = [True for i in range(32)]
                for i in range(32):
                    baselayers[i] = target.data.layers[i]
                target.data.layers = [True for i in range(32)]
                target.data.bones.active = target.data.bones[obj["PARENTDATA_DATA"]["bone"]]
                bpy.ops.object.parent_set(type='BONE_RELATIVE')
                #レイヤー表示を戻す
                target.data.layers = baselayers
                mode("OBJECT")

        pass

    pass

########################################
#ビルドフロムペアレントデータ
########################################
class MYOBJECT_349810(bpy.types.Operator):#ビルドフロムペアレントデータ
    """ペアレントデータから親子を構築する"""
    bl_idname = "object.myobject_349810"
    bl_label = "ビルドフロムペアレントデータ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        parentdata_buildfromparentdata()
        return {'FINISHED'}
########################################



#
#
#↑これ、、すでにあった！！！
#
#


########################################
#複製を実体化
########################################
class MYOBJECT_286013(bpy.types.Operator):#複製を実体化
    """複製を実体化+ローカル化も。"""
    bl_idname = "object.myobject_286013"
    bl_label = "複製を実体化+ローカル化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        selection = get_selected_list()

        #すべてオブジェクトモードに
        baseobj = active()
        for obj in bpy.data.objects:
            activate(obj)
            mode("OBJECT")
        activate(baseobj)
        deselect()
        select(selection)

        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
        #proxyあると落ちる→アーマチュアの除去処理必要
        #アーマチュア名_proxyで検索して該当を削除する
        deltarget = []
        for obj in selection:
            if obj.type == "ARMATURE":
                proxyname = obj.name + "_proxy"
                if proxyname in bpy.data.objects:
                    deltarget.append(bpy.data.objects[proxyname])
        delete(deltarget)
        select(selection)
        bpy.ops.object.make_local(type='SELECT_OBDATA_MATERIAL')

        return {'FINISHED'}
########################################




########################################
#AssetManager用キャラリンク後ポストプロセス
########################################
class MYOBJECT_823369(bpy.types.Operator):#AssetManager用キャラリンク後ポストプロセス
    """AssetManager用キャラリンク後ポストプロセス"""
    bl_idname = "object.myobject_823369"
    bl_label = "AssetManager用キャラリンク後ポストプロセス"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #複製を実体化
        bpy.ops.object.myobject_286013()


        #オートキーフレームオン
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        #最大フレーム10
        bpy.context.scene.frame_end = 10

        #フレーム1
        bpy.ops.screen.frame_jump(end=False)
        
        #アーマチュアを全部キーフレーム入れる
        for obj in get_selected_list():
            if obj.type == "ARMATURE":
                activate(obj)
                mode("POSE")
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                mode("OBJECT")


        #フレーム10に移動
        bpy.ops.screen.frame_jump(end=True)


        return {'FINISHED'}
########################################






class fjw_set_key(bpy.types.Operator):
    """キーフレーム挿入"""
    bl_idname = "object.fjw_set_key"
    bl_label = "キーフレーム挿入"

    def setkey(self, context):
        if active().type == "ARMATURE":
            mode("POSE")
        if active().mode == "OBJECT":
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
        if active().mode == "POSE":
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')


    def armature_autokey(self,context):
        if active().type != "ARMATURE":
            return

        mode("POSE")

        #アーマチュアのキーをオートで入れる
        if bpy.context.scene.frame_current == 10:
            rootname = get_root(active()).name

            #bpy.ops.object.parent_clear(type='CLEAR')
            active().location = Vector((0,0,0))

            self.setkey(context)

            #フレーム10なら微調整じゃないのでオートフレーム。
            armu = ArmatureUtils(active())

            geoname = armu.findname("Geometry")
            if geoname == None:
                #head位置が0,0,0のものを探してやればいいのでは？
                for ebone in active().data.bones:
                    if ebone.head == Vector((0,0,0)):
                        geoname = ebone.name
                        break

            #それでもなければアクティブをジオメトリに使う
            if geoname == None:
                geoname = armu.poseactive().name
            geo = armu.posebone(geoname)
            armu.clearTrans([geo])

            self.setkey(context)

            framejump(1)
            selection = armu.select_all()
            armu.clearTrans(selection)

            self.setkey(context)

            #選択にズーム
            bpy.ops.view3d.view_selected(use_all_regions=False)

            #Bodyがあったらそのまま出力までやっちゃう
            for child in active().children:
                if child.type == "MESH":
                    if "Body" in child.name:
                        activate(child)

                        #dir = os.path.dirname(bpy.data.filepath) + os.sep + "MDData" + os.sep
                        #blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                        #name = "avatar_" + blendname + "_" + rootname
                        #name = name.replace("_MDWork","")
                        name = rootname
                        blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                        blendname = blendname.replace("_MDWork","")
                        dir = os.path.dirname(bpy.data.filepath) + os.sep + "MDData" + os.sep
                        dir += blendname + os.sep + name + os.sep
                        export_mdavatar(self, dir, name, False)
                        self.report({"INFO"},dir+name);
                        break
            framejump(10)
            pass

        pass
    
    def execute(self, context):
        #複数対応
        selection = get_selected_list()
        for obj in selection:
            deselect()
            activate(obj)

            self.setkey(context)
            self.armature_autokey(context)
        return {"FINISHED"}



class framejump_1(bpy.types.Operator):
    """フレーム移動　1"""
    bl_idname = "object.framejump_1"
    bl_label = "1"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        #bpy.ops.screen.frame_offset(delta=-1)
        return {"FINISHED"}


class framejump_5(bpy.types.Operator):
    """フレーム移動　5"""
    bl_idname = "object.framejump_5"
    bl_label = "5"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=4)
        return {"FINISHED"}

class framejump_10(bpy.types.Operator):
    """フレーム移動　10"""
    bl_idname = "object.framejump_10"
    bl_label = "10"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=9)
        return {"FINISHED"}

class framejump_15(bpy.types.Operator):
    """フレーム移動　15"""
    bl_idname = "object.framejump_15"
    bl_label = "15"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=14)
        return {"FINISHED"}


class DialogMain(bpy.types.Operator,MyaddonView3DPanel):
    """DialogMain"""
    bl_idname = "object.dialog_mainpanel"
    bl_label = "MainPanel"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self,width=500) 
    pass




























############################################################################################################################
uiitem("メモ：T/NパネルはF5で位置入替えできる")
############################################################################################################################













#各メニューへの追加
#https://www.blender.org/api/blender_python_api_2_76b_release/info_tutorial_addon.html
def menu_func_VIEW3D_MT_object_apply(self, context):
#    self.layout.operator(,icon="")
    self.layout.operator("object.myobject_557231",icon="FILE_TICK")
    self.layout.operator("object.myobject_661107",icon="FILE_TICK")
    self.layout.operator("object.myobject_234815",icon="RESTRICT_VIEW_ON")

#http://blender.stackexchange.com/questions/3393/add-custom-menu-at-specific-location-in-the-header
def menu_func_VIEW3D_HT_header(self, context):
    layout = self.layout
    #単レ化はいらない
    active = layout.row(align = True)
    #active.operator("object.myobject_985887")


    active = layout.row(align = True)
    #active.label(text="",icon="COLLAPSEMENU")
    active.operator("object.myobject_357169",icon="SNAP_GRID")
    active.operator("object.myobject_33358",icon="SNAP_VERTEX")
    #active.operator("object.myobject_993743",icon="SNAP_EDGE")
    active.operator("object.myobject_911158",icon="SNAP_FACE")

    active = layout.row(align = True)
    active.operator("object.myobject_59910",icon="CURSOR")
    active.operator("object.myobject_995874",icon="ROTATECENTER")

    active = layout.row(align = True)
    #row.operator("object.myobject_938626",icon="CAMERA_DATA")
    active.prop(bpy.context.space_data, "lock_camera", icon="CAMERA_DATA", text="")
    active.prop(bpy.context.space_data, "show_only_render", icon="RESTRICT_RENDER_OFF", text="")
    #active = layout.row(align = True)
    #active.operator("screen.region_quadview",icon="OUTLINER_OB_LATTICE", text="")
    active = layout.row(align = True)
    active.prop(bpy.context.tool_settings, "use_keyframe_insert_auto", icon="REC", text="")
    active.operator("object.framejump_1",icon="REW", text="")
    active.operator("object.framejump_5",icon="SPACE3", text="")
    active.operator("object.framejump_10",icon="FF", text="")
    #active.operator("object.framejump_15",icon="TRIA_RIGHT_BAR", text="")
    active.operator("object.fjw_set_key", icon="KEYINGSET", text="")
    active = layout.row(align = True)
    #active.operator("view3d.hops_helper_popup", text = "Mod", icon="SCRIPTPLUGINS").tab = "MODIFIERS"
    active.operator("object.myobject_979047", text="GL",icon="RENDER_STILL")
    active.operator("object.myobject_171760", text="MASK")
    active.operator("object.myobject_242623", text="",icon="GREASEPENCIL")
    active.operator("object.dialog_mainpanel", text="MAIN")
    active = layout.row(align = True)
    active.operator("object.myobject_96321", text="",icon="SOLO_ON")


############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################

def sub_registration():
    bpy.app.handlers.load_post.append(load_handler)

    #メニュー追加
    bpy.types.VIEW3D_MT_object_apply.append(menu_func_VIEW3D_MT_object_apply)
    bpy.types.VIEW3D_HT_header.append(menu_func_VIEW3D_HT_header)
    pass

def sub_unregistration():
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func_VIEW3D_MT_object_apply)
    bpy.types.VIEW3D_HT_header.remove(menu_func_VIEW3D_HT_header)

    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()

if __name__ == "__main__":
    register()