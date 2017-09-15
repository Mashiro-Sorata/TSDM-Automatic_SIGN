import PIL
from PIL import ImageTk
import wx, wx.adv
from main_service import *
import threading
import win32api

def Tkimg(path, width, height):
    img = PIL.Image.open(path).resize((width, height), PIL.Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def ask_quit():
    if App.location == 'author':
        if tkinter.messagebox.askyesno("提示","是否隐藏到系统托盘自动签到打工？"):
            App.root.withdraw()
        else:
            wx.Exit()
            app.root.destroy()
    elif tkinter.messagebox.askyesno("提示","您还没有成功登录！\n是否直接退出？"):
        app.root.destroy()
    if os.path.exists(App._data_path+'code.png'):
        os.remove(App._data_path+'code.png')
    
def get_user_imgpath():
    if os.path.exists(App._data_path+'author.jpg'):
        return App._data_path+'author.jpg'
    return App._data_path+'default.ico'


class Author_Frame:
    def __init__(self, root, tkimg):
        self.root = root
        
        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=W, padx=10, pady=5)

        self.author = Label(self.frame, image=tkimg)
        self.author.grid(row=0, column=0, sticky=W)
        
        self.account_info = Label(self.frame, textvariable=App.authorinfo_var)
        self.account_info.grid(row=0, column=1, sticky=E, pady=5)

        self.help_button = Button(self.frame, text='帮助文档', command=self.help)
        self.help_button.grid(row=0, column=2, pady=5, sticky=E)

        self.quit = Button(self.frame, text='退出登陆', command=self.delete)
        self.quit.grid(row=1, column=0, pady=5, sticky=W)

        self.auto_sign_cb = Checkbutton(self.frame, text='自动打工', variable=App.mission_var, command=self.mission_click)
        self.auto_sign_cb.grid(row=1, column=1, pady=5)

        self.saylist_button = Button(self.frame, text='签到用语', command=self.input)
        self.saylist_button.grid(row=1, column=2, pady=5, sticky=E)
        
        self.infolist = InfoList(self.frame)
        self.infolist.insert('Initial-message：欢迎您！使者%s！程序将自动进行签到打工，取消请按终止任务按钮；开始后点击隐藏到系统托盘可在后台自动签到打工！' % App.webs.userdata['username'])

        App.webs.get_pgv_cookie()
        App.webs.save_cookie()

        if not hasattr(App, 'sysbar'):
            App.sysbar = SysTrayIcon()
        
    def mission_click(self):
        App.webs.userdata['mission'] = App.mission_var.get()
        App.webs.save_userdata()
        if hasattr(App,'main_job'):
            App.sysbar.stop()
            App.sysbar.start()
    
    def help(self):
        App.author.infolist.delete()
        App.author.infolist.insert('-----------------------------帮助-----------------------------')
        App.author.infolist.insert('-->在程序启动时自动完成签到，勾选自动打工可自动定时执行打工任务')
        App.author.infolist.insert('-->在签到用语按钮打开的文档中可自定义输入签到用语')
        App.author.infolist.insert('     注：每行算一句签到用语，签到时从中随机选取一句进行，每行的内容不少于6个字母或3个中文字！')
        App.author.infolist.insert('-->退出登录后需要重新输入验证码进行登录，退出前请三思！')
        App.author.infolist.insert('-->在退出任务后用户的签到用语不会删除，但是会删除本账号的任务记录(程序根目录下_data文件夹内的logs.txt)')
        App.author.infolist.insert('-->程序可以隐藏到系统托盘在后台自动任务')
        App.author.infolist.insert('-->程序作者：Mashiro_Sorata--最后更新日期：2017-9-12')
        
    def input(self):
        win32api.ShellExecute(0, 'open', 'notepad.exe', App._data_path + 'saylist.txt','',1)
        
    
    def delete(self):
        if tkinter.messagebox.askyesno("警告！","退出登录将退出程序，再次登录需要验证码登录！\n是否继续？"):
            self.frame.destroy()
            App.author = None
            App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
            App.location = 'login'
            os.remove(App._data_path+'cookie.txt')
            if os.path.exists(App._data_path+'author.jpg'):
                os.remove(App._data_path+'author.jpg')
            if os.path.exists(App._data_path+'logs.txt'):
                os.remove(App._data_path+'logs.txt')
            if os.path.exists(App._data_path+'logs.pkl'):
                os.remove(App._data_path+'logs.pkl')
            App.webs.init_cookie()
            App.webs.new_opener()
            wx.Exit()
            #还需要删除和当前账号有关的所有信息
        


