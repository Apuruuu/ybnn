import RPi.GPIO as GPIO
import tkinter as tk
import tkinter.font as tkFont

class GUI():
    def __init__(self, pipe_sensor, pipe_main):
        self.root = tk.Tk()
        self.get_value()
        self.pipe_sensor = pipe_sensor
        self.pipe_main = pipe_main

        # 有重名冲突
        # self.devices = [['light','off','0','','',''],
        #                 ['pump_air','off','0','','',''],
        #                 ['pump_1','off','0','','',''],
        #                 ['pump2','off','0','','',''],
        #                 ['magnetic_stitter','off','0','','',''],
        # ]

        #setting title
        self.root.title("undefined")
        #setting window size
        width=720
        height=500
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.configure(bg='#FFFFFF')
        # self.root.resizable(width=False, height=False)

        # Font-size = 18
        self.ft18 = tkFont.Font(size=18)
        # Font-size = 14
        self.ft14 = tkFont.Font(size=14)
        # Font-size = 10
        self.ft10 = tkFont.Font(size=10)

        self.start_GUI()
        self.refresh_data()
        
        self.root.mainloop()

    def start_GUI(self):
        self.background_canvas()
        self.top_bar_button()
        self.top_bar_text()
        self.equipment_canvas()
        self.equipment_center_value_Text()
        self.liquid_level_mark()
        self.devices_info_and_button()

    def update_GUI(self):
        self.top_bar_value()
        self.equipment_value()
        self.equipment_center_value_Value()
        self.devices_status()
        self.devices()

    def refresh_data(self):
        self.pipe_sensor.send('SHOW_ME_DATA')
        data = self.pipe_main.recv()
        print(data)
        self.temperature = data['temperature']
        self.humidity = data['humidity']
        self.water_temperature = data['water_temperature']
        self.PH_value = data['PH']
        self.lumen = data['lumen']
        self.local_time = data['time']
        self.turbidity = data['turbidity']
        self.height_value = data['height']

        # math
        # 计算液面高度
        if self.height_value == 'N/A':
            self.liquid_level = 0
        else:
            self.liquid_level = self.sensor_height - self.height_value

        self.volume = self.liquid_level * self.cistern_length * self.cistern_width / 1000
        self.volume_text = '%.1f'%self.volume

        if self.lumen == 'N/A':
            self.turbidity_by_lumen = 'N/A'
        else:
            # 流明》浊度计算公式
            self.turbidity_by_lumen = self.lumen

        self.update_GUI()
        self.root.after(1000, self.refresh_data)   # 这里的10000单位为毫秒

    def get_value(self):
########################## setting ###########################
        self.high_value = 0.9
        self.low_value = 0.6
        self.sensor_height = 200
        self.cistern_length = 300
        self.cistern_width = 200
        # 容器参数
        self.cistern_x = 170
        self.cistern_y = 70
        self.cistern_w = 200
        self.cistern_h = 100
        
