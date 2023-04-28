import flet
import math
import pathlib
import os
import pinyin
# 声母列表
initial_consonant_list = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'zh', 'ch', 'sh', 'r',
                          'z', 'c', 's', 'y', 'w']
# 韵母列表
list_of_vowels = ['a', 'o', 'e', 'i', 'u', 'ü', 'ai', 'ei', 'ui', 'ao', 'ou', 'iu', 'ie', 'üe', 'er', 'an', 'en', 'in',
                  'un', 'ün', 'ang', 'eng', 'ing', 'ong']


class Chinese2PinYin(flet.UserControl):

    # 构造方法
    def __init__(self, page: flet.Page):
        super().__init__()
        self.page = page
        self.content = flet.TextField(label='词语之间用空格分割!', multiline=True)
        # 模板路径
        self.template_path = None
        # 生成word路径
        self.word_doc_path = None
        # 创建一个DataTable
        self.table = flet.DataTable(
            border=flet.border.all(0.8, "black"),
            bgcolor=flet.colors.GREY_50,
            border_radius=10,
            vertical_lines=flet.border.BorderSide(1, "black"),
            horizontal_lines=flet.border.BorderSide(1, "black"),
            visible=False,
            columns=[
                flet.DataColumn(flet.Text("词语")),
                flet.DataColumn(flet.Text("本地")),
                flet.DataColumn(flet.Text("百度")),
            ]
        )
        # 保存拼音不同的记录
        self.table_rows = []
        # 选择模板
        self.file_template = flet.FilePicker(on_result=self.pick_file_result)
        # 注音按钮
        self.zhuyin_btn = flet.ElevatedButton('注音', disabled=True, icon=flet.icons.SAVE, on_click=self.generate_pinyin)

    def build(self):
        self.page.overlay.append(self.file_template)
        return flet.Column(controls=[
            flet.Row(
                controls=[
                    flet.Text('声母: ', size=20),
                    flet.Text('\t'.join(initial_consonant_list), size=18)
                ]
            ),
            flet.Column(
                controls=[
                    flet.Text('韵母(24个): ', size=20),
                    flet.Row(
                        controls=[
                            flet.Text('单韵母(6个): ', size=18),
                            flet.Text('\t'.join(list_of_vowels[0:6]), size=18)
                        ]
                    ),
                    flet.Row(
                        controls=[
                            flet.Text('复韵母(8个): ', size=18),
                            flet.Text('\t'.join(list_of_vowels[6:14]), size=18)
                        ]
                    ),
                    flet.Row(
                        controls=[
                            flet.Text('特殊元音韵母(1个): ', size=18),
                            flet.Text(list_of_vowels[14], size=18)
                        ]
                    ),
                    flet.Row(
                        controls=[
                            flet.Text('前鼻韵母(5个): ', size=18),
                            flet.Text('\t'.join(list_of_vowels[15:20]), size=18)
                        ]
                    ),
                    flet.Row(
                        controls=[
                            flet.Text('后鼻韵母(4个): ', size=18),
                            flet.Text('\t'.join(list_of_vowels[20:]), size=18)
                        ]
                    ),
                ]
            ),
            # 分割器
            flet.Divider(height=3, color=flet.colors.BROWN_50),
            flet.Text(value='请输入要注音的汉字: ', size=20),
            self.content,
            flet.Row(
                controls=[
                    flet.ElevatedButton('选择模板...', icon=flet.icons.UPLOAD_FILE, on_click=self.select_template),
                    self.zhuyin_btn
                ],
                alignment=flet.MainAxisAlignment.END
            ),
            self.table,
        ])

    def pick_file_result(self, e: flet.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                self.template_path = file.path
                print(f'名称:{file.name}, 大小: {file.size}')
        self.zhuyin_btn.disabled = False
        self.update()

    def select_template(self, e):
        self.file_template.pick_files(dialog_title='选择拼音模板', initial_directory='.', allowed_extensions=['doc', 'docx'])

    def generate_pinyin(self, e):
        """
        点击"拼音"按钮事件
        :param e:
        :return:
        """
        txt = self.content.value
        # 输出所有的词语
        print(txt)
        self.word_2_pinyin(txt)
        # 表格赋值
        self.table.visible = True
        self.table.rows.extend(self.table_rows)
        self.update()

        def close_dlg(e):
            dialog.open = False
            os.startfile(pathlib.Path.home())  # windows平台打开指定的目录
            self.page.update()

        # 弹框提示word生成路径
        dialog = flet.AlertDialog(
            title=flet.Text('生成文档路径'),
            actions=[
                flet.TextButton("确定", on_click=close_dlg)
            ],
            actions_alignment=flet.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.content =flet.Text(self.word_doc_path)
        dialog.open = True
        self.page.update()

    def word_2_pinyin(self, ciyu):
        """
        词组或汉字转拼音
        """
        # 读取模板
        doc = flet.DocxTemplate(self.template_path)
        # 保存汉字和拼音列表结果
        py_hz = []
        all_words = [item for item in ciyu.strip().replace('\n', ' ').split(" ") if item]  # 去掉换行符,并用空格分割
        line_word_num = 7  # 每行词组个数
        for j in range(1, math.ceil(len(all_words) / line_word_num) + 1):
            word_5 = all_words[line_word_num * (j - 1):line_word_num * j]
            row_1 = {}
            for i in range(len(word_5)):
                py = lazy_pinyin(word_5[i], style='Style.TONE')
                baidu_pinyin = chinese_2_pinyin(word_5[i], 'BAIDU', True)
                if baidu_pinyin and baidu_pinyin == ' '.join(py):
                    pass
                else:
                    self.table_rows.append(flet.DataRow(
                        cells=[
                            flet.DataCell(flet.Text(word_5[i])),
                            flet.DataCell(flet.Text(' '.join(py), selectable=True)),
                            flet.DataCell(flet.Text(baidu_pinyin, selectable=True)),
                        ]))
                if pinyin_start_valid(py[0]):
                    row_1[f'p{i + 1}1'] = py[0][0:2]
                    row_1[f'p{i + 1}2'] = py[0][2:]
                else:
                    row_1[f'p{i + 1}1'] = py[0][0]
                    row_1[f'p{i + 1}2'] = py[0][1:]

                if pinyin_start_valid(py[1]):
                    row_1[f'p{i + 1}3'] = py[1][0:2]
                    row_1[f'p{i + 1}4'] = py[1][2:]
                else:
                    row_1[f'p{i + 1}3'] = py[1][0]
                    row_1[f'p{i + 1}4'] = py[1][1:]
                max_len = max([len(i) for i in py])
                if max_len > 3:
                    row_1[f'h{i + 1}'] = '  '.join(list(word_5[i]))
                elif max_len > 2:
                    row_1[f'h{i + 1}'] = ' '.join(list(word_5[i]))
            py_hz.append(row_1)
        # 需要传入的字典， 需要在word对应的位置输入 {{ first_py }}
        context = {"items": py_hz}
        doc.render(context)  # 渲染到模板中
        # 生成文档
        self.word_doc_path = f"{pathlib.Path.home()}{os.sep}拼音在汉字上面(表格).docx"
        doc.save(self.word_doc_path)


def pinyin_start_valid(pinyin):
    """判断拼音是否以zh,ch,sh开头"""
    return pinyin.startswith('zh') or pinyin.startswith('ch') or pinyin.startswith('sh')


def main(page: flet.Page):
    # 标题
    page.title = '生成汉字拼音工具v1.0'
    page.window_width = 800
    page.window_height = 700
    # 居中
    page.window_center()

    app = Chinese2PinYin(page)

    page.add(app)


if __name__ == '__main__':
    flet.app(target=main, assets_dir='assets')