class Login_Frame:
    def __init__(self, root, username='', passwd=''):
        self.root = root
        
        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=W, padx=10, pady=5)

        self.account_label = Label(self.frame, text='账号：')
        self.account_label.grid(row=0, column=0, pady=5)

        self.password_label = Label(self.frame, text='密码：')
        self.password_label.grid(row=1, column=0, pady=5)

        self.account_var = StringVar()
        self.account_var.set(username)
        self.account_entry = Entry(self.frame, width=30, textvariable=self.account_var)
        self.account_entry.grid(row=0, column=1, columnspan=2, sticky=W, pady=5)

        self.password_var = StringVar()
        self.password_var.set(passwd)
        self.password_entry = Entry(self.frame, width=30, show='*', textvariable=self.password_var)
        self.password_entry.grid(row=1, column=1, columnspan=2, sticky=W, pady=5)
        
        self.login_button = Button(self.frame, text='登录', command=self.login_thread, width=10)
        self.login_button.grid(row=2, column=2, columnspan=2, sticky=E, pady =5)

        self.auto_login_cb = Checkbutton(self.frame, text='自动登录', variable=App.autologin_var, command=self.save_autologin_var)
        self.auto_login_cb.grid(row=2, column=0, sticky=W, pady=5)

        self.showpasswd_var = BooleanVar()
        self.showpasswd_var.set(False)
        self.showpasswd_cb = Checkbutton(self.frame, text='显示密码', variable=self.showpasswd_var, command=self.showpasswd)
        self.showpasswd_cb.grid(row=2, column=1, sticky=W, pady=5)

    def save_autologin_var(self):
        App.webs.userdata['autologin'] = App.autologin_var.get()
        App.webs.save_userdata()

    def showpasswd(self):
        if self.showpasswd_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')

    def login_thread(self):
        self.login_button['state'] = DISABLED
        self.auto_login_cb['state'] = DISABLED
        t = threading.Thread(target=self.push_account_info)
        t.start()

    def push_account_info(self):
        #禁用其他控件
        if App.webs.userdata.get('username') and App.webs.autoLogin():
            #如果成功登录则显示author界面，否则正常登录
            self.frame.destroy()
            App.authorinfo_var.set('欢迎您！\n使者' + App.webs.userdata['username'] + '！')
            App.author_img = Tkimg(get_user_imgpath(), 50, 50)
            App.author = Author_Frame(App.root, App.author_img)
            App.location = 'author'
            App.root.after(5000, App.sysbar.start)
        else:
            self.count = 0
            self.account = self.account_entry.get()
            self.passwd = self.password_entry.get()
            if self.account and self.passwd:
                self.show_other()
            else:
                tkinter.messagebox.showwarning('警告','账号名或者密码不能为空！')
                self.login_button['state'] = NORMAL
                self.auto_login_cb['state'] = NORMAL

    def show_other(self):
        App.webs.get_enter_url(self.account, self.passwd)
        while True:
            if os.path.exists(App._data_path+'code.png'):
                self.frame.destroy()
                App.verify = Verify_Frame(App.root, App._data_path+'code.png')
                App.location = 'verify'
                os.remove(App._data_path+'code.png')
                break
            
