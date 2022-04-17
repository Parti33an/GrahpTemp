'''Программа для отображения параметра (температуры) элемента в расстановке.
Можно выбрать цвет элементов, шрифт и его размер для отображаемого параметра.
Управление: изменение масштаба - колесико мышки, сдвижка экрана - перемещение мыши с зажатой левой кнопкой
'''
VERSION_INFO = "Версия 2.0 релиз Python\n (C)&(P) Ванюков Е.Е.\n\t2015 - 2022"

from random import randint
from tkinter import filedialog, messagebox, colorchooser
from tkinter import font
import tkinter
from tkinter.ttk import Combobox
from tkinter import *
import math
import json
from pathlib import *
from turtle import distance

from numpy import size

#Системные параметры
ICON_NAME = "reactor360.ico"
INI_FILE = "graph.ini"
F_EXT = "csv"
DEFAULT_NAME = '' #'noname.' + F_EXT
PROGRAM_NAME = 'GraphTemp '
ACTIVE_COLOR = 'magenta'

# Меню
M_FILE = 'Файл'
M_OPEN = 'Открыть...'
M_QUIT = "Выйти"
M_PUT = 'Элементы'
M_CLEAR = 'Очистить'
M_TVEL = 'тип '
M_TVEL_ADD_TYPE = "Добавить тип"
M_SERVIS = "Сервис"
M_RESET = "Вернуть в исходное"
M_BEAM = "Луч"
M_CIRCLE = "Окружность"
M_SCALE = "Изменить масштаб"
M_OPTIONS = "Настройки"
M_RADIUS = "Радиус элемента"
M_COLORS = "Цвета элементов"
M_BOLDLINE = "Толщина линии"
M_FONT = "Шрифт"
M_FONTSIZE = "Размер шрифта"
M_HELP = "Помощь"
M_ABOUT = 'О программе'
M_VERSION = "Версия"
BASE_COLORS = {'1':'red', '2':'green', '3': 'yellow'}
BASE_MENU = {M_FILE: [M_OPEN, M_QUIT],
                M_PUT: [],
                M_SERVIS : [M_BEAM ,M_CIRCLE, M_SCALE, M_RESET],  
                M_OPTIONS: [M_RADIUS, M_COLORS, M_BOLDLINE, M_FONT, M_FONTSIZE],
                M_HELP: [M_ABOUT, M_VERSION],
                }

def RGB(red,green,blue): return '#%02x%02x%02x' % (int(red), int(green) , int(blue))

def rand_color(): return RGB(randint(0,255), randint(0,255), randint(0,255))

def radius(x,y): return (x*x+y*y)**0.5

class Arrange():
    def __init__(self, r_tvel=0, step=0):
        self.tvel = {} # структура словарь: Ключ - тип ТВЭЛ, значения -(позиции ТВЭЛ, параметр)
        self.r_tvel = r_tvel
        self.step = step
   
    def add(self, i, j, k, type):
        if type not in self.tvel:
            self.tvel[type]=set()
        self.tvel[type].add((i, j, k))
    
    def get_quantity(self, i):
        if i in self.tvel:
            return len(self.tvel[i])
        else:
            return 0
    
    def get_max(self, i):
        if i in self.tvel:
            return max([self.get_value(item) for item in self.tvel[i]])

    def get_size(self):
        number = 0
        for key in self.tvel:
            number += self.get_quantity(key)
        return number
      
    def get_tvel_types(self):
        return list(self.tvel.keys())
        
    def get_items(self):
        return list(set().union(*list(self.tvel.values())))
    
    def set_default(self):
        tmp = self.get_items()
        min_distance = radius(tmp[0][0]- tmp[-1][0], tmp[0][1]- tmp[-1][1])
        for i in range(len(tmp)):
            for j in range(i+1, len(tmp)):
                distance = radius(tmp[j][0]- tmp[i][0], tmp[j][1]- tmp[i][1])
                min_distance = distance if distance < min_distance else min_distance
        self.step = min_distance
        self.r_tvel = self.step/2*0.9
    
    @classmethod
    def open(cls, filename):
        if filename=='':
            return None
        try:
            with open(filename,'r') as f:
                tmp=Arrange()
                for line in f:
                        data = line.rstrip().split(";")
                        value=[float(data[i]) for i in range(3)]
                        tmp.add(*value, data[3]) # x, y, value, tvel type
                tmp.set_default()
            return tmp
        except:
            messagebox.showerror(
            "Ошибка чтения файла!",
            "Неверный формат или файл не существует!")
            return None
   
    def get_coord(self, item):
        return item[0], item[1]

    def get_type(self, item):
        for key in self.tvel:
            if item  in self.tvel[key]:
                return key

    def get_value(self, item):
        return item[2]
    

