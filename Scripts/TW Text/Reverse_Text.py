# FLM: Reverse Text
# Python script for FontLab 7
# By Adam Twardoch & Vassil Kateliev, 2021-07-05
# Licensed at your choice under:
# - CC-0 (public domain)
# - MIT license, Copyright (c) 2021 Adam Twardoch, Vassil Kateliev

# Get general data
import fontlab as fl6

items = fl6.flItems
app = fl6.flWorkspace.instance()  # active workspace


def processLine(sym_line):
    """Reverses symbols in line"""
    new_line = list(reversed(sym_line))
    return new_line


def processSymbols(symbols):
    """Iterates through symbols, splits into lines, processes each line"""
    symbols_new = []
    sym_line = []
    for symi, sym in enumerate(symbols.symbols()):
        if sym.cr:
            sym_line = processLine(sym_line)
            sym_line.append(sym)
            symbols_new += sym_line
            sym_line = []
        else:
            sym_line.append(sym)
            if symi == len(symbols) - 1:
                sym_line = processLine(sym_line)
    symbols_new += sym_line
    return fl6.fgSymbolList(symbols_new)


def main():
    # Get current text block
    canvas = app.getCanvasUnderCursor()  # current canvas
    block = canvas.textBlocks()[0]  # first flTextBlock
    symbols = block.symbolList()  # fgSymbolList
    symbols = processSymbols(symbols)
    items.requestContent(symbols, 0)  # Update symbols in UI


main()
