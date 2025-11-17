import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pymysql
import pandas as pd
from datetime import datetime
import json
import os
import threading


class MySQLExporterGUI:
    # 配置文件路径
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'dby_config.json')
    
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL 表数据导出工具")
        self.root.geometry("600x680")
        self.root.resizable(False, False)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="MySQL 数据库配置", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # 配置管理区域
        config_frame = ttk.LabelFrame(main_frame, text="配置管理", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 配置名称
        ttk.Label(config_frame, text="配置名称:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.config_name_entry = ttk.Entry(config_frame, width=20)
        self.config_name_entry.insert(0, "默认配置")
        self.config_name_entry.grid(row=0, column=1, pady=5, padx=(0, 10))
        
        # 配置选择
        ttk.Label(config_frame, text="选择配置:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.config_selector = ttk.Combobox(config_frame, width=17, state="readonly")
        self.config_selector.grid(row=0, column=3, pady=5)
        self.config_selector.bind("<<ComboboxSelected>>", self.on_config_selected)
        
        # 配置操作按钮
        config_btn_frame = ttk.Frame(config_frame)
        config_btn_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(config_btn_frame, text="保存配置", command=self.save_current_config, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(config_btn_frame, text="加载配置", command=self.load_selected_config, width=12).grid(row=0, column=1, padx=5)
        ttk.Button(config_btn_frame, text="删除配置", command=self.delete_selected_config, width=12).grid(row=0, column=2, padx=5)
        
        # 主机地址
        ttk.Label(main_frame, text="主机地址:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(main_frame, width=30)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=2, column=1, pady=5)
        
        # 端口
        ttk.Label(main_frame, text="端口:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.insert(0, "3306")
        self.port_entry.grid(row=3, column=1, pady=5)
        
        # 用户名
        ttk.Label(main_frame, text="用户名:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=4, column=1, pady=5)
        
        # 密码
        ttk.Label(main_frame, text="密码:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=5, column=1, pady=5)
        
        # 数据库名
        db_frame = ttk.Frame(main_frame)
        db_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(db_frame, text="数据库名:").pack(side=tk.LEFT)
        self.database_combo = ttk.Combobox(db_frame, width=22)
        self.database_combo.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(db_frame, text="刷新", command=self.refresh_databases, width=8).pack(side=tk.LEFT)
        
        # 表名
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(table_frame, text="表名:").pack(side=tk.LEFT, padx=(0, 24))
        self.table_combo = ttk.Combobox(table_frame, width=22)
        self.table_combo.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(table_frame, text="刷新", command=self.refresh_tables, width=8).pack(side=tk.LEFT)
        
        # 字段选择
        field_frame = ttk.Frame(main_frame)
        field_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(field_frame, text="选择字段:").pack(side=tk.LEFT)
        self.field_label = ttk.Label(field_frame, text="全部字段", foreground="gray")
        self.field_label.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(field_frame, text="选择字段", command=self.open_field_selector, width=10).pack(side=tk.LEFT)
        
        # 存储选中的字段
        self.selected_fields = []
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        # 测试连接按钮
        self.test_button = ttk.Button(button_frame, text="测试连接", command=self.test_connection)
        self.test_button.grid(row=0, column=0, padx=5)
        
        # 导出按钮
        self.export_button = ttk.Button(button_frame, text="导出数据", command=self.export_data)
        self.export_button.grid(row=0, column=1, padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="blue")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        # 进度条（默认隐藏）
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress_bar.grid(row=11, column=0, columnspan=2, pady=5)
        self.progress_bar.grid_remove()  # 初始隐藏
        
        # 加载所有配置
        self.load_all_configs()
        # 加载上次使用的配置
        self.load_last_config()
        
    def load_all_configs(self):
        """加载所有配置名称到下拉框"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    configs = data.get('configs', {})
                    config_names = list(configs.keys())
                    self.config_selector['values'] = config_names
                    if config_names and not self.config_selector.get():
                        self.config_selector.current(0)
        except Exception as e:
            print(f"加载配置列表失败: {e}")
    
    def load_last_config(self):
        """加载上次使用的配置"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    last_used = data.get('last_used', '')
                    configs = data.get('configs', {})
                    
                    if last_used and last_used in configs:
                        self.config_name_entry.delete(0, tk.END)
                        self.config_name_entry.insert(0, last_used)
                        self.fill_form(configs[last_used])
                        # 设置下拉框选中项
                        if last_used in self.config_selector['values']:
                            self.config_selector.set(last_used)
                        self.status_label.config(text=f"已加载配置: {last_used}", foreground="green")
        except Exception as e:
            print(f"加载上次配置失败: {e}")
    
    def fill_form(self, config):
        """填充表单数据"""
        if 'host' in config:
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, config['host'])
        if 'port' in config:
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, config['port'])
        if 'username' in config:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, config['username'])
        if 'password' in config:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, config['password'])
        if 'database' in config:
            self.database_combo.set(config['database'])
        if 'table' in config:
            self.table_combo.set(config['table'])
        if 'selected_fields' in config:
            self.selected_fields = config['selected_fields']
            self.update_field_label()
    
    def get_current_config(self):
        """获取当前表单配置"""
        return {
            'host': self.host_entry.get().strip(),
            'port': self.port_entry.get().strip(),
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get(),
            'database': self.database_combo.get().strip(),
            'table': self.table_combo.get().strip(),
            'selected_fields': self.selected_fields
        }
    
    def save_current_config(self):
        """保存当前配置"""
        config_name = self.config_name_entry.get().strip()
        if not config_name:
            messagebox.showwarning("警告", "请输入配置名称！")
            return
        
        try:
            # 读取现有配置
            data = {'configs': {}, 'last_used': ''}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 添加或更新配置
            data['configs'][config_name] = self.get_current_config()
            data['last_used'] = config_name
            
            # 保存到文件
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 更新下拉框
            self.load_all_configs()
            self.config_selector.set(config_name)
            
            self.status_label.config(text=f"配置 '{config_name}' 已保存", foreground="green")
            messagebox.showinfo("成功", f"配置 '{config_name}' 保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：\n{str(e)}")
    
    def load_selected_config(self):
        """加载选中的配置"""
        selected = self.config_selector.get()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个配置！")
            return
        
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    configs = data.get('configs', {})
                    
                    if selected in configs:
                        self.config_name_entry.delete(0, tk.END)
                        self.config_name_entry.insert(0, selected)
                        self.fill_form(configs[selected])
                        
                        # 更新last_used
                        data['last_used'] = selected
                        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        self.status_label.config(text=f"已加载配置: {selected}", foreground="green")
                    else:
                        messagebox.showerror("错误", f"配置 '{selected}' 不存在！")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败：\n{str(e)}")
    
    def delete_selected_config(self):
        """删除选中的配置"""
        selected = self.config_selector.get()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个配置！")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除配置 '{selected}' 吗？"):
            return
        
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    configs = data.get('configs', {})
                    
                    if selected in configs:
                        del configs[selected]
                        
                        # 如果删除的是last_used，清空它
                        if data.get('last_used') == selected:
                            data['last_used'] = ''
                        
                        # 保存
                        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        # 更新界面
                        self.load_all_configs()
                        self.config_selector.set('')
                        self.status_label.config(text=f"配置 '{selected}' 已删除", foreground="orange")
                        messagebox.showinfo("成功", f"配置 '{selected}' 已删除！")
                    else:
                        messagebox.showerror("错误", f"配置 '{selected}' 不存在！")
        except Exception as e:
            messagebox.showerror("错误", f"删除配置失败：\n{str(e)}")
    
    def on_config_selected(self, event):
        """配置选择变化事件"""
        # 不自动加载，用户需要点击加载按钮
        pass
    
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.grid()
        self.progress_bar.start(10)
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
    
    def run_async(self, task_func, on_complete=None, on_error=None):
        """
        异步执行任务
        :param task_func: 要执行的任务函数
        :param on_complete: 任务完成后的回调函数
        :param on_error: 错误处理回调函数
        """
        def wrapper():
            try:
                result = task_func()
                if on_complete:
                    self.root.after(0, lambda: on_complete(result))
            except Exception as e:
                if on_error:
                    self.root.after(0, lambda: on_error(e))
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", f"操作失败：\n{str(e)}"))
            finally:
                self.root.after(0, self.hide_progress)
        
        self.show_progress()
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def update_field_label(self):
        """更新字段显示标签"""
        if self.selected_fields:
            count = len(self.selected_fields)
            self.field_label.config(text=f"已选择 {count} 个字段", foreground="green")
        else:
            self.field_label.config(text="全部字段", foreground="gray")
    
    def refresh_databases(self):
        """刷新数据库列表"""
        if not self.host_entry.get().strip() or not self.username_entry.get().strip():
            messagebox.showwarning("警告", "请先填写主机地址和用户名！")
            return
        
        self.status_label.config(text="正在获取数据库列表...", foreground="orange")
        
        def task():
            connection = pymysql.connect(
                host=self.host_entry.get().strip(),
                port=int(self.port_entry.get().strip() or 3306),
                user=self.username_entry.get().strip(),
                password=self.password_entry.get(),
                connect_timeout=3,
                charset='utf8mb4'
            )
            
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            # 过滤系统数据库
            databases = [db for db in databases if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
            return databases
        
        def on_complete(databases):
            self.database_combo['values'] = databases
            self.status_label.config(text=f"已加载 {len(databases)} 个数据库", foreground="green")
        
        def on_error(e):
            self.status_label.config(text="获取数据库列表失败", foreground="red")
            if isinstance(e, pymysql.Error):
                messagebox.showerror("连接失败", f"无法获取数据库列表：\n{str(e)}\n\n请检查连接信息或手动输入。")
            else:
                messagebox.showwarning("警告", f"连接超时或出错：\n{str(e)}\n\n您可以手动输入数据库名。")
        
        self.run_async(task, on_complete, on_error)
    
    def refresh_tables(self):
        """刷新表列表"""
        database = self.database_combo.get().strip()
        if not database:
            messagebox.showwarning("警告", "请先选择或输入数据库名！")
            return
        
        if not self.host_entry.get().strip() or not self.username_entry.get().strip():
            messagebox.showwarning("警告", "请先填写主机地址和用户名！")
            return
        
        self.status_label.config(text="正在获取表列表...", foreground="orange")
        
        def task():
            connection = pymysql.connect(
                host=self.host_entry.get().strip(),
                port=int(self.port_entry.get().strip() or 3306),
                user=self.username_entry.get().strip(),
                password=self.password_entry.get(),
                database=database,
                connect_timeout=3,
                charset='utf8mb4'
            )
            
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            connection.close()
            return tables
        
        def on_complete(tables):
            self.table_combo['values'] = tables
            self.status_label.config(text=f"已加载 {len(tables)} 个表", foreground="green")
        
        def on_error(e):
            self.status_label.config(text="获取表列表失败", foreground="red")
            if isinstance(e, pymysql.Error):
                messagebox.showerror("连接失败", f"无法获取表列表：\n{str(e)}\n\n请检查数据库名或手动输入。")
            else:
                messagebox.showwarning("警告", f"连接超时或出错：\n{str(e)}\n\n您可以手动输入表名。")
        
        self.run_async(task, on_complete, on_error)
    
    def open_field_selector(self):
        """打开字段选择器"""
        database = self.database_combo.get().strip()
        table = self.table_combo.get().strip()
        
        if not database or not table:
            messagebox.showwarning("警告", "请先选择数据库和表！")
            return
        
        if not self.host_entry.get().strip() or not self.username_entry.get().strip():
            messagebox.showwarning("警告", "请先填写连接信息！")
            return
        
        # 连接参数
        conn_params = {
            'host': self.host_entry.get().strip(),
            'port': int(self.port_entry.get().strip() or 3306),
            'user': self.username_entry.get().strip(),
            'password': self.password_entry.get(),
            'database': database,
            'connect_timeout': 3,
            'charset': 'utf8mb4'
        }
        
        # 打开字段选择对话框
        dialog = FieldSelectorDialog(self.root, conn_params, table, self.selected_fields)
        if dialog.result:
            self.selected_fields = dialog.result
            self.update_field_label()
    
    def get_connection_params(self):
        """获取连接参数"""
        try:
            return {
                'host': self.host_entry.get().strip(),
                'port': int(self.port_entry.get().strip()),
                'user': self.username_entry.get().strip(),
                'password': self.password_entry.get(),
                'database': self.database_combo.get().strip(),
                'charset': 'utf8mb4'
            }
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字！")
            return None
    
    def validate_inputs(self):
        """验证输入"""
        if not self.host_entry.get().strip():
            messagebox.showwarning("警告", "请输入主机地址！")
            return False
        if not self.username_entry.get().strip():
            messagebox.showwarning("警告", "请输入用户名！")
            return False
        if not self.database_combo.get().strip():
            messagebox.showwarning("警告", "请输入数据库名！")
            return False
        if not self.table_combo.get().strip():
            messagebox.showwarning("警告", "请输入表名！")
            return False
        return True
    
    def test_connection(self):
        """测试数据库连接"""
        if not self.validate_inputs():
            return
        
        params = self.get_connection_params()
        if not params:
            return
        
        self.status_label.config(text="正在测试连接...", foreground="orange")
        
        def task():
            connection = pymysql.connect(**params)
            connection.close()
            return True
        
        def on_complete(result):
            self.status_label.config(text="连接成功！", foreground="green")
            self.save_current_config()
            messagebox.showinfo("成功", "数据库连接测试成功！")
        
        def on_error(e):
            self.status_label.config(text="连接失败", foreground="red")
            messagebox.showerror("连接失败", f"无法连接到数据库：\n{str(e)}")
        
        self.run_async(task, on_complete, on_error)
    
    def get_column_descriptions(self, connection, table_name):
        """获取字段描述作为表头"""
        cursor = connection.cursor()
        query = """
            SELECT COLUMN_NAME, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """
        cursor.execute(query, (self.database_combo.get().strip(), table_name))
        results = cursor.fetchall()
        cursor.close()
        
        # 创建字段名到描述的映射，如果没有描述则使用字段名
        column_mapping = {}
        for column_name, comment in results:
            if comment and comment.strip():
                column_mapping[column_name] = comment
            else:
                column_mapping[column_name] = column_name
        
        return column_mapping
    
    def export_data(self):
        """导出表数据"""
        if not self.validate_inputs():
            return
        
        params = self.get_connection_params()
        if not params:
            return
        
        table_name = self.table_combo.get().strip()
        selected_fields = self.selected_fields.copy()
        
        # 先选择保存位置（在主线程）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{table_name}_{timestamp}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            self.status_label.config(text="已取消导出", foreground="blue")
            return
        
        self.status_label.config(text="正在导出数据...", foreground="orange")
        
        def task():
            # 连接数据库
            connection = pymysql.connect(**params)
            
            # 获取字段描述
            column_mapping = self.get_column_descriptions(connection, table_name)
            
            if not column_mapping:
                connection.close()
                raise Exception(f"表 '{table_name}' 不存在或没有字段！")
            
            # 查询表数据，如果有选中字段则只查询选中的字段
            if selected_fields:
                # 过滤掉不存在的字段
                valid_fields = [f for f in selected_fields if f in column_mapping]
                if not valid_fields:
                    connection.close()
                    raise Exception("选中的字段都不存在于表中！")
                
                fields_str = ", ".join([f"`{f}`" for f in valid_fields])
                query = f"SELECT {fields_str} FROM `{table_name}`"
                
                # 只保留选中字段的映射
                column_mapping = {k: v for k, v in column_mapping.items() if k in valid_fields}
            else:
                query = f"SELECT * FROM `{table_name}`"
            
            df = pd.read_sql(query, connection)
            connection.close()
            
            if df.empty:
                raise Exception("表中没有数据！")
            
            # 重命名列为描述
            df.rename(columns=column_mapping, inplace=True)
            
            # 导出到Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            return len(df)
        
        def on_complete(row_count):
            self.status_label.config(text="导出成功！", foreground="green")
            self.save_current_config()
            messagebox.showinfo("成功", f"数据已成功导出到：\n{file_path}\n\n共导出 {row_count} 行数据")
        
        def on_error(e):
            self.status_label.config(text="导出失败", foreground="red")
            if isinstance(e, pymysql.Error):
                messagebox.showerror("数据库错误", f"导出失败：\n{str(e)}")
            else:
                messagebox.showerror("错误", f"发生错误：\n{str(e)}")
        
        self.run_async(task, on_complete, on_error)


class FieldSelectorDialog:
    """字段选择对话框"""
    def __init__(self, parent, conn_params, table_name, selected_fields):
        self.result = None
        self.conn_params = conn_params
        self.table_name = table_name
        self.field_vars = {}
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择字段")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text=f"表: {table_name}", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 操作按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self.select_all, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="反选", command=self.invert_selection, width=10).pack(side=tk.LEFT, padx=5)
        
        # 字段列表框架（带滚动条）
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(bottom_frame, text="确定", command=self.confirm, width=12).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="取消", command=self.cancel, width=12).pack(side=tk.RIGHT, padx=5)
        
        # 加载字段
        self.load_fields(selected_fields)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # 等待窗口关闭
        self.dialog.wait_window()
    
    def load_fields(self, selected_fields):
        """加载字段列表"""
        try:
            connection = pymysql.connect(**self.conn_params)
            cursor = connection.cursor()
            
            query = """
                SELECT COLUMN_NAME, COLUMN_COMMENT, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            cursor.execute(query, (self.conn_params['database'], self.table_name))
            fields = cursor.fetchall()
            cursor.close()
            connection.close()
            
            if not fields:
                ttk.Label(self.scrollable_frame, text="未找到字段！", foreground="red").pack(pady=20)
                return
            
            # 创建字段复选框
            for idx, (field_name, comment, data_type) in enumerate(fields):
                # 创建行框架
                row_frame = ttk.Frame(self.scrollable_frame)
                row_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # 复选框变量
                var = tk.BooleanVar(value=field_name in selected_fields)
                self.field_vars[field_name] = var
                
                # 复选框
                cb = ttk.Checkbutton(row_frame, variable=var)
                cb.pack(side=tk.LEFT, padx=(0, 5))
                
                # 字段名（加粗）
                name_label = ttk.Label(row_frame, text=field_name, font=("Arial", 9, "bold"), width=20, anchor="w")
                name_label.pack(side=tk.LEFT, padx=(0, 10))
                
                # 类型
                type_label = ttk.Label(row_frame, text=f"[{data_type}]", foreground="gray", width=15, anchor="w")
                type_label.pack(side=tk.LEFT, padx=(0, 10))
                
                # 描述
                desc_text = comment if comment and comment.strip() else "无描述"
                desc_label = ttk.Label(row_frame, text=desc_text, foreground="blue")
                desc_label.pack(side=tk.LEFT)
                
        except Exception as e:
            error_label = ttk.Label(self.scrollable_frame, text=f"加载字段失败：{str(e)}", foreground="red")
            error_label.pack(pady=20)
    
    def select_all(self):
        """全选"""
        for var in self.field_vars.values():
            var.set(True)
    
    def invert_selection(self):
        """反选"""
        for var in self.field_vars.values():
            var.set(not var.get())
    
    def confirm(self):
        """确认选择"""
        self.result = [field for field, var in self.field_vars.items() if var.get()]
        self.dialog.destroy()
    
    def cancel(self):
        """取消"""
        self.result = None
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = MySQLExporterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