class Verify_Frame:
    def __init__(self, root, code_path):
        self.root = root
        
        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=W, padx=10, pady=5)

        self.verify_label = Label(self.frame, text='验证码：')
        self.verify_label.grid(row=0, column=0, pady=5)

        self.tkimg = Tkimg(code_path, 160, 70)
        self.verify_img = Label(self.frame, image=self.tkimg)
        self.verify_img.grid(row=0, column=1, sticky=W, pady=5)

        self.verify_entry = Entry(self.frame,width=8)
        self.verify_entry.grid(row=0, column=2, sticky=E, padx=5, pady =5)

        self.push_button = Button(self.frame, text='确定', command=self.verify_thread, width=5)
        self.push_button.grid(row=1, column=0, columnspan=3, pady=5)

    def verify_thread(self):
        self.push_button['state'] = DISABLED
        t = threading.Thread(target=self.push_code)
        t.start()

    def push_code(self):
        self.count = 0
        code = self.verify_entry.get().strip()
        if code:
            App.webs.get_login_data(code)
            response = App.webs.get_response(App.webs.urls['enter_url'], App.webs.post_data)
            html = gzip_decode(response)
            if App.webs.is_login(html):
                App.webs.save_cookie()
                App.webs.save_userdata()
                self.show_other()
            else:
                error_freeze = re.search(r'密码错误次数过多', html)
                error_verify = re.search(r'验证码错误', html)
                chance = re.search(r'登录失败，您还可以尝试 (.+?) 次', html)
                if error_freeze:
                    tkinter.messagebox.showerror('错误提示','密码错误次数过多，请20分钟后重试！')
                    App.root.destroy()
                elif error_verify:
                    tkinter.messagebox.showerror('错误提示','验证码错误，请重新登录！')
                    self.frame.destroy()
                    App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
                    App.location = 'login'
                elif chance:
                    prompt = chance.group(0) + '！\n是否重试(取消直接退出程序)？'
                    if tkinter.messagebox.askretrycancel('登录提示',prompt):
                        self.frame.destroy()
                        App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
                        App.location = 'login'
                    else:
                        App.root.destroy()
                else:
                    if tkinter.messagebox.askretrycancel('登录提示','登录失败！是否重试(取消直接退出程序)？'):
                        self.frame.destroy()
                        App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
                        App.location = 'login'
                    else:
                        App.root.destroy()
        else:
            tkinter.messagebox.showwarning('警告','验证码不能为空！')
            self.push_button['state'] = NORMAL
        

    def show_other(self):
        if (not os.path.exists(App._data_path+'author.jpg')) and (not self.count):
            if App.webs.autoLogin():
                App.webs.get_author_image()
            else:
                if tkinter.messagebox.askretrycancel('登录提示','登录失败！是否重试(取消直接退出程序)？'):
                    self.frame.destroy()
                    App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
                    App.location = 'login'
                else:
                    App.root.destroy()
        while True:
            if os.path.exists(App._data_path+'author.jpg'):
                #如果成功登录则显示author界面，负责返回登录界面
                self.frame.destroy()
                App.authorinfo_var.set('欢迎您！\n使者' + App.webs.userdata['username'] + '！')
                App.author_img = Tkimg(App._data_path+'author.jpg', 50, 50)
                App.author = Author_Frame(App.root, App.author_img)
                App.location = 'author'
                App.root.after(5000, App.sysbar.start)
                break
            elif self.count > 5:
                self.frame.destroy()
                App.authorinfo_var.set('欢迎您！\n使者' + App.webs.userdata['username'] + '！')
                App.author_img = Tkimg(get_user_imgpath(), 50, 50)
                App.author = Author_Frame(App.root, App.author_img)
                App.location = 'author'
                App.root.after(5000, App.sysbar.start)
                break
            self.count += 1
                
        


