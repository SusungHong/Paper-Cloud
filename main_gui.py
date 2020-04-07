import parse_pdf
import embed
import os
import sys
import json
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class MainWidget(QWidget):

    def __init__(self):

        super().__init__()

        # Set window title
        self.setWindowTitle("Paper Cloud")

        # Top form box
        formbox = QHBoxLayout()
        self.setLayout(formbox)

        # Left and right box
        leftbox = QVBoxLayout()
        rightbox = QVBoxLayout()

        # Search box
        sform = QFrame()
        leftbox.addWidget(sform)

        box = QHBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        sform.setLayout(box)

        self.search_edit = QLineEdit()
        search_button = QPushButton("Search")

        self.search_edit.setPlaceholderText("Search")
        box.addWidget(self.search_edit)

        search_button.clicked.connect(self.search_btn_clicked)
        box.addWidget(search_button)

        # Paper-info box
        self.pdf_label = QLabel("PDF Name:")
        extract_btn = QPushButton('Extract Information')
        extract_btn.clicked.connect(self.extract_btn_clicked)
        leftbox.addWidget(self.pdf_label)
        leftbox.addWidget(extract_btn)

        title_label = QLabel("Title")
        self.title_edit = QLineEdit()
        author_label = QLabel("Authors")
        self.author_edit = QLineEdit()
        abstract_label = QLabel("Abstract")
        self.abstract_edit = QPlainTextEdit()
        leftbox.addWidget(title_label)
        leftbox.addWidget(self.title_edit)
        leftbox.addWidget(author_label)
        leftbox.addWidget(self.author_edit)
        leftbox.addWidget(abstract_label)
        leftbox.addWidget(self.abstract_edit)

        save_info_btn = QPushButton("Edit Info")
        save_info_btn.clicked.connect(self.save_info_btn_clicked)
        leftbox.addWidget(save_info_btn)

        emb_label = QLabel("Embeddings")
        leftbox.addWidget(emb_label)

        # Re-embed box
        rform = QFrame()
        leftbox.addWidget(rform)

        box = QHBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        rform.setLayout(box)

        self.reembed_combo = QComboBox()
        for i in range(2, 10):
            self.reembed_combo.addItem(str(i))
        self.reembed_combo.setCurrentIndex(3)
        box.addWidget(self.reembed_combo)

        reembed_btn = QPushButton("Re-Embed")
        reembed_btn.clicked.connect(self.reembed_btn_clicked)
        box.addWidget(reembed_btn)

        # Save embedding button
        saveembed_btn = QPushButton("Save Embedding and Paper Info")
        saveembed_btn.clicked.connect(self.saveembed_btn_clicked)
        leftbox.addWidget(saveembed_btn)

        leftbox.addStretch(1)

        # Add graphics view in the right box
        self.view = GraphView(self)
        rightbox.addWidget(self.view)

        # Arrange left and right boxes
        formbox.addLayout(leftbox)
        formbox.addLayout(rightbox)

        formbox.setStretchFactor(leftbox, 0)
        formbox.setStretchFactor(rightbox, 1)

        self.setGeometry(100, 100, 1250, 900)

    def search_btn_clicked(self):
        search_str = self.search_edit.text()
        self.view.select_searched(search_str)

    def save_info_btn_clicked(self):
        if len(self.view.selected_inx) > 0:
            self.view.titles[self.view.selected_inx[0]] = self.title_edit.text()
            self.view.authors[self.view.selected_inx[0]] = self.author_edit.text()
            self.view.abstracts[self.view.selected_inx[0]] = self.abstract_edit.toPlainText()

    def reembed_btn_clicked(self):
        self.view.df = parse_pdf.make_union_df(self.view.paper_word_counts)
        self.view.embedding = embed.tsne(self.view.df, int(self.reembed_combo.currentText()))
        self.view.prev_pos = QPointF(0, 0)
        self.view.selected_inx = []
        self.view.redraw()

    def saveembed_btn_clicked(self):
        self.view.save_embedding_csv()

    def extract_btn_clicked(self):
        if len(self.view.selected_inx) > 0:
            inx = self.view.selected_inx[0]
            pdf = self.view.pdf_names[inx]
            meta = parse_pdf.extract_metadata(os.path.join(self.view.base_path, pdf))
            self.view.titles[inx] = meta['Title']
            self.view.authors[inx] = meta['Author']
            self.view.abstracts[inx] = meta['Abstract']
            self.title_edit.setText(meta['Title'])
            self.author_edit.setText(meta['Author'])
            self.abstract_edit.setPlainText(meta['Abstract'])

    def closeEvent(self, e):
        # Save the data
        self.view.save_embedding_csv()
        e.accept()