class ServiceDialog():
    def __init__(self, parrent, *args, title = "", geometry = "250x250+200+200", func = lambda: True):
        self.dlg = Toplevel(parrent, bd = 3)
        self.dlg.title(title)
        self.dlg.geometry(geometry)
        self.dlg.resizable(width = False, height= False)
        self.dlg.grab_set()
        #self.window = Label(self.dlg)
        labels = []
        self.entrys = []
        for i in range(len(args)):
            labels.append(Label(self.dlg, text = args[i]))
            #label_r.place(relx=0, rely=0.5, height=20, width=100)
            labels[i].pack(pady=5)
            self.entrys.append(Entry(self.dlg, width=10))
            self.entrys[i].pack(pady=3)
        
        self.entrys[0].focus_set() 
        self.entrys[len(self.entrys)-1].bind("<Return>", lambda obj=self: func(self))
              
        button_ok = Button( self.dlg, text = "Ок", command = lambda obj=self: func(self)) 
        button_ok.bind("<Return>", lambda obj=self: func(self))
        button_ok.pack(side='left', pady = 20, padx=30)
        button_cancel = Button(self.dlg, text="Отмена", command = self.destroy) 
        button_cancel.bind("<Return>", self.destroy)
        button_cancel.pack(side='right',pady = 20, padx=30)
        self.dlg.bind("<Escape>", self.destroy)
    
    def get_value(self):
        try:
            return [float(i.get()) for i in self.entrys]
        except:
            messagebox.showerror("Ошибка типа данных!", "Попробуйте еще раз...")
    
    def destroy(self, *args):
        self.dlg.destroy()
       

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.parent = parent
        self.x0 = 0
        self.y0 = 0

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height

        self.width = event.width 
        self.height = event.height 

        # resize the canvas 
        self.config(width=self.width, height=self.height)
        if(self.parent.arrange != None):
            self.parent.get_scale()
            self.set_center()
            self.parent.draw_arrange()
    
    def get_center(self):
        return self.width/2 + self.x0, self.height/2 - self.y0
    
    def set_center(self, *args):
        if args == ():
            self.x0 = 0
            self.y0 = 0
        else:
            self.x0 = args[0]
            self.y0 = args[1]

