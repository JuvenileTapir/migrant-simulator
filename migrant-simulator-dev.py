import pickle
import random
import time
import math
import copy
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

class Item:

    def __init__(self,ident,name="...",description='...'',display=True):
        self.ident=ident
        self.name=name
        self.description=description
        self.display=display

    def is_same_as_this(self,other):
        return self.ident==other.ident

    def is_in_list(self,l):
        for n in l:
            if self.is_same_as_this(n):
                return True
        return False

    def remove_this_from_list(self,l):
        for i in range(0,len(l)):
            if self.is_same_as_this(l[i]):
                del l[i]
                return l
        raise ValueError

class Path:

    def __init__(self,tonode):
        self.tonode=tonode
        self.text=''
        self.aftertext=''
        self.required=[]
        self.antirequired=[]
        self.gives=[]
        self.giveifhas=1
        self.takes=[]
        self.takesall=0
        self.gold=0
        self.cangoldneg=0
        self.goldreq=0
        self.hp=0
        self.maxhp=0
        self.canhpoverfill=0
        self.showifcannot=0
        self.displayinline=1

    def can_pass(self,gamestate):
        gstate=copy.deepcopy(gamestate)
        try:
            for n in self.required:
                gstate.inventory=n.remove_this_from_list(gstate.inventory)
            for n in self.antirequired:
                if n.is_in_list(gstate.inventory):
                    return False
            return goldreq>=gstate.gold
        except:
            return False

    def altered_state(self,gstate):
        if self.giveifhas:
            gstate.inventory=gstate.inventory+self.gives
        else:
            for n in self.gives:
                if not n.is_in_list(gstate.inventory):
                    gstate.inventory.append(n)
        if self.takesall==0:
            for n in self.takes:
                if n in gstate.inventory:
                    n.remove_this_from_list(gstate.inventory)
        else:
            for n in self.takes:
                while n in gstate.inventory:
                    n.remove_this_from_list(gstate.inventory)
        gstate.gold+=self.gold
        if self.cangoldneg==0 and gstate.gold<0:
            gstate.gold=0
        gstate.hp+=self.hp
        gstate.maxhp+=self.maxhp
        if self.canhpoverfill==0 and gstate.hp>gstate.maxhp:
            gstate.hp=gstate.maxhp
        return gstate

class Node:

    def __init__(self,title):
        self.title=title
        self.text=''
        self.paths={}
        self.israndom=0

class GameState:

    def __init__(self,node,inventory,gold,hp,maxhp):
        self.node=node
        self.inventory=inventory
        self.gold=gold
        self.hp=hp
        self.maxhp=maxhp

class Game(object):

    def __init__(self,name='',nodes={},start=None,history=[]):
        self.name=name
        self.nodes=nodes
        self.start=start
        self.history=history

class App:

    def __init__(self, master):
        self.master=master
        master.wm_title("Node Selector")
        self.game=Game()
        self.file_name=None
        self.nodeid=None
        self.pathid=None
        self.generalresult=None
        self.startinginventory=[]

        self.nodechoice=StringVar(master,'')

        self.nodeselectlabel=Label(master,text="Nodes:")
        self.nodeselectlabel.grid(row=0,column=0,rowspan=3)

        self.nodelist=Listbox(master,selectmode=SINGLE)
        self.nodelist.grid(row=0,column=1)
        self.nodelistscroll=Scrollbar(master,command=self.nodelist.yview)
        self.nodelistscroll.grid(row=0,column=2,sticky=N+S+W)
        self.nodelisthscroll=Scrollbar(master,command=self.nodelist.xview,orient=HORIZONTAL)
        self.nodelisthscroll.grid(row=1,column=1,sticky=N+E+W)
        self.nodelist.configure(yscrollcommand=self.nodelistscroll.set,width=80,xscrollcommand=self.nodelisthscroll.set)
        self.nodelist.bind("<Return>",self.updatenodechoicefromlist)
        self.nodelist.bind("<Double-Button-1>",self.updatenodechoicefromlist)

        self.nodeselect=Entry(master,textvariable=self.nodechoice)
        self.nodeselect.grid(row=2,column=1,sticky=E+W)
        self.nodeselect.bind("<Return>",self.updatenodechoicetolist)

        self.nodetextdisplay=StringVar(master,'topkek')

        self.nodetext=Label(master,textvariable=self.nodetextdisplay,justify=CENTER)
        self.nodetext.grid(row=0,column=3,rowspan=2)

        self.nsbutton=Button(master,text="Open Node",command=self.nodeupdated)
        self.nsbutton.grid(row=2,column=3)

        self.startnodelabel=Label(master,text="Start Node: ")
        self.startnodelabel.grid(row=3,column=0)
        self.startnodeentry=Entry(master)
        self.startnodeentry.grid(row=3,column=1,columnspan=2,sticky=E+W)

        self.startgoldlabel=Label(master,text="Start Gold: ")
        self.startgoldlabel.grid(row=4,column=0)
        self.startgoldentry=Entry(master)
        self.startgoldentry.grid(row=4,column=1,columnspan=2,sticky=E+W)

        self.starthplabel=Label(master,text="Start HP: ")
        self.starthplabel.grid(row=5,column=0)
        self.starthpentry=Entry(master)
        self.starthpentry.grid(row=5,column=1,columnspan=2,sticky=E+W)

        self.startmaxhplabel=Label(master,text="Start Max HP: ")
        self.startmaxhplabel.grid(row=6,column=0)
        self.startmaxhpentry=Entry(master)
        self.startmaxhpentry.grid(row=6,column=1,columnspan=2,sticky=E+W)

        self.startinventorylabel=Label(master,text="Inventory:")
        self.startinventorylabel.grid(row=7,column=0)
        self.startinventorylist=Listbox(master)
        self.startinventorylist.grid(row=7,column=1,sticky=E+W)
        self.startinventoryscroll=Scrollbar(master,command=self.startinventorylist.yview)
        self.startinventoryscroll.grid(row=7,column=2,sticky=N+S+W)
        self.startinventorylist.configure(yscrollcommand=self.startinventoryscroll.set)

        self.nsmenubar=Menu(master)

        self.filemenu=Menu(self.nsmenubar)
        self.filemenu.add_command(label="New",command=self.fm_new)
        self.filemenu.add_command(label="Save",command=self.save)
        self.filemenu.add_command(label="Save As",command=self.save_as)
        self.filemenu.add_command(label="Open",command=self.open_file)
        self.nsmenubar.add_cascade(label='File',menu=self.filemenu)

        self.nodesmenu=Menu(self.nsmenubar)
        self.nodesmenu.add_command(label="New",command=self.newnode)
        self.nodesmenu.add_command(label="Rename",command=self.renamenode)
        self.nodesmenu.add_command(label="Delete",command=self.deletenode)
        self.nsmenubar.add_cascade(label="Nodes",menu=self.nodesmenu)

        self.startinvmenu=Menu(self.nsmenubar)
        self.startinvmenu.add_command(label="Add Item",command=self.add_start_inv)
        self.startinvmenu.add_command(label="Remove Item",command=self.del_start_inv)
        self.nsmenubar.add_cascade(label="Starting Inventory",menu=self.startinvmenu)

        self.nseditmenu=Menu(self.nsmenubar)
        self.nseditmenu.add_command(label="Rename Game",command=self.fm_name)

        master.config(menu=self.nsmenubar)

        self.nodeeditor=Toplevel(master)
        self.nodeeditor.wm_title("Node Editor")

        self.nodeeditortitlelabel=Label(self.nodeeditor,text="Title: ")
        self.nodeeditortitlelabel.grid(row=0,column=0,sticky=E+S)

        self.nodeeditortitleentry=Entry(self.nodeeditor)
        self.nodeeditortitleentry.grid(row=0,column=1,columnspan=2,sticky=E+S+W)

        self.nodeeditortextlabel=Label(self.nodeeditor,text="Text: ")
        self.nodeeditortextlabel.grid(row=1,column=0,sticky=N)

        self.nodeeditortext=Text(self.nodeeditor)
        self.nodeeditortext.grid(row=1,column=1,columnspan=2)
        self.nodeeditortextscrollbar=Scrollbar(self.nodeeditor,command=self.nodeeditortext.yview)
        self.nodeeditortextscrollbar.grid(row=1,column=3,sticky=N+S+W)
        self.nodeeditortext.configure(yscrollcommand=self.nodeeditortextscrollbar.set)

        self.pathselectorlabel=Label(self.nodeeditor,text="Paths: ")
        self.pathselectorlabel.grid(row=2,column=0)

        self.pathchoice=StringVar(master,'')

        self.pathlist=Listbox(self.nodeeditor,selectmode=SINGLE)
        self.pathlist.grid(row=2,column=1,columnspan=2,sticky=N+E+S+W)
        self.pathlistscroll=Scrollbar(self.nodeeditor,command=self.pathlist.yview)
        self.pathlistscroll.grid(row=2,column=3,sticky=N+S+W)
        self.pathlisthscroll=Scrollbar(self.nodeeditor,command=self.pathlist.xview,orient=HORIZONTAL)
        self.pathlisthscroll.grid(row=3,column=1,columnspan=2,sticky=N+E+W)
        self.pathlist.configure(yscrollcommand=self.pathlistscroll.set,xscrollcommand=self.pathlisthscroll.set)
        self.pathlist.bind("<Return>",self.updatepathchoicefromlist)
        self.pathlist.bind("<Double-Button-1>",self.updatepathchoicefromlist)

        self.pathselect=Entry(self.nodeeditor,textvariable=self.pathchoice)
        self.pathselect.grid(row=4,column=1,columnspan=2,sticky=N+E+W)
        self.pathselect.bind("<Return>",self.updatepathchoicetolist)

        self.pathselectionbutton=Button(self.nodeeditor,text="Open Path",command=self.pathupdated)
        self.pathselectionbutton.grid(row=4,column=3)

        self.is_rand=IntVar(master,0)
        self.nodeeditorisrandbutton=Checkbutton(self.nodeeditor,text='Chosen path is random',variable=self.is_rand)
        self.nodeeditorisrandbutton.grid(row=6,column=1,columnspan=2)

        self.nodeeditorsavebutton=Button(self.nodeeditor,text="Save",command=self.save_node)
        self.nodeeditorsavebutton.grid(row=7,column=0,columnspan=3)

        self.patheditor=Toplevel(master)
        self.patheditor.wm_title("Path Editor")
        self.petonodelabel=Label(self.patheditor,text="Path To Node: ")
        self.petonodelabel.grid(row=0,column=0)

        self.petonodeentry=Entry(self.patheditor)
        self.petonodeentry.grid(row=0,column=1,sticky=E+W)

        self.petextlabel=Label(self.patheditor,text="Path Text: ")
        self.petextlabel.grid(row=1,column=0)

        self.petextentry=Entry(self.patheditor)
        self.petextentry.grid(row=1,column=1,sticky=E+W)

        self.peaftertextlabel=Label(self.patheditor,text="Text Displayed On Choice: ")
        self.peaftertextlabel.grid(row=2,column=0)

        self.peaftertexttext=Text(self.patheditor)
        self.peaftertexttext.grid(row=2,column=1,columnspan=3)
        self.peaftertextscrollbar=Scrollbar(self.patheditor,command=self.peaftertexttext.yview)
        self.peaftertextscrollbar.grid(row=2,column=4,sticky=N+S+W)
        self.peaftertexttext.configure(yscrollcommand=self.peaftertextscrollbar.set,height=12)

        self.pedisplayinline=IntVar(master,value=1)
        self.pedisplayinlinecheck=Checkbutton(self.patheditor,text="Display Inline", variable=self.pedisplayinline)
        self.pedisplayinlinecheck.grid(row=2,column=5,rowspan=2)

        self.perequiredlabel=Label(self.patheditor,text="Required: ")
        self.perequiredlabel.grid(row=3,column=0)
        self.perequiredlist=Listbox(self.patheditor)
        self.perequiredlist.grid(row=3,column=1,columnspan=3,sticky=E+W)
        self.perequiredscroll=Scrollbar(self.patheditor,command=self.perequiredlist.yview)
        self.perequiredscroll.grid(row=3,column=4,sticky=N+S+W)
        self.perequiredlist.configure(yscrollcommand=self.perequiredscroll.set,height=4)

        self.peantirequiredlabel=Label(self.patheditor,text="Antirequired: ")
        self.peantirequiredlabel.grid(row=4,column=0)
        self.peantirequiredlist=Listbox(self.patheditor)
        self.peantirequiredlist.grid(row=4,column=1,columnspan=3,sticky=E+W)
        self.peantirequiredscroll=Scrollbar(self.patheditor,command=self.peantirequiredlist.yview)
        self.peantirequiredscroll.grid(row=4,column=4,sticky=N+S+W)
        self.peantirequiredlist.configure(yscrollcommand=self.peantirequiredscroll.set,height=4)

        self.peshowifcannot=IntVar(master,value=0)
        self.peshowifcannotcheck=Checkbutton(self.patheditor,text="Show choice if cannot be taken", variable=self.peshowifcannot)
        self.peshowifcannotcheck.grid(row=3,column=5,rowspan=2)

        self.pegiveslabel=Label(self.patheditor,text="Gives: ")
        self.pegiveslabel.grid(row=5,column=0)
        self.pegiveslist=Listbox(self.patheditor)
        self.pegiveslist.grid(row=5,column=1,columnspan=3,sticky=E+W)
        self.pegivesscroll=Scrollbar(self.patheditor,command=self.pegiveslist.yview)
        self.pegivesscroll.grid(row=5,column=4,sticky=N+S+W)
        self.pegiveslist.configure(yscrollcommand=self.pegivesscroll.set,height=4)

        self.pegiveifhas=IntVar(master,value=1)
        self.pegiveifhascheck=Checkbutton(self.patheditor,text="Gives item if player already has one", variable=self.pegiveifhas)
        self.pegiveifhascheck.grid(row=5,column=5)

        self.petakeslabel=Label(self.patheditor,text="Takes: ")
        self.petakeslabel.grid(row=6,column=0)
        self.petakeslist=Listbox(self.patheditor)
        self.petakeslist.grid(row=6,column=1,columnspan=3,sticky=E+W)
        self.petakesscroll=Scrollbar(self.patheditor,command=self.petakeslist.yview)
        self.petakesscroll.grid(row=6,column=4,sticky=N+S+W)
        self.petakeslist.configure(yscrollcommand=self.petakesscroll.set,height=4)

        self.petakesall=IntVar(master,value=0)
        self.petakesallcheck=Checkbutton(self.patheditor,text="Takes all of an item", variable=self.petakesall)
        self.petakesallcheck.grid(row=6,column=5)

        self.pegoldlabel=Label(self.patheditor,text="Gold Given:\n(can be negative)")
        self.pegoldlabel.grid(row=7,column=0)
        self.pegoldentry=Entry(self.patheditor)
        self.pegoldentry.grid(row=7,column=1)
        self.pegoldentry.insert(0,'0')

        self.pegoldreqlabel=Label(self.patheditor,text="Gold Required:\n(can be negative)")
        self.pegoldreqlabel.grid(row=7,column=2)
        self.pegoldreqentry=Entry(self.patheditor)
        self.pegoldreqentry.grid(row=7,column=3)
        self.pegoldreqentry.insert(0,'0')

        self.pecangoldneg=IntVar(master,value=0)
        self.pecangoldnegcheck=Checkbutton(self.patheditor,text="Can drop gold value below 0", variable=self.pecangoldneg)
        self.pecangoldnegcheck.grid(row=7,column=5)

        self.pehplabel=Label(self.patheditor,text="HP Given:\n(can be negative)")
        self.pehplabel.grid(row=8,column=0)
        self.pehpentry=Entry(self.patheditor)
        self.pehpentry.grid(row=8,column=1)
        self.pehpentry.insert(0,'0')

        self.pemaxhplabel=Label(self.patheditor,text="Max HP Given:\n(can be negative)")
        self.pemaxhplabel.grid(row=8,column=2)
        self.pemaxhpentry=Entry(self.patheditor)
        self.pemaxhpentry.grid(row=8,column=3)
        self.pemaxhpentry.insert(0,'0')

        self.pecanhpoverfill=IntVar(master,value=0)
        self.pecanhpoverfillcheck=Checkbutton(self.patheditor,text="Can raise HP value above max HP", variable=self.pecanhpoverfill)
        self.pecanhpoverfillcheck.grid(row=8,column=5)

        self.pesavepathbutton=Button(self.patheditor,text="Save",command=self.save_path)
        self.pesavepathbutton.grid(row=9,column=0,columnspan=6)

        self.menubarpaths=Menu(self.nodeeditor)
        self.menubarpaths.add_command(label="New",command=self.newpath)
        self.menubarpaths.add_command(label="Rename",command=self.renamepath)
        self.menubarpaths.add_command(label="Delete",command=self.deletepath)

        self.nemenubar=Menu(self.nodeeditor)
        self.nemenubar.add_cascade(label="File",menu=self.filemenu)
        self.nemenubar.add_cascade(label="Paths",menu=self.menubarpaths)

        self.nodeeditor.config(menu=self.nemenubar)

        self.menubaritems=Menu(self.patheditor)
        self.menubaritems.add_command(label="Add Required Item",command=self.add_required)
        self.menubaritems.add_command(label="Add Antirequired Item",command=self.add_antirequired)
        self.menubaritems.add_command(label="Add Item to Give",command=self.add_gives)
        self.menubaritems.add_command(label="Add Item to Take",command=self.add_takes)
        self.menubaritems.add_separator()
        self.menubaritems.add_command(label="Remove Required Item",command=self.del_required)
        self.menubaritems.add_command(label="Remove Antirequired Item",command=self.del_antirequired)
        self.menubaritems.add_command(label="Remove Item to Give",command=self.del_gives)
        self.menubaritems.add_command(label="Remove Item to Take",command=self.del_takes)

        self.pemenubar=Menu(self.patheditor)
        self.pemenubar.add_cascade(label="File",menu=self.filemenu)
        self.pemenubar.add_cascade(label="Items",menu=self.menubaritems)

        self.patheditor.config(menu=self.pemenubar)

    def get_item_dialog(self):
        self.itemdialog=Toplevel(self.master)

        self.itemdialogidlabel=Label(self.itemdialog,text="Item ID: ")
        self.itemdialogidlabel.grid(row=0,column=0)
        self.itemdialogidentry=Entry(self.itemdialog)
        self.itemdialogidentry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        self.itemdialogidentry.focus()

        self.itemdialognamelabel=Label(self.itemdialog,text="Item Name: ")
        self.itemdialognamelabel.grid(row=1,column=0)
        self.itemdialognameentry=Entry(self.itemdialog)
        self.itemdialognameentry.grid(row=1,column=1,columnspan=2,sticky=E+W)

        self.itemdialogdesclabel=Label(self.itemdialog,text="Item Description: ")
        self.itemdialogdesclabel.grid(row=2,column=0)
        self.itemdialogdesctext=Text(self.itemdialog)
        self.itemdialogdesctext.grid(row=2,column=1,sticky=N+E+S+W)
        self.itemdialogdesctextscrollbar=Scrollbar(self.itemdialog,command=self.itemdialogdesctext.yview)
        self.itemdialogdesctextscrollbar.grid(row=2,column=2,sticky=N+S+W)
        self.itemdialogdesctext.configure(yscrollcommand=self.itemdialogdesctextscrollbar.set)

        self.itemdialogvisiblevar=IntVar(self.itemdialog,1)
        self.itemdialogvisiblecheck=Checkbutton(self.itemdialog,text="Is visible in inventory",variable=self.itemdialogvisiblevar)
        self.itemdialogvisiblecheck.grid(row=3,column=0,columnspan=3)

        self.itemdialogbutton=Button(self.itemdialog,text="OK",command=self.get_item_confirm)
        self.itemdialogbutton.grid(row=4,column=0,columnspan=3)
        self.master.wait_window(self.itemdialog)

    def get_item_confirm(self):
        self.generalresult=Item(self.itemdialogidentry.get(),self.itemdialognameentry.get(),self.itemdialogdesctext.get('0.0',END),self.itemdialogvisiblevar.get())
        self.itemdialog.destroy()

    def get_item(self):
        self.get_item_dialog()
        return self.generalresult

    def get_itemid_dialog(self):
        self.itemiddialog=Toplevel(self.master)

        self.itemiddialogidlabel=Label(self.itemiddialog,text="Item ID: ")
        self.itemiddialogidlabel.grid(row=0,column=0)
        self.itemiddialogidentry=Entry(self.itemiddialog)
        self.itemiddialogidentry.grid(row=0,column=1,sticky=E+W)
        self.itemiddialogidentry.focus()

        self.itemiddialogbutton=Button(self.itemiddialog,text="OK",command=self.get_itemid_confirm)
        self.itemiddialogbutton.grid(row=1,column=0,columnspan=2)
        self.master.wait_window(self.itemiddialog)

    def get_itemid_confirm(self):
        self.generalresult=Item(self.itemiddialogidentry.get())
        self.itemiddialog.destroy()

    def get_itemid(self):
        self.get_itemid_dialog()
        return self.generalresult

    def add_required(self):
        self.game.nodes[self.nodeid].paths[self.pathid].required.append(self.get_itemid())
        self.updateitemlists()

    def add_antirequired(self):
        self.game.nodes[self.nodeid].paths[self.pathid].antirequired.append(self.get_itemid())
        self.updateitemlists()

    def add_gives(self):
        self.game.nodes[self.nodeid].paths[self.pathid].gives.append(self.get_item())
        self.updateitemlists()

    def add_takes(self):
        self.game.nodes[self.nodeid].paths[self.pathid].takes.append(self.get_itemid())
        self.updateitemlists()

    def add_start_inv(self):
        self.startinginventory.append(self.get_itemid())
        self.updatestartinv()

    def updatestartinv(self):
        self.startinventorylist.delete(0,END)
        for n in list(sorted(list(self.startinginventory))):
            self.startinventorylist.insert(END,n.ident)

    def del_start_inv(self):
        try:
            self.startinginventory.remove(self.get_itemid())
            self.updatestartinv()
        except:
            pass

    def del_required(self):
        try:
            self.game.nodes[self.nodeid].paths[self.pathid].required.remove(self.get_itemid())
            self.updateitemlists()
        except:
            pass

    def del_antirequired(self):
        try:
            self.game.nodes[self.nodeid].paths[self.pathid].antirequired.remove(self.get_itemid())
            self.updateitemlists()
        except:
            pass

    def del_gives(self):
        try:
            self.game.nodes[self.nodeid].paths[self.pathid].gives.remove(self.get_itemid())
            self.updateitemlists()
        except:
            pass

    def del_takes(self):
        try:
            self.game.nodes[self.nodeid].paths[self.pathid].takes.remove(self.get_itemid())
            self.updateitemlists()
        except:
            pass

    def save_node(self):
        self.game.nodes[self.nodeid].title=self.nodeeditortitleentry.get()
        self.game.nodes[self.nodeid].text=self.nodeeditortext.get('0.0',END)
        self.game.nodes[self.nodeid].israndom=self.is_rand.get()

    def save_path(self):
        self.game.nodes[self.nodeid].paths[self.pathid].tonode=self.petonodeentry.get()
        self.game.nodes[self.nodeid].paths[self.pathid].text=self.petextentry.get()
        self.game.nodes[self.nodeid].paths[self.pathid].aftertext=self.peaftertexttext.get('0.0',END)
        self.game.nodes[self.nodeid].paths[self.pathid].displayinline=self.pedisplayinline.get()
        self.game.nodes[self.nodeid].paths[self.pathid].showifcannot=self.peshowifcannot.get()
        self.game.nodes[self.nodeid].paths[self.pathid].giveifhas=self.pegiveifhas.get()
        self.game.nodes[self.nodeid].paths[self.pathid].takesall=self.petakesall.get()
        self.game.nodes[self.nodeid].paths[self.pathid].cangoldneg=self.pecangoldneg.get()
        self.game.nodes[self.nodeid].paths[self.pathid].canhpoverfill=self.pecanhpoverfill.get()

    def updatenodechoicefromlist(self,event):
        self.nodechoice.set(self.nodelist.get(ACTIVE))
        self.nodetextdisplay.set(self.game.nodes[self.nodechoice.get()].title+"\n"+self.game.nodes[self.nodechoice.get()].text[:64])

    def updatenodechoicetolist(self,*args):
        try:
            self.nodelist.selection_clear(0,END)
            self.nodelist.selection_set(self.nodelist.index(self.nodechoice.get()))
            self.nodelist.yview_moveto(0)
            self.nodelist.yview_scroll(self.nodelist.index(self.nodechoice.get()),"units")
            self.nodetextdisplay.set(self.game.nodes[self.nodechoice.get()].title+"\n"+self.game.nodes[self.nodechoice.get()].text[:64])
        except:
            pass

    def pathupdated(self):
        self.pathid=self.pathchoice.get()
        try:
            self.petonodeentry.delete(0,END)
        except:
            pass
        self.petonodeentry.insert(END,self.game.nodes[self.nodeid].paths[self.pathid].tonode)
        try:
            self.petextentry.delete(0,END)
        except:
            pass
        self.petextentry.insert(END,self.game.nodes[self.nodeid].paths[self.pathid].text)
        try:
            self.peaftertexttext.delete('0.0',END)
        except:
            pass
        self.peaftertexttext.insert('0.0',self.game.nodes[self.nodeid].paths[self.pathid].aftertext)
        self.updateitemlists()
        self.displayinline=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].displayinline)
        self.showifcannot=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].showifcannot)
        self.giveifhas=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].giveifhas)
        self.takesall=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].takesall)
        self.cangoldneg=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].cangoldneg)
        self.canhpoverfill=IntVar(self.master,self.game.nodes[self.nodeid].paths[self.pathid].canhpoverfill)

    def nodeupdated(self):
        self.nodeid=self.nodechoice.get()
        self.nodetextdisplay.set(self.game.nodes[self.nodeid].title+"\n"+self.game.nodes[self.nodeid].text)
        try:
            self.nodeeditortitleentry.delete(0,END)
        except:
            pass
        self.nodeeditortitleentry.insert(END,self.game.nodes[self.nodeid].title)
        try:
            self.nodeeditortext.delete('0.0',END)
        except:
            pass
        self.nodeeditortext.insert('0.0',self.game.nodes[self.nodeid].text)
        self.is_rand=IntVar(self.master,self.game.nodes[self.nodeid].israndom)
        self.updatepathlist()

    def updatepathchoicefromlist(self,event):
        self.pathchoice.set(self.pathlist.get(ACTIVE))

    def updatepathchoicetolist(self,*args):
        try:
            self.pathlist.selection_clear(0,END)
            self.pathlist.selection_set(self.pathlist.index(self.pathchoice.get()))
            self.pathlist.yview_moveto(0)
            self.pathlist.yview_scroll(self.pathlist.index(self.pathchoice.get()),"units")
        except:
            pass

    def fm_new(self):
        self.game=Game()
        self.fm_name()

    def fm_name(self):
        self.gamenamequery=Toplevel(self.master)
        self.gnqlabel=Label(self.gamenamequery,text="What is the name of the game?")
        self.gnqlabel.grid(row=0,column=0)
        self.gnqentry=Entry(self.gamenamequery)
        self.gnqentry.grid(row=1,column=0)
        self.gnqbutton=Button(self.gamenamequery,text="OK",command=self.fm_nameconfirm)
        self.gnqbutton.grid(row=2,column=0)

    def fm_nameconfirm(self):
        self.game.name=self.gnqentry.get()
        self.gamenamequery.destroy()
        self.updatenodelist()

    def save(self):
        if self.file_name==None:
            self.save_as()
        self.game.start=GameState(self.startnodeentry.get(),self.startinginventory,int(self.startgoldentry.get()),int(self.starthpentry.get()),int(self.startmaxhpentry.get()))
        file=open(self.file_name,'wb')
        pickle.dump(self.game,file)
        file.close()

    def save_as(self):
        self.file_name=filedialog.asksaveasfilename(defaultextension=".mig30",filetypes=(("Migrant Simulator 3.0",".mig30"),("All files","*")))
        self.save()

    def open_file(self):
        self.file_name=filedialog.askopenfilename()
        file=open(self.file_name,mode='rb')
        self.game=pickle.load(file)
        file.close()
        self.updatenodelist()
        self.startinginventory=self.game.start.inventory
        self.updatestartinv()
        try:
            self.startnodeentry.delete(0,END)
        except:
            pass
        self.startnodeentry.insert(END,self.game.start.node)
        try:
            self.startgoldentry.delete(0,END)
        except:
            pass
        self.startgoldentry.insert(END,self.game.start.gold)
        try:
            self.starthpentry.delete(0,END)
        except:
            pass
        self.starthpentry.insert(END,self.game.start.hp)
        try:
            self.startmaxhpentry.delete(0,END)
        except:
            pass
        self.startmaxhpentry.insert(END,self.game.start.maxhp)

    def newnode(self):
        self.newnodequery=Toplevel(self.master)
        self.newnodelabelid=Label(self.newnodequery,text='Node ID: ')
        self.newnodelabelid.grid(row=0,column=0)
        self.newnodeentryid=Entry(self.newnodequery)
        self.newnodeentryid.grid(row=0,column=1)
        self.newnodelabeltitle=Label(self.newnodequery,text="Node Title: ")
        self.newnodelabeltitle.grid(row=1,column=0)
        self.newnodeentrytitle=Entry(self.newnodequery)
        self.newnodeentrytitle.grid(row=1,column=1)
        self.newnodebutton=Button(self.newnodequery,text='OK',command=self.newnodeconfirm)
        self.newnodebutton.grid(row=2,column=0,columnspan=2)

    def newnodeconfirm(self):
        self.game.nodes[self.newnodeentryid.get()]=Node(self.newnodeentrytitle.get())
        self.newnodequery.destroy()
        self.updatenodelist()

    def newpath(self):
        self.newpathquery=Toplevel(self.master)
        self.newpathlabelid=Label(self.newpathquery,text='Path ID: ')
        self.newpathlabelid.grid(row=0,column=0)
        self.newpathentryid=Entry(self.newpathquery)
        self.newpathentryid.grid(row=0,column=1)
        self.newpathlabeltonode=Label(self.newpathquery,text="Path To Node: ")
        self.newpathlabeltonode.grid(row=1,column=0)
        self.newpathentrytonode=Entry(self.newpathquery)
        self.newpathentrytonode.grid(row=1,column=1)
        self.newpathbutton=Button(self.newpathquery,text='OK',command=self.newpathconfirm)
        self.newpathbutton.grid(row=2,column=0,columnspan=2)

    def newpathconfirm(self):
        self.game.nodes[self.nodeid].paths[self.newpathentryid.get()]=Path(self.newpathentrytonode.get())
        self.newpathquery.destroy()
        self.updatepathlist()

    def renamenode(self):
        self.renamenodequery=Toplevel(self.master)
        self.renamenodelabelold=Label(self.renamenodequery,text='Old Node ID: ')
        self.renamenodelabelold.grid(row=0,column=0)
        self.renamenodeentryold=Entry(self.renamenodequery)
        self.renamenodeentryold.grid(row=0,column=1)
        self.renamenodelabelnew=Label(self.renamenodequery,text="New Node ID: ")
        self.renamenodelabelnew.grid(row=1,column=0)
        self.renamenodeentrynew=Entry(self.renamenodequery)
        self.renamenodeentrynew.grid(row=1,column=1)
        self.renamenodebutton=Button(self.renamenodequery,text='OK',command=self.renamenodeconfirm)
        self.renamenodebutton.grid(row=2,column=0,columnspan=2)

    def renamenodeconfirm(self):
        n=self.game.nodes[self.renamenodeentryold.get()]
        del self.game.nodes[self.renamenodeentryold.get()]
        self.game.nodes[self.renamenodeentrynew.get()]=n
        self.renamenodequery.destroy()
        self.updatenodelist()

    def renamepath(self):
        self.renamepathquery=Toplevel(self.master)
        self.renamepathlabelold=Label(self.renamepathquery,text='Old Path ID: ')
        self.renamepathlabelold.grid(row=0,column=0)
        self.renamepathentryold=Entry(self.renamepathquery)
        self.renamepathentryold.grid(row=0,column=1)
        self.renamepathlabelnew=Label(self.renamepathquery,text="New Path ID: ")
        self.renamepathlabelnew.grid(row=1,column=0)
        self.renamepathentrynew=Entry(self.renamepathquery)
        self.renamepathentrynew.grid(row=1,column=1)
        self.renamepathbutton=Button(self.renamepathquery,text='OK',command=self.renamepathconfirm)
        self.renamepathbutton.grid(row=2,column=0,columnspan=2)

    def renamepathconfirm(self):
        n=self.game.nodes[nodeid].paths[self.renamepathentryold.get()]
        del self.game.nodes[nodeid].paths[self.renamepathentryold.get()]
        self.game.nodes[nodeid].paths[self.renamepathentrynew.get()]=n
        self.renamepathquery.destroy()
        self.updatepathlist()

    def deletenode(self):
        self.deletenodequery=Toplevel(self.master)
        self.deletenodelabelid=Label(self.deletenodequery,text='Node ID to be deleted: ')
        self.deletenodelabelid.grid(row=0,column=0)
        self.deletenodeentryid=Entry(self.deletenodequery)
        self.deletenodeentryid.grid(row=0,column=1)
        self.deletenodebutton=Button(self.deletenodequery,text='OK',command=self.deletenodeconfirm)
        self.deletenodebutton.grid(row=1,column=0,columnspan=2)

    def deletenodeconfirm(self):
        del self.game.nodes[self.deletenodeentryid]
        self.deletenodequery.destroy()
        self.updatenodelist()

    def deletepath(self):
        self.deletepathquery=Toplevel(self.master)
        self.deletepathlabelid=Label(self.deletepathquery,text='Path ID to be deleted: ')
        self.deletepathlabelid.grid(row=0,column=0)
        self.deletepathentryid=Entry(self.deletepathquery)
        self.deletepathentryid.grid(row=0,column=1)
        self.deletepathbutton=Button(self.deletepathquery,text='OK',command=self.deletepathconfirm)
        self.deletepathbutton.grid(row=1,column=0,columnspan=2)

    def deletepathconfirm(self):
        del self.game.nodes[nodeid].paths[self.deletepathentryid]
        self.deletepathquery.destroy()
        self.updatepathlist()

    def updatenodelist(self):
        self.nodelist.delete(0,END)
        for n in list(sorted(list(self.game.nodes))):
            self.nodelist.insert(END,n)

    def updatepathlist(self):
        self.pathlist.delete(0,END)
        for n in list(sorted(list(self.game.nodes[self.nodeid].paths))):
            self.pathlist.insert(END,n)

    def updateitemlists(self):
        self.perequiredlist.delete(0,END)
        for n in list(sorted(self.game.nodes[self.nodeid].paths[self.pathid].required)):
            self.perequiredlist.insert(END,n.id)
        self.peantirequiredlist.delete(0,END)
        for n in list(sorted(self.game.nodes[self.nodeid].paths[self.pathid].antirequired)):
            self.peantirequiredlist.insert(END,n.id)
        self.pegiveslist.delete(0,END)
        for n in list(sorted(self.game.nodes[self.nodeid].paths[self.pathid].gives)):
            self.pegiveslist.insert(END,n.id)
        self.petakeslist.delete(0,END)
        for n in list(sorted(self.game.nodes[self.nodeid].paths[self.pathid].takes)):
            self.petakeslist.insert(END,n.id)

root = Tk()

app = App(root)

root.mainloop()
##root.destroy() # optional; see description below
