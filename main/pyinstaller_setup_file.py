import PyInstaller.__main__

PyInstaller.__main__.run([
    'credoware.py',
    '--onedir',
    '--windowed',
    '--icon=icon.ico',
    '--name= CredoWare',
    '--add-data=logo.png;.',
    '--add-data=csl_series_logger_manual.pdf;.',
    '--add-data=reload.png;.',

    '--hidden-import=pandas',
    '--hidden-import=svglib',
    '--hidden-import=reportlab',
    '--hidden-import=matplotlib',
    '--hidden-import=numpy',
    '--hidden-import=PyQt5',
    '--hidden-import=pyqtgraph',
    '--hidden-import=pyserial',
    '--hidden-import=semantic_version'

])