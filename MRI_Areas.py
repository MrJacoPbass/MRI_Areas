
import tkinter as tk
import customtkinter as ctk
import cv2 as cv
import numpy as np
import nibabel as nb

from Backbone import MRI_Area

def _photo_image(canvas, image: np.ndarray):
    height, width = image.shape
    data = f'P5 {width} {height} 255 '.encode() + image.astype(np.uint8).tobytes()
    return tk.PhotoImage(master = canvas, width=width, height=height, data=data, format='PPM')

class main(ctk.CTk):
    def __init__(self, Title, size):
        super().__init__()
        # Initialize it
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(size[0], size[1])
        self.maxsize(size[0], size[1])
        self.title(Title)
        

class frame(tk.Frame):
    def __init__(self, parent, *, relx = 0, rely = 0, relwidth = 1, relheight = 1, TYPE, **kwargs):
        super().__init__(parent, **kwargs)
        self.place(relx = relx, rely = rely, relwidth = relwidth, relheight = relheight)
        self.update_idletasks()


class slider(ctk.CTkSlider):
    def __init__(self, parent, *, rwidth = 1, relx = 0, rely = 0, var = 0, low = -100, high = 100, **kwargs):
        super().__init__(parent, from_ = low, to = high, **kwargs)
        self.var = tk.IntVar(self, var)
        self.configure(width = parent.master.winfo_width() * rwidth, variable = self.var)
        self.place(relx = relx, rely = rely)
        
        ctk.CTkLabel(self.master, textvariable = self.var).place(x = -30, y = -5, relx = relx, rely = rely)
        
        #TODO: Adapt width dynamically.
        #self.bind("<Configure>", lambda *_, parent = parent, rwidth = rwidth: self.WindowSize_changed(*_, self = self, parent = parent, rwidth = rwidth))   
        
    def link(self, target, MODE):
        self.var.trace('w', lambda *_, target = target, MODE = MODE: self._SliderChanged(*_, self = self, target = target, MODE = MODE ))
        return
    
    def _SliderChanged(*args, self, target, MODE):
        if MODE == 'LOWER': 
            a = self.get()
            if target.get() < a:
                target.set(a)
            else:
                target.set(target.get())
            
        if MODE == 'GREATER':
            a = self.get()
            if target.get() > a:
                target.set(a)
            else:
                target.set(target.get())
        
        return
    
    # def WindowSize_changed(*args, self, parent, rwidth):
    #     print(self._name)
    #     self.configure(width = parent.winfo_width() * rwidth)
    #     return
        
