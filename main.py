import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from matplotlib.ticker import MultipleLocator

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Построитель графиков")
        self.data_sets = []
        
        # Физические размеры сетки (28.5x20 см)
        self.grid_width_cm = 27  # Ширина сетки (ось X)
        self.grid_height_cm = 20.0  # Высота сетки (ось Y)
        self.orientation = "normal"
        
        # Создание элементов управления
        self.control_frame = ttk.Frame(self.root, padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.init_ui()
        
        # Инициализация графической области
        self.figure = Figure(figsize=(11.69, 8.27), dpi=100)  # A4 landscape 297x210 мм
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.NONE)
        
        # Построение сетки при запуске
        self.setup_grid()
        self.setup_plot_appearance()

    def init_ui(self):
        ttk.Button(self.control_frame, text="Загрузить данные", 
                command=self.load_file).pack(pady=5, fill=tk.X)
        
        ttk.Label(self.control_frame, text="Подпись оси X:").pack(pady=5)
        self.x_label_entry = ttk.Entry(self.control_frame)
        self.x_label_entry.pack(fill=tk.X)
        
        ttk.Label(self.control_frame, text="Подпись оси Y:").pack(pady=5)
        self.y_label_entry = ttk.Entry(self.control_frame)
        self.y_label_entry.pack(fill=tk.X)
        
        ttk.Label(self.control_frame, text="Тип линии:").pack(pady=5)
        self.line_type = ttk.Combobox(self.control_frame, 
                                    values=["Прямая", "Кривая"], 
                                    state="readonly")
        self.line_type.current(0)
        self.line_type.pack(fill=tk.X)
        
        ttk.Button(self.control_frame, text="Добавить график", 
                command=self.add_plot).pack(pady=5, fill=tk.X)
        
        self.plot_list = ttk.Treeview(self.control_frame, columns=('name'), show='headings')
        self.plot_list.heading('name', text='Графики')
        self.plot_list.pack(pady=5, fill=tk.X)
        
        ttk.Button(self.control_frame, text="Сохранить график", 
                command=self.save_plot).pack(pady=5, fill=tk.X)
        
        # Кнопка для сброса графиков
        ttk.Button(self.control_frame, text="Сбросить графики", 
                command=self.reset_plots).pack(pady=5, fill=tk.X)

        ttk.Button(self.control_frame, text="Изменить ориентацию листа", 
                command=self.toggle_orientation).pack(pady=5, fill=tk.X)
    
    def update_labels(self):
        """Обновляет подписи осей и их положение."""
        x_label = self.x_label_entry.get().strip()
        y_label = self.y_label_entry.get().strip()
        
        # Получаем смещения из полей ввода
        try:
            x_offset_x = float(self.x_label_offset_x.get())
            x_offset_y = float(self.x_label_offset_y.get())
            y_offset_x = float(self.y_label_offset_x.get())
            y_offset_y = float(self.y_label_offset_y.get())
        except ValueError:
            x_offset_x, x_offset_y = 1.0, 0.0  # Значения по умолчанию
            y_offset_x, y_offset_y = 0.0, 1.0
        
        # Устанавливаем подписи осей с учётом смещения
        self.ax.set_xlabel(x_label or "X", ha='right', position=(x_offset_x, x_offset_y), labelpad=15)
        self.ax.set_ylabel(y_label or "Y", ha='left', position=(y_offset_x, y_offset_y), labelpad=15, rotation='vertical')
        
        self.canvas.draw()
    
    def reset_plots(self):
        self.data_sets = []  # Очищаем данные
        self.plot_list.delete(*self.plot_list.get_children())
        self.x_label_entry.delete(0, tk.END)
        self.y_label_entry.delete(0, tk.END)
        self.update_plot()

    def setup_grid(self):
        # Очищаем график
        self.ax.cla()
        
        # Устанавливаем размер сетки
        self.ax.set_xlim(0, self.grid_width_cm)
        self.ax.set_ylim(0, self.grid_height_cm)
        
        # Настройка сетки
        self.ax.xaxis.set_major_locator(MultipleLocator(1))  # Основные линии каждые 1 см
        self.ax.xaxis.set_minor_locator(MultipleLocator(0.1))  # Вспомогательные линии каждые 1 мм
        self.ax.yaxis.set_major_locator(MultipleLocator(1))  # Основные линии каждые 1 см
        self.ax.yaxis.set_minor_locator(MultipleLocator(0.1))  # Вспомогательные линии каждые 1 мм
        
        # Жирные линии каждые 5 см
        for i in range(0, int(self.grid_width_cm) + 1, 5):
            self.ax.axvline(i, color='black', linewidth=1.5)
        for i in range(0, int(self.grid_height_cm) + 1, 5):
            self.ax.axhline(i, color='black', linewidth=1.5)
        
        # Стиль сетки
        self.ax.grid(which='major', color='black', linestyle='-', linewidth=0.5)
        self.ax.grid(which='minor', color='gray', linestyle=':', linewidth=0.3)
        
        # Рамка вокруг графика
        for spine in self.ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(0.5)
        
        # Обновляем canvas
        self.canvas.draw()

    def setup_plot_appearance(self):
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        
        # Создаем текстовые объекты для подписей осей
        self.x_label_text = self.ax.text(0.5, -0.1, "X", transform=self.ax.transAxes, 
                                        ha='center', va='center', fontsize=12)
        self.y_label_text = self.ax.text(-0.1, 0.5, "Y", transform=self.ax.transAxes, 
                                        ha='center', va='center', fontsize=12, rotation=90)
        
        # Инициализация переменных для перетаскивания
        self.dragging = None
        self.drag_start = None
        
        # Привязка обработчиков событий
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)
    
    def on_click(self, event):
        """Обрабатывает нажатие мыши на подписи осей."""
        if event.inaxes is not None:  # Проверяем, что клик произошел в области графика
            # Проверяем, попали ли мы на подпись оси X
            if self.x_label_text.get_window_extent(renderer=self.canvas.get_renderer()).contains(event.x, event.y):
                self.dragging = 'x'
                self.drag_start = (event.xdata, event.ydata)
                print("Начато перетаскивание подписи оси X")
            
            # Проверяем, попали ли мы на подпись оси Y
            if self.y_label_text.get_window_extent(renderer=self.canvas.get_renderer()).contains(event.x, event.y):
                self.dragging = 'y'
                self.drag_start = (event.xdata, event.ydata)
                print("Начато перетаскивание подписи оси Y")

    def on_motion(self, event):
        """Обрабатывает движение мыши."""
        if self.dragging and event.inaxes is not None:
            dx = event.xdata - self.drag_start[0]
            dy = event.ydata - self.drag_start[1]
            
            if self.dragging == 'x':
                # Обновляем позицию подписи оси X
                new_x = self.x_label_text.get_position()[0] + dx / self.grid_width_cm
                new_y = self.x_label_text.get_position()[1] + dy / self.grid_height_cm
                self.x_label_text.set_position((new_x, new_y))
            elif self.dragging == 'y':
                # Обновляем позицию подписи оси Y
                new_x = self.y_label_text.get_position()[0] + dx / self.grid_width_cm
                new_y = self.y_label_text.get_position()[1] + dy / self.grid_height_cm
                self.y_label_text.set_position((new_x, new_y))
            
            self.canvas.draw()

    def on_release(self, event):
        """Обрабатывает отпускание мыши."""
        self.dragging = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Текст", "*.txt")])
        if file_path:
            try:
                df = pd.read_csv(file_path, header=None, 
                                converters={0: float, 1: float},
                                decimal=',')
                self.current_data = df.values
                messagebox.showinfo("Успех", f"Загружено {len(df)} точек")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

    def add_plot(self):
        if hasattr(self, 'current_data'):
            self.data_sets.append({
                'data': self.current_data,
                'x_label': self.x_label_entry.get().strip() or "X",  # Исправлено
                'y_label': self.y_label_entry.get().strip() or "Y",  # Исправлено
                'line_type': self.line_type.get(),

            })
            self.plot_list.insert('', 'end', values=(f"График {len(self.data_sets)}"))
            self.update_plot()

    def is_rounded(self, value):
        """Проверяет, является ли значение подходящим для шкалы."""
        if value <= 0:
            return False
        exponent = np.floor(np.log10(value))
        base = 10 ** exponent
        # Проверяем, является ли значение кратным 1, 2 или 5
        return (value / base in [1, 2, 5])

    def round_to_nearest(self, value):
        """Округляет значение до ближайшего подходящего."""
        if value <= 0:
            return 1
        exponent = np.floor(np.log10(value))
        base = 10 ** exponent
        # Округляем до ближайшего подходящего значения
        if value / base <= 2:
            return 2 * base
        elif value / base <= 5:
            return 5 * base
        else:
            return 10 * base

    def calculate_scale(self, min_value, max_value, divisions):
        # Определяем диапазон значений
        range_value = max_value - min_value
        
        # Вычисляем начальную цену деления
        price = range_value / divisions
        
        # Подбираем подходящую цену деления
        while not self.is_rounded(price):
            price = self.round_to_nearest(price)
        
        # Определяем начало отсчета
        start = np.floor(min_value / price) * price
        
        return price, start

    def toggle_orientation(self):
        """Переключает ориентацию графика."""
        if self.orientation == "normal":
            self.orientation = "swapped"
            
            # Меняем размеры осей
            self.grid_width_cm, self.grid_height_cm = self.grid_height_cm, self.grid_width_cm  # Меняем местами
            
            # Устанавливаем новые пределы для осей
            self.ax.set_xlim(0, self.grid_width_cm)   # Теперь это 20 см
            self.ax.set_ylim(0, self.grid_height_cm)  # Теперь это 30 см
            
            # Меняем размеры Figure и Canvas
            self.figure.set_size_inches(8.27, 11.69)  # A4 portrait
            self.canvas.get_tk_widget().config(width=800, height=1100)  # Примерные размеры в пикселях
        else:
            self.orientation = "normal"
            
            # Возвращаем размеры осей обратно
            self.grid_width_cm, self.grid_height_cm = self.grid_height_cm, self.grid_width_cm  # Меняем местами обратно
            
            # Устанавливаем новые пределы для осей
            self.ax.set_xlim(0, self.grid_width_cm)   # Теперь это 30 см
            self.ax.set_ylim(0, self.grid_height_cm)  # Теперь это 20 см
            
            # Возвращаем размеры Figure и Canvas обратно
            self.figure.set_size_inches(11.69, 8.27)  # A4 landscape
            self.canvas.get_tk_widget().config(width=1100, height=800)  # Примерные размеры в пикселях

        # Перерисовываем график
        self.update_plot()

    def update_plot(self):
        # Очищаем график, но сохраняем сетку
        self.ax.cla()
        self.setup_grid()  # Перерисовываем сетку
        
        if not self.data_sets:
            return

        all_x = np.concatenate([ds['data'][:, 0] for ds in self.data_sets])
        all_y = np.concatenate([ds['data'][:, 1] for ds in self.data_sets])
        
        # Определяем диапазон данных
        x_price, x_start = self.calculate_scale(all_x.min(), all_x.max(), self.grid_width_cm)
        y_price, y_start = self.calculate_scale(all_y.min(), all_y.max(), self.grid_height_cm)
        
        # Вычисляем конечные значения для осей
        x_end = x_start + x_price * self.grid_width_cm
        y_end = y_start + y_price * self.grid_height_cm
        
        # Определяем порядок величины для осей
        x_order = np.floor(np.log10(x_price)) if x_price > 0 else 0
        y_order = np.floor(np.log10(y_price)) if y_price > 0 else 0
        
        # Преобразуем данные в координаты сетки
        x_scaled = (all_x - x_start) / (x_end - x_start) * self.grid_width_cm
        y_scaled = (all_y - y_start) / (y_end - y_start) * self.grid_height_cm
        
        # Округляем координаты до ближайшего деления сетки
        x_rounded = np.round(x_scaled / 0.1) * 0.1
        y_rounded = np.round(y_scaled / 0.1) * 0.1
        
        # Построение графиков
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        markers = ['o', 'x', 's', '^', 'v', 'D']

        for idx, ds in enumerate(self.data_sets):
            x = ds['data'][:, 0]
            y = ds['data'][:, 1]
            color = colors[idx % len(colors)]
            marker = markers[idx % len(markers)]
            
            # Преобразуем данные в координаты сетки
            x_scaled = (x - x_start) / (x_end - x_start) * self.grid_width_cm
            y_scaled = (y - y_start) / (y_end - y_start) * self.grid_height_cm
            
            # Округляем координаты до ближайшего деления сетки
            x_rounded = np.round(x_scaled / 0.1) * 0.1
            y_rounded = np.round(y_scaled / 0.1) * 0.1
            
            # Построение точек
            self.ax.plot(x_rounded, y_rounded, marker, color=color, markersize=4)  # Уменьшили размер точек
            
            if ds['line_type'] == "Кривая":
                self.plot_curve(x_rounded, y_rounded, self.ax, color)
            else:
                self.plot_straight(x_rounded, y_rounded, self.ax, color)
        
        # Настройка подписей осей
        x_label = self.x_label_entry.get().strip() or "X"
        y_label = self.y_label_entry.get().strip() or "Y"
        
        if x_order != 0:
            x_label += f" ($\\times 10^{{{int(x_order)}}}$)"
        if y_order != 0:
            y_label += f" ($\\times 10^{{{int(y_order)}}}$)"
        
        self.ax.set_xlabel(x_label, ha='right', position=(1, 0), labelpad=15)
        self.ax.set_ylabel(y_label, ha='left', position=(0, 1), labelpad=15, rotation='vertical')
        
        # Настройка подписей делений
        # Подписи для оси X
        x_ticks = np.arange(0, self.grid_width_cm + 1, 1)  # Деления каждые 1 см
        x_labels = [f"{(x_start + i * x_price) / 10**x_order:.1f}" for i in range(len(x_ticks))]
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels)
        
        # Подписи для оси Y
        y_ticks = np.arange(0, self.grid_height_cm + 1, 1)  # Деления каждые 1 см
        y_labels = [f"{(y_start + i * y_price) / 10**y_order:.1f}" for i in range(len(y_ticks))]
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(y_labels)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_curve(self, x, y, ax, color):
        """Строит кривую через точки с использованием PchipInterpolator."""
        # Убедимся, что данные не пустые
        if len(x) == 0:
            return
        
        # Сортируем данные по оси X
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]
        
        # Удаляем дубликаты по оси X
        unique_mask = np.diff(x_sorted) > 0
        unique_mask = np.insert(unique_mask, 0, True)  # Первый элемент всегда уникальный
        x_unique = x_sorted[unique_mask]
        y_unique = y_sorted[unique_mask]
        
        # Если после удаления дубликатов осталось меньше двух точек, строим прямую
        if len(x_unique) < 2:
            ax.plot(x_sorted, y_sorted, '-', color=color, linewidth=1)
            return
        
        # Строим интерполяцию
        pchip = PchipInterpolator(x_unique, y_unique)
        x_smooth = np.linspace(x_unique.min(), x_unique.max(), 300)
        ax.plot(x_smooth, pchip(x_smooth), '-', color=color, linewidth=1)

    def plot_straight(self, x, y, ax, color):
        coeffs = np.polyfit(x, y, 1)
        ax.plot(x, np.poly1d(coeffs)(x), '-', color=color, linewidth=1)

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
        )
        if file_path:
            self.figure.savefig(
                file_path,
                dpi=300,
                bbox_inches='tight',
                pad_inches=0.2,
                metadata={'CreationDate': None}
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()