class InfoList:
    def __init__(self, root):
        self.root = root
        
        self.frame = Frame(self.root)
        self.frame.grid(row=3, column=0, columnspan=3, pady=5)

        self.ststray_button = Button(self.frame, text='隐藏到系统托盘', command=self.mainhide)
        self.ststray_button.grid(row=0, column=0, pady=5, sticky=W)

        self.start_pause_button = Button(self.frame, textvariable=App.start_status_var, command=self.start_pause)
        self.start_pause_button.grid(row=0, column=1, pady=5)
        
        self.clear_button = Button(self.frame, text='清除消息列表', command=self.delete)
        self.clear_button.grid(row=0, column=2, pady=5, sticky=E)

        self.childframe = Frame(self.frame)
        self.childframe.grid(row=1, column=0, columnspan=3, pady=5)

        self.Yscrollbar = Scrollbar(self.childframe)
        self.Yscrollbar.pack(side=RIGHT, fill=Y)

        self.Xscrollbar = Scrollbar(self.childframe, orient = HORIZONTAL)
        self.Xscrollbar.pack(side=BOTTOM, fill=X)
        
        
        self.infolist = Listbox(self.childframe, width=45, yscrollcommand=self.Yscrollbar.set, xscrollcommand=self.Xscrollbar.set)
        self.infolist.pack(side=LEFT, fill=BOTH)

        self.Yscrollbar.config(command=self.infolist.yview)
        self.Xscrollbar.config(command=self.infolist.xview)

    def start_pause(self):
        if App.start_status_var.get() == '开始任务':
            App.author.infolist.insert('--------------------------任务开始！--------------------------')
            App.start_status_var.set('终止任务')
            App.sysbar.start()
        else:
            App.author.infolist.insert('--------------------------任务停止！--------------------------')
            App.start_status_var.set('开始任务')
            App.sysbar.stop()
        mission_flag=App.log.mission_avaliable()
        if mission_flag != True:
            App.dt.set(mission_flag)
        
    def insert(self, value ,pos=END):
        self.infolist.insert(pos, value)

    def delete(self, from_=0, to=END):
        self.infolist.delete(from_, to)

    def mainhide(self):
        App.root.withdraw()

#--------------------------------APP-------------------------------
class App:
    root = Tk()
    _code = 'utf-8'
    _data_path = os.curdir + '\\_data\\'
    sysapp = wx.App()
    log = Logs(_data_path)
    webs = WebService(_data_path)
    autologin_var = BooleanVar()
    mission_var = BooleanVar()
    authorinfo_var = StringVar()
    start_status_var = StringVar()
    location = ''
    author = None
    dt = IntVar()
    thread_status = True
    fail = 0
    
    def __init__(self):
        App.root.iconbitmap(App._data_path+'default.ico')
        App.root.resizable(False, False)
        App.root.title('Auto-Sign')
        App.authorinfo_var.set('')
        App.autologin_var.set(App.webs.userdata['autologin'])
        App.mission_var.set(App.webs.userdata['mission'])
        App.start_status_var.set('终止任务')
        App.dt.set(8)
        self.init_show()
        


    def init_show(self):
        if App.autologin_var.get():
            if os.path.exists(App._data_path+'cookie.txt') and App.webs.autoLogin():
                App.author_img = Tkimg(get_user_imgpath(), 50, 50)
                App.authorinfo_var.set('欢迎您！\n使者' + App.webs.userdata['username'] + '！')
                App.author = Author_Frame(App.root, App.author_img)
                App.location = 'author'
                App.root.after(5000, App.sysbar.start)
            elif App.webs.userdata.get('username'):
                App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
                App.location = 'login'
            else:
                App.login = Login_Frame(App.root)
                App.location = 'login'
        else:
            App.login = Login_Frame(App.root, App.webs.userdata['username'], App.webs.userdata['password'])
            App.location = 'login'
            
        
    def mainloop(self):
        App.root.mainloop()
            

    
        
#-------------------------------------------------------------------