class button(tk.Button):
    def __init__(self, parent,* , relx = 0, rely = 0, TYPE = None, preset_image = np.array([]), **kwargs):
        super().__init__(parent, **kwargs)
        self.place(relx = relx, rely = rely)
        self.img = preset_image
        self.miniature = preset_image.copy()
        self.memory = preset_image.copy()
        
        self.Label = ctk.CTkLabel(self.master, text = '')
        self.FileName = ctk.CTkLabel(self.master, text = '')
        
        if TYPE == 'OPEN':
            self.FileName.place(x = 50, y = 60, relx = relx, rely = rely, anchor = 'c')
        if TYPE == 'SAVE':
            self.Label.place(x = 50, y = 60, relx = relx, rely = rely, anchor = 'c')

        
    def open_image(self, canvas, container):
        global var, Imgs, nifti_Flag , M_image, Flag_analysed
        path = tk.filedialog.askopenfilename()
        if path == '': return
        elif path[-3:] == 'nii': 
            # Nifti format. Need to select the slice too
            Nifti = nb.load(path)
            Imgs = Nifti.get_fdata()
            # self.img = Imgs[:,:,int(Slice_select.get())]
            self.img = (Imgs[:,:,int(Slice_select.get())] / Imgs[:,:,int(Slice_select.get())].max() * 255)
            self.miniature = (Imgs[:,:,int(Slice_select.get())] / Imgs[:,:,int(Slice_select.get())].max() * 255)
            self.memory = (Imgs[:,:,int(Slice_select.get())] / Imgs[:,:,int(Slice_select.get())].max() * 255)
            
            Slice_select.configure(to = int(Imgs.shape[2]))
            
            M_img = cv.resize(self.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
            M_image = _photo_image(Miniature, M_img)
            Miniature.itemconfig(Miniature_container, image = M_image)
            
            nifti_Flag = True
        else: 
            self.img = cv.imread(path, 0)
            self.miniature = cv.imread(path, 0)
            self.memory = cv.imread(path, 0)

            
            M_img = cv.resize(self.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
            M_image = _photo_image(Miniature, M_img)
            Miniature.itemconfig(Miniature_container, image = M_image)
            
            nifti_Flag = False
        name = path.split('/')
        self.FileName.configure(text = name[-1])
        
        res = cv.resize(self.img, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
        self.image = _photo_image(canvas, res)
        canvas.itemconfig(container, image = self.image)
        canvas.configure(width = res.shape[0] + 20 , height = res.shape[1] + 20 )
        
        Flag_analysed = False
        var.set('Area Percentage')
        return 
    
    def save_image(self):
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".tif")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        try:
            cv.imwrite(f.name, Open.img)
            self.Label.configure(text = 'Succesfully saved', text_color = 'black')
        except Exception:
            self.Label.configure(text = 'Could not save image', text_color = 'red')

        return

class selector(tk.Canvas):
    """ Tkinter Canvas mouse position widget. 
    
    answered Apr 20, 2019 at 10:39
    martineau
    at https://stackoverflow.com/questions/55636313/selecting-an-area-of-an-image-with-a-mouse-and-recording-the-dimensions-of-the-s
    """

    def __init__(self, canvas):
        self.canvas = canvas
        self.canv_width = self.canvas.cget('width')
        self.canv_height = self.canvas.cget('height')
        self.reset()

        # Create canvas cross-hair lines.
        xhair_opts = dict(dash=(3, 2), fill='white', state=tk.HIDDEN)
        self.lines = (self.canvas.create_line(0, 0, 0, self.canv_height, **xhair_opts),
                      self.canvas.create_line(0, 0, self.canv_width,  0, **xhair_opts))
    

    def cur_selection(self):
        return (self.start, self.end)

    def begin(self, event):
        self.hide()
        self.start = (event.x, event.y)  # Remember position (no drawing).
        
    def update(self, event):
        self.end = (event.x, event.y)
        self._update(event)
        self._command(self.start, (event.x, event.y))  # User callback.

    def _update(self, event):
        # Update cross-hair lines.
        self.canvas.coords(self.lines[0], event.x, 0, event.x, self.canv_height)
        self.canvas.coords(self.lines[1], 0, event.y, self.canv_width, event.y)
        self.show()

    def reset(self):
        self.start = self.end = None

    def hide(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.HIDDEN)
        self.canvas.itemconfigure(self.lines[1], state=tk.HIDDEN)

    def show(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.NORMAL)
        self.canvas.itemconfigure(self.lines[1], state=tk.NORMAL)

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<B1-Motion>", self.update)
        self.canvas.bind("<ButtonRelease-1>", self.quit)

    def quit(self, event):
        self.hide()  # Hide cross-hairs.
        self.reset()


class SelectionObject:
    """ Widget to display a rectangular area on given canvas defined by two points
        representing its diagonal.
        
        answered Apr 20, 2019 at 10:39
        martineau
        at https://stackoverflow.com/questions/55636313/selecting-an-area-of-an-image-with-a-mouse-and-recording-the-dimensions-of-the-s
    """
        
    def __init__(self, canvas, select_opts):
        # Create attributes needed to display selection.
        self.canvas = canvas
        self.select_opts1 = select_opts
        self.width = self.canvas.cget('width')
        self.height = self.canvas.cget('height')
        
        

        #self.canvas.bind('<B1-Motion>', self.motion)
        # Options for areas outside rectanglar selection.
        select_opts1 = self.select_opts1.copy()  # Avoid modifying passed argument.
        select_opts1.update()  # Hide initially.
        # Separate options for area inside rectanglar selection.
        select_opts2 = dict(dash=(2, 2), fill='', outline='white')
        
        
        # Initial extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = 10, 10,  int(self.width) - 10 , int(self.height) - 10
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        self.rects = (
            # Area *outside* selection (inner) rectangle.
            self.canvas.create_rectangle(omin_x, omin_y,  omax_x, imin_y, **select_opts1),
            self.canvas.create_rectangle(omin_x, imin_y,  imin_x, imax_y, **select_opts1),
            self.canvas.create_rectangle(imax_x, imin_y,  omax_x, imax_y, **select_opts1),
            self.canvas.create_rectangle(omin_x, imax_y,  omax_x, omax_y, **select_opts1),
            # Inner rectangle.
            self.canvas.create_rectangle(imin_x, imin_y,  imax_x, imax_y, **select_opts2)
        )
        self.handles = (
            self.create_circle(imin_x, imin_y, 5),
            self.create_circle(imin_x, imax_y + 1 , 5),
            self.create_circle(imax_x, imin_y, 5),
            self.create_circle(imax_x, imax_y + 1, 5)
            )
        
        # Reset Button
        Reset = tk.Button(canvas.master, width = 10, height = 2, text = 'Reset', command = self.reset)
        Reset.pack( pady=10)
        
    def create_circle(self, x, y, r): #center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, fill = '#fff', activefill = '#000000')
        
    def reset(self):
        global Reset_image, M_image, Flag_analysed, var, top_anchor
        # Resets the box positions.
        imin_x, imin_y,  imax_x, imax_y = 10, 10,  int(self.width) - 10 , int(self.height) - 10
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height


        # Area *outside* selection (inner) rectangle.
        self.canvas.coords(self.rects[0], omin_x, omin_y,  omax_x, imin_y)
        self.canvas.coords(self.rects[1],omin_x, imin_y,  imin_x, imax_y)
        self.canvas.coords(self.rects[2],imax_x, imin_y,  omax_x, imax_y)
        self.canvas.coords(self.rects[3],omin_x, imax_y,  omax_x, omax_y)
        # Inner rectangle.
        self.canvas.coords(self.rects[4],imin_x, imin_y,  imax_x, imax_y)
        
        self.canvas.coords(self.handles[0], imin_x - 5, imin_y - 5, imin_x + 5, imin_y + 5)
        self.canvas.coords(self.handles[1], imin_x - 5, imax_y - 4, imin_x + 5, imax_y + 6)
        self.canvas.coords(self.handles[2], imax_x - 5, imin_y - 5, imax_x + 5, imin_y + 5)
        self.canvas.coords(self.handles[3], imax_x - 5, imax_y - 4, imax_x + 5, imax_y + 6)
    
        res = cv.resize(Open.miniature, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
        Reset_image = _photo_image(canvas, res)
        canvas.itemconfig(container, image = Reset_image)
        
        M_img = cv.resize(Open.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
        M_image = _photo_image(Miniature, M_img)
        Miniature.itemconfig(Miniature_container, image = M_image)
        
        
        Open.img = Open.miniature.copy()
        
        S_zoom.set(0)
        top_anchor = np.array([0,0])
        ZoomIn(Open.img, S_zoom.get())
        
        Flag_analysed = False
        var.set('Area Percentage')
    def update(self, start, end):
        self.width = self.canvas.cget('width')
        self.height = self.canvas.cget('height')
        
        # Current extrema of inner and outer rectangles.
        X, Y = self._get_coords(start, end)
        
        if X < 10 or (int(self.width) - 10) < X or Y < 10 or (int(self.height) - 10) < Y: return  #Out of bounds
        
        for i in self.handles:
            
            pos = self.canvas.coords(i)
            
            if (pos[0] - 20 < X < pos[2] + 20):
                self.canvas.coords(i, X - 5, (pos[1] + pos[3]) / 2 - 5, X + 5, (pos[1] + pos[3]) / 2 + 5)
                
            if (pos[1] - 20 < Y < pos[3] + 20):
                self.canvas.coords(i, (pos[0] + pos[2]) / 2 - 5, Y - 5, (pos[0] + pos[2]) / 2 + 5,  Y + 5)
                
            if (pos[0] - 20 < X < pos[2] + 20) and (pos[1] - 10 < Y < pos[3] + 10):
                self.canvas.coords(i, X - 5, Y - 5, X + 5,  Y + 5)
            
            
        self.canvas.update_idletasks()
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height
        imin_TL = self.canvas.coords(self.handles[0])
        imin_x = (imin_TL[0] + imin_TL[2]) / 2
        imin_y = (imin_TL[1] + imin_TL[3]) / 2
        imax_BR = self.canvas.coords(self.handles[3])
        imax_x = (imax_BR[0] + imax_BR[2]) / 2
        imax_y = (imax_BR[1] + imax_BR[3]) / 2
        # Update coords of all rectangles based on these extrema.
        self.canvas.coords(self.rects[0], omin_x, omin_y,  omax_x, imin_y),
        self.canvas.coords(self.rects[1], omin_x, imin_y,  imin_x, omax_y),
        self.canvas.coords(self.rects[2], imax_x, imin_y,  omax_x, omax_y),
        self.canvas.coords(self.rects[3], omin_x, imax_y,  omax_x, omax_y),
        self.canvas.coords(self.rects[4], imin_x, imin_y,  imax_x, imax_y),
        
        
        # self.canvas.coords(self.handles[1], imin_x - 5, imax_y - 5, imin_x + 5, imax_y + 5),
        # self.canvas.coords(self.handles[2], imax_x - 5, imin_y - 5, imax_x + 5, imin_y + 5),
        # self.canvas.coords(self.handles[3], imax_x - 5, imax_y - 5, imax_x + 5, imax_y + 5),


        # Update the image here, but for the moment do it through a button.
        
        for rect in self.rects:  # Make sure all are now visible.
            self.canvas.itemconfigure(rect, state=tk.NORMAL)

    
    def _get_coords(self, start, end):
        """ Determine coords of a polygon defined by the start and
            end points one of the diagonals of a rectangular area.
        """
        return (end[0], end[1])
    
    def hide(self):
        for rect in self.rects:
            self.canvas.itemconfigure(rect, state=tk.HIDDEN)

def Extract_rect(img, S: SelectionObject):
    handles = S.handles
    Corner_boxes = (canvas.coords(handles[0]), canvas.coords(handles[3]))       # TL, BR
    Corner_coords = []
    for i in Corner_boxes:
        x = np.clip((((i[0] + i[2]) / 2) - 10) * (img.shape[1] / 600), 0, img.shape[1])  # The last parenthesis converts from canvas coordinates
        y = np.clip((((i[1] + i[3]) / 2) - 10) * (img.shape[0] / 600), 0, img.shape[0])  # to original image resolution.
        Corner_coords.append((round(x), round(y)))
    Crop = img[Corner_coords[0][1]:Corner_coords[1][1], Corner_coords[0][0]:Corner_coords[1][0]].copy()  # Row(y) - Column(x); not (x, y)
    return  Crop, Corner_coords

def Incrust_treated(Crop_Results, Corner_coords):
    Open.img = Open.miniature.copy().astype("uint8")
    Open.img[Corner_coords[0][1]:Corner_coords[1][1], Corner_coords[0][0]:Corner_coords[1][0]] = Crop_Results
    return Open.img

def MRI_Redraw(img, thres):  
    global imagen, Results, C_Results, Flag_analysed, var, Area_real_var, zoom, top_anchor 
    Flag_analysed = True
    
    zoom = int(S_zoom.get())
    if zoom != 0:
        size = img.shape
            
        zoom_edge = np.floor(np.array(size) * zoom / 200).astype(int)
        InBounds = (0 <= top_anchor[0] + zoom_edge[0] < size[0] - 1) and (0 <= top_anchor[1] + zoom_edge[1] < size[1]) and (0 <= top_anchor[0] + size[0] - zoom_edge[0] < size[0] - 1) and (0 <= top_anchor[1] + size[1] - zoom_edge[1] < size[1])
        if InBounds:
            Zoomed = img[top_anchor[0] + zoom_edge[0] : top_anchor[0] + size[0] - zoom_edge[0], 
                         top_anchor[1] + zoom_edge[1] : top_anchor[1] + size[1] - zoom_edge[1]]
            Crop, Corner_coordinates_1 = Extract_rect(Zoomed, selection_obj)
            Corner_coordinates = [tuple(np.array(Corner_coordinates_1[0]) + 
                                       np.array([zoom_edge[0] + top_anchor[1], zoom_edge[1] + top_anchor[0]])), 
                                 tuple(np.array(Corner_coordinates_1[1]) + 
                                       np.array([zoom_edge[0]+ top_anchor[1], zoom_edge[1] + top_anchor[0]]))]
        else:
            Crop, Corner_coordinates = Extract_rect(img, selection_obj)
    else: 
        Crop, Corner_coordinates = Extract_rect(img, selection_obj)
        
    C_Results = MRI_Area(Crop, thres, shape = img.shape)
    var.set(f'Area Percentage: {C_Results[1][2]: .2f}%')
    Area_real_var.set(f'Area: {C_Results[1][1] / 100 * n_scaleX.get() * n_scaleY.get(): .2f} arb.u.\u00b2')

    Results = Incrust_treated(C_Results[0], Corner_coordinates)
    res = cv.resize(Results, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
    imagen = _photo_image(canvas, res)
    canvas.itemconfig(container, image = imagen)
    #canvas.configure(width = res.shape[0] + 20 , height = res.shape[1] + 20 )
    ZoomIn(Results, S_zoom.get())
    
def update_screen(a):
    if Flag_analysed == False : return
    GUI.update_idletasks()
    MRI_Redraw(Open.miniature, (S_Low.get(), S_Up.get()))
    

def update_slice(a):
    global M_image, imagen
    if nifti_Flag == True:    
        slice_var = int(Slice_select.get())
        Open.img = (Imgs[:,:,slice_var] / Imgs[:,:,slice_var].max() * 255)
        Open.miniature = (Imgs[:,:,slice_var] / Imgs[:,:,slice_var].max() * 255)
        Open.memory = (Imgs[:,:,slice_var] / Imgs[:,:,slice_var].max() * 255)
        update_screen(a)
        M_img = cv.resize(Open.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
        M_image = _photo_image(Miniature, M_img)
        Miniature.itemconfig(Miniature_container, image = M_image)
        res = cv.resize(Open.img, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
        imagen = _photo_image(canvas, res)
        canvas.itemconfig(container, image = imagen)
        
def Rotate():
    global M_image, imagen, Imgs
    
    if nifti_Flag == True:
        slice_var = int(Slice_select.get())
        for i in range(0, Imgs.shape[2]):
            if i == slice_var: continue
    
            Imgs[:,:,i] = cv.rotate(Imgs[:,:,i], cv.ROTATE_90_COUNTERCLOCKWISE)
        
    
    Open.img = cv.rotate(Open.img, cv.ROTATE_90_COUNTERCLOCKWISE)
    Open.miniature = cv.rotate(Open.miniature, cv. ROTATE_90_COUNTERCLOCKWISE)
    Open.memory = cv.rotate(Open.memory, cv. ROTATE_90_COUNTERCLOCKWISE)
    
    M_img = cv.resize(Open.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
    M_image = _photo_image(Miniature, M_img)
    Miniature.itemconfig(Miniature_container, image = M_image)
    res = cv.resize(Open.img, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
    imagen = _photo_image(canvas, res)
    canvas.itemconfig(container, image = imagen)
    
    if nifti_Flag == True:
        Imgs[:,:,slice_var] = cv.rotate(Imgs[:,:,slice_var], cv.ROTATE_90_COUNTERCLOCKWISE)
# System settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize the GUI        
GUI = main("MR Areas", (720, 640))

top_anchor = np.array([0,0])
top_anchor_previous = np.array([0,0])
# Place the frames
Xsep = 0.3
R_frame = frame(GUI, relx = Xsep, relwidth = 1 - Xsep, bg = 'grey', TYPE = 'IMAGE_VIEW')
L_frame = frame(GUI, relwidth = Xsep, TYPE = 'MENU')

Flag_analysed = False; nifti_Flag = False
# _______________________ Right Frame (IMAGE) ____________________
canvas = tk.Canvas(R_frame, height = 0, width = 0)
canvas.pack(expand = True)


img =  cv.imread("Default.tif", 0)
res = cv.resize(img, dsize=(600, 600), interpolation=cv.INTER_CUBIC)

image = _photo_image(canvas, res)
canvas.configure(width = res.shape[0] + 20 , height = res.shape[1] + 20 )
container = canvas.create_image(10, 10, image=image, anchor = 'nw')

# Create selection object to show current selection boundaries.
selection_obj = SelectionObject(canvas, dict(dash=(2, 2), stipple='gray25', fill='#ffa9a9',
                                             outline=''))

# Callback function to update it given two points of its diagonal.
def on_drag(start, end, **kwarg):  # Must accept these arguments.
     selection_obj.update(start, end)

# Create mouse position tracker that uses the function.
posn_tracker = selector(canvas)
posn_tracker.autodraw(command=on_drag)  # Enable callbacks.

# Code to analyse the image.


# _____________________ Left Frame ___________________
# Slice slider:
tk.Label(L_frame, text = 'Select slice').place(relx = 0.3, rely = 0.25)
Slice_select = slider(L_frame, rwidth = 0.6, relx = 0.2, rely = 0.28, var = 0, low = 0, high = 50,
                      command = update_slice)

S_Low = slider(L_frame, rwidth = 0.6, relx = 0.2, rely = 0.35, var = -20, command = update_screen)
S_Up = slider(L_frame, rwidth = 0.6, relx = 0.2, rely = 0.40, var = 20, command = update_screen)
S_Low.link(S_Up, "LOWER")
S_Up.link(S_Low, "GREATER")


PlaceHolderImage = tk.PhotoImage(width=1, height=1)
Rotate = button(L_frame, relx = 0.74, rely = 0.44, height = 20, width = 20,  image = PlaceHolderImage, relief = tk.RIDGE, command = Rotate)
Rotate.FileName.configure(text = "Rotate 90 degrees.")
Rotate.FileName.place(relx = 0.2, rely = 0.44)

# Create Buttons.

# The Open button is a very important one because its the container of the image that will be analysed_____
Open = button(L_frame, relx = 0.25, rely = 0.01, height = 2, width = 15,
              text = 'Open', TYPE = "OPEN", preset_image = img)
Open.configure(command = lambda x = Open, y = canvas, c = container: button.open_image(x, y, c))

Miniature = tk.Canvas(L_frame, height = 180, width = 180)
Miniature.place(relx = 0.2, rely = 0.5)
M_img = cv.resize(Open.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)

M_image = _photo_image(Miniature, M_img)
Miniature_container = Miniature.create_image(0, 0, image=M_image, anchor = 'nw')

# Scale
tk.Label(L_frame, text = 'Set the image dimensions').place(relx = 0.2 ,rely = 0.75)
n_scaleX = tk.IntVar(L_frame, 0)
scaleX = tk.Entry(L_frame, textvariable = n_scaleX, width = 10)
scaleX.place(relx = 0.23, rely = 0.78)
n_scaleY = tk.IntVar(L_frame, 0)
scaleY = tk.Entry(L_frame, textvariable = n_scaleY, width = 10)
scaleY.place(relx = 0.53, rely = 0.78)
#Labels that display the areas.
var = tk.StringVar(L_frame, 'Area percentage: None')
Area = tk.Label(L_frame, textvariable = var, height = 1, width = 25, 
                anchor = tk.CENTER, font = ("Arial", 12), pady = 10, relief=tk.RAISED)
Area.pack(side='bottom', pady = 20)

# Real Area
Area_real_var = tk.StringVar(L_frame, 'Area: None')
Area_real = tk.Label(L_frame, textvariable = Area_real_var, height = 1, width = 25, 
                anchor = tk.CENTER, font = ("Arial", 12), pady = 10, relief=tk.RAISED)
Area_real.pack(side='bottom', pady = 0)


#__________________________________________________________________________________________________________
Save = button(L_frame, relx = 0.25, rely = 0.13, height = 2, width = 15,
              text = 'Save', TYPE = "SAVE")
Save.configure(command = lambda x = Save: button.save_image(x))

# Code
Analyse = button(R_frame, text = 'Analyse', height = 3, width = 15,
                 command = lambda: MRI_Redraw(Open.miniature, (S_Low.get(), S_Up.get())))
Analyse.pack(pady = 10, padx = 50)


def ZoomIn(img, zoom):
    """
    This function zooms in. #TODO: Its still left to implement the ability of moving what you can see
    """
    global M_image, imagen, top_anchor

    zoom = int(zoom)
    size = img.shape
        
    zoom_edge = np.floor(np.array(size) * zoom / 200).astype(int)
    Crop = img[top_anchor[0] + zoom_edge[0] : top_anchor[0] + size[0] - zoom_edge[0], 
               top_anchor[1] + zoom_edge[1] : top_anchor[1] + size[1] - zoom_edge[1]]
    Open.img = Crop
    # Open.memory = Open.miniature.copy()
    # Open.miniature = Crop
    
    
    # M_img = cv.resize(Open.miniature, dsize=(180, 180), interpolation=cv.INTER_CUBIC)
    # M_image = _photo_image(Miniature, M_img)
    # Miniature.itemconfig(Miniature_container, image = M_image)
    res = cv.resize(Open.img, dsize=(600, 600), interpolation=cv.INTER_CUBIC)
    imagen = _photo_image(canvas, res)
    canvas.itemconfig(container, image = imagen)


def move_image(event):
    global top_anchor, top_anchor_previous
    top_anchor_temp = top_anchor.copy()
    
    factor = 0.3
    top_anchor_final = np.array((int((event.x - 100) * factor), int((event.y - 100) * factor)))
    direction = top_anchor_final - top_anchor_previous
    top_anchor_previous = top_anchor_final
    top_anchor_temp = top_anchor_temp + np.array((direction[1], direction[0]))
        
    size = Open.memory.shape
    zoom_edge = np.floor(np.array(size) * S_zoom.get() / 200).astype(int)
    InBounds = (0 < top_anchor_temp[0] + zoom_edge[0] < size[0] - 1) and (0 < top_anchor_temp[1] + zoom_edge[1] < size[1]) and (0 < top_anchor_temp[0] + size[0] - zoom_edge[0] < size[0] - 1) and (0 < top_anchor_temp[1] + size[1] - zoom_edge[1] < size[1])
    if InBounds: 
        top_anchor = top_anchor_temp
        ZoomIn(Open.memory, S_zoom.get())
    
Miniature.bind("<B1-Motion>", move_image)

S_zoom = slider(R_frame, rwidth = 0.5, relx = 0.1, rely = 0.8, low = 0, high = 100, var =  0, 
                command = lambda x: ZoomIn(Open.memory,  S_zoom.get()))
    
Zoom = button(R_frame, text = "Zoom", height = 2, width = 15,
              command = lambda: ZoomIn(Open.memory, S_zoom.get()))
Zoom.place(relx = 0.1, rely = 0.83)
# Run
GUI.mainloop()




