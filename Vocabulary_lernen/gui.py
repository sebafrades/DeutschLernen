from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QStackedWidget,
)

from PySide6.QtGui import QShortcut, QKeySequence, QPixmap
from PySide6.QtCore import Qt

from trainer import Trainer

from Vocabulary import (
    Vocabulary_Nicos_Weg_A2_0,
    Vocabulary_Nicos_Weg_A2_1,
    Vocabulary_Nicos_Weg_A2_2,
    Vocabulary_Nicos_Weg_A2_3,
    Vocabulary_Nicos_Weg_A2_4,
    Vocabulary_Nicos_Weg_A2_7,
    Grammatik_Aktiv,
)

ALL_SUBCHAPTERS = "All Subchapters"
ALL_TOPICS = "All Topics"

SOURCE_NICOS_WEG = "Nico's Weg"
SOURCE_GRAMMATIK_AKTIV = "Grammatik Aktiv"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("German Vocabulary Trainer")
        self.resize(500, 340)

        # ==================================================
        # VOCABULARIES
        # ==================================================

        # Nico's Weg: {chapter_name: {subchapter_name: [Word, ...]}}
        self.nicos_weg_chapters = {
            "Chapter 0": Vocabulary_Nicos_Weg_A2_0,
            "Chapter 1": Vocabulary_Nicos_Weg_A2_1,
            "Chapter 2": Vocabulary_Nicos_Weg_A2_2,
            "Chapter 3": Vocabulary_Nicos_Weg_A2_3,
            "Chapter 4": Vocabulary_Nicos_Weg_A2_4,
            "Chapter 7": Vocabulary_Nicos_Weg_A2_7,
        }

        # Grammatik Aktiv: {topic_name: [Word, ...]} -- flat, no subchapters
        self.grammatik_aktiv = Grammatik_Aktiv

        self.trainer = None
        self.current_word = None

        # ==================================================
        # MODE MENU
        # ==================================================

        self.mode_menu = QComboBox()

        self.mode_menu.addItems([
            "Consecutive",
            "Random",
            "Image Game"
        ])

        self.mode_menu.model().item(2).setEnabled(False)

        self.current_mode = None

        # ==================================================
        # STACKED WIDGET
        # ==================================================

        self.pages = QStackedWidget()

        self.setCentralWidget(self.pages)

        # ==================================================
        # SELECTION PAGE
        # ==================================================

        self.selection_page = QWidget()

        selection_layout = QVBoxLayout()

        # ---------- Source ----------

        self.source_menu = QComboBox()
        self.source_menu.addItems([SOURCE_NICOS_WEG, SOURCE_GRAMMATIK_AKTIV])
        self.source_menu.currentTextChanged.connect(self.update_chapters)

        source_label = QLabel("Source")

        selection_layout.addWidget(source_label)
        selection_layout.addWidget(self.source_menu)

        # ---------- Chapter / Topic ----------

        self.chapter_menu = QComboBox()
        self.chapter_menu.currentTextChanged.connect(self.update_subchapters)

        self.chapter_label = QLabel("Chapter")

        selection_layout.addWidget(self.chapter_label)
        selection_layout.addWidget(self.chapter_menu)

        # ---------- Subchapter ----------

        self.subchapter_menu = QComboBox()

        self.subchapter_label = QLabel("Subchapter")

        selection_layout.addWidget(self.subchapter_label)
        selection_layout.addWidget(self.subchapter_menu)

        # ---------- Mode ----------

        mode_label = QLabel("Mode")

        selection_layout.addWidget(mode_label)
        selection_layout.addWidget(self.mode_menu)

        # ---------- Start ----------

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_trainer)

        selection_layout.addWidget(self.start_button)

        self.selection_page.setLayout(selection_layout)

        self.pages.addWidget(self.selection_page)

        # Populate chapter/subchapter for the initially selected source
        self.update_chapters(self.source_menu.currentText())

        # ==================================================
        # TRAINER PAGE
        # ==================================================

        self.trainer_page = QWidget()

        trainer_layout = QVBoxLayout()

        # ---------- Word ----------

        self.wordLabel = QLabel()
        self.wordLabel.setAlignment(Qt.AlignCenter)
        self.wordLabel.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            padding: 15px;
        """)

        trainer_layout.addWidget(self.wordLabel)

        # ---------- Image ----------

        self.imageLabel = QLabel()
        self.imageLabel.setFixedSize(400, 250)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setStyleSheet("""
            border: 1px solid #555;
            background-color: #2d2d2d;
        """)

        imageLayout = QHBoxLayout()
        imageLayout.addStretch()
        imageLayout.addWidget(self.imageLabel)
        imageLayout.addStretch()

        trainer_layout.addLayout(imageLayout)

        # ---------- Answer ----------

        self.answerBox = QLineEdit()
        self.answerBox.setPlaceholderText("Type the translation")

        trainer_layout.addWidget(self.answerBox)

        # ---------- Buttons ----------

        self.checkButton = QPushButton("Check")

        self.showAnswerButton = QPushButton("Show Answer")
        self.showAnswerButton.setEnabled(False)

        buttonLayout = QHBoxLayout()

        buttonLayout.addWidget(self.checkButton)
        buttonLayout.addWidget(self.showAnswerButton)

        trainer_layout.addLayout(buttonLayout)

        # ---------- Result ----------

        self.resultLabel = QLabel()
        self.resultLabel.setAlignment(Qt.AlignCenter)

        trainer_layout.addWidget(self.resultLabel)

        # ---------- Example ----------

        self.exampleLabel = QLabel()
        self.exampleLabel.setAlignment(Qt.AlignCenter)
        self.exampleLabel.setWordWrap(True)
        self.exampleLabel.setStyleSheet("""
            font-size: 20px;
            color: #aaa;
            font-style: italic;
        """)

        trainer_layout.addWidget(self.exampleLabel)

        # ---------- Next ----------

        self.nextButton = QPushButton("Next")
        self.nextButton.setEnabled(False)

        trainer_layout.addWidget(self.nextButton)

        # ---------- Retry Missed ----------

        self.retryMissedButton = QPushButton("Retry Missed Words")
        self.retryMissedButton.setEnabled(False)
        self.retryMissedButton.hide()

        trainer_layout.addWidget(self.retryMissedButton)

        # ---------- Back to Menu ----------

        self.backToMenuButton = QPushButton("Back to Menu")
        self.backToMenuButton.setEnabled(False)
        self.backToMenuButton.hide()

        trainer_layout.addWidget(self.backToMenuButton)

        self.trainer_page.setLayout(trainer_layout)

        self.pages.addWidget(self.trainer_page)

        # Start on selection page
        self.pages.setCurrentWidget(self.selection_page)

        # ==================================================
        # STYLE
        # ==================================================

        self.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }

        QWidget {
            background-color: #1e1e1e;
            color: white;
        }

        QLabel {
            color: white;
            font-size: 18px;
        }

        QLineEdit {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 8px;
            font-size: 18px;
        }

        QComboBox {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 8px;
            font-size: 18px;
        }

        QPushButton {
            background-color: #3c3c3c;
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-size: 16px;
        }

        QPushButton:hover {
            background-color: #505050;
        }

        QPushButton:disabled {
            background-color: #222;
            color: #666;
        }
        """)

        # ==================================================
        # CONNECTIONS
        # ==================================================

        self.checkButton.clicked.connect(self.check_answer)
        self.showAnswerButton.clicked.connect(self.show_answer)
        self.nextButton.clicked.connect(self.next_question)
        self.retryMissedButton.clicked.connect(self.retry_missed_words)
        self.backToMenuButton.clicked.connect(self.back_to_menu)

        self.answerBox.returnPressed.connect(self.check_answer)

        QShortcut(
            QKeySequence("Ctrl+Return"),
            self,
            activated=self.show_answer
        )

        QShortcut(
            QKeySequence("Ctrl+Enter"),
            self,
            activated=self.show_answer
        )

        QShortcut(
            QKeySequence("Ctrl+Shift+N"),
            self,
            activated=self.next_question
        )

    # ==================================================
    # SELECTION PAGE LOGIC
    # ==================================================

    def update_chapters(self, source_name):
        """Refill the chapter/topic dropdown whenever the source changes."""

        self.chapter_menu.blockSignals(True)
        self.chapter_menu.clear()
        self.chapter_menu.blockSignals(False)

        if source_name == SOURCE_NICOS_WEG:

            self.chapter_label.setText("Chapter")

            self.subchapter_label.show()
            self.subchapter_menu.show()
            self.subchapter_menu.setEnabled(True)

            self.chapter_menu.addItems(self.nicos_weg_chapters.keys())

        else:

            self.chapter_label.setText("Topic")

            self.subchapter_menu.clear()
            self.subchapter_label.hide()
            self.subchapter_menu.hide()
            self.subchapter_menu.setEnabled(False)

            self.chapter_menu.addItem(ALL_TOPICS)
            self.chapter_menu.addItems(self.grammatik_aktiv.keys())

    def update_subchapters(self, chapter_name):
        """Refill the subchapter dropdown whenever the chapter selection changes.

        Only relevant for Nico's Weg; Grammatik Aktiv has no subchapters.
        """

        if not chapter_name:
            return

        if self.source_menu.currentText() != SOURCE_NICOS_WEG:
            return

        vocabulary_dict = self.nicos_weg_chapters.get(chapter_name)

        if vocabulary_dict is None:
            return

        self.subchapter_menu.clear()
        self.subchapter_menu.addItem(ALL_SUBCHAPTERS)
        self.subchapter_menu.addItems(vocabulary_dict.keys())

    # ==================================================
    # TRAINER LOGIC
    # ==================================================

    def start_trainer(self):

        selected_source = self.source_menu.currentText()

        if selected_source == SOURCE_NICOS_WEG:

            selected_chapter = self.chapter_menu.currentText()
            selected_subchapter = self.subchapter_menu.currentText()

            vocabulary_dict = self.nicos_weg_chapters[selected_chapter]

            if selected_subchapter == ALL_SUBCHAPTERS:
                words = [word for words in vocabulary_dict.values() for word in words]
            else:
                words = vocabulary_dict[selected_subchapter]

        else:

            selected_topic = self.chapter_menu.currentText()

            if selected_topic == ALL_TOPICS:
                words = [word for words in self.grammatik_aktiv.values() for word in words]
            else:
                words = self.grammatik_aktiv[selected_topic]

        self.current_mode = self.mode_menu.currentText()

        self.trainer = Trainer(words)

        self.answerBox.setEnabled(True)
        self.checkButton.setEnabled(True)
        self.retryMissedButton.hide()
        self.retryMissedButton.setEnabled(False)
        self.backToMenuButton.hide()
        self.backToMenuButton.setEnabled(False)

        self.pages.setCurrentWidget(self.trainer_page)

        if self.current_mode == "Consecutive":
            self.next_word()

        elif self.current_mode == "Random":
            self.random_word()

    def display_word(self, word):

        self.current_word = word

        self.wordLabel.setText(word.question)

        if word.image:

            from pathlib import Path

            image_path = Path(__file__).parent / word.image
            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():

                self.imageLabel.setPixmap(
                    pixmap.scaled(
                        self.imageLabel.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )

                self.imageLabel.show()

            else:

                self.imageLabel.clear()
                self.imageLabel.hide()

        else:

            self.imageLabel.clear()
            self.imageLabel.hide()

        self.answerBox.clear()
        self.answerBox.setFocus()

        self.resultLabel.clear()
        self.exampleLabel.clear()

        self.showAnswerButton.setEnabled(False)
        self.nextButton.setEnabled(False)

    def next_word(self):

        word = self.trainer.next_word()

        if word is None:
            self.end_game()
            return

        self.display_word(word)

    def random_word(self):

        word = self.trainer.random_word()

        self.display_word(word)

    def check_answer(self):

        answer = self.answerBox.text().strip()

        if answer.lower() == self.current_word.answer.lower():

            self.current_word.correct += 1

            self.resultLabel.setText("✔ Correct!")

            if self.current_word.example:
                self.exampleLabel.setText(f"Example: {self.current_word.example}")

            self.nextButton.setEnabled(True)

        else:

            self.current_word.wrong += 1

            self.resultLabel.setText("✘ Wrong! Try again.")

            self.showAnswerButton.setEnabled(True)

            self.answerBox.clear()
            self.answerBox.setFocus()

    def show_answer(self):

        self.trainer.mark_missed(self.current_word)

        self.resultLabel.setText(
            f"Answer: {self.current_word.answer}"
        )

        if self.current_word.example:
            self.exampleLabel.setText(f"Example: {self.current_word.example}")

        self.nextButton.setEnabled(True)

    def next_question(self):

        if self.current_mode == "Consecutive":
            self.next_word()

        elif self.current_mode == "Random":
            self.random_word()

    def end_game(self):

        self.wordLabel.setText("Vocabulary complete!")
        self.imageLabel.clear()
        self.imageLabel.hide()

        self.answerBox.clear()
        self.answerBox.setEnabled(False)

        self.checkButton.setEnabled(False)
        self.showAnswerButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.exampleLabel.clear()

        self.backToMenuButton.setEnabled(True)
        self.backToMenuButton.show()

        if self.trainer.has_missed_words():
            count = len(self.trainer.missed_words)
            self.resultLabel.setText(f"{count} word(s) missed.")
            self.retryMissedButton.setEnabled(True)
            self.retryMissedButton.show()
        else:
            self.resultLabel.setText("Perfect run!")
            self.retryMissedButton.hide()

    def retry_missed_words(self):

        self.trainer.retry_missed()

        self.answerBox.setEnabled(True)
        self.checkButton.setEnabled(True)
        self.retryMissedButton.hide()
        self.retryMissedButton.setEnabled(False)
        self.backToMenuButton.hide()
        self.backToMenuButton.setEnabled(False)

        self.next_word()

    def back_to_menu(self):

        self.trainer = None
        self.current_word = None
        self.current_mode = None

        self.retryMissedButton.hide()
        self.retryMissedButton.setEnabled(False)
        self.backToMenuButton.hide()
        self.backToMenuButton.setEnabled(False)

        self.pages.setCurrentWidget(self.selection_page)