########################## setting ###########################


    def background_canvas(self):
        # background canvas
        canvas_bg=tk.Canvas(self.root, width=720, height=500, bg='#FFFFFF', bd=0)
        canvas_bg.place(x=0,y=0,width=720, height=500)
        # line1 w-e
        canvas_bg.create_line(0,70,720,70 ,width=2, fill='#000000')

        for i in range(8):
            x = i*100
            canvas_bg.create_line(x,500, x,480, width=2, fill='#000000')
            for j in range(1,10):
                x1 = x + j*10
                canvas_bg.create_line(x1,500, x1,490, width=2, fill='#000000')

        for i in range(5):
            y = i*100
            canvas_bg.create_line(700,y,720,y, width=2, fill='#000000')
            for j in range(1,10):
                y1 = y + j*10
                canvas_bg.create_line(710,y1,720,y1, width=2, fill='#000000')
        
    def top_bar_button(self):
        # camera button
        camera_button=tk.Button(self.root, text='Camera', justify='center', font=self.ft10, bg='#EFEFEF', fg='#000000')
        camera_button.place(x=10,y=10,width=50,height=50)
        camera_button["command"] = self.open_camera

        # graph button
        graph_button=tk.Button(self.root, text='Graph', justify='center', font=self.ft10, bg='#EFEFEF', fg='#000000')
        graph_button.place(x=70,y=10,width=50,height=50)
        graph_button["command"] = self.open_graph

        # maintenance button
        maintenance_button=tk.Button(self.root, text='Maint.', justify='center', font=self.ft10, bg='#EFEFEF', fg='#000000')
        maintenance_button.place(x=130,y=10,width=50,height=50)
        maintenance_button["command"] = self.open_maintenance
    
    def top_bar_text(self):
        # temperature model    
        Temperature_text=tk.Label(self.root, text="気温[C]:", anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        Temperature_text.place(x=180,y=10,width=100,height=27)
        
        # humidity model    
        humidity_text=tk.Label(self.root, text="湿度[%]:", anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        humidity_text.place(x=180,y=37,width=100,height=27)
        
        # local time model    
        local_time_text=tk.Label(self.root, text="時間:", anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        local_time_text.place(x=350,y=10,width=72,height=27)
        message1_text=tk.Label(self.root, text="警告：システム再起動後に", 
                                anchor='w', font=self.ft10, bg='#FFFFFF', fg='#FF0000')
        message1_text.place(x=350,y=37,width=200,height=15)
        message1_text=tk.Label(self.root, text="時刻合わせを忘れないで下さい！", 
                                anchor='w', font=self.ft10, bg='#FFFFFF', fg='#FF0000')
        message1_text.place(x=350,y=52,width=200,height=15)

    def top_bar_value(self):
        Temperature_value=tk.Label(self.root, text=str(self.temperature)[:5], anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        Temperature_value.place(x=280,y=10,width=70,height=27)

        humidity_value=tk.Label(self.root, text=str(self.humidity)[:5], anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        humidity_value.place(x=280,y=37,width=70,height=27)

        local_time_value=tk.Label(self.root, text=self.local_time, anchor='w', font=self.ft18, bg='#FFFFFF', fg='#000000')
        local_time_value.place(x=410,y=10,width=250,height=27)

    def equipment_canvas(self):
        # Equipment canvas
        self.canvas_equipment=tk.Canvas(self.root, bg='#FFFFFF')
        self.canvas_equipment.place(x=0,y=71,width=450, height=210)

        # # 绘制画布刻度线（仅用于设计布局时）
        # for i in range(8):
        #     x = i*100
        #     self.canvas_equipment.create_line(x,190, x,210, width=1, fill='#000000')
        #     for j in range(1,10):
        #         x1 = x + j*10
        #         self.canvas_equipment.create_line(x1,200, x1,210, width=1, fill='#000000')

        # for i in range(3):
        #     y = i*100
        #     self.canvas_equipment.create_line(430,y,450,y, width=1, fill='#000000')
        #     for j in range(1,10):
        #         y1 = y + j*10
        #         self.canvas_equipment.create_line(440,y1,450,y1, width=1, fill='#000000')



        # 绘制容器
        self.canvas_equipment.create_line(self.cistern_x,self.cistern_y, 
                                    self.cistern_x,self.cistern_y+self.cistern_h, 
                                    self.cistern_x+self.cistern_w,self.cistern_y+self.cistern_h, 
                                    self.cistern_x+self.cistern_w,self.cistern_y, 
                                    width=6, fill='#000000')

    def equipment_value(self):
        # 绘制水
        water_h = self.cistern_y +self.cistern_h - self.liquid_level
        self.canvas_equipment.create_polygon(self.cistern_x+3,water_h,
                                        self.cistern_x+self.cistern_w-3,water_h,
                                        self.cistern_x+self.cistern_w-3,self.cistern_y+self.cistern_h-3,
                                        self.cistern_x+3,self.cistern_y+self.cistern_h-3,
                                        fill='#99FFFF')
        # 绘制容器刻度线
        for i in range(10):
            if i%2 != 0:
                w = self.cistern_w/20
            else:
                w = self.cistern_w/10

            y = self.cistern_y + self.cistern_h*i/10
            self.canvas_equipment.create_line(self.cistern_x,y, self.cistern_x+w,y, width=2, fill='#000000')

    def equipment_center_value_Text(self):
        # 数值显示（固定文本部分）
        self.value_start_point_Y = 70
        self.value_height = 15
        liquid_level_text=tk.Label(self.canvas_equipment, text="高さ[mm]:", anchor='e', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_text.place(x=230,y=self.value_start_point_Y+0*self.value_height,width=70, height=15)

        liquid_level_text=tk.Label(self.canvas_equipment, text="容積[ml]:", anchor='e', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_text.place(x=230,y=self.value_start_point_Y+1*self.value_height,width=70, height=15)
        
        liquid_level_text=tk.Label(self.canvas_equipment, text="温度[C]:", anchor='e', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_text.place(x=230,y=self.value_start_point_Y+2*self.value_height,width=70, height=15)
        
        liquid_level_text=tk.Label(self.canvas_equipment, text="PH :", anchor='e', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_text.place(x=230,y=self.value_start_point_Y+3*self.value_height,width=70, height=15)
        
        liquid_level_text=tk.Label(self.canvas_equipment, text="濁度[%]:", anchor='e', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_text.place(x=230,y=self.value_start_point_Y+4*self.value_height,width=70, height=15)

    def equipment_center_value_Value(self):
        # 数值显示（数值部分）
        liquid_level_value=tk.Label(self.canvas_equipment, text=self.liquid_level, anchor='w', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_value.place(x=295,y=self.value_start_point_Y+0*self.value_height,width=55, height=15)

        liquid_level_value=tk.Label(self.canvas_equipment, text=self.volume_text, anchor='w', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_value.place(x=295,y=self.value_start_point_Y+1*self.value_height,width=55, height=15)

        liquid_level_value=tk.Label(self.canvas_equipment, text=self.water_temperature, anchor='w', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_value.place(x=295,y=self.value_start_point_Y+2*self.value_height,width=55, height=15)

        liquid_level_value=tk.Label(self.canvas_equipment, text=self.PH_value, anchor='w', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_value.place(x=295,y=self.value_start_point_Y+3*self.value_height,width=55, height=15)

        liquid_level_value=tk.Label(self.canvas_equipment, text=self.turbidity_by_lumen, anchor='w', font=self.ft10, bg='#EEEEEE', fg='#000000')
        liquid_level_value.place(x=295,y=self.value_start_point_Y+4*self.value_height,width=55, height=15)

    def devices_status(self):
        # print devices status
        self.pump_air_status=tk.Label(self.canvas_equipment, text="ON", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        self.pump_air_status.place(x=0,y=85,width=60, height=15)
        self.pump1_status=tk.Label(self.canvas_equipment, text="OFF", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        self.pump1_status.place(x=80,y=85,width=60, height=15)
        self.pump2_status=tk.Label(self.canvas_equipment, text="OFF", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        self.pump2_status.place(x=380,y=85,width=60, height=15)
        self.magnetic_stirrer_status=tk.Label(self.canvas_equipment, text="OFF", anchor='e', font=self.ft10, bg='#FFFFFF', fg='#000000')
        self.magnetic_stirrer_status.place(x=180,y=190,width=60, height=15)
        self.light_status=tk.Label(self.canvas_equipment, text="OFF", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        self.light_status.place(x=240,y=45,width=60, height=15)

    def liquid_level_mark(self):
        # 绘制最高最低水位标
        self.draw_mark(self.cistern_x,self.cistern_y+self.cistern_h*(1-self.high_value),'#FF2222',self.canvas_equipment)
        self.draw_mark(self.cistern_x,self.cistern_y+self.cistern_h*(1-self.low_value),'#22DDDD',self.canvas_equipment)

    def devices(self):
        # draw pump air
        r=16
        air_x = 30
        air_y = 50
        air_color = '#CCCCCC'
        self.draw_pump(air_x,air_y,r,air_color,self.canvas_equipment)
        self.canvas_equipment.create_line(air_x+r,air_y, 
                                    air_x+2*r,air_y, 
                                    air_x+2*r,air_y-1.5*r, 
                                    air_x+12*r,air_y-1.5*r,
                                    air_x+12*r,air_y+6*r,
                                    width=6, fill=air_color)

        # draw pump 1
        pump1_x = 110
        pump1_y = 50
        pump1_color = '#AAAAFF'
        self.draw_pump(pump1_x,pump1_y,r,pump1_color,self.canvas_equipment)
        self.canvas_equipment.create_line(pump1_x+r,pump1_y, 
                                    pump1_x+6*r,pump1_y, 
                                    pump1_x+6*r,pump1_y+1*r, 
                                    width=6, fill=pump1_color)

        # draw pump 2
        pump2_x = 410
        pump2_y = 50
        pump2_color = '#99FF99'
        self.draw_pump(pump2_x,pump2_y,r,pump2_color,self.canvas_equipment)
        self.canvas_equipment.create_line(pump2_x-r,pump2_y, 
                                    pump2_x-3*r,pump2_y, 
                                    pump2_x-3*r,pump2_y+6*r, 
                                    width=6, fill=pump2_color)

        # magnetic stirrer
        magnetic_stirrer_x = 270
        magnetic_stirrer_y = 190
        self.draw_magnetic_stirrer(magnetic_stirrer_x,magnetic_stirrer_y,self.canvas_equipment)

        # light
        light_x = 270
        light_y = 25
        self.draw_light(light_x,light_y,self.canvas_equipment)

    def devices_info_and_button(self):
        pump_air_text=tk.Label(self.canvas_equipment, text="Pump AIR", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_air_text.place(x=0,y=70,width=60, height=15)
        self.pump_air_timer=tk.Entry(self.canvas_equipment, font=self.ft10, fg='#000000', bg='#efefef')
        self.pump_air_timer.place(x=0,y=100,width=40,height=15)
        pump_air_text_s=tk.Label(self.canvas_equipment, text="[s]", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_air_text_s.place(x=40,y=100,width=20, height=15)
        pump_air_ON_button=tk.Button(self.canvas_equipment, text='ON', justify='center', font=self.ft14, bg='#33FF33', fg='#000000')
        pump_air_ON_button.place(x=2,y=120,width=26,height=20)
        pump_air_ON_button["command"] = self.pump_air_on
        pump_air_OFF_button=tk.Button(self.canvas_equipment, text='OFF', justify='center', font=self.ft10, bg='#FF3333', fg='#000000')
        pump_air_OFF_button.place(x=32,y=120,width=26,height=20)
        pump_air_OFF_button["command"] = self.pump_air_off

        pump_1_text=tk.Label(self.canvas_equipment, text="Pump 1", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_1_text.place(x=80,y=70,width=60, height=15)
        self.pump_1_timer=tk.Entry(self.canvas_equipment, font=self.ft10, fg='#000000', bg='#efefef')
        self.pump_1_timer.place(x=80,y=100,width=40,height=15)
        pump_1_text_s=tk.Label(self.canvas_equipment, text="[s]", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_1_text_s.place(x=120,y=100,width=20, height=15)
        pump_1_ON_button=tk.Button(self.canvas_equipment, text='ON', justify='center', font=self.ft14, bg='#33FF33', fg='#000000')
        pump_1_ON_button.place(x=82,y=120,width=26,height=20)
        pump_1_ON_button["command"] = self.pump_1_on
        pump_1_OFF_button=tk.Button(self.canvas_equipment, text='OFF', justify='center', font=self.ft10, bg='#FF3333', fg='#000000')
        pump_1_OFF_button.place(x=112,y=120,width=26,height=20)
        pump_1_OFF_button["command"] = self.pump_1_off

        pump_2_text=tk.Label(self.canvas_equipment, text="Pump 2", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_2_text.place(x=380,y=70,width=60, height=15)
        self.pump_2_timer=tk.Entry(self.canvas_equipment, font=self.ft10, fg='#000000', bg='#efefef')
        self.pump_2_timer.place(x=380,y=100,width=40,height=15)
        pump_2_text_s=tk.Label(self.canvas_equipment, text="[s]", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        pump_2_text_s.place(x=420,y=100,width=20, height=15)
        pump_2_ON_button=tk.Button(self.canvas_equipment, text='ON', justify='center', font=self.ft14, bg='#33FF33', fg='#000000')
        pump_2_ON_button.place(x=382,y=120,width=26,height=20)
        pump_2_ON_button["command"] = self.pump_2_on
        pump_2_OFF_button=tk.Button(self.canvas_equipment, text='OFF', justify='center', font=self.ft10, bg='#FF3333', fg='#000000')
        pump_2_OFF_button.place(x=412,y=120,width=26,height=20)
        pump_2_OFF_button["command"] = self.pump_2_off

        magnetic_stirrer_text=tk.Label(self.canvas_equipment, text="magnetic stirrer", anchor='e', font=self.ft10, bg='#FFFFFF', fg='#000000')
        magnetic_stirrer_text.place(x=120,y=175,width=120, height=15)
        self.magnetic_stirrer_timer=tk.Entry(self.canvas_equipment, font=self.ft10, fg='#000000', bg='#efefef')
        self.magnetic_stirrer_timer.place(x=300,y=185,width=40,height=15)
        magnetic_stirrer_text_s=tk.Label(self.canvas_equipment, text="[s]", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        magnetic_stirrer_text_s.place(x=340,y=185,width=20, height=15)
        magnetic_stirrer_ON_button=tk.Button(self.canvas_equipment, text='ON', justify='center', font=self.ft14, bg='#33FF33', fg='#000000')
        magnetic_stirrer_ON_button.place(x=362,y=180,width=26,height=20)
        magnetic_stirrer_ON_button["command"] = self.magnetic_stirrer_on
        magnetic_stirrer_OFF_button=tk.Button(self.canvas_equipment, text='OFF', justify='center', font=self.ft10, bg='#FF3333', fg='#000000')
        magnetic_stirrer_OFF_button.place(x=392,y=180,width=26,height=20)
        magnetic_stirrer_OFF_button["command"] = self.magnetic_stirrer_off

        light_text=tk.Label(self.canvas_equipment, text="Light:", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        light_text.place(x=245,y=5,width=50, height=15)
        self.light_timer=tk.Entry(self.canvas_equipment, font=self.ft10, fg='#000000', bg='#efefef')
        self.light_timer.place(x=300,y=5,width=40,height=15)
        light_text_s=tk.Label(self.canvas_equipment, text="[s]", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        light_text_s.place(x=340,y=5,width=20, height=15)
        light_ON_button=tk.Button(self.canvas_equipment, text='ON', justify='center', font=self.ft14, bg='#33FF33', fg='#000000')
        light_ON_button.place(x=302,y=20,width=26,height=20)
        light_ON_button["command"] = self.light_on
        light_OFF_button=tk.Button(self.canvas_equipment, text='OFF', justify='center', font=self.ft10, bg='#FF3333', fg='#000000')
        light_OFF_button.place(x=332,y=20,width=26,height=20)
        light_OFF_button["command"] = self.light_off

    def open_camera(self):
        print("open carema")

    def open_graph(self):
        print("open graph")

    def open_maintenance(self):
        print("open maintenance")

    def draw_pump(self, x, y, r, color, canvas_name):
        canvas_name.create_line(x-(2*r), y, x-r, y, width=6, fill=color)
        canvas_name.create_line(x+(2*r), y, x+r, y, width=6, fill=color)
        canvas_name.create_oval(x-r,y-r,x+r,y+r, width=2)
        canvas_name.create_line(x-(r/2), y-(r*1.732/2), x-(r/2), y+(r*1.732/2), x+r, y, x-(r/2), y-(r*1.732/2), width=2)

    def draw_mark(self,x,y,color,canvas_name):
        mark_size = 8
        canvas_name.create_polygon(x,y,x-mark_size,y-mark_size*1.732/2,
                                    x-mark_size,y+mark_size*1.732/2,x,y,
                                    fill=color)

    def draw_magnetic_stirrer(self,x,y,canvas_name):
        mark_size = 20
        canvas_name.create_oval(x-mark_size,y-mark_size/2,x+mark_size,y+mark_size/2, width=2)
        canvas_name.create_polygon(x+5,y-mark_size/2,
                                    x-5,y-5-mark_size/2,
                                    x-3,y+5-mark_size/2,
                                    x+5,y-mark_size/2,
                                    fill='#FF2222')
        canvas_name.create_polygon(x-5,y+mark_size/2,
                                    x+5,y-5+mark_size/2,
                                    x+3,y+5+mark_size/2,
                                    x-5,y+mark_size/2,
                                    fill='#2222FF')

    def draw_light(self,x,y,canvas_name):
        mark_size = 20
        canvas_name.create_line(x-mark_size, y-mark_size/5,
                                x+mark_size, y-mark_size/5,
                                x+mark_size, y+mark_size/5,
                                x-mark_size, y+mark_size/5,
                                x-mark_size, y-mark_size/5,
                                width=2, fill='#000000')
        for i in range(6):
            x1 = x-mark_size + mark_size/2.5*i
            canvas_name.create_line(x1, y+mark_size/5+3,
                                    x1, y+mark_size/5+11,
                                    width=2, fill='#000000')

    def pump_air_off(self):
        return 0

    def pump_air_on(self):
        print(self.pump_air_timer.get())

    def pump_1_off(self):
        return 0

    def pump_1_on(self):
        print(self.pump_1_timer.get())

    def pump_2_off(self):
        return 0

    def pump_2_on(self):
        print(self.pump_2_timer.get())

    def magnetic_stirrer_off(self):
        return 0

    def magnetic_stirrer_on(self):
        print(self.magnetic_stirrer_timer.get())

    def light_off(self):
        self.light_status=tk.Label(self.canvas_equipment, text="OFF", justify='center', font=self.ft10, bg='#FFFFFF', fg='#000000')
        PIN_NO=21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_NO, GPIO.OUT)
        GPIO.output(PIN_NO,GPIO.LOW)
        GPIO.cleanup(PIN_NO)

    def light_on(self):
        self.light_status=tk.Label(self.canvas_equipment, text="ON", justify='center', font=self.ft10, bg='#FFFFFF', fg='#22FF22')
        print(self.light_timer.get())
        PIN_NO=21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_NO, GPIO.OUT)
        GPIO.output(PIN_NO,GPIO.HIGH)


import time
from time import strftime
from multiprocessing import Process, Pipe
import random

def send_data(pipe_sensor, pipe_main):
        while True:
            data = pipe_sensor.recv()
            if data == 'SHOW_ME_DATA':
                cache = {'temperature':random.uniform(10.0,49.9), 
                        'humidity':random.uniform(0.0,100.0),
                        'water_temperature':random.uniform(20.0,40.0),
                        'PH':random.uniform(3.0,9.0),
                        'lumen':random.uniform(0.0,10000.0),
                        'time':strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'turbidity':random.uniform(0.0,100000.0),
                        'height':random.uniform(100.0,200.0),
                        }
                pipe_main.send(cache)

if __name__ == "__main__":



    pipe_sensor = Pipe()
    pipe_main = Pipe()
    sender = Process(target=send_data, args=(pipe_sensor[1], pipe_main[0]))
    gui = Process(target=GUI, args=(pipe_sensor[0], pipe_main[1]))

    sender.start()
    gui.start()

    sender.join()
    gui.join()