class App(Tk):
    global parameters
    menuitem={}

    def __init__(self):
        super().__init__()
        self.configure(bg='blue')
        self.title( PROGRAM_NAME + " - " + DEFAULT_NAME)
        if (Path(ICON_NAME).exists()):
            self.iconbitmap(default = ICON_NAME)
        else:
            pass
        screen_height=int(self.wm_maxsize()[1])  # получаем размер экрана и вычисляем размер окна приложения
        self.start_position_askdialog="+{}+{}".format(int(screen_height/3), int(screen_height/3))
        #self.geometry('{}x{}+{}+{}'.format(int(screen_height*0.9), int(screen_height*0.9), 0, 0))
        self.state("zoomed") #- окно на весь экран над панелью задач
        self.minsize(400, 400)
        self.arrange = None 
        self.scale = 0
        self.boldline = 1
        self.font_size = 1
        self.font = "Arial"
        self.font_list = [f for f in font.families()]
        self.filename = ''
        self.mouse_position=[0,0]
        self.mouse_xy = ()
        self.last_dir = Path.cwd()
        self.colors = BASE_COLORS
        self.menu_ = BASE_MENU
        self.menu_[M_PUT] = [*list(self.colors.keys())]

        self.screen = ResizingCanvas(self, bg='white')
        self.statusbar = Label(self, text="  No data", bd=3, relief=SUNKEN, anchor=W)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.screen.pack(fill="both", expand=True)
        self.screen.bind("<MouseWheel>", self.mouse_wheel)
        self.screen.bind("<Button-1>", self.mouse_B1)
        self.screen.bind("<B1-Motion>", self.mouse_B1motion)

       
        self.load_ini()
        self.create_menu()

    def create_menu(self):
        self.mainmenu = Menu(self, bd=3)
        for key in self.menu_:
            App.menuitem[key] = Menu(self.mainmenu, tearoff=0, bd=1)
            if key!=M_PUT:
                for tag in self.menu_[key]:
                    App.menuitem[key].add_command(label=tag, command=lambda x=tag: self.callback(x)) #https://webdevblog.ru/kak-ispolzovat-v-python-lyambda-funkcii/ - почему lambda надо писать так
            else:
                self.create_menu_tvel()
            self.mainmenu.add_cascade(label=key, menu=App.menuitem[key])
        self.config(menu=self.mainmenu)

    def create_menu_tvel(self):
       for tag in self.menu_[M_PUT]:
            App.menuitem[M_PUT].add_command(label=tag) 
    
    def destroy_menu(self):
        self.mainmenu.destroy()
        self.menuitem={}
            
    def update(self):
        titlename = PROGRAM_NAME + " - " + self.filename
        self.title(titlename)
        status = "  No data"
        if (self.arrange):
            status = "   Количество элементов всего: {NUM}".format(NUM = len(self.arrange.get_items()))
            for i in self.arrange.get_tvel_types():
                num = self.arrange.get_quantity(i)
                if num != 0:
                    status += "   "+ i +": "+ str(num) + " Макс значение = " + str(self.arrange.get_max(i))
        self.statusbar['text'] = status
        
    def load_ini(self):
        #global COLORS, TVEL
        try:
            with open(INI_FILE,'r') as f:
                self.last_dir = f.readline().rstrip()
                self.colors = json.loads(f.readline())
                font = f.readline().rstrip()
                if font in self.font_list:
                    self.font = font 
                self.menu_[M_PUT] = [*list(self.colors.keys())]
        except:
            print("Ошибка чтения ini файла")
        
    def save_ini(self):
        try:
            with open(INI_FILE,'w') as f:
                f.write("{}\n".format(self.last_dir))
                f.write("{}\n".format(json.dumps(self.colors)))
                f.write("{}".format(self.font))
        except:
            pass
         
    def mouse_wheel(self, event):
        if self.arrange != None:
            self.scale *= (1+event.delta/120*0.03)
            self.draw_arrange()
    
    def mouse_B1motion(self, event):
        if self.arrange != None:
            self.screen.set_center(event.x - self.mouse_xy[0], -(event.y - self.mouse_xy[1]))
            self.draw_arrange()

    def mouse_B1(self, event):
        self.mouse_xy = (event.x, event.y)

    def circle(self, x , y , radius, width=1, outline='black', dash = None , text = None):
        scale=self.scale
        x0, y0 = self.screen.get_center()
        self.screen.create_oval( (x0 + x * scale) - radius * scale,
                                (y0 - y * scale) - radius * scale,
                                (x0 + x * scale) + radius * scale,
                                (y0 - y * scale) + radius * scale,
                                width= width, outline= outline, dash = dash)
        self.screen.create_text((x0 + x * scale) ,
                                (y0 - y * scale) , text= text , font = (self.font, int(radius * scale * 0.7 * self.font_size))) #"Impact" "Lucida Console" "Times New Roman"

    def draw_arrange(self):
        if (self.arrange != None):
            scale = self.scale
            self.screen.delete("all")            #очистить экран
            x0, y0 = self.screen.get_center()
            self.screen.create_line(x0, y0, x0 + 2*scale, y0 , arrow='last', arrowshape=(scale/2,scale/2*1/0.8, scale/2*0.2/0.8))  # arrowshape see https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
            self.screen.create_line(x0, y0, x0 , y0 - 2*scale , arrow='last', arrowshape=(scale/2,scale/2*1/0.8, scale/2*0.2/0.8))
            
            for item in self.arrange.get_items():
                x, y = self.arrange.get_coord(item)
                a = self.colors[self.arrange.get_type(item)]
                self.circle(x, y, self.arrange.r_tvel, width=self.boldline, outline = self.colors[self.arrange.get_type(item)], text = str(int(self.arrange.get_value(item))))
  
    def get_scale(self):
        if (self.arrange!= None):
            max_radius = max(*[radius(*self.arrange.get_coord(item)) for item in self.arrange.get_items()])
            self.scale = min(self.screen.width, self.screen.height) / (2*max_radius + self.arrange.step)

    def draw_beam(self):
        def ok(object):
            angle = object.get_value()[0]
            x0, y0 = self.screen.get_center()
            scale = self.scale
            self.screen.create_line(x0, y0, x0 * (1 + math.cos(angle/180*math.pi)), y0 *(1 - math.sin(angle/180*math.pi)) , dash = int(scale))
            object.destroy()
        if self.arrange:
            dlg = ServiceDialog(self, "Введите угол наклона луча", title = M_BEAM, geometry = '250x120' + self.start_position_askdialog, func = ok)
   
    def draw_circle(self):
        def ok(object):
            tmp = object.get_value()[0]
            if (tmp>0.0):
                object.destroy()
                self.circle(0, 0, tmp, width=2, outline='black', dash = int(self.scale))
            else:
                messagebox.showerror(
                    "Ошибка ввода данных!",
                    "Требуется положительное значение!")
        if self.arrange:
            dlg = ServiceDialog(self, "Введите радиус окружности", title = M_CIRCLE, geometry = '250x120' + self.start_position_askdialog, func = ok)

    def change_scale(self):
        def ok(object):
            tmp = object.get_value()[0]
            if (tmp>0.0):
                self.scale *= tmp
                object.destroy()
                self.draw_arrange()
            else:
                messagebox.showerror(
                    "Ошибка ввода данных!",
                    "Требуется положительное значение!")
        if self.arrange:
            dlg = ServiceDialog(self, "Введите изменение масштаба", title = M_SCALE, geometry = '250x120' + self.start_position_askdialog, func = ok)

    def reset(self):
        if self.arrange:
            self.arrange.rotation = 0
            self.arrange.position = [0, 0]
            self.screen.set_center()
            self.get_scale()
            self.draw_arrange()
    
    def set_boldline(self):
        def ok(object):
            tmp = int(object.get_value()[0])
            if (tmp>0):
                self.boldline = tmp
                object.destroy()
                self.draw_arrange()
            else:
                messagebox.showerror(
                    "Ошибка ввода данных!",
                    "Требуется положительное целое значение!")
        if self.arrange:
            dlg = ServiceDialog(self, "Введите толщину линии", title = M_BOLDLINE, geometry = '250x120' + self.start_position_askdialog, func = ok)

    def set_radius(self):
        def ok(object):
            tmp = object.get_value()[0]
            if (tmp>0):
                self.arrange.r_tvel = tmp
                object.destroy()
                self.draw_arrange()
            else:
                messagebox.showerror(
                    "Ошибка ввода данных!",
                    "Требуется положительное значение!")
        if self.arrange:
            dlg = ServiceDialog(self, "Введите радиус элемента", title = M_RADIUS, geometry = '250x120' + self.start_position_askdialog, func = ok)
    
    def set_font_size(self):
        def ok(object):
            tmp = object.get_value()[0]
            if (tmp>0):
                self.font_size = tmp
                object.destroy()
                self.draw_arrange()
            else:
                messagebox.showerror(
                    "Ошибка ввода данных!",
                    "Требуется положительное значение!")
        if self.arrange:
            dlg = ServiceDialog(self, "Введите мультипликатор размера шрифта", title = M_FONTSIZE, geometry = '250x120' + self.start_position_askdialog, func = ok)

    def set_font(self):
        def get_choice(event):
            self.font = combo_choice.get()
            self.draw_arrange()
        
        def close(*args):
            dialog.destroy()
            #self.draw_arrange()
            
        dialog = Toplevel(self, bd = 3 ) 
        dialog.geometry('280x100'+self.start_position_askdialog)
        dialog.title("Выбрать шрифт")
        dialog.focus_set()
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.resizable(width = False, height= False)
        Button(dialog, text = "Ок", width= 10, command = close).place(relx=0.35, rely=0.65)        # https://question-it.com/questions/2758962/kak-sdelat-dialog-shrifta-v-tkinter
        combo_choice = Combobox(dialog, values = self.font_list, state = 'readonly')
        combo_choice.current(self.font_list.index(self.font))
        combo_choice.place(relx=0.23, rely=0.23)
        combo_choice.bind("<<ComboboxSelected>>", get_choice)
        dialog.bind("<Escape>", close)        

    def choose_colors(self):
        def get_choice(event):
            tvel_type = combo_choice.get()
            color_tvel.config(bg=self.colors[tvel_type])
            
        def change_color():
            tvel_type = combo_choice.get()
            (rgb, hx) = colorchooser.askcolor(title = "Выберите цвет")
            # print(rgb) 
            if (rgb!= None):
                self.colors[tvel_type] = RGB(*rgb)
            color_tvel.config(bg=self.colors[tvel_type])
            self.draw_arrange()
        
        def close(*args):
            dialog.destroy()
            #self.draw_arrange()
            
        dialog = Toplevel(self, bd = 3 ) 
        dialog.geometry('280x100'+self.start_position_askdialog)
        dialog.title("Выбрать цвета")
        dialog.focus_set()
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.resizable(width = False, height= False)
        list_colors=list(self.colors.keys())
        color_tvel=Button(dialog, width = 1, height= 1, bg= self.colors[list_colors[0]], command = change_color)
        color_tvel.place(relx=0.8, rely=0.23)
        Button(dialog, text = "Ок", width= 10, command = close).place(relx=0.35, rely=0.65)
        combo_choice = Combobox(dialog, values=list_colors, state = 'readonly')
        combo_choice.current(0)
        combo_choice.place(relx=0.23, rely=0.23)
        combo_choice.bind("<<ComboboxSelected>>", get_choice)
        dialog.bind("<Escape>", close)        
       
    def show_version(self):
        messagebox.showinfo(title = PROGRAM_NAME, message = VERSION_INFO)       
    
    def show_about(self):
        messagebox.showinfo(title = PROGRAM_NAME, message = __doc__)       

    def open_file(self):
        temp_filename =  filedialog.askopenfilename(initialdir = self.last_dir, title = "Выберите файл",filetypes = (("*.{}".format(F_EXT),"*.{}".format(F_EXT)),("all files","*.*")))
        tmp = Arrange.open(temp_filename) 
        if tmp:
            self.arrange = tmp
            for key in self.arrange.get_tvel_types():
                if key not in self.colors:
                    self.colors[key]=rand_color()
            
            for key in list(self.colors.keys()):
                if key not in self.arrange.get_tvel_types():
                    self.colors.pop(key)
            # перерисовываем меню
            self.menu_[M_PUT] = [i for i in self.colors]
            self.destroy_menu()
            self.create_menu()
            self.get_scale()
            self.draw_arrange()
            self.filename = temp_filename
            self.last_dir = Path(self.filename).parent  #https://python-scripts.com/pathlib

    def quit(self):
        answer = True
        if answer:
            self.save_ini()
            self.destroy()

    def callback(self, tag):
        if tag == M_OPEN:
            self.open_file()
        if tag == M_QUIT:
            return self.quit() # return, чтобы после уничтожения окна не вызывался self.update
        if tag == M_SCALE:
            self.change_scale()
        if tag == M_RESET:
            self.reset()
        if tag == M_BEAM:
            self.draw_beam()
        if tag == M_CIRCLE:
            self.draw_circle()
        if tag == M_COLORS:
            self.choose_colors()
        if tag == M_BOLDLINE:
            self.set_boldline()
        if tag == M_FONT:
            self.set_font()
        if tag == M_FONTSIZE:
            self.set_font_size()
        if tag == M_RADIUS:
            self.set_radius()
        if tag == M_VERSION:
            self.show_version()
        if tag == M_ABOUT:
            self.show_about()
        self.update()
    
if (__name__ == "__main__"):
    app=App()
    app.protocol('WM_DELETE_WINDOW', app.quit)
    app.mainloop()

