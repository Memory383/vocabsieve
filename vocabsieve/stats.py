from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from operator import itemgetter

class StatisticsWindow(QDialog):
    def __init__(self, parent, src_name="Generic", path=None, methodname="generic"):
        super().__init__(parent)
        self.settings = parent.settings
        self.rec = parent.rec
        self.setWindowTitle(f"Statistics")
        self.tabs = QTabWidget()
        self.mlw = QWidget()  # Most looked up words
        self.known = QWidget()  # Known words
        self.tabs.resize(400, 500)
        self.tabs.addTab(self.mlw, "Most looked up words")
        self.initMLW()
        self.tabs.addTab(self.known, "Known words")
        self.initKnown()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)

    def initMLW(self):
        items = self.rec.countAllLemmaLookups(self.settings.value('target_language', 'en'))
        items = sorted(items, key=itemgetter(1), reverse=True) # Sort by counts, descending
        self.mlw.layout = QVBoxLayout(self.mlw)
        
        levels = [5, 8, 12, 20]
        level_prev = 1e9
        words_for_level = {}
        lws = {}
        for level in reversed(levels):
            count = 0
            #lws[level] = QListWidget()
            lws[level] = QLabel()
            lws[level].setWordWrap(True)
            #lws[level].setFlow(QListView.LeftToRight)
            #lws[level].setResizeMode(QListView.Adjust)
            #lws[level].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            #lws[level].setWrapping(True)
            content = ""
            for item in items:
                if level_prev > item[1] >= level and not item[0].startswith("http") and item[0]:
                    #lws[level].addItem(item[0])
                    content += item[0] + " "
                    count += 1
            lws[level].setText(content)
            self.mlw.layout.addWidget(QLabel(f"<h3>{level}+ lookups (<i>{count}</i>)</h3>"))
            self.mlw.layout.addWidget(lws[level])
            level_prev = level

    def initKnown(self):
        threshold = self.settings.value('tracking/known_threshold', 100) # Score needed to be considered known
        w_lookup = self.settings.value('tracking/w_lookup', 15) # Weight for each lookup, max 1 per day
        w_seen = self.settings.value('tracking/w_seen', 8) # W for seeing
        w_anki_ctx = self.settings.value('tracking/w_anki_ctx', 30) # W for being on context field of a mature card
        w_anki_word = self.settings.value('tracking/w_anki_word', 70) # W for being on the word field of a mature card
        w_anki_ctx_y = self.settings.value('tracking/w_anki_ctx_y', 20) # W for being on context field of a young card
        w_anki_word_y = self.settings.value('tracking/w_anki_word_y', 40) # W for being on the word field of a young card
        
        self.known.layout = QVBoxLayout(self.known)
        score = {}

        lookup_data = self.rec.countAllLemmaLookups(self.settings.value('target_language', 'en'))
        for word, count in lookup_data:
            score[word] = score.get(word, 0) + count * w_lookup

        # TODO implement the other three scoring sources
        seen_data = self.rec.getSeen(self.settings.value('target_language', 'en'))
        for word, count in seen_data:
            print(word,count)
            score[word] = score.get(word, 0) + count * w_seen

        known_words = [word for word, score in score.items() if score >= threshold and word.isalpha()]
        self.known.layout.addWidget(QLabel(f"<h3>Known words (<i>{len(known_words)}</i>)</h3>"))
        known_words_widget = QPlainTextEdit(" ".join(known_words))
        known_words_widget.setReadOnly(True)
        self.known.layout.addWidget(known_words_widget)