class SysTrayIcon(wx.adv.TaskBarIcon):
    ID_ABOUT = wx.NewId()
    ID_EXIT = wx.NewId()
    ID_SHOW_APP = wx.NewId()
    TITLE = 'TSDM自动签到'

    def __init__(self):
        wx.adv.TaskBarIcon.__init__(self)
        self.SetIcon(wx.Icon(get_user_imgpath()), self.TITLE) # 设置图标和标题
        self.Bind(wx.EVT_MENU, self.onAbout, id=self.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onShow, id=self.ID_SHOW_APP)

    def start(self):
        if App.thread_status:
            t = threading.Thread(target=self.main_mission)
            t.start()


    def main_mission(self):
        App.thread_status = False
        _mission = True
        if App.log.sign_avaliable():
            App.author.infolist.insert('-->正在进行签到......')
            App.webs.get_sign_data()
            content = App.webs.do_sign()
            if content:
                App.author.infolist.insert('-->'+content)
                App.log.log2file(content)
                App.log.update_log('sign')
            else:
                App.author.infolist.insert('<Error-00>:签到失败！请保证saylist.txt里的每行的内容不少于6个字母或3个中文字！')
                _mission = False
            time.sleep(5)

        if App.mission_var.get():
            if _mission and App.log.mission_avaliable() == True:
                App.author.infolist.insert('-->登入任务界面中......')
                if not App.webs.pre_mission():
                    App.author.infolist.insert('<Error-01>:登录状态错误，打工任务失败！(可尝试重新登陆)')
                else:
                    flag = App.webs.do_mission()
                    if flag == 'fail':
                        if App.fail < 5:
                            App.dt.set(10)
                            App.fail += 1
                            App.author.infolist.insert('<Error-02>:打工失败，程序将尝试重新打工...')
                        else:
                            App.log.log2file('打工失败次数过多，程序自动退出！')
                            App.root.destroy()
                            App.sysapp.Destroy()
                            wx.Exit()
                    elif not flag:
                        if App.webs.mission_money:
                            App.author.infolist.insert('-->' + App.webs.mission_money.group(1))
                            App.log.log2file('打工成功！'+App.webs.mission_money.group(1))
                            App.log.update_log('mission')
                            App.dt.set(6*60*60)
                        else:
                            App.author.infolist.insert('--><Error-03>:打工页面返回值异常，程序将尝试重新打工...')
                            App.dt.set(10)
                    else:
                        App.author.infolist.insert('-->程序将在%s后自动打工...' % flag)
                        App.log.log2file('-->程序将在%s后自动打工...' % flag)
                        dtliststr = re.findall(r'\d+',flag)
                        dtlist = []
                        for each in dtliststr:
                            dtlist.append(int(each))
                        App.log.get_missionedtime(dtlist)
                        App.dt.set(int(dtlist[0])*60*60 + int(dtlist[1])*60 + int(dtlist[2]))
            else:
                mission_flag=App.log.mission_avaliable()
                if mission_flag != True:
                    App.dt.set(mission_flag)
            App.author.infolist.insert('-->程序将在 '+(App.log.now()+timedelta(seconds=App.dt.get())).ctime()+' 自动完成任务，可将程序隐藏至任务栏后台运行哦！')
        elif _mission:
            App.dt.set(1200)
        
        App.thread_status = True
        App.main_job = App.root.after(App.dt.get()*1000, self.start)

    def stop(self):
        App.root.after_cancel(App.main_job)
        

    def onAbout(self, event):
        wx.MessageBox('程序作者：Mashiro_Sorata\n最后更新日期：2017-9-12', "关于")

    def onExit(self, event):
        App.root.destroy()
        App.sysapp.Destroy()
        wx.Exit()


    def onShow(self, event):
        App.root.deiconify()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        for each in self.getMenus():
            menu.Append(each[1], each[0])
        return menu

    def getMenus(self):
        return [('进入程序', self.ID_SHOW_APP),
                ('关于', self.ID_ABOUT),
                ('退出程序',self.ID_EXIT)]





app = App()

app.root.protocol("WM_DELETE_WINDOW",ask_quit)

app.mainloop()