# QGraphicsView displaying QGraphicsScene
class GraphView(QGraphicsView):

    def __init__(self, parent):

        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.ellipses = []
        self.texts = []
        self.selected_inx = []  # index of the selected nodes

        self.setRenderHint(QPainter.HighQualityAntialiasing)

        # Set base path to research papers
        self.base_path = 'papers/'
        self.pdf_names = []
        self.paper_word_counts = []
        self.titles = []
        self.authors = []
        self.abstracts = []

        self.df = None
        self.embedding = None

        emb, nl, tl, aul, abl, wcl = self.read_embedding_csv()
        if emb is None:
            # No well-formatted csv
            # Initialize variables
            self.init_file_variables()
            # Get the embedding
            self.embedding = embed.tsne(self.df, 5)
        else:
            # Initialize variables
            self.embedding = emb
            self.pdf_names = nl.tolist()
            self.titles = tl.tolist()
            self.authors = aul.tolist()
            self.abstracts = abl.tolist()
            self.paper_word_counts = wcl
            # Find new/deleted files
            curr_lst = []
            for file in os.listdir(self.base_path):
                if file.endswith(".pdf"):
                    curr_lst.append(file)
            prev_lst = nl
            new = set(curr_lst) - set(prev_lst)
            deleted = set(prev_lst) - set(curr_lst)
            for deleted_name in deleted:
                del_inx = self.pdf_names.index(deleted_name)
                self.embedding = self.embedding.drop(del_inx).reset_index(drop=True)
                del self.pdf_names[del_inx]
                del self.titles[del_inx]
                del self.authors[del_inx]
                del self.abstracts[del_inx]
                del self.paper_word_counts[del_inx]
            for new_name in new:
                self.pdf_names.append(new_name)
                self.titles.append("")
                self.authors.append("")
                self.abstracts.append("")
                full_txt = parse_pdf.extract_text(os.path.join(self.base_path, new_name))
                self.paper_word_counts.append(parse_pdf.count_word(full_txt))
                nne = embed.new_node_embedding(self.embedding, self.paper_word_counts)
                self.embedding = self.embedding.append(nne, ignore_index=True)

        self.prev_pos = QPointF(0, 0)

        self.rubber_origin = QPoint()
        self.rubber = QRectF()
        self.rubber_item = None
        self.rubber_mode = False
        '''
        pairwise_max_word = np.empty([len(df), len(df)], dtype="U25")
        for i in range(len(df)):
            for j in range(len(df)):
                if i <= j:
                    break
                else:
                    mult_freq = df.loc[i][:] * df.loc[j][:]
                    pairwise_max_word[i][j] = mult_freq.idxmax()
        print(pairwise_max_word)
        '''

    def init_file_variables(self):
        # Get all words and merge it into a dataframe
        self.paper_word_counts = []
        self.pdf_names = []
        for file in os.listdir(self.base_path):
            if file.endswith(".pdf"):
                self.pdf_names.append(file)
                self.titles.append("")
                self.authors.append("")
                self.abstracts.append("")
                full_txt = parse_pdf.extract_text(os.path.join(self.base_path, file))
                self.paper_word_counts.append(parse_pdf.count_word(full_txt))
        df = parse_pdf.make_union_df(self.paper_word_counts)
        self.df = embed.preprocess(df)

    def moveEvent(self, e):

        self.redraw()

    def redraw(self):

        rect = QRectF(self.rect())
        rect.adjust(0, 0, -2, -2)

        self.scene.setSceneRect(rect)

        # Display embedding
        w = rect.width()
        h = rect.height()

        # Adjust embedding
        min1 = self.embedding['t-SNE 1'].min()
        min2 = self.embedding['t-SNE 2'].min()
        max1 = self.embedding['t-SNE 1'].max()
        max2 = self.embedding['t-SNE 2'].max()
        scale_factor1 = w * 0.8 / (max1 - min1)
        scale_factor2 = h * 0.8 / (max2 - min2)
        self.embedding['t-SNE 1'] = (self.embedding['t-SNE 1'] - min1) * scale_factor1 + 0.1 * w
        self.embedding['t-SNE 2'] = (self.embedding['t-SNE 2'] - min2) * scale_factor2 + 0.1 * h

        pen = QPen(QColor(100, 100, 100), 3)
        brush = QBrush(QColor(0, 255, 255))

        if len(self.ellipses) > 0:
            self.ellipses = []
            self.texts = []
            self.scene.clear()

        for i in range(len(self.embedding)):
            if i in self.selected_inx:
                brush = QBrush(QColor(255, 0, 0))
                font = QFont("consolas", 10, QFont.Bold)
            else:
                brush = QBrush(QColor(0, 255, 255))
                font = QFont("consolas", 10)
            rect = QRectF(QPointF(self.embedding.loc[i][0] - 7, self.embedding.loc[i][1] - 7),
                          QPointF(self.embedding.loc[i][0] + 7, self.embedding.loc[i][1] + 7))
            self.ellipses.append(self.scene.addEllipse(rect, pen, brush))
            text = self.scene.addText(self.pdf_names[i], font)
            text.setDefaultTextColor(QColor(100, 100, 100))
            text.setPos(QPointF(self.embedding.loc[i][0] - 40, self.embedding.loc[i][1] - 35))
            self.texts.append(text)

    def updateSelectedIndexDisplay(self):
        if len(self.selected_inx) > 0:
            first_inx = self.selected_inx[0]
            self.parent().pdf_label.setText("PDF Name:\n" + self.pdf_names[first_inx])
            self.parent().title_edit.setText(str(self.titles[first_inx]))
            self.parent().author_edit.setText(str(self.authors[first_inx]))
            self.parent().abstract_edit.setPlainText(str(self.abstracts[first_inx]))
        for i in range(len(self.ellipses)):
            if i in self.selected_inx:
                self.ellipses[i].setBrush(QBrush(QColor(255, 0, 0)))
                self.texts[i].setDefaultTextColor(QColor(0, 0, 0))
                self.texts[i].setFont(QFont("consolas", 10, QFont.Bold))
            else:
                self.ellipses[i].setBrush(QBrush(QColor(0, 255, 255)))
                self.texts[i].setDefaultTextColor(QColor(100, 100, 100))
                self.texts[i].setFont(QFont("consolas", 10))

    def mousePressEvent(self, e):

        modifiers = QApplication.keyboardModifiers()

        if e.button() == Qt.LeftButton:
            if modifiers == Qt.ControlModifier:
                # Find the clicked item
                clicked_item = self.itemAt(e.pos())
                if clicked_item is None:
                    # Set rubber mode
                    pen = QPen(QColor(100, 100, 100), 3)
                    brush = QBrush(QColor(0, 0, 255, 128))
                    self.rubber_mode = True
                    self.rubber_origin = e.pos()
                    rubber = QRectF(e.pos(), QSizeF())
                    self.rubber_item = self.scene.addRect(rubber, pen, brush)
                    return None
                t = clicked_item.type()
                if t == 4:  # Ellipse
                    i = self.ellipses.index(clicked_item)
                    if i in self.selected_inx:
                        self.selected_inx.remove(i)
                        self.updateSelectedIndexDisplay()
                    else:
                        self.selected_inx.append(i)
                        self.updateSelectedIndexDisplay()
                elif t == 8:  # Text
                    i = self.texts.index(clicked_item)
                    if i in self.selected_inx:
                        self.selected_inx.remove(i)
                        self.updateSelectedIndexDisplay()
                    else:
                        self.selected_inx.append(i)
                        self.updateSelectedIndexDisplay()
                self.prev_pos = e.pos()
            else:
                # Find the clicked item
                clicked_item = self.itemAt(e.pos())
                if clicked_item is None:
                    # Set rubber mode
                    self.selected_inx = []
                    self.updateSelectedIndexDisplay()
                    pen = QPen(QColor(100, 100, 100), 1)
                    brush = QBrush(QColor(0, 100, 150, 128))
                    self.rubber_mode = True
                    self.rubber_origin = e.pos()
                    rubber = QRectF(e.pos(), QSizeF(-1, -1))
                    self.rubber_item = self.scene.addRect(rubber, pen, brush)
                    return None
                t = clicked_item.type()
                if t == 4:  # Ellipse
                    i = self.ellipses.index(clicked_item)
                    if i in self.selected_inx:
                        pass
                    else:
                        self.selected_inx = [i]
                        self.updateSelectedIndexDisplay()
                elif t == 8:  # Text
                    i = self.texts.index(clicked_item)
                    if i in self.selected_inx:
                        pass
                    else:
                        self.selected_inx = [i]
                        self.updateSelectedIndexDisplay()
                self.prev_pos = e.pos()
        else:
            pass

    def mouseMoveEvent(self, e):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            return None

        # Compute delta and set next pos
        if e.buttons() & Qt.LeftButton:
            if (len(self.selected_inx) > 0) & (not self.rubber_mode):
                dx = e.pos().x() - self.prev_pos.x()
                dy = e.pos().y() - self.prev_pos.y()
                self.prev_pos = e.pos()
                for i in self.selected_inx:
                    r = self.ellipses[i].rect()
                    r.translate(dx, dy)
                    self.embedding.loc[i][0] = r.center().x()
                    self.embedding.loc[i][1] = r.center().y()
                    self.ellipses[i].setRect(r)
                    self.texts[i].setPos(self.texts[i].pos() + QPointF(dx, dy))
            elif self.rubber_mode:
                # Adjust rubber
                self.rubber_item.setRect(QRectF(self.rubber_origin, e.pos()).normalized())

    def mouseReleaseEvent(self, e):
        # Select ellipses contained in rubber
        if self.rubber_mode:
            self.rubber_mode = False
            for i in range(len(self.ellipses)):
                if self.rubber_item.rect().contains(self.ellipses[i].rect()):
                    if i not in self.selected_inx:
                        self.selected_inx.append(i)
                        self.updateSelectedIndexDisplay()
            self.scene.removeItem(self.rubber_item)

    def mouseDoubleClickEvent(self, e):
        # Find the clicked item
        clicked_item = self.itemAt(e.pos())
        if clicked_item is None:
            return None
        t = clicked_item.type()

        i = 0
        if t == 4:
            i = self.ellipses.index(clicked_item)
        elif t == 8:
            i = self.texts.index(clicked_item)

        if i in self.selected_inx:
            for inx in self.selected_inx:
                os.startfile(os.path.join(self.base_path, self.pdf_names[inx]).replace('/', '\\'))
        else:
            os.startfile(os.path.join(self.base_path, self.pdf_names[i]).replace('/', '\\'))

    def read_embedding_csv(self):
        # Read embedding csv file if exists
        if os.path.isfile("embedding.csv"):
            embedding = pd.read_csv("embedding.csv", index_col=0)
            # Check if the csv is well-typed
            if len(embedding.columns) == 7:
                if (embedding.columns[0] == 't-SNE 1') \
                        & (embedding.columns[1] == 't-SNE 2') \
                        & (embedding.columns[2] == 'File name') \
                        & (embedding.columns[3] == 'Title') \
                        & (embedding.columns[4] == 'Author') \
                        & (embedding.columns[5] == 'Abstract') \
                        & (embedding.columns[6] == 'Word Count'):
                    count_dicts = []
                    for dicstr in embedding['Word Count']:
                        count_dicts.append(json.loads(dicstr))
                    return embedding[['t-SNE 1', 't-SNE 2']], embedding['File name'].fillna(''), \
                           embedding['Title'].fillna(''), embedding['Author'].fillna(''), \
                           embedding['Abstract'].fillna(''), count_dicts
        return None, None, None, None, None, None

    def save_embedding_csv(self):
        wcsl = []
        for dic in self.paper_word_counts:
            wcsl.append(json.dumps(dic))
        concatenated = pd.concat([self.embedding,
                                  pd.Series(self.pdf_names, name='File name'),
                                  pd.Series(self.titles, name='Title'),
                                  pd.Series(self.authors, name='Author'),
                                  pd.Series(self.abstracts, name='Abstract'),
                                  pd.Series(wcsl, name='Word Count')],
                                 axis=1)
        concatenated.to_csv("embedding.csv", mode='w')

    def select_searched(self, search_str):
        indices = []
        for i in range(len(self.pdf_names)):
            if self.pdf_names[i].find(search_str) != -1:
                indices.append(i)
        if len(indices) > 0:
            self.selected_inx = indices
            self.updateSelectedIndexDisplay()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWidget()
    mw.show()
    sys.exit(app.exec_())
